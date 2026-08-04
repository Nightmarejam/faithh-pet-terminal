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

# Destination priority.
# NOTE 2026-08-01: the original list (/mnt/x, /mnt/z, /mnt/e) was written for the old
# Windows drive mappings and is dead on servicebox — the NAS `ai/` share is NOT mounted
# here (only media, backups, archive, personal are). A run against the old list found no
# writable destination at all. The live corpus lives on the NAS at
#   /volume1/homelab/ai/misfiled/AI/legal_tax_db
# which is reachable over SSH but not via a local mount, so we write locally and sync.
DEST_PRIORITY = [
    Path("/mnt/nas/ai/legal_tax_db"),                 # if the ai/ share ever gets mounted
    Path("/home/jonat/ai-stack/data/legal_tax_db"),   # servicebox local (788G free) ← current
    Path("/mnt/x/AI/legal_tax_db"),                   # legacy Windows X: mapping
    Path("/mnt/e/legal_tax_db"),                      # legacy E: fallback
]

# After a run, sync to the NAS copy with:
#   rsync -av /home/jonat/ai-stack/data/legal_tax_db/ \
#     nas:/volume1/homelab/ai/misfiled/AI/legal_tax_db/
# (and consider moving it out of a folder literally named "misfiled")

CHROMADB_HOST = "servicebox.taileb8c60.ts.net"
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

    # ── added 2026-08-01 — all URLs HEAD-verified 200/application-pdf before commit ──
    # Filing gaps found while working the 2024/2025 Form 1065
    "i1065sk1_partner_k1":       "https://www.irs.gov/pub/irs-pdf/i1065sk1.pdf",
    "i4562_depreciation_form":   "https://www.irs.gov/pub/irs-pdf/i4562.pdf",
    "p3402_llc_taxation":        "https://www.irs.gov/pub/irs-pdf/p3402.pdf",
    "p544_dispositions_assets":  "https://www.irs.gov/pub/irs-pdf/p544.pdf",
    "p542_corporations":         "https://www.irs.gov/pub/irs-pdf/p542.pdf",
    # Insolvency / discharge-of-debt tax treatment
    "p908_bankruptcy_tax_guide": "https://www.irs.gov/pub/irs-pdf/p908.pdf",
    "p4681_canceled_debts":      "https://www.irs.gov/pub/irs-pdf/p4681.pdf",
    "f982_debt_discharge":       "https://www.irs.gov/pub/irs-pdf/f982.pdf",
    # Coalition / exempt-entity formation
    "p557_taxexempt_status":     "https://www.irs.gov/pub/irs-pdf/p557.pdf",
    "i1023ez_exempt_app":        "https://www.irs.gov/pub/irs-pdf/i1023ez.pdf",
    "i1024_exempt_app":          "https://www.irs.gov/pub/irs-pdf/i1024.pdf",
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

    # ── added 2026-08-01 — all HEAD-verified 200 ──
    # ors_063 already covers LLC dissolution/reinstatement (63.647-63.657) — the sections
    # that established the 5-year reinstatement window. Keeping it indexed is load-bearing.
    "ors_065_nonprofit":        "https://www.oregonlegislature.gov/bills_laws/ors/ors065.html",
    "ors_128_charitable_trusts":"https://www.oregonlegislature.gov/bills_laws/ors/ors128.html",
    # Debtor exemptions — ORS 18.345/18.348 are the Oregon exemption schedules
    "ors_018_exemptions":       "https://www.oregonlegislature.gov/bills_laws/ors/ors018.html",
    # Water / submerged land — the actual controlling law for a floating structure,
    # which county zoning largely is not (see LOCAL_LAND_USE note below)
    "ors_274_submerged_lands":  "https://www.oregonlegislature.gov/bills_laws/ors/ors274.html",
    "ors_196_removal_fill":     "https://www.oregonlegislature.gov/bills_laws/ors/ors196.html",
    "ors_830_marine_board":     "https://www.oregonlegislature.gov/bills_laws/ors/ors830.html",
}

FEDERAL_LAW_HTML = {
    "usc_26_irc_subchapA":  "https://www.law.cornell.edu/uscode/text/26/subtitle-A",
    "usc_26_irc_subchapC":  "https://www.law.cornell.edu/uscode/text/26/subtitle-C",
    "usc_17_copyright":     "https://www.law.cornell.edu/uscode/text/17",
    "usc_15_commerce":      "https://www.law.cornell.edu/uscode/text/15/chapter-2",
    "cfr_26_part1":         "https://www.law.cornell.edu/cfr/text/26/part-1",

    # ── added 2026-08-01 — all HEAD-verified 200 ──
    # Title 11 overview plus the four sections that decide what a debtor keeps,
    # what the estate takes, what survives discharge, and what forfeits discharge.
    "usc_11_bankruptcy":              "https://www.law.cornell.edu/uscode/text/11",
    "usc_11_522_exemptions":          "https://www.law.cornell.edu/uscode/text/11/522",
    "usc_11_541_estate_property":     "https://www.law.cornell.edu/uscode/text/11/541",
    "usc_11_523_discharge_exceptions":"https://www.law.cornell.edu/uscode/text/11/523",
    "usc_11_727_discharge":           "https://www.law.cornell.edu/uscode/text/11/727",
    # Federal reservoir permitting — Detroit Lake is an Army Corps project
    "usc_33_403_rivers_harbors":      "https://www.law.cornell.edu/uscode/text/33/403",
    "usc_33_1344_cwa_404":            "https://www.law.cornell.edu/uscode/text/33/1344",
}

# Local / agency land-use sources (added 2026-08-01).
#
# WHY THIS IS THIN, DELIBERATELY: Detroit, Oregon sits on Detroit Lake — a federal
# reservoir behind an Army Corps dam, ringed by Willamette National Forest. For a
# literally floating structure, the binding constraints are federal and state-agency
# (Corps §10/§404, USFS special-use permit, DSL submerged-land authorization, Marion
# County only for any upland component). County zoning is likely the LEAST binding
# constraint, so the statutes above matter more than the code below.
#
# codepublishing.com (the usual host for Marion County Code Titles 16/17) returns
# HTTP 403 to non-browser user agents — verified. The county's own site serves the
# Rural Zone Code as per-chapter PDFs and does not block; that is the better source.
LOCAL_LAND_USE_HTML = {
    "marion_planning_zoning_index": "https://www.co.marion.or.us/PW/Planning/zoning",
    "detroit_or_ordinances":        "https://detroitoregon.us/ordinances/",
    "oregon_statewide_planning_goals":"https://www.oregon.gov/lcd/OP/Pages/Goals.aspx",
}

# Marion County Rural Zone Code, county-hosted PDFs (Title 17 = outside urban growth
# boundaries, which is what Detroit-area rural land is). 17.110 verified 200; add
# further chapters once the applicable zone for a specific parcel is known.
LOCAL_LAND_USE_PDFS = {
    "mcc_17_110_general_provisions":
        "https://www.co.marion.or.us/PW/Planning/zoning/Documents/RuralZoneCode/CHAP17.110.pdf",
}

# ─────────────────────────────────────────────────────────────────────────────
# BLANK FILING FORMS  (added 2026-08-01)
#
# The corpus had INSTRUCTIONS (i1065, i4562, i1040...) but not the FORMS themselves,
# so it could explain a return but not be used to prepare one.
#
# ⚠ TAX-YEAR SPECIFIC. Tom Cat Sound's first return is a SHORT YEAR ending 2024-12-31,
# so it must be filed on TY2024 forms, not current-year. IRS keeps prior years under
# /pub/irs-prior/ with the `name--YYYY.pdf` convention. All HEAD-verified 200.
#
# Schedule B-2 (election out of the BBA centralized audit regime) has no TY2024 file in
# the prior-year archive — the current revision is the one IRS serves, so it's taken from
# /pub/irs-pdf/. Confirm it's the right revision for a 2024 return before filing.
# ─────────────────────────────────────────────────────────────────────────────
TAX_FORMS_PDFS = {
    # ── TY2024 partnership return ──
    "f1065_2024":               "https://www.irs.gov/pub/irs-prior/f1065--2024.pdf",
    "f1065sk1_2024":            "https://www.irs.gov/pub/irs-prior/f1065sk1--2024.pdf",
    "f4562_2024":               "https://www.irs.gov/pub/irs-prior/f4562--2024.pdf",
    "i1065_2024":               "https://www.irs.gov/pub/irs-prior/i1065--2024.pdf",
    "i1065sk1_2024":            "https://www.irs.gov/pub/irs-prior/i1065sk1--2024.pdf",
    "i4562_2024":               "https://www.irs.gov/pub/irs-prior/i4562--2024.pdf",
    # BBA elect-out — current revision (no TY2024 in the prior-year archive)
    "f1065sb2_electout":        "https://www.irs.gov/pub/irs-pdf/f1065sb2.pdf",
    "i1065sb2_electout":        "https://www.irs.gov/pub/irs-pdf/i1065sb2.pdf",
    # ── Attachments that Form 1065 page 1 explicitly requires ──
    # Line 2  "Cost of goods sold (attach Form 1125-A)"
    # Line 6  "Net gain (loss) from Form 4797, Part II, line 17 (attach Form 4797)"
    # Which of the two the Reverb equipment sales belong on is an OPEN QUESTION — see
    # FILING_WORKSPACE.md in the tomcat-sound repo. Both are fetched so either path works.
    # (Form 1125-A carries its instructions on the form itself; there is no separate i1125a.)
    "f1125a_cogs_2024":         "https://www.irs.gov/pub/irs-prior/f1125a--2024.pdf",
    "f4797_2024":               "https://www.irs.gov/pub/irs-prior/f4797--2024.pdf",
    "i4797_2024":               "https://www.irs.gov/pub/irs-prior/i4797--2024.pdf",
    "f4797_2025":               "https://www.irs.gov/pub/irs-prior/f4797--2025.pdf",
    "i4797_2025":               "https://www.irs.gov/pub/irs-prior/i4797--2025.pdf",
    # ── TY2024 personal ──
    "f1040_2024":               "https://www.irs.gov/pub/irs-prior/f1040--2024.pdf",
    "f1040s1_2024":             "https://www.irs.gov/pub/irs-prior/f1040s1--2024.pdf",
    "f1040se_2024":             "https://www.irs.gov/pub/irs-prior/f1040se--2024.pdf",
    "i1040gi_2024":             "https://www.irs.gov/pub/irs-prior/i1040gi--2024.pdf",
    # ── amendment path (TAX_FAST_PATH strategy: file personal now, amend for the K-1) ──
    "f1040x":                   "https://www.irs.gov/pub/irs-pdf/f1040x.pdf",
    "i1040x":                   "https://www.irs.gov/pub/irs-pdf/i1040x.pdf",
    # ── penalty abatement ──
    "f843_abatement":           "https://www.irs.gov/pub/irs-pdf/f843.pdf",
    "i843_abatement":           "https://www.irs.gov/pub/irs-pdf/i843.pdf",
    # ── TY2025 partnership (the still-accruing return) ──
    # Deliberately using /pub/irs-prior/ rather than /pub/irs-pdf/: the latter silently
    # rolls to the next tax year, so a re-run months from now would fetch TY2026 under
    # the same filename. Prior-year URLs are stable. All HEAD-verified 200.
    "f1065_2025":               "https://www.irs.gov/pub/irs-prior/f1065--2025.pdf",
    "f1065sk1_2025":            "https://www.irs.gov/pub/irs-prior/f1065sk1--2025.pdf",
    "f4562_2025":               "https://www.irs.gov/pub/irs-prior/f4562--2025.pdf",
    "i1065_2025":               "https://www.irs.gov/pub/irs-prior/i1065--2025.pdf",
    "i1065sk1_2025":            "https://www.irs.gov/pub/irs-prior/i1065sk1--2025.pdf",
    "i4562_2025":               "https://www.irs.gov/pub/irs-prior/i4562--2025.pdf",
    # ── TY2025 personal ──
    "f1040_2025":               "https://www.irs.gov/pub/irs-prior/f1040--2025.pdf",
    "f1040s1_2025":             "https://www.irs.gov/pub/irs-prior/f1040s1--2025.pdf",
    "f1040se_2025":             "https://www.irs.gov/pub/irs-prior/f1040se--2025.pdf",
    "i1040gi_2025":             "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf",
    # ── Oregon ──
    "or65_partnership_2024":
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-65_101-065_2024.pdf",
    "or65_partnership_2025":
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-65_101-065_2025.pdf",
}

# HTML references that belong with the forms rather than the statute set.
TAX_FORMS_HTML = {
    "irm_20_1_1_penalty_relief": "https://www.irs.gov/irm/part20/irm_20-001-001r",
    "irs_penalty_relief":        "https://www.irs.gov/payments/penalty-relief",
    "or_dor_forms_index":        "https://www.oregon.gov/dor/forms/Pages/default.aspx",
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
    # ── added 2026-08-01 ──
    "i1065sk1", "i4562", "p3402", "p544",
    "p908", "p4681", "f982",
    "p557", "i1023ez", "i1024",
    "ors_065_nonprofit", "ors_018_exemptions",
    "ors_274_submerged_lands", "ors_196_removal_fill", "ors_830_marine_board",
    "usc_11_", "usc_33_",
    "mcc_17_", "detroit_or_ordinances", "oregon_statewide_planning_goals",
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
    # Check specific prefixes before the broad 'p'/'i1' IRS catch-all, since several
    # 2026-08 additions (p908, p4681, f982, p557...) are topical rather than generic.
    if doc_key.startswith('mcc_') or doc_key.startswith(('marion_', 'detroit_', 'oregon_statewide')):
        return "land_use_local"
    elif doc_key.startswith(('p908', 'p4681', 'f982')):
        return "insolvency"
    elif doc_key.startswith(('p557', 'i1023', 'i1024')):
        return "exempt_org"
    elif doc_key.startswith(('p', 'i1', 'f')):
        return "irs_pub"
    elif doc_key.startswith('ors_'):
        if 'landuse' in doc_key or 'planning' in doc_key:
            return "land_use"
        if doc_key.startswith(('ors_274', 'ors_196', 'ors_830')):
            return "water_submerged_land"
        if doc_key.startswith('ors_018'):
            return "debtor_exemptions"
        if doc_key.startswith(('ors_065', 'ors_128')):
            return "nonprofit"
        return "oregon_tax"
    elif doc_key.startswith('usc_11'):
        return "bankruptcy"
    elif doc_key.startswith('usc_33'):
        return "federal_water"
    elif doc_key.startswith(('usc_', 'cfr_')):
        return "federal_law"
    elif doc_key.startswith('circ'):
        return "music_law"
    return "other"


def get_jurisdiction(doc_key: str) -> str:
    """Determine jurisdiction from document key."""
    if doc_key.startswith(('mcc_', 'marion_', 'detroit_')):
        return "oregon_local"
    if doc_key.startswith(('ors_', 'oregon_statewide')):
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
    # ── added 2026-08-01 ──
    if doc_key in ['i1065sk1_partner_k1', 'i4562_depreciation_form', 'p3402_llc_taxation',
                   'p544_dispositions_assets', 'p542_corporations']:
        hats.append("tax_partnership")
    if doc_key in ['p908_bankruptcy_tax_guide', 'p4681_canceled_debts', 'f982_debt_discharge',
                   'ors_018_exemptions', 'usc_11_bankruptcy', 'usc_11_522_exemptions',
                   'usc_11_541_estate_property', 'usc_11_523_discharge_exceptions',
                   'usc_11_727_discharge']:
        hats.append("insolvency")
    if doc_key in ['p557_taxexempt_status', 'i1023ez_exempt_app', 'i1024_exempt_app',
                   'ors_065_nonprofit', 'ors_128_charitable_trusts']:
        hats.append("coalition_formation")
    if doc_key in ['ors_274_submerged_lands', 'ors_196_removal_fill', 'ors_830_marine_board',
                   'usc_33_403_rivers_harbors', 'usc_33_1344_cwa_404',
                   'mcc_17_110_general_provisions', 'marion_planning_zoning_index',
                   'detroit_or_ordinances', 'oregon_statewide_planning_goals']:
        hats.append("land_use")
    return ",".join(hats) if hats else "general"


def should_index(doc_key: str) -> bool:
    """Check if document should be indexed to ChromaDB."""
    # --no-index: fetch to disk only, skip embedding.
    #
    # Added 2026-08-01. index_to_chromadb() uses ChromaDB's DEFAULT embedding function
    # over HttpClient, which means the *server* embeds — i.e. on the Gen8's CPU. The
    # standing rule for this fleet is to embed on the Windows 3090 and write to Chroma
    # over the tailnet, precisely to keep sustained compute off the Gen8. Indexing the
    # 2026-08 additions (ORS chapters ~900KB each, p17 ~3MB, Title 11) is thousands of
    # chunks and would pin that box for a long stretch.
    #
    # Fetching is cheap and safe to run any time. Index as a separate, deliberate pass.
    if "--no-index" in sys.argv:
        return False
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
        "land_use_local": dest / "land_use_local",   # added 2026-08-01
        "filing_forms": dest / "filing_forms",       # added 2026-08-01
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

    # ─── Download local / agency land-use sources (added 2026-08-01) ───
    print("\n🗺️ Downloading local & agency land-use sources...")
    for doc_key, url in LOCAL_LAND_USE_HTML.items():
        print(f"  → {doc_key}")
        dest_path = folders["land_use_local"] / f"{doc_key}.html"
        result = download_file(url, dest_path, is_pdf=False)
        download_log.append(result)

        if result["status"] == "success":
            stats["downloaded"] += 1
        elif result["status"] == "skipped_exists":
            stats["skipped"] += 1
        else:
            stats["failed"] += 1
            print(f"    ✗ {result.get('error', 'Unknown error')}")

        if should_index(doc_key) and dest_path.exists():
            text = extract_html_text(dest_path)
            if text:
                title = doc_key.replace('_', ' ').upper()
                chunks = index_to_chromadb(doc_key, f"Local {title}", text, url, dest)
                stats["indexed_chunks"] += chunks
                if chunks > 0:
                    stats["indexed_docs"] += 1

        time.sleep(REQUEST_DELAY)

    # ─── Download blank filing forms (added 2026-08-01) ───
    # Never indexed: fillable PDFs extract as noise and would pollute retrieval.
    print("\n🧾 Downloading blank filing forms (TY2024-specific)...")
    for doc_key, url in TAX_FORMS_PDFS.items():
        print(f"  → {doc_key}")
        dest_path = folders["filing_forms"] / f"{doc_key}.pdf"
        result = download_file(url, dest_path, is_pdf=True)
        download_log.append(result)
        if result["status"] == "success":
            stats["downloaded"] += 1
        elif result["status"] == "skipped_exists":
            stats["skipped"] += 1
        else:
            stats["failed"] += 1
            print(f"    ✗ {result.get('error', 'Unknown error')}")
        time.sleep(REQUEST_DELAY)

    for doc_key, url in TAX_FORMS_HTML.items():
        print(f"  → {doc_key}")
        dest_path = folders["filing_forms"] / f"{doc_key}.html"
        result = download_file(url, dest_path, is_pdf=False)
        download_log.append(result)
        if result["status"] == "success":
            stats["downloaded"] += 1
        elif result["status"] == "skipped_exists":
            stats["skipped"] += 1
        else:
            stats["failed"] += 1
            print(f"    ✗ {result.get('error', 'Unknown error')}")
        time.sleep(REQUEST_DELAY)

    for doc_key, url in LOCAL_LAND_USE_PDFS.items():
        print(f"  → {doc_key}")
        dest_path = folders["land_use_local"] / f"{doc_key}.pdf"
        result = download_file(url, dest_path, is_pdf=True)
        download_log.append(result)

        if result["status"] == "success":
            stats["downloaded"] += 1
        elif result["status"] == "skipped_exists":
            stats["skipped"] += 1
        else:
            stats["failed"] += 1
            print(f"    ✗ {result.get('error', 'Unknown error')}")

        if should_index(doc_key) and dest_path.exists():
            text = extract_pdf_text(dest_path)
            if text:
                title = doc_key.replace('_', ' ').upper()
                chunks = index_to_chromadb(doc_key, f"Marion County {title}", text, url, dest)
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
