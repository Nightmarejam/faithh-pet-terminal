#!/usr/bin/env python3
"""Tests for confirmability source tiering.

Runs with no torch, no GPU and no live Chroma: source_tier takes its client and
embedder as arguments precisely so the ranking rule can be tested in isolation.

The behaviour under test is the one that motivated the module — a curated entry
must beat a raw transcript chunk even when the chunk is *closer* by distance,
because 63,770 bulk chunks against a few hundred curated entries means distance
alone will always favour the bulk.

Run:  python3 tests/test_source_tier.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from backend import source_tier as st  # noqa: E402


class FakeCollection:
    def __init__(self, rows, dimension=768):
        self.rows = rows
        self.metadata = {"dimension": dimension}

    def query(self, query_embeddings, n_results, include=None):
        rows = self.rows[:n_results]
        return {
            "documents": [[r[0] for r in rows]],
            "metadatas": [[r[1] for r in rows]],
            "distances": [[r[2] for r in rows]],
        }


class FakeClient:
    def __init__(self, cols):
        self.cols = cols

    def get_collection(self, name):
        if name not in self.cols:
            raise KeyError(name)
        return self.cols[name]


def embed(_q):
    return [0.0] * 768


def main() -> int:
    failures = []

    # 1. Curated beats closer bulk. Bulk is at distance 0.30, curated at 0.50 —
    #    bulk is genuinely more similar, and must still lose.
    client = FakeClient({
        st.CURATED_COLLECTION: FakeCollection([
            ("curated entry", {"tier": "asserted", "source_tier": 1.0,
                               "title": "curated entry"}, 0.50)]),
        st.BULK_COLLECTION: FakeCollection([
            ("raw transcript chunk", {}, 0.30)]),
    })
    hits = st.tiered_search(client, embed, "q", n_results=2)
    if not hits or hits[0]["collection"] != st.CURATED_COLLECTION:
        failures.append(
            f"curated did not outrank closer bulk: {[(h['collection'], round(h['score'],3)) for h in hits]}")

    # 2. confirmed outranks asserted at equal distance.
    client = FakeClient({
        st.CURATED_COLLECTION: FakeCollection([
            ("a", {"tier": "asserted", "source_tier": 1.0, "title": "a"}, 0.40),
            ("c", {"tier": "confirmed", "source_tier": 3.0, "title": "c"}, 0.40)]),
        st.BULK_COLLECTION: FakeCollection([]),
    })
    hits = st.tiered_search(client, embed, "q", n_results=2)
    if not hits or hits[0]["metadata"].get("tier") != "confirmed":
        failures.append(f"confirmed did not outrank asserted: {[h['metadata'] for h in hits]}")

    # 3. refuted is excluded outright, not merely down-ranked. A claim checked and
    #    found false must never be offered as supporting evidence.
    client = FakeClient({
        st.CURATED_COLLECTION: FakeCollection([
            ("bad", {"tier": "refuted", "source_tier": 0.0, "title": "bad"}, 0.01)]),
        st.BULK_COLLECTION: FakeCollection([]),
    })
    hits = st.tiered_search(client, embed, "q", n_results=5)
    if any(h["metadata"].get("tier") == "refuted" for h in hits):
        failures.append("refuted entry was returned; it must be excluded")

    # 4. A dimension-mismatched collection is skipped, not queried. Querying it is
    #    the 2026-07-26 failure: rejected silently, best_distance pinned at 1.0.
    client = FakeClient({
        st.CURATED_COLLECTION: FakeCollection([], dimension=768),
        st.BULK_COLLECTION: FakeCollection([("384 junk", {}, 0.01)], dimension=384),
    })
    hits = st.tiered_search(client, embed, "q", n_results=5)
    if any(h["collection"] == st.BULK_COLLECTION for h in hits):
        failures.append("queried a 384d collection with a 768d vector")

    # 5. A missing collection degrades instead of raising.
    client = FakeClient({st.CURATED_COLLECTION: FakeCollection([("x", {"tier": "asserted"}, 0.2)])})
    try:
        hits = st.tiered_search(client, embed, "q", n_results=3)
        if len(hits) != 1:
            failures.append(f"missing bulk collection: expected 1 hit, got {len(hits)}")
    except Exception as exc:
        failures.append(f"missing collection raised instead of degrading: {exc}")

    # 6. Bulk without metadata still gets the floor weight, not a crash.
    if st.weight_for(st.BULK_COLLECTION, None) != st.BULK_WEIGHT:
        failures.append("bulk with no metadata did not get BULK_WEIGHT")

    if failures:
        print(f"FAIL — {len(failures)} problem(s):\n")
        for f in failures:
            print("  " + f)
        return 1
    print("OK — source tiering: curated beats closer bulk, confirmed beats asserted, "
          "refuted excluded, dimension mismatch skipped, missing collection degrades.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
