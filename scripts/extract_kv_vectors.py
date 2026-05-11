#!/usr/bin/env python3
"""
Extract K/V tensors from a Qwen2-family model via Hugging Face transformers.

Same architectural family as Qwen2 ~15B (GQA, head_dim typically 128). Uses a
small checkpoint so CPU RAM stays reasonable; distributions are
architecture-shaped, not a substitute for layer-wise 15B weights.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "data" / "kv_vectors"


def extract_kv_via_forward_pass(
    model_name: str,
    layer_indices: list[int],
) -> tuple:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"Loading {model_name} for KV extraction...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.float32,
        trust_remote_code=True,
    )
    model.eval()
    n_layers = model.config.num_hidden_layers
    for li in layer_indices:
        if li < 0 or li >= n_layers:
            raise ValueError(f"layer_idx {li} out of range [0, {n_layers})")

    texts = [
        "The avatar transitions between operational states by",
        "In distributed systems, context compression allows",
        "The recursive polar transform converts cartesian coordinates",
        "When multiple agent states must coexist in memory,",
        "Quantization error accumulates across transformer layers when",
    ]

    all_k: list = []
    all_v: list = []

    for text in texts:
        input_ids = tokenizer.encode(text, return_tensors="pt")
        with torch.no_grad():
            outputs = model(input_ids, use_cache=True, output_hidden_states=False)
            past_kv = outputs.past_key_values
        if past_kv is None:
            raise RuntimeError("Model returned no past_key_values")

        for layer_idx in layer_indices:
            K = past_kv[layer_idx][0][0]
            V = past_kv[layer_idx][1][0]
            # [n_kv_heads, seq, head_dim]
            k_vecs = K.reshape(-1, K.shape[-1])
            v_vecs = V.reshape(-1, V.shape[-1])
            all_k.append(k_vecs)
            all_v.append(v_vecs)

    K_all = torch.cat(all_k, dim=0)
    V_all = torch.cat(all_v, dim=0)

    print(f"Extracted {K_all.shape[0]} K rows, {V_all.shape[0]} V rows")
    print(f"Per-vector dim (head_dim): {K_all.shape[1]}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(K_all, OUT_DIR / "K_qwen2_sample.pt")
    torch.save(V_all, OUT_DIR / "V_qwen2_sample.pt")
    meta = {
        "model_name": model_name,
        "layer_indices": layer_indices,
        "k_shape": list(K_all.shape),
        "v_shape": list(V_all.shape),
    }
    import json

    (OUT_DIR / "extraction_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"Saved to {OUT_DIR}/")
    return K_all, V_all


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--model",
        default="Qwen/Qwen2-1.5B",
        help="HF model id (default: small Qwen2 for CPU)",
    )
    p.add_argument(
        "--layers",
        default="5,12,20",
        help="Comma-separated layer indices",
    )
    args = p.parse_args()
    layers = [int(x.strip()) for x in args.layers.split(",") if x.strip()]
    try:
        K, V = extract_kv_via_forward_pass(args.model, layers)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(
        f"K stats: mean={K.mean():.4f}, std={K.std():.4f}, "
        f"min={K.min():.4f}, max={K.max():.4f}"
    )
    print(
        f"V stats: mean={V.mean():.4f}, std={V.std():.4f}, "
        f"min={V.min():.4f}, max={V.max():.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
