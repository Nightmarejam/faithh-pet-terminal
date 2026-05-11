#!/usr/bin/env python3
"""
Torbox Downloader - Bulk library acquisition via Torbox API
Downloads torrents through Torbox cloud service, then fetches to NAS.

Usage:
    python3 scripts/torbox_downloader.py add <magnet_or_file>
    python3 scripts/torbox_downloader.py list
    python3 scripts/torbox_downloader.py download <torrent_id> [--dest /path]
    python3 scripts/torbox_downloader.py download-all [--dest /path]
    python3 scripts/torbox_downloader.py status
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from urllib.parse import urlparse, unquote

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

TORBOX_API_KEY = os.environ.get("TORBOX_API_KEY", "1fab2e70-4cac-4c25-a6c5-4d6da6cb70f1")
TORBOX_BASE_URL = "https://api.torbox.app/v1/api"

# Default download destinations
NAS_DEST = Path("/mnt/x/learning_portal/torbox_downloads")
FALLBACK_DEST = Path("/mnt/e/torbox_downloads")

# Categories for organization
CATEGORIES = {
    "programming": ["programming", "python", "java", "rust", "javascript", "coding", "software", "algorithm"],
    "system_design": ["system design", "architecture", "distributed", "scalability", "microservices"],
    "electronics": ["electronics", "circuit", "arduino", "raspberry", "embedded", "pcb", "schematic"],
    "animal_care": ["animal", "veterinary", "pet", "livestock", "poultry", "goat", "chicken", "dog", "cat"],
    "permaculture": ["permaculture", "organic", "sustainable", "garden", "farming", "agriculture", "soil"],
    "landworks": ["earthworks", "excavation", "grading", "drainage", "landscaping", "land management"],
    "architecture": ["architecture", "house", "building", "construction", "blueprint", "floor plan"],
    "audio": ["audio", "sound", "recording", "mixing", "mastering", "acoustics", "synthesizer"],
    "other": []
}

# ─────────────────────────────────────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def api_request(method: str, endpoint: str, **kwargs) -> Dict:
    """Make authenticated API request to Torbox."""
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {TORBOX_API_KEY}"
    
    url = f"{TORBOX_BASE_URL}{endpoint}"
    
    try:
        response = requests.request(method, url, headers=headers, timeout=60, **kwargs)
        data = response.json()
        
        if not data.get("success", False):
            print(f"⚠ API Error: {data.get('detail', 'Unknown error')}")
        
        return data
    except requests.RequestException as e:
        return {"success": False, "error": str(e), "detail": str(e)}


def get_user_info() -> Dict:
    """Get current user/subscription info."""
    return api_request("GET", "/user/me")


def list_torrents() -> List[Dict]:
    """List all torrents in account."""
    result = api_request("GET", "/torrents/mylist")
    if result.get("success"):
        return result.get("data", [])
    return []


def add_torrent(magnet_or_file: str, name: str = None) -> Dict:
    """Add a torrent via magnet link or .torrent file."""
    if magnet_or_file.startswith("magnet:"):
        # Magnet link
        data = {"magnet": magnet_or_file}
        if name:
            data["name"] = name
        return api_request("POST", "/torrents/createtorrent", data=data)
    elif os.path.isfile(magnet_or_file):
        # .torrent file
        with open(magnet_or_file, "rb") as f:
            files = {"file": f}
            data = {}
            if name:
                data["name"] = name
            return api_request("POST", "/torrents/createtorrent", data=data, files=files)
    else:
        return {"success": False, "detail": "Invalid magnet link or file path"}


def get_torrent_info(torrent_id: int) -> Dict:
    """Get detailed info about a specific torrent."""
    result = api_request("GET", f"/torrents/mylist?id={torrent_id}")
    if result.get("success") and result.get("data"):
        return result["data"]
    return {}


def request_download_link(torrent_id: int, file_id: int = None, zip_link: bool = True) -> Dict:
    """Request a download link for a torrent or specific file."""
    params = {"token": TORBOX_API_KEY, "torrent_id": torrent_id, "zip_link": str(zip_link).lower()}
    if file_id is not None:
        params["file_id"] = file_id
    
    return api_request("GET", "/torrents/requestdl", params=params)


def control_torrent(torrent_id: int, operation: str) -> Dict:
    """Control torrent: pause, resume, delete."""
    return api_request("POST", "/torrents/controltorrent", 
                       data={"torrent_id": torrent_id, "operation": operation})


# ─────────────────────────────────────────────────────────────────────────────
# DOWNLOAD HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_destination() -> Path:
    """Find writable destination."""
    for dest in [NAS_DEST, FALLBACK_DEST]:
        try:
            dest.mkdir(parents=True, exist_ok=True)
            test_file = dest / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            return dest
        except Exception:
            pass
    return FALLBACK_DEST


def categorize_torrent(name: str) -> str:
    """Determine category based on torrent name."""
    name_lower = name.lower()
    for category, keywords in CATEGORIES.items():
        if any(kw in name_lower for kw in keywords):
            return category
    return "other"


def download_file(url: str, dest_path: Path, chunk_size: int = 8192) -> bool:
    """Download a file from URL to destination."""
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with requests.get(url, stream=True, timeout=300) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            downloaded = 0
            
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = (downloaded / total) * 100
                        print(f"\r  Downloading: {pct:.1f}% ({downloaded / 1024 / 1024:.1f} MB)", end="")
            
            print()  # newline after progress
            return True
    except Exception as e:
        print(f"\n  ✗ Download error: {e}")
        return False


def download_torrent(torrent_id: int, dest_base: Path = None) -> bool:
    """Download a completed torrent to local storage."""
    if dest_base is None:
        dest_base = get_destination()
    
    # Get torrent info
    torrents = list_torrents()
    torrent = next((t for t in torrents if t.get("id") == torrent_id), None)
    
    if not torrent:
        print(f"✗ Torrent {torrent_id} not found")
        return False
    
    name = torrent.get("name", f"torrent_{torrent_id}")
    status = torrent.get("download_state", "unknown")
    
    print(f"📦 {name}")
    print(f"   Status: {status}")
    
    if status not in ["completed", "uploading", "cached"]:
        print(f"   ⚠ Not ready for download (status: {status})")
        return False
    
    # Get download link
    result = request_download_link(torrent_id, zip_link=True)
    
    if not result.get("success"):
        print(f"   ✗ Failed to get download link: {result.get('detail')}")
        return False
    
    download_url = result.get("data")
    if not download_url:
        print("   ✗ No download URL returned")
        return False
    
    # Determine category and destination
    category = categorize_torrent(name)
    dest_dir = dest_base / category
    
    # Clean filename
    safe_name = "".join(c for c in name if c.isalnum() or c in " ._-")[:100]
    ext = ".zip" if "zip" in download_url.lower() else ""
    dest_path = dest_dir / f"{safe_name}{ext}"
    
    print(f"   Category: {category}")
    print(f"   Destination: {dest_path}")
    
    if dest_path.exists():
        print("   ⚠ Already downloaded, skipping")
        return True
    
    # Download
    success = download_file(download_url, dest_path)
    
    if success:
        size_mb = dest_path.stat().st_size / 1024 / 1024
        print(f"   ✓ Downloaded: {size_mb:.1f} MB")
    
    return success


# ─────────────────────────────────────────────────────────────────────────────
# CLI COMMANDS
# ─────────────────────────────────────────────────────────────────────────────

def cmd_status():
    """Show account status and subscription info."""
    result = get_user_info()
    if not result.get("success"):
        print(f"✗ Failed to get user info: {result.get('detail')}")
        return
    
    data = result.get("data", {})
    print("=" * 50)
    print("TORBOX ACCOUNT STATUS")
    print("=" * 50)
    print(f"Email: {data.get('email')}")
    print(f"Plan: {data.get('plan')} (Premium)")
    print(f"Expires: {data.get('premium_expires_at')}")
    print(f"Total Downloaded: {data.get('total_bytes_downloaded', 0) / 1024 / 1024 / 1024:.2f} GB")
    print(f"Torrents Downloaded: {data.get('torrents_downloaded', 0)}")


def cmd_list():
    """List all torrents in account."""
    torrents = list_torrents()
    
    if not torrents:
        print("No torrents found")
        return
    
    print("=" * 80)
    print(f"{'ID':<8} {'Status':<12} {'Size':<10} {'Name'}")
    print("=" * 80)
    
    for t in torrents:
        tid = t.get("id", "?")
        status = t.get("download_state", "unknown")[:10]
        size = t.get("size", 0) / 1024 / 1024
        name = t.get("name", "Unknown")[:50]
        print(f"{tid:<8} {status:<12} {size:>7.1f} MB  {name}")


def cmd_add(magnet_or_file: str, name: str = None):
    """Add a new torrent."""
    print(f"Adding torrent: {magnet_or_file[:60]}...")
    result = add_torrent(magnet_or_file, name)
    
    if result.get("success"):
        data = result.get("data", {})
        print(f"✓ Added: {data.get('name', 'Unknown')}")
        print(f"  ID: {data.get('torrent_id')}")
        print(f"  Hash: {data.get('hash')}")
    else:
        print(f"✗ Failed: {result.get('detail')}")


def cmd_download(torrent_id: int, dest: str = None):
    """Download a specific torrent."""
    dest_path = Path(dest) if dest else get_destination()
    download_torrent(torrent_id, dest_path)


def cmd_download_all(dest: str = None):
    """Download all completed torrents."""
    dest_path = Path(dest) if dest else get_destination()
    torrents = list_torrents()
    
    completed = [t for t in torrents if t.get("download_state") in ["completed", "uploading", "cached"]]
    
    if not completed:
        print("No completed torrents to download")
        return
    
    print(f"Found {len(completed)} completed torrents")
    print(f"Destination: {dest_path}")
    print()
    
    for t in completed:
        download_torrent(t["id"], dest_path)
        print()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Torbox Downloader")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # status
    subparsers.add_parser("status", help="Show account status")
    
    # list
    subparsers.add_parser("list", help="List all torrents")
    
    # add
    add_parser = subparsers.add_parser("add", help="Add a torrent")
    add_parser.add_argument("magnet_or_file", help="Magnet link or .torrent file")
    add_parser.add_argument("--name", help="Custom name for the torrent")
    
    # download
    dl_parser = subparsers.add_parser("download", help="Download a specific torrent")
    dl_parser.add_argument("torrent_id", type=int, help="Torrent ID")
    dl_parser.add_argument("--dest", help="Destination directory")
    
    # download-all
    dlall_parser = subparsers.add_parser("download-all", help="Download all completed torrents")
    dlall_parser.add_argument("--dest", help="Destination directory")
    
    args = parser.parse_args()
    
    if args.command == "status":
        cmd_status()
    elif args.command == "list":
        cmd_list()
    elif args.command == "add":
        cmd_add(args.magnet_or_file, args.name)
    elif args.command == "download":
        cmd_download(args.torrent_id, args.dest)
    elif args.command == "download-all":
        cmd_download_all(args.dest)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
