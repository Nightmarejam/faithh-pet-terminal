#!/usr/bin/env python3
"""
fossil_compare — compare two fossil records from two storage locations (Mac vs Gen8).
No database: just reads two JSON files and tells you if the formula + storage agree.

Usage:  python3 fossil_compare.py fossils/exp5_seed42.json /path/to/gen8_exp5_seed42.json
"""
import sys, json

def load(p):
    return json.load(open(p))

def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: fossil_compare.py <fossil_A.json> <fossil_B.json>")
    a, b = load(sys.argv[1]), load(sys.argv[2])
    print(f"A: {sys.argv[1]}  @ {a.get('location')}  hash={a.get('fossil_hash')}")
    print(f"B: {sys.argv[2]}  @ {b.get('location')}  hash={b.get('fossil_hash')}")

    if a.get("seed") != b.get("seed") or a.get("ticks") != b.get("ticks"):
        print("\n⚠️  Different seed/ticks — not a valid identity comparison.")
    if a.get("fossil_hash") == b.get("fossil_hash"):
        print("\n✅ IDENTICAL — same seed produced the same fossil in both locations.")
        print("   The formula is deterministic and the two stores agree. Integrity confirmed.")
        return
    print("\n❌ DIVERGED — same seed, different fossil. Something differs. Drilling in:")
    ra, rb = a.get("results", {}), b.get("results", {})
    keys = sorted(set(ra) | set(rb)) if isinstance(ra, dict) and isinstance(rb, dict) else []
    for k in keys:
        if ra.get(k) != rb.get(k):
            print(f"   {k}: A={ra.get(k)!r}  vs  B={rb.get(k)!r}")
    print("\n   Likely causes: non-determinism in the sim (unseeded entropy), code drift"
          " between locations, or a real storage discrepancy — exactly what you wanted to catch.")

if __name__ == "__main__":
    main()
