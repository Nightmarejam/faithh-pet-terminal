#!/usr/bin/env python3
"""Run Band 2 generation 7 confirmation (0.2 vs 0.4) and build a combined aggregate report."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_levels(levels_csv: str) -> list[float]:
    out: list[float] = []
    for chunk in levels_csv.split(","):
        s = chunk.strip()
        if not s:
            continue
        out.append(float(s))
    if not out:
        raise ValueError("No noise levels provided")
    return out


def level_tag(noise_amp: float) -> str:
    return str(round(noise_amp, 3)).replace(".", "p")


def run_cmd(cmd: list[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd), check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run generation-7 confirmation sweep and aggregate.")
    parser.add_argument(
        "--levels",
        default="0.2,0.4",
        help="Comma-separated noise amplitude levels.",
    )
    parser.add_argument("--runs", type=int, default=10, help="Runs per noise level.")
    parser.add_argument(
        "--output",
        default="reports/alife/band2_gen7_confirmation_aggregate.json",
        help="Combined output path relative to repo root.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    levels = parse_levels(args.levels)
    runs = max(1, args.runs)

    exp_script = repo_root / "projects/alife/experiments/band2_generation7_confirm.py"
    agg_script = repo_root / "scripts/alife_aggregate_band2.py"

    per_level_outputs: dict[str, str] = {}

    for amp in levels:
        tag = level_tag(amp)
        print(f"\n=== Noise level {amp} (tag n{tag}) ===", flush=True)
        for i in range(1, runs + 1):
            print(f"Run {i}/{runs}", flush=True)
            run_cmd(
                [
                    sys.executable,
                    str(exp_script),
                    "--noise-amp",
                    str(amp),
                    "--label",
                    f"r{i:02d}",
                ],
                cwd=repo_root,
            )

        out = f"reports/alife/band2_generation7_n{tag}_aggregate.json"
        run_cmd(
            [
                sys.executable,
                str(agg_script),
                "--generation",
                "7",
                "--pattern",
                f"reports/alife/band2_generation7_n{tag}_*.json",
                "--output",
                out,
            ],
            cwd=repo_root,
        )
        per_level_outputs[str(amp)] = out

    combined: dict[str, object] = {
        "experiment": "band2_cooperation",
        "generation": 7,
        "noise_levels": levels,
        "runs_per_level": runs,
        "per_noise": {},
        "best_noise_by_A_minus_B_mean_band3_score_gap": None,
        "best_noise_gap_value": None,
        "generated_at": datetime.now().isoformat(),
    }

    best_noise = None
    best_gap = None

    for amp in levels:
        key = str(amp)
        agg_path = repo_root / per_level_outputs[key]
        data = json.loads(agg_path.read_text(encoding="utf-8"))
        per_noise = {
            "aggregate_path": per_level_outputs[key],
            "run_count": data.get("run_count"),
            "hypothesis_support_rate": data.get("hypothesis_support_rate"),
            "population_A": data.get("population_A"),
            "population_B": data.get("population_B"),
            "deltas_A_minus_B": data.get("deltas_A_minus_B"),
            "trust_stability_A_higher_fraction": data.get("trust_stability_A_higher_fraction"),
            "band3_candidates_A_mean": data.get("band3_candidates_A_mean"),
            "band3_candidates_B_mean": data.get("band3_candidates_B_mean"),
        }
        combined["per_noise"][key] = per_noise

        gap = (
            data.get("deltas_A_minus_B", {})
            .get("mean_band3_score_mean_gap")
        )
        if isinstance(gap, (int, float)):
            if best_gap is None or gap > best_gap:
                best_gap = float(gap)
                best_noise = amp

    combined["best_noise_by_A_minus_B_mean_band3_score_gap"] = best_noise
    combined["best_noise_gap_value"] = best_gap

    out_path = (repo_root / args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    print(f"\nCombined aggregate written: {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
