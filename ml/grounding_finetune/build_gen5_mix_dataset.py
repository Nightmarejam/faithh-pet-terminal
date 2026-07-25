#!/usr/bin/env python3
"""
Build a ShareGPT-format mixed dataset:
- base grounding dataset (already ShareGPT)
- Generation 5 stable training examples (instruction/input/output JSONL)
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


SYSTEM_PROMPT = (
    "You are FAITHH (Friendly AI Teaching & Helping Hub), Jonathan's personal AI assistant. "
    "Be accurate, evidence-grounded, and explicit about uncertainty when evidence is missing. "
    "Do not fabricate file names, metrics, commits, or experiment outcomes."
)


def read_jsonl(path: Path) -> list[dict]:
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def to_sharegpt_from_instruction(example: dict) -> dict:
    instruction = example.get("instruction", "").strip()
    input_payload = example.get("input", {})
    output_text = example.get("output", "").strip()
    input_text = json.dumps(input_payload, ensure_ascii=True, sort_keys=True)

    user_text = instruction
    if input_text and input_text != "{}":
        user_text += "\n\nInput data:\n" + input_text

    return {
        "conversations": [
            {"from": "system", "value": SYSTEM_PROMPT},
            {"from": "human", "value": user_text},
            {"from": "gpt", "value": output_text},
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build mixed ShareGPT dataset from grounding + gen5 stable data")
    parser.add_argument(
        "--base",
        default="/home/jonat/ai-stack/ml/grounding_finetune/data/grounding_train_v2.jsonl",
        help="Base ShareGPT JSONL",
    )
    parser.add_argument(
        "--gen5",
        default="/home/jonat/ai-stack/ml/training_data/seeded_batches/gen5_stable_training_20260402_021813.jsonl",
        help="Gen5 instruction-style JSONL",
    )
    parser.add_argument(
        "--gen5-repeat",
        type=int,
        default=15,
        help="Repeat factor for gen5 examples to increase influence",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Shuffle seed",
    )
    parser.add_argument(
        "--output",
        default="/home/jonat/ai-stack/ml/grounding_finetune/data/grounding_train_gen5_mix.jsonl",
        help="Output ShareGPT JSONL",
    )
    args = parser.parse_args()

    base_path = Path(args.base)
    gen5_path = Path(args.gen5)
    out_path = Path(args.output)

    base_rows = read_jsonl(base_path)
    gen5_rows_raw = read_jsonl(gen5_path)
    gen5_rows = [to_sharegpt_from_instruction(x) for x in gen5_rows_raw]

    if args.gen5_repeat < 1:
        raise ValueError("--gen5-repeat must be >= 1")

    mixed = list(base_rows)
    for _ in range(args.gen5_repeat):
        mixed.extend(gen5_rows)

    rng = random.Random(args.seed)
    rng.shuffle(mixed)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in mixed:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")

    print(f"Base examples: {len(base_rows)}")
    print(f"Gen5 examples: {len(gen5_rows)}")
    print(f"Gen5 repeat:   {args.gen5_repeat}")
    print(f"Mixed total:   {len(mixed)}")
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()
