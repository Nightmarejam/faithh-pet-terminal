#!/usr/bin/env python3
"""
FAITHH Legal/Tax Database Collector
Downloads IRS publications, Oregon statutes, and copyright circulars.
Indexes selected documents to ChromaDB on Gen8.

CRITICAL: Do NOT import sentence_transformers or torch in this script.
See decisions_log.json infra_002 - PyTorch CUDA init crashes WSL.
Use ChromaDB's default embedding function instead.
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup

# Lazy import for PDF extraction
pdfplumber = None

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

# Destination priority: NAS first, E: drive fallback
DEST_PRIORITY = [
    Path("/mnt/x/AI/legal_tax_db"),      # NAS via X: drive
    Path("/mnt/z/AI/legal_tax_db"),      # NAS via Z: drive (legacy)
    Path("/mnt/e/legal_tax_db"),         # E: drive fallback
]

CHROMADB_HOST = "192.158.1.243"
CHROMADB_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"

USER_AGENT = "FAITHH Legal DB Collector / research use"
REQUEST_DELAY = 2  # seconds between requests

# Chunk settings
CHUNK_SIZE = 400  # tokens (approximate as chars/4)
CHUNK_OVERLAP = 50

# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENT SOURCES
# ─────────────────────────────────────────────────────────────────────────────

IRS_PDFS = {
    "p17_federal_income_tax":    "https://www.irs.gov/pub/irs-pdf/p17.pdf",
    "p334_small_business":       "https://www.irs.gov/pub/irs-pdf/p334.pdf",
    "p535_business_expenses":    "https://www.irs.gov/pub/irs-pdf/p535.pdf",
    "p541_partnerships":         "https://www.irs.gov/pub/irs-pdf/p541.pdf",
    "p587_home_office":          "https://www.irs.gov/pub/irs-pdf/p587.pdf",
    "p946_depreciation":         "https://www.irs.gov/pub/irs-pdf/p946.pdf",
    "p463_travel_car_gift":      "https://www.irs.gov/pub/irs-pdf/p463.pdf",
    "p560_retirement_plans":     "https://www.irs.gov/pub/irs-pdf/p560.pdf",
    "p505_withholding_estimated":"https://www.irs.gov/pub/irs-pdf/p505.pdf",
    "i1065_form_instructions":   "https://www.irs.gov/pub/irs-pdf/i1065.pdf",
    "i1040_instructions":        "https://www.irs.gov/pub/irs-pdf/i1040gi.pdf",
    "i1040se_schedule_e":        "https://www.irs.gov/pub/irs-pdf/i1040se.pdf",
    "i1040sse_self_employment":  "https://www.irs.gov/pub/irs-pdf/i1040sse.pdf",
    "i1040sc_schedule_c":        "https://www.irs.gov/pub/irs-pdf/i1040sc.pdf",
}

OREGON_HTML = {
    "ors_063_llc":       "https://www.oregonlegislature.gov/bills_laws/ors/ors063.html",
    "ors_314_income":    "https://www.oregonlegislature.gov/bills_laws/ors/ors314.html",
    "ors_316_personal":  "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",
    "ors_317_corp":      "https://www.oregonlegislature.gov/bills_laws/ors/ors317.html",
    "ors_318_corp2":     "https://www.oregonlegislature.gov/bills_laws/ors/ors318.html",
    "ors_060_biz_corps": "https://www.oregonlegislature.gov/bills_laws/ors/ors060.html",
    "ors_215_landuse":   "https://www.oregonlegislature.gov/bills_laws/ors/ors215.html",
    "ors_197_planning":  "https://www.oregonlegislature.gov/bills_laws/ors/ors197.html",
}

FEDERAL_LAW_HTML = {
    "usc_26_irc_subchapA":  "https://www.law.cornell.edu/uscode/text/26/subtitle-A",
    "usc_26_irc_subchapC":  "https://www.law.cornell.edu/uscode/text/26/subtitle-C",
    "usc_17_copyright":     "https://www.law.cornell.edu/uscode/text/17",
    "usc_15_commerce":      "https://www.law.cornell.edu/uscode/text/15/chapter-2",
    "cfr_26_part1":         "https://www.law.cornell.edu/cfr/text/26/part-1",
}

MUSIC_LAW_PDFS = {
    "circ01_copyright_basics":    "https://www.copyright.gov/circs/circ01.pdf",
    "circ56a_sound_recordings":   "https://www.copyright.gov/circs/circ56a.pdf",
    "circ50_musical_compositions":"https://www.copyright.gov/circs/circ50.pdf",
}

# Documents to index into ChromaDB (others just stored on disk)
INDEX_THESE = [
    "p17", "p334", "p535", "p541", "p587", "p946",
    "p463", "p505", "i1065", "i1040", "i1040se",
    "ors_063_llc", "ors_314_income", "ors_316_personal",
    "ors_215_landuse", "ors_197_planning",
    "usc_17_copyright",
    "circ01_copyright_basics", "circ56a_sound_recordings",
    "circ50_musical_compositions",
]

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_destination() -> Optional[Path]:
    """Find first writable destination."""
    for dest in DEST_PRIORITY:
        try:
            dest.mkdir(parents=True, exist_ok=True)
            test_file = dest / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            print(f"✓ Using destination: {dest}")
            return dest
        except Exception as e:
            print(f"✗ Cannot write to {dest}: {e}")
    return None


def download_file(url: str, dest_path: Path, is_pdf: bool = False) -> dict:
    """Download a file with proper error handling."""
    result = {
        "url": url,
        "path": str(dest_path),
        "status": "pending",
        "size_mb": 0,
        "timestamp": datetime.now().isoformat(),
    }
    
    if dest_path.exists():
        result["status"] = "skipped_exists"
        result["size_mb"] = round(dest_path.stat().st_size / 1024 / 1024, 2)
        return result
    
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=60, stream=is_pdf)
        response.raise_for_status()
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if is_pdf:
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            dest_path.write_text(response.text, encoding='utf-8')
        
        result["status"] = "success"
        result["size_mb"] = round(dest_path.stat().st_size / 1024 / 1024, 2)
        
    except requests.Timeout:
        result["status"] = "error_timeout"
        result["error"] = "Request timed out"
    except requests.RequestException as e:
        result["status"] = "error_request"
        result["error"] = str(e)
    except Exception as e:
        result["status"] = "error_other"
        result["error"] = str(e)
    
    return result


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from PDF using pdfplumber."""
    global pdfplumber
    if pdfplumber is None:
        import pdfplumber as _pdfplumber
        pdfplumber = _pdfplumber
    
    text_parts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as e:
        print(f"  ⚠ PDF extraction error for {pdf_path.name}: {e}")
        return ""
    
    return "\n\n".join(text_parts)


def extract_html_text(html_path: Path) -> str:
    """Extract clean text from HTML, stripping nav/scripts."""
    try:
        html = html_path.read_text(encoding='utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
        
    except Exception as e:
        print(f"  ⚠ HTML extraction error for {html_path.name}: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE * 4, overlap: int = CHUNK_OVERLAP * 4) -> list:
    """Split text into overlapping chunks (size in chars, ~4 chars per token)."""
    if not text:
        return []
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('. ')
            if last_period > chunk_size // 2:
                chunk = chunk[:last_period + 1]
                end = start + last_period + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return [c for c in chunks if len(c) > 50]  # Filter tiny chunks


def get_category(doc_key: str) -> str:
    """Determine category from document key."""
    if doc_key.startswith(('p', 'i1')):
        return "irs_pub"
    elif doc_key.startswith('ors_'):
        if 'landuse' in doc_key or 'planning' in doc_key:
            return "land_use"
        return "oregon_tax"
    elif doc_key.startswith(('usc_', 'cfr_')):
        return "federal_law"
    elif doc_key.startswith('circ'):
        return "music_law"
    return "other"


def get_jurisdiction(doc_key: str) -> str:
    """Determine jurisdiction from document key."""
    if doc_key.startswith('ors_'):
        return "oregon"
    return "federal"


def get_hats(doc_key: str) -> str:
    """Determine applicable hats for document."""
    hats = []
    if doc_key in ['p17', 'p505', 'i1040', 'i1040se', 'i1040sse', 'ors_316_personal']:
        hats.append("tax_personal")
    if doc_key in ['p334', 'p535', 'p541', 'p587', 'p946', 'p463', 'p560', 'i1065', 'i1040sc', 
                   'ors_063_llc', 'ors_314_income', 'ors_317_corp', 'ors_318_corp2']:
        hats.append("tax_partnership")
    if doc_key in ['usc_17_copyright', 'circ01_copyright_basics', 'circ56a_sound_recordings', 
                   'circ50_musical_compositions']:
        hats.append("music_copyright")
    if doc_key in ['ors_060_biz_corps', 'ors_063_llc']:
        hats.append("business_law")
    if doc_key in ['ors_215_landuse', 'ors_197_planning']:
        hats.append("land_use")
    return ",".join(hats) if hats else "general"


def should_index(doc_key: str) -> bool:
    """Check if document should be indexed to ChromaDB."""
    for pattern in INDEX_THESE:
        if pattern in doc_key:
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# CHROMADB INDEXING (NO SENTENCE TRANSFORMERS)
# ─────────────────────────────────────────────────────────────────────────────

def index_to_chromadb(doc_key: str, title: str, text: str, url: str, dest: Path) -> int:
    """Index document chunks to ChromaDB using default embedding function."""
    import chromadb
    
    chunks = chunk_text(text)
    if not chunks:
        print(f"  ⚠ No chunks extracted for {doc_key}")
        return 0
    
    try:
        client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
        
        category = get_category(doc_key)
        jurisdiction = get_jurisdiction(doc_key)
        hats = get_hats(doc_key)
        download_date = datetime.now().strftime("%Y-%m-%d")
        
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"legal_{doc_key}_{i}_{hashlib.md5(chunk[:100].encode()).hexdigest()[:8]}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "source": url,
                "title": title,
                "category": category,
                "jurisdiction": jurisdiction,
                "doc_key": doc_key,
                "download_date": download_date,
                "hat": hats,
                "project": "legal_tax_db",
                "chunk_index": i,
                "source_type": "document_content",
            })
        
        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i+batch_size]
            batch_docs = documents[i:i+batch_size]
            batch_metas = metadatas[i:i+batch_size]
            collection.upsert(ids=batch_ids, documents=batch_docs, metadatas=batch_metas)
        
        print(f"  ✓ Indexed {len(chunks)} chunks for {doc_key}")
        return len(chunks)
        
    except Exception as e:
        print(f"  ✗ ChromaDB error for {doc_key}: {e}")
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("FAITHH Legal/Tax Database Collector")
    print("=" * 60)
    
    # Find writable destination
    dest = get_destination()
    if not dest:
        print("ERROR: No writable destination found!")
        sys.exit(1)
    
    # Create folder structure
    folders = {
        "federal_irs": dest / "federal_irs",
        "federal_law": dest / "federal_law",
        "oregon_state": dest / "oregon_state",
        "music_law": dest / "music_law",
    }
    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=True)
    
    download_log = []
    stats = {
        "downloaded": 0,
        "skipped": 0,
        "failed": 0,
        "indexed_chunks": 0,
        "indexed_docs": 0,
    }
    
    # ─── Download IRS PDFs ───
    print("\n📄 Downloading IRS Publications...")
    for doc_key, url in IRS_PDFS.items():
        print(f"  → {doc_key}")
        dest_path = folders["federal_irs"] / f"{doc_key}.pdf"
        result = download_file(url, dest_path, is_pdf=True)
        download_log.append(result)
        
        if result["status"] == "success":
            stats["downloaded"] += 1
        elif result["status"] == "skipped_exists":
            stats["skipped"] += 1
        else:
            stats["failed"] += 1
            print(f"    ✗ {result.get('error', 'Unknown error')}")
        
        # Index if needed
        if should_index(doc_key) and dest_path.exists():
            text = extract_pdf_text(dest_path)
            if text:
                chunks = index_to_chromadb(doc_key, f"IRS {doc_key.upper()}", text, url, dest)
                stats["indexed_chunks"] += chunks
                if chunks > 0:
                    stats["indexed_docs"] += 1
        
        time.sleep(REQUEST_DELAY)
    
    # ─── Download Oregon HTML ───
    print("\n📜 Downloading Oregon Revised Statutes...")
    for doc_key, url in OREGON_HTML.items():
        print(f"  → {doc_key}")
        dest_path = folders["oregon_state"] / f"{doc_key}.html"
        result = download_file(url, dest_path, is_pdf=False)
        download_log.append(result)
        
        if result["status"] == "success":
            stats["downloaded"] += 1
        elif result["status"] == "skipped_exists":
            stats["skipped"] += 1
        else:
            stats["failed"] += 1
            print(f"    ✗ {result.get('error', 'Unknown error')}")
        
        # Index if needed
        if should_index(doc_key) and dest_path.exists():
            text = extract_html_text(dest_path)
            if text:
                title = doc_key.replace('_', ' ').upper()
                chunks = index_to_chromadb(doc_key, f"Oregon {title}", text, url, dest)
                stats["indexed_chunks"] += chunks
                if chunks > 0:
                    stats["indexed_docs"] += 1
        
        time.sleep(REQUEST_DELAY)
    
    # ─── Download Federal Law HTML ───
    print("\n⚖️ Downloading Federal Law (Cornell LII)...")
    for doc_key, url in FEDERAL_LAW_HTML.items():
        print(f"  → {doc_key}")
        dest_path = folders["federal_law"] / f"{doc_key}.html"
        result = download_file(url, dest_path, is_pdf=False)
        download_log.append(result)
        
        if result["status"] == "success":
            stats["downloaded"] += 1
        elif result["status"] == "skipped_exists":
            stats["skipped"] += 1
        else:
            stats["failed"] += 1
            print(f"    ✗ {result.get('error', 'Unknown error')}")
        
        # Index if needed
        if should_index(doc_key) and dest_path.exists():
            text = extract_html_text(dest_path)
            if text:
                title = doc_key.replace('_', ' ').upper()
                chunks = index_to_chromadb(doc_key, f"Federal {title}", text, url, dest)
                stats["indexed_chunks"] += chunks
                if chunks > 0:
                    stats["indexed_docs"] += 1
        
        time.sleep(REQUEST_DELAY)
    
    # ─── Download Music Law PDFs ───
    print("\n🎵 Downloading Copyright Office Circulars...")
    for doc_key, url in MUSIC_LAW_PDFS.items():
        print(f"  → {doc_key}")
        dest_path = folders["music_law"] / f"{doc_key}.pdf"
        result = download_file(url, dest_path, is_pdf=True)
        download_log.append(result)
        
        if result["status"] == "success":
            stats["downloaded"] += 1
        elif result["status"] == "skipped_exists":
            stats["skipped"] += 1
        else:
            stats["failed"] += 1
            print(f"    ✗ {result.get('error', 'Unknown error')}")
        
        # Index if needed
        if should_index(doc_key) and dest_path.exists():
            text = extract_pdf_text(dest_path)
            if text:
                title = doc_key.replace('_', ' ').title()
                chunks = index_to_chromadb(doc_key, f"Copyright {title}", text, url, dest)
                stats["indexed_chunks"] += chunks
                if chunks > 0:
                    stats["indexed_docs"] += 1
        
        time.sleep(REQUEST_DELAY)
    
    # ─── Save download log ───
    log_path = dest / "download_log.json"
    with open(log_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "destination": str(dest),
            "stats": stats,
            "downloads": download_log,
        }, f, indent=2)
    
    # ─── Summary ───
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Destination: {dest}")
    print(f"Downloaded: {stats['downloaded']} files")
    print(f"Skipped (already exist): {stats['skipped']} files")
    print(f"Failed: {stats['failed']} files")
    print(f"Indexed to ChromaDB: {stats['indexed_docs']} documents, {stats['indexed_chunks']} chunks")
    print(f"Download log: {log_path}")
    
    # List failures
    failures = [d for d in download_log if d["status"].startswith("error")]
    if failures:
        print("\nFailed downloads:")
        for f in failures:
            print(f"  - {f['url']}: {f.get('error', 'Unknown')}")
    
    return stats


if __name__ == "__main__":
    main()
