#!/usr/bin/env python3
"""
FAITHH Media Download Helper
==============================
Downloads media from TorBox and organizes it for Plex with correct naming.

Quality preference: 4K Remux > 4K > 1080p Remux > 1080p > 720p

Usage:
    # Add a magnet and download to movies
    python3 scripts/media_download.py movie "The Matrix" --year 1999 --magnet "magnet:?..."

    # Add from TorBox torrent ID (already queued)
    python3 scripts/media_download.py movie "The Matrix" --year 1999 --id 12345

    # TV show episode
    python3 scripts/media_download.py tv "Breaking Bad" --season 1 --episode 1 --id 12345

    # Check what's downloading
    python3 scripts/media_download.py status

    # List cached torrents ready to download
    python3 scripts/media_download.py list
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent.parent
MEDIA_ROOT = Path("/mnt/x/media")
MOVIES_DIR = MEDIA_ROOT / "movies"
TV_DIR = MEDIA_ROOT / "tv"
MUSIC_DIR = MEDIA_ROOT / "music"
DOWNLOADS_DIR = MEDIA_ROOT / "downloads"

# Get API key from env or config
TORBOX_API_KEY = os.environ.get("TORBOX_API_KEY", "")
TORBOX_BASE = "https://api.torbox.app/v1/api"

HEADERS = lambda: {"Authorization": f"Bearer {TORBOX_API_KEY}"}

# Quality scoring for auto-selection (higher = better)
QUALITY_SCORES = {
    "remux": 100,
    "2160p": 90, "4k": 90, "uhd": 90,
    "bluray": 80, "blu-ray": 80,
    "1080p": 70,
    "webrip": 60, "web-dl": 65, "webdl": 65,
    "720p": 40,
    "hdtv": 30,
    "cam": -100, "ts": -100, "tc": -100,
}


def score_torrent_name(name: str) -> int:
    """Score a torrent name by quality indicators."""
    name_lower = name.lower()
    score = 0
    for keyword, points in QUALITY_SCORES.items():
        if keyword in name_lower:
            score += points
    return score


def add_torrent(magnet: str) -> dict:
    """Add a magnet link to TorBox."""
    resp = requests.post(
        f"{TORBOX_BASE}/torrents/createtorrent",
        headers=HEADERS(),
        data={"magnet": magnet},
        timeout=30,
    )
    return resp.json()


def list_torrents() -> list:
    """List all TorBox torrents."""
    resp = requests.get(
        f"{TORBOX_BASE}/torrents/mylist",
        headers=HEADERS(),
        timeout=15,
    )
    data = resp.json()
    return data.get("data", [])


def get_download_link(torrent_id: int, file_id: int = 0) -> str | None:
    """Get a direct download link for a torrent file."""
    resp = requests.get(
        f"{TORBOX_BASE}/torrents/requestdl",
        headers=HEADERS(),
        params={"token": TORBOX_API_KEY, "torrent_id": torrent_id, "file_id": file_id},
        timeout=15,
    )
    data = resp.json()
    return data.get("data")


def sanitize_filename(name: str) -> str:
    """Remove characters not safe for filenames."""
    return re.sub(r'[<>:"/\\|?*]', "", name).strip()


def make_movie_name(title: str, year: int, source_filename: str) -> str:
    """Generate Plex-compliant movie filename."""
    ext = Path(source_filename).suffix or ".mkv"
    safe_title = sanitize_filename(title)
    return f"{safe_title} ({year}){ext}"


def make_tv_path(show: str, season: int, episode: int, 
                  source_filename: str) -> Path:
    """Generate Plex-compliant TV show path."""
    ext = Path(source_filename).suffix or ".mkv"
    safe_show = sanitize_filename(show)
    ep_name = f"{safe_show} - S{season:02d}E{episode:02d}{ext}"
    return TV_DIR / safe_show / f"Season {season:02d}" / ep_name


def cmd_list(args):
    """List TorBox torrents with quality scores."""
    torrents = list_torrents()
    if not torrents:
        print("No torrents in TorBox.")
        return

    print(f"\n{'ID':<12} {'Status':<12} {'Size':<10} {'Score':<8} Name")
    print("-" * 80)
    for t in sorted(torrents, key=lambda x: x.get("id", 0), reverse=True)[:30]:
        tid = t.get("id", "?")
        status = t.get("download_state", t.get("status", "?"))[:11]
        size_mb = t.get("size", 0) / 1024 / 1024
        name = t.get("name", "Unknown")[:55]
        score = score_torrent_name(name)
        print(f"{tid:<12} {status:<12} {size_mb:<10.0f} {score:<8} {name}")


def cmd_status(args):
    """Show downloading/processing torrents."""
    torrents = list_torrents()
    active = [t for t in torrents if t.get("download_state") not in 
              ("cached", "completed", "seeding")]
    if not active:
        print("No active downloads.")
    for t in active:
        pct = t.get("progress", 0) * 100
        name = t.get("name", "Unknown")[:60]
        state = t.get("download_state", "?")
        print(f"[{pct:5.1f}%] {state:<12} {name}")


def cmd_movie(args):
    """Download a movie from TorBox and name it for Plex."""
    if not TORBOX_API_KEY:
        print("ERROR: Set TORBOX_API_KEY environment variable")
        sys.exit(1)

    torrent_id = args.id
    year = args.year or 0

    if args.magnet:
        print(f"Adding magnet to TorBox...")
        result = add_torrent(args.magnet)
        if not result.get("success"):
            print(f"ERROR: {result}")
            sys.exit(1)
        torrent_id = result.get("data", {}).get("torrent_id")
        print(f"Added as torrent ID: {torrent_id}")
        print("Waiting for TorBox to process...")
        time.sleep(5)

    if not torrent_id:
        print("ERROR: Provide --id or --magnet")
        sys.exit(1)

    # Find the torrent
    torrents = list_torrents()
    torrent = next((t for t in torrents if t.get("id") == torrent_id), None)
    if not torrent:
        print(f"ERROR: Torrent {torrent_id} not found")
        sys.exit(1)

    name = torrent.get("name", "unknown")
    status = torrent.get("download_state", "?")
    print(f"\nTorrent: {name}")
    print(f"Status:  {status}")
    print(f"Size:    {torrent.get('size', 0) / 1024 / 1024 / 1024:.1f} GB")
    print(f"Quality score: {score_torrent_name(name)}")

    if status not in ("cached", "completed", "seeding"):
        print(f"\nNot ready yet (status: {status}). Add to TorBox and wait.")
        return

    # Get download link
    print("\nGetting download link...")
    link = get_download_link(torrent_id)
    if not link:
        print("ERROR: Could not get download link")
        sys.exit(1)

    # Determine output filename
    movie_filename = make_movie_name(args.title, year, name)
    output_path = MOVIES_DIR / movie_filename

    print(f"\nWill save as: {output_path}")
    confirm = input("Download? [y/N] ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    MOVIES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nDownloading to {output_path}...")
    print(f"Use this command (wget handles resume):")
    print(f'\nwget -c -O "{output_path}" "{link}"\n')
    print("Or with aria2c for faster parallel download:")
    print(f'\naria2c -x 16 -s 16 -o "{movie_filename}" -d "{MOVIES_DIR}" "{link}"\n')


def cmd_tv(args):
    """Download a TV episode from TorBox and name it for Plex."""
    if not args.id:
        print("ERROR: Provide --id")
        sys.exit(1)

    torrents = list_torrents()
    torrent = next((t for t in torrents if t.get("id") == args.id), None)
    if not torrent:
        print(f"ERROR: Torrent {args.id} not found")
        sys.exit(1)

    name = torrent.get("name", "unknown")
    out_path = make_tv_path(args.title, args.season, args.episode, name)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    link = get_download_link(args.id)
    if not link:
        print("ERROR: Could not get download link")
        return

    print(f"Will save as: {out_path}")
    print(f'\nwget -c -O "{out_path}" "{link}"\n')


def main():
    # Load API key from .env if not in environment
    global TORBOX_API_KEY
    if not TORBOX_API_KEY:
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("TORBOX_API_KEY="):
                    TORBOX_API_KEY = line.split("=", 1)[1].strip().strip('"')
                    break

    parser = argparse.ArgumentParser(description="FAITHH Media Download Helper")
    sub = parser.add_subparsers(dest="command")

    # list command
    sub.add_parser("list", help="List TorBox torrents with quality scores")

    # status command
    sub.add_parser("status", help="Show active downloads")

    # movie command
    mp = sub.add_parser("movie", help="Download a movie")
    mp.add_argument("title", help="Movie title")
    mp.add_argument("--year", type=int, default=0, help="Release year")
    mp.add_argument("--id", type=int, help="TorBox torrent ID")
    mp.add_argument("--magnet", help="Magnet link to add first")

    # tv command
    tp = sub.add_parser("tv", help="Download a TV episode")
    tp.add_argument("title", help="Show title")
    tp.add_argument("--season", type=int, required=True)
    tp.add_argument("--episode", type=int, required=True)
    tp.add_argument("--id", type=int, required=True, help="TorBox torrent ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    {"list": cmd_list, "status": cmd_status,
     "movie": cmd_movie, "tv": cmd_tv}[args.command](args)


if __name__ == "__main__":
    main()
