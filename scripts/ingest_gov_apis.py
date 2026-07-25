#!/usr/bin/env python3
"""
Government API Ingest Pipeline
Fetches data from Tier 1 government APIs relevant to Constella framework.
Saves raw JSON to NAS and indexes summaries to ChromaDB.

APIs:
  1. USAspending.gov — federal spending by program (UCF baseline)
  2. Federal Register — recent rule changes (Civic Tome analog)
  3. Census.gov — Oregon poverty/demographics (UCF calibration)
  4. FEC — campaign finance (Auctor token dynamics)
     Note: FEC requires free API key at https://api.data.gov/signup

Usage:
  python3 scripts/ingest_gov_apis.py [--api all|usaspending|federal_register|census|fec]
  
  Set FEC_API_KEY env var for FEC data:
  FEC_API_KEY=your_key python3 scripts/ingest_gov_apis.py --api fec
"""
import requests
import json
import os
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

NAS_BASE = "/mnt/z"
NAS_GOV_API = f"{NAS_BASE}/AI"
CHROMADB_HOST = "servicebox.taileb8c60.ts.net"
CHROMADB_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"

NAS_PATHS = {
    "usaspending":      "/volume1/raw_ingest/gov_api/usaspending",
    "federal_register": "/volume1/raw_ingest/gov_api/federal_register",
    "census":           "/volume1/raw_ingest/gov_api/census",
    "fec":              "/volume1/raw_ingest/gov_api/fec",
}

HEADERS = {"User-Agent": "FAITHH-Constella-Research/1.0 (jonathan@faithh.local)"}
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def save_to_nas_via_ssh(data: dict, remote_path: str, filename: str) -> bool:
    """Save JSON data to NAS using SSH stdin redirect."""
    import subprocess
    full_path = f"{remote_path}/{filename}"
    content = json.dumps(data, indent=2)
    result = subprocess.run(
        ["ssh", "nas", f"cat > {full_path}"],
        input=content.encode(),
        capture_output=True
    )
    if result.returncode == 0:
        print(f"  Saved to NAS: {full_path}")
        return True
    else:
        print(f"  NAS save failed: {result.stderr.decode()}")
        return False


def index_to_chromadb(documents: list) -> int:
    """Index document list to ChromaDB. Each doc: {id, text, metadata}"""
    import chromadb
    client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    collection = client.get_collection(COLLECTION_NAME)
    
    for doc in documents:
        collection.upsert(
            ids=[doc["id"]],
            documents=[doc["text"]],
            metadatas=[doc["metadata"]]
        )
    return len(documents)


# =============================================================================
# 1. USAspending.gov — Top federal agencies by spending
# =============================================================================
def ingest_usaspending():
    print("\n=== USAspending.gov — Federal Spending ===")
    
    # Top-tier agencies spending overview
    url = "https://api.usaspending.gov/api/v2/references/toptier_agencies/"
    print(f"  Fetching: {url}")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    # Save raw
    filename = f"toptier_agencies_{TODAY}.json"
    save_to_nas_via_ssh(data, NAS_PATHS["usaspending"], filename)
    
    # Also fetch spending by budget function (UCF relevant)
    url2 = "https://api.usaspending.gov/api/v2/budget_functions/list_budget_functions/"
    print(f"  Fetching budget functions: {url2}")
    resp2 = requests.get(url2, headers=HEADERS, timeout=30)
    if resp2.ok:
        data2 = resp2.json()
        save_to_nas_via_ssh(data2, NAS_PATHS["usaspending"], f"budget_functions_{TODAY}.json")
    
    # Index summary to ChromaDB
    agencies = data.get("results", [])[:20]
    agency_text = "\n".join([
        f"- {a.get('agency_name', 'Unknown')}: ${a.get('current_total_budget_authority_amount', 0):,.0f} total budget authority"
        for a in agencies
    ])
    
    documents = [{
        "id": f"usaspending_agencies_{TODAY}",
        "text": f"""USAspending.gov — Top Federal Agencies by Budget Authority ({TODAY})
Retrieved from US federal spending database. Relevant to Constella UCF (Universal Civic Floor) modeling.
Top agencies by budget authority:
{agency_text}

Source: api.usaspending.gov | Domain: government spending | Constella principle: UCF baseline calibration""",
        "metadata": {
            "domain": "constella",
            "source_type": "government_api",
            "api_source": "usaspending.gov",
            "constella_principle": "UCF",
            "date": TODAY,
            "quality_score": 0.9
        }
    }]
    
    indexed = index_to_chromadb(documents)
    print(f"  Indexed {indexed} documents to ChromaDB")
    return True


# =============================================================================
# 2. Federal Register — Recent significant rules (Civic Tome analog)
# =============================================================================
def ingest_federal_register():
    print("\n=== Federal Register — Recent Rule Changes ===")
    
    # Recent significant rules — the living document analog
    url = "https://www.federalregister.gov/api/v1/documents.json"
    params = {
        "conditions[type][]": ["RULE", "PROPOSED_RULE"],
        "conditions[significant]": 1,
        "per_page": 20,
        "order": "newest",
        "fields[]": ["title", "abstract", "document_number", "publication_date",
                     "agencies", "significant", "type", "action", "html_url"]
    }
    
    print(f"  Fetching significant rules...")
    resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    filename = f"significant_rules_{TODAY}.json"
    save_to_nas_via_ssh(data, NAS_PATHS["federal_register"], filename)
    
    results = data.get("results", [])
    print(f"  Retrieved {len(results)} recent significant rules")
    
    documents = []
    for i, rule in enumerate(results[:10]):
        title = rule.get("title", "Unknown")
        abstract = rule.get("abstract") or "No abstract available"
        pub_date = rule.get("publication_date", TODAY)
        agencies = ", ".join([a.get("name", "") for a in rule.get("agencies", [])][:3])
        doc_num = rule.get("document_number", f"rule_{i}")
        
        documents.append({
            "id": f"fed_register_{doc_num}",
            "text": f"""Federal Register — {rule.get('type', 'RULE')}: {title}
Published: {pub_date} | Agencies: {agencies}
Abstract: {abstract[:500]}
Source: federalregister.gov | Document: {doc_num}
Constella relevance: Civic Tome analog — living governance document, rule amendments, structured change process""",
            "metadata": {
                "domain": "constella",
                "source_type": "government_api",
                "api_source": "federalregister.gov",
                "constella_principle": "Civic_Tome",
                "date": pub_date,
                "quality_score": 0.8
            }
        })
    
    indexed = index_to_chromadb(documents)
    print(f"  Indexed {indexed} documents to ChromaDB")
    return True


# =============================================================================
# 3. Census.gov — Oregon demographics and poverty thresholds
# =============================================================================
def ingest_census():
    print("\n=== Census.gov — Oregon Demographics ===")
    
    # American Community Survey — Oregon poverty and population
    # Variable: B17001_001E = total population for poverty status
    #           B17001_002E = population below poverty level
    # Oregon FIPS: 41, get all counties
    url = "https://api.census.gov/data/2022/acs/acs1"
    params = {
        "get": "NAME,B01001_001E,B17001_001E,B17001_002E,B19013_001E",
        "for": "state:41",  # Oregon
        "key": ""  # Census API is free without key for basic queries
    }
    
    print(f"  Fetching Oregon ACS data...")
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        filename = f"oregon_demographics_{TODAY}.json"
        save_to_nas_via_ssh({"data": data, "source": url, "date": TODAY},
                            NAS_PATHS["census"], filename)
        
        # Parse results — data[0] is headers, data[1:] is rows
        headers_row = data[0]
        rows = data[1:]
        
        results_text = ""
        for row in rows:
            record = dict(zip(headers_row, row))
            total_pop = int(record.get("B01001_001E", 0) or 0)
            poverty_universe = int(record.get("B17001_001E", 0) or 0)
            below_poverty = int(record.get("B17001_002E", 0) or 0)
            median_income = int(record.get("B19013_001E", 0) or 0)
            poverty_rate = (below_poverty / poverty_universe * 100) if poverty_universe > 0 else 0
            results_text += f"""
Oregon (2022 ACS):
  Total population: {total_pop:,}
  Population in poverty: {below_poverty:,} ({poverty_rate:.1f}%)
  Median household income: ${median_income:,}"""
        
        documents = [{
            "id": f"census_oregon_{TODAY}",
            "text": f"""Census.gov — Oregon Demographics and Poverty Data ({TODAY})
American Community Survey 2022 1-Year Estimates for Oregon (FIPS 41).
{results_text}

Source: api.census.gov | ACS 2022
Constella relevance: UCF (Universal Civic Floor) calibration — real poverty threshold data
for Oregon jurisdiction. Used to ground the UCF minimum resource allocation in actual
demographic reality rather than theoretical minimums.""",
            "metadata": {
                "domain": "constella",
                "source_type": "government_api",
                "api_source": "census.gov",
                "constella_principle": "UCF",
                "date": TODAY,
                "quality_score": 0.95,
                "jurisdiction": "Oregon"
            }
        }]
        
        indexed = index_to_chromadb(documents)
        print(f"  Indexed {indexed} documents (Oregon poverty rate: {poverty_rate:.1f}%)")
        
    except Exception as e:
        print(f"  Census API error: {e}")
        print("  Note: Census ACS 1-year may not be available — trying 5-year estimate...")
        # Fallback: use poverty threshold API (no key needed)
        threshold_url = "https://api.census.gov/data/timeseries/poverty/histpov2"
        params2 = {"get": "YEAR,POOR,PTOTAL,PCTPOOR", "for": "us:1", "YEAR": "2022"}
        try:
            resp2 = requests.get(threshold_url, params=params2, headers=HEADERS, timeout=30)
            if resp2.ok:
                data2 = resp2.json()
                save_to_nas_via_ssh({"data": data2, "source": threshold_url, "date": TODAY},
                                    NAS_PATHS["census"], f"us_poverty_threshold_{TODAY}.json")
                print(f"  Saved national poverty threshold data as fallback")
        except Exception as e2:
            print(f"  Fallback also failed: {e2}")
    
    return True


# =============================================================================
# 4. FEC — Campaign finance (Auctor token dynamics)
# =============================================================================
def ingest_fec():
    print("\n=== FEC — Campaign Finance (Auctor Token Dynamics) ===")
    
    # Load key from .env if not in environment
    api_key = os.environ.get("FEC_API_KEY") or os.environ.get("FEC_API")
    if not api_key:
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            for line in open(env_path):
                if line.startswith("FEC_API"):
                    api_key = line.strip().split("=", 1)[-1]
                    break
    if not api_key:
        print("  No FEC_API_KEY found. Set it in .env or environment. Skipping.")
        return False
    
    # Presidential candidates by receipts — who holds civic voice (Auctor analog)
    url = "https://api.open.fec.gov/v1/candidates/totals/"
    params = {
        "api_key": api_key,
        "sort": "-receipts",
        "per_page": 20,
        "election_year": 2024,
        "election_full": True,
    }
    
    print(f"  Fetching top committees by receipts (cycle 2024)...")
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        filename = f"fec_top_candidates_2024_{TODAY}.json"
        save_to_nas_via_ssh(data, NAS_PATHS["fec"], filename)
        
        results = data.get("results", [])
        print(f"  Retrieved {len(results)} candidates with fundraising totals")
        
        candidate_text = "\n".join([
            f"- {c.get('name', 'Unknown')} ({c.get('office_full', '')}): "
            f"${c.get('receipts', 0):,.0f} raised, ${c.get('disbursements', 0):,.0f} spent"
            for c in results[:10]
        ])
        
        documents = [{
            "id": f"fec_candidates_2024_{TODAY}",
            "text": f"""FEC — Top Candidates by Receipts, 2024 Election Cycle ({TODAY})
Federal Election Commission data on candidate fundraising and spending.
Top candidates by total receipts:
{candidate_text}

Source: api.open.fec.gov | Election year: 2024
Constella relevance: Auctor token dynamics — real-world model of how civic voice concentrates.
FEC data demonstrates the pattern Constella is designed to address: campaign finance shows
exactly how civic voice (funding = influence) concentrates into a small number of actors.
The Auctor token fixed-pool + quarterly decay design directly counters this dynamic by
making civic voice non-accumulative and time-decaying.""",
            "metadata": {
                "domain": "constella",
                "source_type": "government_api",
                "api_source": "fec.gov",
                "constella_principle": "Auctor",
                "date": TODAY,
                "quality_score": 0.9
            }
        }]
        
        indexed = index_to_chromadb(documents)
        print(f"  Indexed {indexed} documents to ChromaDB")
        
    except requests.HTTPError as e:
        if "429" in str(e) or "rate" in str(e).lower():
            print(f"  Rate limited with DEMO_KEY. Set FEC_API_KEY for full access.")
        else:
            print(f"  FEC API error: {e}")
    
    return True


# =============================================================================
# Main
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Government API Ingest Pipeline")
    parser.add_argument("--api", default="all",
                        choices=["all", "usaspending", "federal_register", "census", "fec"],
                        help="Which API to ingest (default: all)")
    args = parser.parse_args()
    
    print(f"Government API Ingest Pipeline — {TODAY}")
    print("=" * 60)
    
    runners = {
        "usaspending":      ingest_usaspending,
        "federal_register": ingest_federal_register,
        "census":           ingest_census,
        "fec":              ingest_fec,
    }
    
    if args.api == "all":
        for name, fn in runners.items():
            try:
                fn()
                time.sleep(1)  # Rate limit courtesy
            except Exception as e:
                print(f"  ERROR in {name}: {e}")
    else:
        runners[args.api]()
    
    print("\n" + "=" * 60)
    print("Ingest complete. Data saved to NAS + indexed to ChromaDB.")
    print("NAS paths:")
    for name, path in NAS_PATHS.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()
