#!/usr/bin/env python3
"""
fossil_run — run an ALife experiment DETERMINISTICALLY and capture a local fossil
record with a hash. No database. Fixes two root problems found in the experiments:
they had no seed (non-reproducible) and never saved their own results (empty result
files). Wraps the experiments WITHOUT modifying them.

The point: run the same seeded experiment in two places (this Mac, and Gen8 later) and
compare the fossil hashes. Identical hash = the formula + storage agree. Divergent hash
= something differs (non-determinism, code drift, or a real storage discrepancy) — which
is exactly the cross-location integrity check you wanted.

Usage:  python3 fossil_run.py 5 --seed 42 --ticks 5000
Output: fossils/exp5_seed42.json  (results + outcome + SHA-256 fingerprint)
"""
import sys, os, json, time, random, hashlib, argparse
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "experiments"))
sys.path.insert(0, str(HERE))

RUNNERS = {  # experiment number -> (module, function)
    5: ("exp5_parasitic", "run_experiment_5"),
}

def fingerprint(obj) -> str:
    """Stable SHA-256 over the canonical JSON — the fossil's comparable identity."""
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()

def run(exp, seed, ticks, log_interval):
    if exp not in RUNNERS:
        raise SystemExit(f"exp {exp} not wired yet. Available: {sorted(RUNNERS)}")
    mod_name, fn_name = RUNNERS[exp]

    # DETERMINISM — seed every entropy source the sim can draw from
    random.seed(seed)
    try:
        import config
        config.RANDOM_SEED = seed
    except Exception:
        pass

    mod = __import__(mod_name)
    fn = getattr(mod, fn_name)
    t0 = time.time()
    results = fn(ticks=ticks, log_interval=log_interval)
    dt = round(time.time() - t0, 1)

    record = {
        "experiment": exp, "seed": seed, "ticks": ticks,
        "location": os.uname().nodename, "wall_seconds": dt,
        "results": results,
    }
    record["fossil_hash"] = fingerprint(record["results"])

    out_dir = HERE / "fossils"; out_dir.mkdir(exist_ok=True)
    out = out_dir / f"exp{exp}_seed{seed}.json"
    out.write_text(json.dumps(record, indent=2, default=str))
    print(f"\n{'='*60}\nFOSSIL CAPTURED (no database — local file)")
    print(f"  file:     {out}")
    print(f"  location: {record['location']}")
    print(f"  outcome:  {results.get('outcome') if isinstance(results, dict) else '?'}")
    print(f"  hash:     {record['fossil_hash']}")
    print(f"\nCompare later: run the SAME seed on Gen8, then")
    print(f"  python3 fossil_compare.py fossils/exp{exp}_seed{seed}.json <gen8_copy.json>")
    return record

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("exp", type=int, help="experiment number (5 wired)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--ticks", type=int, default=5000)
    ap.add_argument("--log-interval", type=int, default=1000)
    a = ap.parse_args()
    run(a.exp, a.seed, a.ticks, a.log_interval)
