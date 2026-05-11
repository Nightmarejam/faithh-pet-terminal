#!/usr/bin/env python3
"""Run Gen10 head-to-head confirmation for two bias levels and aggregate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_biases(biases_csv: str) -> list[float]:
    vals: list[float] = []
    for part in biases_csv.split(","):
        s = part.strip()
        if not s:
            continue
        vals.append(float(s))
    if len(vals) != 2:
        raise ValueError("Head-to-head requires exactly two bias values.")
    return vals


def ntag(noise_amp: float) -> str:
    return str(round(noise_amp, 3)).replace(".", "p")


def btag(bias_shift: float) -> str:
    sign = "p" if bias_shift >= 0 else "m"
    num = str(round(abs(bias_shift), 3)).replace(".", "p")
    return f"{sign}{num}"


def run_cmd(cmd: list[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd), check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Gen10 head-to-head runner.")
    parser.add_argument("--noise-amp", type=float, default=0.4)
    parser.add_argument("--biases", default="0.0,-0.05")
    parser.add_argument("--runs", type=int, default=40)
    parser.add_argument(
        "--output",
        default="reports/alife/band2_gen10_head_to_head_aggregate.json",
        help="Combined output path relative to repo root.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    exp_script = repo_root / "projects/alife/experiments/band2_generation10_head_to_head.py"
    agg_script = repo_root / "scripts/alife_aggregate_band2.py"

    noise_amp = args.noise_amp
    biases = parse_biases(args.biases)
    runs = max(1, args.runs)
    noise_tag = ntag(noise_amp)

    per_bias_outputs: dict[str, str] = {}

    for bias in biases:
        bias_key = str(bias)
        bias_tag = btag(bias)
        print(f"\n=== Bias shift {bias} (tag b{bias_tag}) ===", flush=True)
        for i in range(1, runs + 1):
            print(f"Run {i}/{runs}", flush=True)
            label = f"h2h_b{bias_tag}_r{i:02d}"
            run_cmd(
                [
                    sys.executable,
                    str(exp_script),
                    "--noise-amp",
                    str(noise_amp),
                    "--bias-shift",
                    str(bias),
                    "--label",
                    label,
                ],
                cwd=repo_root,
            )

        out = f"reports/alife/band2_generation10_n{noise_tag}_b{bias_tag}_aggregate.json"
        run_cmd(
            [
                sys.executable,
                str(agg_script),
                "--generation",
                "10",
                "--pattern",
                f"reports/alife/band2_generation10_n{noise_tag}_b{bias_tag}_*.json",
                "--output",
                out,
            ],
            cwd=repo_root,
        )
        per_bias_outputs[bias_key] = out

    combined: dict[str, object] = {
        "experiment": "band2_cooperation_gen10_head_to_head",
        "generation": 10,
        "noise_amp": noise_amp,
        "biases": biases,
        "runs_per_bias": runs,
        "per_bias": {},
        "decision": {},
        "generated_at": datetime.now().isoformat(),
    }

    # Pull key metrics and make explicit win table
    keys = [
        "mean_band3_score_mean_gap",
        "hypothesis_support_rate",
        "trust_stability_gap",
        "trust_stability_A_higher_fraction",
        "band3_candidates_A_mean",
        "band3_candidates_B_mean",
        "mean_net_resource_mean_gap",
    ]
    metric_map: dict[str, dict[str, float]] = {}

    for bias in biases:
        bkey = str(bias)
        data = json.loads((repo_root / per_bias_outputs[bkey]).read_text(encoding="utf-8"))
        combined["per_bias"][bkey] = {
            "aggregate_path": per_bias_outputs[bkey],
            "run_count": data.get("run_count"),
            "hypothesis_support_rate": data.get("hypothesis_support_rate"),
            "trust_stability_gap": data.get("trust_stability_gap"),
            "trust_stability_A_higher_fraction": data.get("trust_stability_A_higher_fraction"),
            "band3_candidates_A_mean": data.get("band3_candidates_A_mean"),
            "band3_candidates_B_mean": data.get("band3_candidates_B_mean"),
            "population_A": data.get("population_A"),
            "population_B": data.get("population_B"),
            "deltas_A_minus_B": data.get("deltas_A_minus_B"),
        }
        deltas = data.get("deltas_A_minus_B", {})
        metric_map[bkey] = {
            "mean_band3_score_mean_gap": float(deltas.get("mean_band3_score_mean_gap", 0.0)),
            "hypothesis_support_rate": float(data.get("hypothesis_support_rate", 0.0)),
            "trust_stability_gap": float(data.get("trust_stability_gap", 0.0)),
            "trust_stability_A_higher_fraction": float(data.get("trust_stability_A_higher_fraction", 0.0)),
            "band3_candidates_A_mean": float(data.get("band3_candidates_A_mean", 0.0)),
            "band3_candidates_B_mean": float(data.get("band3_candidates_B_mean", 0.0)),
            "mean_net_resource_mean_gap": float(deltas.get("mean_net_resource_mean_gap", 0.0)),
        }

    a = str(biases[0])
    b = str(biases[1])
    wins: dict[str, str] = {}
    for k in keys:
        va = metric_map[a][k]
        vb = metric_map[b][k]
        if va > vb:
            wins[k] = a
        elif vb > va:
            wins[k] = b
        else:
            wins[k] = "tie"

    # Primary endpoint hierarchy:
    # 1) mean_band3_score_mean_gap, 2) hypothesis_support_rate, 3) trust_stability_A_higher_fraction
    primary_order = [
        "mean_band3_score_mean_gap",
        "hypothesis_support_rate",
        "trust_stability_A_higher_fraction",
    ]
    winner = "tie"
    for k in primary_order:
        w = wins[k]
        if w != "tie":
            winner = w
            break

    combined["decision"] = {
        "comparison_biases": [biases[0], biases[1]],
        "metric_wins": wins,
        "primary_endpoint_hierarchy": primary_order,
        "winner_by_hierarchy": winner,
        "winner_metrics": metric_map[winner] if winner in metric_map else {},
    }

    out_path = (repo_root / args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    print(f"\nCombined head-to-head aggregate written: {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
