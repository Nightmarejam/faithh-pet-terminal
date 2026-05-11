#!/usr/bin/env python3
"""Synthesize an aggregate JSON into a concise markdown report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def fmt(v: float | int | None) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, int):
        return str(v)
    return f"{v:.4f}"


def get_mean(section: dict, key: str) -> float | None:
    val = section.get(key, {})
    if isinstance(val, dict):
        m = val.get("mean")
        if isinstance(m, (int, float)):
            return float(m)
    return None


def add_condition_summary(lines: list[str], label: str, node: dict) -> None:
    pa = node.get("population_A", {})
    pb = node.get("population_B", {})
    lines.append(f"### {label}")
    lines.append("")
    lines.append(f"- Runs: {node.get('run_count', 'n/a')}")
    lines.append(f"- Hypothesis support rate: {fmt(node.get('hypothesis_support_rate'))}")
    lines.append(f"- A-B trust stability gap: {fmt(node.get('trust_stability_gap'))}")
    lines.append(
        f"- A/B mean Band3 score: {fmt(get_mean(pa,'mean_band3_score'))} / {fmt(get_mean(pb,'mean_band3_score'))}"
    )
    lines.append(
        f"- A/B mean Band3 candidates: {fmt(node.get('band3_candidates_A_mean'))} / {fmt(node.get('band3_candidates_B_mean'))}"
    )
    canon = node.get("canon_profile")
    if isinstance(canon, dict):
        sig = canon.get("field_signature", {})
        comps = canon.get("components", {})
        lines.append("- Canon profile:")
        lines.append(
            f"  - field_signature: noise_amp={sig.get('noise_amp','n/a')}, bias_shift={sig.get('bias_shift','n/a')}"
        )
        lines.append(f"  - stability_score: {fmt(canon.get('stability_score'))}")
        lines.append(f"  - quality_outcome_class: {canon.get('quality_outcome_class', 'n/a')}")
        lines.append(
            "  - components: "
            f"support_rate={fmt(comps.get('hypothesis_support_rate'))}, "
            f"trust_consistency={fmt(comps.get('trust_direction_consistency'))}, "
            f"band3_gap_norm={fmt(comps.get('band3_gap_normalized'))}, "
            f"band3_gap={fmt(comps.get('mean_band3_score_gap_A_minus_B'))}"
        )
    lines.append("")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create markdown synthesis from aggregate JSON.")
    parser.add_argument("--input", required=True, help="Aggregate JSON path (repo-relative)")
    parser.add_argument("--output", required=True, help="Output markdown path (repo-relative)")
    parser.add_argument("--title", default="ALife Aggregate Synthesis")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    inp = (repo / args.input).resolve()
    out = (repo / args.output).resolve()
    data = json.loads(inp.read_text(encoding="utf-8"))

    lines: list[str] = []
    lines.append(f"# {args.title}")
    lines.append("")
    lines.append(f"- Generated: {datetime.now().isoformat()}")
    lines.append(f"- Source: `{args.input}`")
    lines.append(f"- Experiment: `{data.get('experiment', 'unknown')}`")
    lines.append(f"- Generation: `{data.get('generation', 'unknown')}`")
    lines.append("")

    per_noise = data.get("per_noise")
    per_bias = data.get("per_bias")
    if isinstance(per_noise, dict):
        lines.append("## Per-Noise Summary")
        lines.append("")
        for noise_key, node in per_noise.items():
            if not isinstance(node, dict):
                continue
            add_condition_summary(lines, f"noise={noise_key}", node)
    elif isinstance(per_bias, dict):
        lines.append("## Per-Bias Summary")
        lines.append("")
        for bias_key, node in per_bias.items():
            if not isinstance(node, dict):
                continue
            add_condition_summary(lines, f"bias_shift={bias_key}", node)
    else:
        lines.append("## Aggregate Summary")
        lines.append("")
        pa = data.get("population_A", {})
        pb = data.get("population_B", {})
        lines.append(f"- Runs: {data.get('run_count', 'n/a')}")
        lines.append(f"- Hypothesis support rate: {fmt(data.get('hypothesis_support_rate'))}")
        lines.append(f"- A-B trust stability gap: {fmt(data.get('trust_stability_gap'))}")
        lines.append(
            f"- A/B mean Band3 score: {fmt(get_mean(pa,'mean_band3_score'))} / {fmt(get_mean(pb,'mean_band3_score'))}"
        )
        lines.append(
            f"- A/B mean Band3 candidates: {fmt(data.get('band3_candidates_A_mean'))} / {fmt(data.get('band3_candidates_B_mean'))}"
        )
        lines.append("")

    best_noise = data.get("best_noise_by_A_minus_B_mean_band3_score_gap")
    best_bias = data.get("best_bias_by_A_minus_B_mean_band3_score_gap")
    if best_noise is not None:
        lines.append("## Decision Signal")
        lines.append("")
        lines.append(f"- Best noise by A-B mean Band3 score gap: `{best_noise}`")
        lines.append(f"- Best gap value: {fmt(data.get('best_noise_gap_value'))}")
        lines.append("")
    elif best_bias is not None:
        lines.append("## Decision Signal")
        lines.append("")
        lines.append(f"- Best bias_shift by A-B mean Band3 score gap: `{best_bias}`")
        lines.append(f"- Best gap value: {fmt(data.get('best_bias_gap_value'))}")
        lines.append("")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
