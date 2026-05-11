#!/usr/bin/env python3
"""
Audio Schematics Scraper
Downloads schematics from audiocircuit.dk, gyraf.dk, and other sources.
Stores raw files on NAS, indexes metadata to ChromaDB.

Usage:
    python3 scripts/scrape_audio_schematics.py [--dry-run] [--source gyraf|audiocircuit|all]
"""

import os
import sys
import json
import time
import hashlib
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import Optional, List, Dict
import argparse

from bs4 import BeautifulSoup
import requests

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

NAS_BASE = Path("/mnt/x/AI/audio_schematics")
FALLBACK_BASE = Path("/mnt/e/audio_schematics")

USER_AGENT = "FAITHH Audio Schematic Collector / research use"
REQUEST_DELAY = 1.5  # seconds between requests
MAX_CONCURRENT = 3   # concurrent downloads

CHROMADB_HOST = "192.158.1.243"
CHROMADB_PORT = 8000

# ─────────────────────────────────────────────────────────────────────────────
# SOURCES
# ─────────────────────────────────────────────────────────────────────────────

GYRAF_SCHEMATICS_URL = "https://gyraf.dk/schematics/schematics.html"
GYRAF_DIY_URL = "http://www.gyraf.dk/gy_pd/gyraf_diy.html"
GYRAF_SSL_URL = "https://www.gyraf.dk/gy_pd/ssl/ssl.htm"

# Known high-value schematics from Gyraf (direct links)
GYRAF_PRIORITY = {
    # SSL 4000E
    "ssl_clone_full": "https://www.gyraf.dk/gy_pd/ssl/ssl.pdf",
    "ssl_82e26_vca_compressor": "http://www.gyraf.dk/gy_pd/ssl/ssl_82e26.gif",
    "ssl_82e27_bus_comp": "http://www.gyraf.dk/gy_pd/ssl/ssl_82e27.gif",
    "ssl_clone_schematic": "https://www.gyraf.dk/gy_pd/ssl/ssl_sch.gif",
    "ssl_gerbers": "https://www.gyraf.dk/gy_pd/ssl/SSL.zip",
    
    # Sony C800G
    "sony_c800g_schematic": "https://gyraf.dk/schematics/Sony_C800G_Schematic.gif",
    
    # SSL Input
    "ssl_4000e_input_old": "https://gyraf.dk/schematics/SSL_82E01_Channel_Amplifier_Old.GIF",
    "ssl_4000e_input_new": "https://gyraf.dk/schematics/SSL_82E01_Channel_Amplifier.GIF",
    "ssl_4000e_talkback": "https://gyraf.dk/schematics/SSL_82E33_Talkback.GIF",
    
    # Neumann
    "neumann_pv15_isolation": "https://gyraf.dk/schematics/Pv15.gif",
    "neumann_pv46_line": "https://gyraf.dk/schematics/Pv46.gif",
    "neumann_w444_fader": "https://gyraf.dk/schematics/Neu_444.gif",
    "neumann_472_isolation": "https://gyraf.dk/schematics/Neu_472.gif",
    "neumann_482_distribution": "https://gyraf.dk/schematics/Neu_482.gif",
    "neumann_v475_mixbus": "https://gyraf.dk/schematics/Neu_v475.gif",
    "neumann_we66_riaa": "https://gyraf.dk/schematics/Neumann_Playback_Equalizer_WE_66.pdf",
    
    # VCAs
    "aphex_1537a_vca": "https://gyraf.dk/schematics/Aphex_1537A_VCA.pdf",
    "aphex_vca_505": "https://gyraf.dk/schematics/Aphex_VCA_505_card.pdf",
    "vca_ben_duncan_article": "https://gyraf.dk/schematics/VCAs_Ben_Duncan.pdf",
    "dbx_2150_app_notes": "https://gyraf.dk/schematics/dbx2150vca_AN.pdf",
    "dbx_202_vca": "https://gyraf.dk/schematics/Dbx202.pdf",
    
    # NTP
    "ntp_m100_opamp": "https://gyraf.dk/schematics/NTP_M100_OPAMP.GIF",
    "ntp_m100_schematics": "https://gyraf.dk/schematics/NTP_M100_Schematics.pdf",
    "ntp_brochure": "https://gyraf.dk/schematics/NTP_Brochure.pdf",
    
    # Compressors
    "aphex_exciter_ii": "https://gyraf.dk/schematics/Aphex_Exiter_II.PDF",
    
    # Mixers
    "mackie_cr1604_vlz": "https://gyraf.dk/schematics/Mackie%20CR1604%20VLZ.pdf",
    "neotek_elite_input_a": "https://gyraf.dk/schematics/Neotek_Elite_Input_A.GIF",
    "neotek_elite_input_b": "https://gyraf.dk/schematics/Neotek_Elite_Input_B.GIF",
    "neotek_elite_mixamps": "https://gyraf.dk/schematics/Neotek_Elite_Mixamps.GIF",
    
    # Reference
    "transformer_design": "https://gyraf.dk/schematics/RadioDesigners%20Handbook%20-%20Ch.5%20-%20Transformers.pdf",
    "tube_intro": "https://gyraf.dk/schematics/RadioDesigners%20Handbook%20-%20Ch.1%20and%202%20-%20Introduction%20to%20the%20radio%20valve.pdf",
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_destination() -> Optional[Path]:
    """Find first writable destination."""
    for dest in [NAS_BASE, FALLBACK_BASE]:
        try:
            dest.mkdir(parents=True, exist_ok=True)
            test_file = dest / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            return dest
        except Exception as e:
            print(f"✗ Cannot write to {dest}: {e}")
    return None


def categorize_schematic(name: str, url: str) -> Dict:
    """Extract metadata from schematic name/URL."""
    name_lower = name.lower()
    url_lower = url.lower()
    
    # Determine category
    if "ssl" in name_lower:
        category = "ssl"
        manufacturer = "SSL"
    elif "neumann" in name_lower or "neu_" in name_lower:
        category = "neumann"
        manufacturer = "Neumann"
    elif "neve" in name_lower:
        category = "neve"
        manufacturer = "Neve"
    elif "ntp" in name_lower:
        category = "ntp"
        manufacturer = "NTP"
    elif "sony" in name_lower:
        category = "sony"
        manufacturer = "Sony"
    elif "vca" in name_lower or "dbx" in name_lower or "aphex" in name_lower:
        category = "vca"
        manufacturer = "Various"
    elif "neotek" in name_lower:
        category = "neotek"
        manufacturer = "Neotek"
    elif "mackie" in name_lower:
        category = "mackie"
        manufacturer = "Mackie"
    else:
        category = "other"
        manufacturer = "Unknown"
    
    # Determine type
    if "compressor" in name_lower or "comp" in name_lower:
        schematic_type = "compressor"
    elif "preamp" in name_lower or "pre" in name_lower or "input" in name_lower:
        schematic_type = "preamp"
    elif "eq" in name_lower or "equalizer" in name_lower:
        schematic_type = "eq"
    elif "vca" in name_lower:
        schematic_type = "vca"
    elif "mixer" in name_lower or "mixbus" in name_lower or "mix" in name_lower:
        schematic_type = "mixer"
    elif "mic" in name_lower:
        schematic_type = "microphone"
    elif "transformer" in name_lower:
        schematic_type = "transformer"
    elif "psu" in name_lower or "power" in name_lower:
        schematic_type = "power_supply"
    else:
        schematic_type = "other"
    
    # Determine format
    ext = Path(urlparse(url).path).suffix.lower()
    
    return {
        "category": category,
        "manufacturer": manufacturer,
        "schematic_type": schematic_type,
        "format": ext.lstrip('.') or "unknown",
    }


async def download_file(session: aiohttp.ClientSession, url: str, dest_path: Path, 
                        semaphore: asyncio.Semaphore) -> Dict:
    """Download a single file with rate limiting."""
    result = {
        "url": url,
        "path": str(dest_path),
        "status": "pending",
        "size_bytes": 0,
        "timestamp": datetime.now().isoformat(),
    }
    
    if dest_path.exists():
        result["status"] = "skipped_exists"
        result["size_bytes"] = dest_path.stat().st_size
        return result
    
    async with semaphore:
        try:
            await asyncio.sleep(REQUEST_DELAY)
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status != 200:
                    result["status"] = f"error_http_{response.status}"
                    return result
                
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                content = await response.read()
                async with aiofiles.open(dest_path, 'wb') as f:
                    await f.write(content)
                
                result["status"] = "success"
                result["size_bytes"] = len(content)
                
        except asyncio.TimeoutError:
            result["status"] = "error_timeout"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
    
    return result


async def scrape_gyraf_priority(dest: Path, dry_run: bool = False) -> List[Dict]:
    """Download priority schematics from Gyraf."""
    results = []
    
    print(f"\n📐 Downloading {len(GYRAF_PRIORITY)} priority Gyraf schematics...")
    
    if dry_run:
        for name, url in GYRAF_PRIORITY.items():
            meta = categorize_schematic(name, url)
            print(f"  [DRY] {name} -> {meta['category']}/{meta['schematic_type']}")
        return results
    
    headers = {"User-Agent": USER_AGENT}
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for name, url in GYRAF_PRIORITY.items():
            meta = categorize_schematic(name, url)
            ext = meta["format"] or "bin"
            
            # Organize by category
            category_dir = dest / "gyraf" / meta["category"]
            dest_path = category_dir / f"{name}.{ext}"
            
            tasks.append(download_file(session, url, dest_path, semaphore))
        
        results = await asyncio.gather(*tasks)
    
    # Print summary
    success = sum(1 for r in results if r["status"] == "success")
    skipped = sum(1 for r in results if r["status"] == "skipped_exists")
    failed = sum(1 for r in results if r["status"].startswith("error"))
    
    print(f"  ✓ Downloaded: {success}, Skipped: {skipped}, Failed: {failed}")
    
    return results


async def scrape_gyraf_index(dest: Path, dry_run: bool = False) -> List[Dict]:
    """Scrape the Gyraf schematics index page for additional files."""
    results = []
    
    print(f"\n📐 Scraping Gyraf schematics index...")
    
    try:
        response = requests.get(GYRAF_SCHEMATICS_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links to schematics
        links = soup.find_all('a', href=True)
        schematic_links = {}
        
        for link in links:
            href = link['href']
            if any(ext in href.lower() for ext in ['.pdf', '.gif', '.png', '.jpg', '.zip']):
                full_url = urljoin(GYRAF_SCHEMATICS_URL, href)
                name = Path(urlparse(href).path).stem
                # Skip if already in priority list
                if name not in GYRAF_PRIORITY and full_url not in GYRAF_PRIORITY.values():
                    schematic_links[name] = full_url
        
        print(f"  Found {len(schematic_links)} additional schematics")
        
        if dry_run:
            for name, url in list(schematic_links.items())[:10]:
                meta = categorize_schematic(name, url)
                print(f"  [DRY] {name} -> {meta['category']}/{meta['schematic_type']}")
            return results
        
        headers = {"User-Agent": USER_AGENT}
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = []
            for name, url in schematic_links.items():
                meta = categorize_schematic(name, url)
                ext = meta["format"] or "bin"
                
                category_dir = dest / "gyraf" / meta["category"]
                dest_path = category_dir / f"{name}.{ext}"
                
                tasks.append(download_file(session, url, dest_path, semaphore))
            
            results = await asyncio.gather(*tasks)
        
        success = sum(1 for r in results if r["status"] == "success")
        skipped = sum(1 for r in results if r["status"] == "skipped_exists")
        failed = sum(1 for r in results if r["status"].startswith("error"))
        
        print(f"  ✓ Downloaded: {success}, Skipped: {skipped}, Failed: {failed}")
        
    except Exception as e:
        print(f"  ✗ Error scraping index: {e}")
    
    return results


def save_manifest(dest: Path, results: List[Dict]):
    """Save download manifest with metadata."""
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "destination": str(dest),
        "total_files": len(results),
        "success": sum(1 for r in results if r["status"] == "success"),
        "skipped": sum(1 for r in results if r["status"] == "skipped_exists"),
        "failed": sum(1 for r in results if r["status"].startswith("error")),
        "total_bytes": sum(r.get("size_bytes", 0) for r in results),
        "files": results,
    }
    
    manifest_path = dest / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n📋 Manifest saved: {manifest_path}")
    return manifest


async def main():
    parser = argparse.ArgumentParser(description="Scrape audio schematics")
    parser.add_argument("--dry-run", action="store_true", help="Preview without downloading")
    parser.add_argument("--source", choices=["gyraf", "all"], default="all", help="Source to scrape")
    args = parser.parse_args()
    
    print("=" * 60)
    print("FAITHH Audio Schematics Scraper")
    print("=" * 60)
    
    dest = get_destination()
    if not dest:
        print("ERROR: No writable destination found!")
        sys.exit(1)
    
    print(f"✓ Destination: {dest}")
    
    all_results = []
    
    if args.source in ["gyraf", "all"]:
        # Priority schematics first
        results = await scrape_gyraf_priority(dest, args.dry_run)
        all_results.extend(results)
        
        # Then scrape index for additional files
        results = await scrape_gyraf_index(dest, args.dry_run)
        all_results.extend(results)
    
    if not args.dry_run and all_results:
        manifest = save_manifest(dest, all_results)
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total files: {manifest['total_files']}")
        print(f"Downloaded: {manifest['success']}")
        print(f"Skipped: {manifest['skipped']}")
        print(f"Failed: {manifest['failed']}")
        print(f"Total size: {manifest['total_bytes'] / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    asyncio.run(main())
