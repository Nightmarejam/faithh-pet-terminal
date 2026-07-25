#!/usr/bin/env python3
"""Index V-Dem Country-Year v16 CSV into ChromaDB governance_corpus (human-readable rows)."""

from __future__ import annotations

import csv
import io
import re
import zipfile
from datetime import datetime

import chromadb

CHROMA_HOST = "servicebox.taileb8c60.ts.net"
CHROMA_PORT = 8000
COLLECTION = "governance_corpus"
ZIP_PATH = "/mnt/x/staging/V-Dem-CD-v16_csv.zip"
CSV_MEMBER = "V-Dem-CD-v16.csv"

KEY_INDICATORS = {
    "v2x_polyarchy": "Electoral Democracy Index",
    "v2x_libdem": "Liberal Democracy Index",
    "v2x_partipdem": "Participatory Democracy Index",
    "v2x_delibdem": "Deliberative Democracy Index",
    "v2x_egaldem": "Egalitarian Democracy Index",
    "v2x_accountability": "Accountability Index",
    "v2x_freexp_altinf": "Freedom of Expression Index",
    "v2x_rule": "Rule of Law Index",
    "v2x_corr": "Political Corruption Index",
    "v2xel_frefair": "Free and Fair Elections Index",
}

BATCH_SIZE = 500


def _safe_id_segment(s: str) -> str:
    s = s.strip().lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_]+", "_", s).strip("_") or "unknown"


def main() -> None:
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    col = client.get_collection(COLLECTION)

    count_before = col.count()
    print(f"Before: {count_before:,}")

    all_docs: list[str] = []
    all_meta: list[dict] = []
    all_ids: list[str] = []
    rows_processed = 0
    id_counts: dict[str, int] = {}

    print(f"Extracting V-Dem CSV from {ZIP_PATH} ...")

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        with z.open(CSV_MEMBER) as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))

            for row in reader:
                country = (row.get("country_name") or "").strip()
                year_raw = (row.get("year") or "").strip()

                if not country or not year_raw:
                    continue

                try:
                    year_int = int(year_raw)
                except ValueError:
                    continue

                if year_int < 1990:
                    continue

                lines = [f"Country: {country}, Year: {year_int}"]
                for col_key, label in KEY_INDICATORS.items():
                    val = (row.get(col_key) or "").strip()
                    if val and val.upper() != "NA":
                        try:
                            fval = float(val)
                            lines.append(f"{label}: {fval:.3f}")
                        except ValueError:
                            pass

                if len(lines) < 3:
                    continue

                doc_text = "\n".join(lines)
                base_id = f"vdem_{_safe_id_segment(country)}_{year_int}"
                n = id_counts.get(base_id, 0)
                id_counts[base_id] = n + 1
                doc_id = base_id if n == 0 else f"{base_id}_{n}"

                all_docs.append(doc_text)
                all_meta.append(
                    {
                        "source": "vdem_v16",
                        "type": "democracy_indicators",
                        "country": country,
                        "year": year_int,
                        "title": f"V-Dem indicators: {country} {year_int}",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                all_ids.append(doc_id)
                rows_processed += 1

                if len(all_docs) >= BATCH_SIZE:
                    col.add(
                        documents=all_docs,
                        metadatas=all_meta,
                        ids=all_ids,
                    )
                    all_docs, all_meta, all_ids = [], [], []
                    print(f"  Indexed {rows_processed:,} rows...")

            if all_docs:
                col.add(
                    documents=all_docs,
                    metadatas=all_meta,
                    ids=all_ids,
                )
                print(f"  Final batch: {rows_processed:,} rows total.")

    print(f"\nRows processed: {rows_processed:,}")
    print(f"governance_corpus count: {col.count():,}")


if __name__ == "__main__":
    main()
