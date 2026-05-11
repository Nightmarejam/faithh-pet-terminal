#!/usr/bin/env python3
"""
Export seeded ALife batch results into a training-ready corpus.

Inputs:
- reports/index_runs/alife_seeded_batch_*.json

Outputs:
- ml/training_data/seeded_batches/seeded_batch_corpus_<timestamp>.jsonl
- ml/training_data/seeded_batches/seeded_batch_corpus_<timestamp>_splits.json
- ml/training_data/seeded_batches/seeded_batch_params_<timestamp>.json
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import UTC, datetime
from pathlib import Path


REPO_ROOT = Path("/home/jonat/ai-stack")


def latest_seeded_batch_file() -> Path:
    files = sorted((REPO_ROOT / "reports/index_runs").glob("alife_seeded_batch_*.json"))
    if not files:
        raise FileNotFoundError("No seeded batch files found in reports/index_runs")
    return files[-1]


def build_training_examples(batch: dict) -> list[dict]:
    examples = []
    for run in batch.get("runs", []):
        params = run.get("params", {})
        result = run.get("result_summary", {})
        variant = run.get("variant", "unknown_variant")

        prompt = (
            "Given this ALife seeded run configuration, predict and explain likely dynamics.\n"
            f"- variant: {variant}\n"
            f"- floor_threshold: {params.get('NAKED_FLOOR_THRESHOLD')}\n"
            f"- floor_bonus: {params.get('NAKED_FLOOR_BONUS')}\n"
            f"- drain_rate: {params.get('PARASITE_DRAIN_RATE')}\n"
            f"- ticks: {params.get('ticks')}\n"
            "Return: collapse risk, expected floor activation regime, adaptation pressure, and governance relevance."
        )
        completion = (
            f"Observed result: collapsed={result.get('collapsed')}, "
            f"final_population={result.get('final_population')}, "
            f"floor_activations={result.get('floor_activations')}, "
            f"max_adapt_reached={result.get('max_adapt_reached')}, "
            f"strategy_escape_tick={result.get('strategy_escape_tick')}.\n"
            "Interpretation: use these outcomes to calibrate UCF/floor policy and adversarial adaptation expectations."
        )
        examples.append(
            {
                "source": "seeded_alife_batch",
                "variant": variant,
                "task_type": "governance_alife_reasoning",
                "input": prompt,
                "output": completion,
                "metadata": {
                    "seed": run.get("seed"),
                    "params": params,
                    "result_summary": result,
                    "quality_score": 0.91,
                },
            }
        )
    return examples


def make_splits(examples: list[dict], seed: int = 42) -> dict:
    items = examples[:]
    random.Random(seed).shuffle(items)
    n = len(items)
    train_end = max(1, int(n * 0.7))
    val_end = max(train_end + 1, int(n * 0.9)) if n > 2 else n
    return {
        "train": items[:train_end],
        "validation": items[train_end:val_end],
        "test": items[val_end:],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export seeded batch to training corpus")
    parser.add_argument("--batch-json", default="", help="Optional explicit seeded batch JSON path")
    parser.add_argument(
        "--output-dir",
        default="/home/jonat/ai-stack/ml/training_data/seeded_batches",
    )
    parser.add_argument("--split-seed", type=int, default=42)
    args = parser.parse_args()

    batch_path = Path(args.batch_json) if args.batch_json else latest_seeded_batch_file()
    if not batch_path.exists():
        raise FileNotFoundError(batch_path)

    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    examples = build_training_examples(batch)
    if not examples:
        raise RuntimeError("No examples generated from batch file")
    splits = make_splits(examples, seed=args.split_seed)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    corpus_jsonl = output_dir / f"seeded_batch_corpus_{stamp}.jsonl"
    splits_json = output_dir / f"seeded_batch_corpus_{stamp}_splits.json"
    params_json = output_dir / f"seeded_batch_params_{stamp}.json"

    with corpus_jsonl.open("w", encoding="utf-8") as fh:
        for ex in examples:
            fh.write(json.dumps(ex, ensure_ascii=True) + "\n")

    splits_json.write_text(
        json.dumps(
            {
                "generated_at_utc": datetime.now(UTC).isoformat(),
                "source_batch": str(batch_path),
                "counts": {k: len(v) for k, v in splits.items()},
                "splits": splits,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    recommended_params = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source_batch": str(batch_path),
        "training_goal": "specialized governance-ALife reasoning model",
        "recommended_recipe": {
            "approach": "QLoRA first, full fine-tune later if needed",
            "epochs": 3,
            "learning_rate": 2e-4,
            "lr_schedule": "cosine",
            "warmup_ratio": 0.05,
            "max_seq_len": 2048,
            "lora_r": 16,
            "lora_alpha": 16,
            "batch_size": 1,
            "grad_accumulation": 8,
            "eval_every_steps": 25,
            "early_stop_patience_evals": 4,
        },
        "reporting_metrics": [
            "heldout_loss",
            "grounded_answer_rate",
            "unsupported_claim_rate",
            "governance_retrieval_precision_top5",
            "alife_mechanism_alignment_score",
        ],
        "minimum_publishable_run_set": {
            "seeded_batch_runs": 15,
            "distinct_scenarios": 5,
            "validation_queries_per_class": 12,
        },
    }
    params_json.write_text(json.dumps(recommended_params, indent=2), encoding="utf-8")

    print(f"Source batch: {batch_path}")
    print(f"Corpus JSONL: {corpus_jsonl}")
    print(f"Splits JSON: {splits_json}")
    print(f"Params JSON: {params_json}")
    print(f"Examples: {len(examples)}")


if __name__ == "__main__":
    main()
