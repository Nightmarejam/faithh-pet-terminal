#!/usr/bin/env python3
"""Run Band 2 generation 9 bias-shift sweep and build combined aggregate."""

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
        raise ValueError("No bias levels provided")
    return out


def noise_tag(noise_amp: float) -> str:
    return str(round(noise_amp, 3)).replace(".", "p")


def bias_tag(bias_shift: float) -> str:
    sign = "p" if bias_shift >= 0 else "m"
    num = str(round(abs(bias_shift), 3)).replace(".", "p")
    return f"{sign}{num}"


def run_cmd(cmd: list[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd), check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}")


def band3_gap_normalized(gap: float) -> float:
    if gap <= 0:
        return 0.0
    return min(1.0, gap / 0.05)


def outcome_class(stability_score: float, gap: float) -> str:
    if stability_score >= 0.66 and gap > 0:
        return "constructive"
    if stability_score >= 0.4 and gap >= 0:
        return "neutral"
    return "corrosive"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run generation-9 bias-shift sweep and aggregate.")
    parser.add_argument(
        "--bias-levels",
        default="0.0,-0.05,-0.1,-0.12,-0.15",
        help="Comma-separated bias_shift levels for Population B.",
    )
    parser.add_argument("--noise-amp", type=float, default=0.4, help="Shared noise amplitude.")
    parser.add_argument("--runs", type=int, default=20, help="Runs per bias level.")
    parser.add_argument(
        "--output",
        default="reports/alife/band2_gen9_bias_shift_aggregate.json",
        help="Combined output path relative to repo root.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    bias_levels = parse_levels(args.bias_levels)
    runs = max(1, args.runs)
    ntag = noise_tag(args.noise_amp)

    exp_script = repo_root / "projects/alife/experiments/band2_generation9_bias_shift.py"
    agg_script = repo_root / "scripts/alife_aggregate_band2.py"

    per_bias_outputs: dict[str, str] = {}

    for bias in bias_levels:
        btag = bias_tag(bias)
        print(f"\n=== Bias shift {bias} (tag b{btag}) ===", flush=True)
        for i in range(1, runs + 1):
            print(f"Run {i}/{runs}", flush=True)
            label = f"b{btag}_r{i:02d}"
            run_cmd(
                [
                    sys.executable,
                    str(exp_script),
                    "--noise-amp",
                    str(args.noise_amp),
                    "--bias-shift",
                    str(bias),
                    "--label",
                    label,
                ],
                cwd=repo_root,
            )

        out = f"reports/alife/band2_generation9_n{ntag}_b{btag}_aggregate.json"
        run_cmd(
            [
                sys.executable,
                str(agg_script),
                "--generation",
                "9",
                "--pattern",
                f"reports/alife/band2_generation9_n{ntag}_b{btag}_*.json",
                "--output",
                out,
            ],
            cwd=repo_root,
        )
        per_bias_outputs[str(bias)] = out

    combined: dict[str, object] = {
        "experiment": "band2_cooperation_gen9_bias_shift",
        "generation": 9,
        "noise_amp": args.noise_amp,
        "bias_levels": bias_levels,
        "runs_per_level": runs,
        "per_bias": {},
        "best_bias_by_A_minus_B_mean_band3_score_gap": None,
        "best_bias_gap_value": None,
        "generated_at": datetime.now().isoformat(),
    }

    best_bias = None
    best_gap = None

    for bias in bias_levels:
        key = str(bias)
        agg_path = repo_root / per_bias_outputs[key]
        data = json.loads(agg_path.read_text(encoding="utf-8"))
        delta = data.get("deltas_A_minus_B", {})
        gap = float(delta.get("mean_band3_score_mean_gap", 0.0))
        support = float(data.get("hypothesis_support_rate", 0.0))
        trust_frac = float(data.get("trust_stability_A_higher_fraction", 0.0))
        stability_score = (support + trust_frac + band3_gap_normalized(gap)) / 3.0
        canon_profile = {
            "field_signature": {
                "noise_amp": args.noise_amp,
                "bias_shift": bias,
            },
            "stability_score": round(stability_score, 4),
            "quality_outcome_class": outcome_class(stability_score, gap),
            "components": {
                "hypothesis_support_rate": support,
                "trust_direction_consistency": trust_frac,
                "band3_gap_normalized": band3_gap_normalized(gap),
                "mean_band3_score_gap_A_minus_B": gap,
            },
        }

        per_bias = {
            "aggregate_path": per_bias_outputs[key],
            "run_count": data.get("run_count"),
            "hypothesis_support_rate": support,
            "trust_stability_gap": data.get("trust_stability_gap"),
            "population_A": data.get("population_A"),
            "population_B": data.get("population_B"),
            "deltas_A_minus_B": delta,
            "trust_stability_A_higher_fraction": trust_frac,
            "band3_candidates_A_mean": data.get("band3_candidates_A_mean"),
            "band3_candidates_B_mean": data.get("band3_candidates_B_mean"),
            "canon_profile": canon_profile,
        }
        combined["per_bias"][key] = per_bias

        if best_gap is None or gap > best_gap:
            best_gap = gap
            best_bias = bias

    combined["best_bias_by_A_minus_B_mean_band3_score_gap"] = best_bias
    combined["best_bias_gap_value"] = best_gap

    out_path = (repo_root / args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    print(f"\nCombined aggregate written: {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
