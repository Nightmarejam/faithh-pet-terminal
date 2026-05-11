#!/usr/bin/env python3
"""
PolarQuant Experiment A — Python quality check vs block q4_0 on Qwen2 KV-shaped vectors.

Encoding matches the 4-level / 128-dim layout described in
vendor/polar_quant/README.md (paper-aligned, 62-byte nominal record):
  64×4b + 32×2b + 16×2b + 8×2b angle indices + 8×fp16 radii.

Reference repo is CUDA-only; this file reimplements encode/decode in PyTorch.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "kv_vectors"
RESULTS_JSON = DATA_DIR / "experiment_a_results.json"

# --- PolarQuant constants (d=128, L=4) ----------------------------------------
HEAD_DIM = 128
POLAR_ANGLE_BITS = (64 * 4) + (32 * 2) + (16 * 2) + (8 * 2)  # 368
POLAR_RADIUS_BITS = 8 * 16  # fp16
POLAR_TOTAL_BITS = POLAR_ANGLE_BITS + POLAR_RADIUS_BITS  # 496
F16_VECTOR_BITS = HEAD_DIM * 16


def make_rotation_matrix(d: int, seed: int = 42) -> torch.Tensor:
    g = torch.Generator().manual_seed(seed)
    s = torch.randn(d, d, generator=g)
    q, _ = torch.linalg.qr(s)
    return q.float()


def build_codebook(
    n_bits: int,
    lo: float,
    hi: float,
    level: int,
    n_grid: int = 16384,
) -> torch.Tensor:
    """Lloyd on grid with PDF from PolarQuant paper (README table)."""
    grid = torch.linspace(lo, hi, n_grid)
    if level == 0:
        weights = torch.ones(n_grid) / n_grid
    else:
        exponent = (1 << level) - 1
        theta = grid
        sin2theta = torch.sin(2 * theta).clamp(min=0.0)
        weights = torch.pow(sin2theta, float(exponent))
        weights = weights / weights.sum()

    n_codes = 1 << n_bits
    cdf = torch.cumsum(weights, dim=0)
    centroids = torch.zeros(n_codes)
    for i in range(n_codes):
        target = (i + 0.5) / n_codes
        idx = torch.searchsorted(cdf, torch.tensor(target)).clamp(0, n_grid - 1)
        centroids[i] = grid[idx]

    for _ in range(80):
        boundaries = torch.zeros(n_codes + 1)
        boundaries[0] = lo
        boundaries[-1] = hi
        for j in range(1, n_codes):
            boundaries[j] = 0.5 * (centroids[j - 1] + centroids[j])
        old = centroids.clone()
        for c in range(n_codes):
            mask = (grid >= boundaries[c]) & (grid < boundaries[c + 1])
            w = weights[mask]
            if w.sum() > 1e-15:
                centroids[c] = (w * grid[mask]).sum() / w.sum()
        if (centroids - old).abs().max() < 1e-6:
            break
    return centroids


def polar_encode_levels(y: torch.Tensor) -> tuple[list[torch.Tensor], torch.Tensor]:
    """
    Four recursive polar levels on 128-dim rotated vector y.
    Returns list of angle tensors [64,], [32,], [16,], [8,] and final radii (8,).
    """
    r = y.float().clone()
    angles: list[torch.Tensor] = []
    for level in range(4):
        a = r[0::2]
        b = r[1::2]
        if level == 0:
            theta = torch.atan2(b, a)
            theta = torch.remainder(theta, 2 * math.pi)
        else:
            # Pairs are nonnegative radii from the prior level → angle in [0, pi/2].
            theta = torch.atan2(b, a.clamp(min=1e-20))
        r = torch.sqrt(a * a + b * b + 1e-20)
        angles.append(theta)
    assert r.numel() == 8
    return angles, r


def polar_decode_levels(
    angles_q: list[torch.Tensor],
    r8: torch.Tensor,
) -> torch.Tensor:
    """Inverse of polar_encode_levels from quantized angles + 8 radii."""
    r = r8.float().clone()
    for level in range(3, -1, -1):
        th = angles_q[level]
        n = th.numel()
        nxt = torch.empty(2 * n, dtype=torch.float32, device=r.device)
        nxt[0::2] = r * torch.cos(th)
        nxt[1::2] = r * torch.sin(th)
        r = nxt
    assert r.numel() == HEAD_DIM
    return r


def quantize_angles(angles: list[torch.Tensor], codebooks: list[torch.Tensor]) -> list[torch.Tensor]:
    out = []
    for th, cb in zip(angles, codebooks):
        d = (th.unsqueeze(1) - cb.unsqueeze(0)).abs()
        out.append(d.argmin(dim=1).to(torch.int64))
    return out


def angles_from_indices(indices: list[torch.Tensor], codebooks: list[torch.Tensor]) -> list[torch.Tensor]:
    return [cb[idx] for cb, idx in zip(codebooks, indices)]


def quantize_radii_fp16(r8: torch.Tensor) -> torch.Tensor:
    return r8.half().float()


def q4_0_block_quantize(x: torch.Tensor, block_size: int = 32) -> torch.Tensor:
    """Per-block absmax q4-style baseline (not identical to GGML q4_0 but same class)."""
    x_flat = x.float().reshape(-1)
    n = x_flat.numel()
    pad = (block_size - n % block_size) % block_size
    if pad:
        x_flat = torch.cat([x_flat, torch.zeros(pad, device=x_flat.device)])
    blocks = x_flat.view(-1, block_size)
    scales = blocks.abs().amax(dim=1, keepdim=True).clamp(min=1e-8)
    norm = blocks / scales
    q = (norm * 7.5).round().clamp(-8, 7) / 7.5
    recon = (q * scales).reshape(-1)[:n]
    return recon


def build_default_codebooks(device: torch.device) -> list[torch.Tensor]:
    cbs = [
        build_codebook(4, 0.0, 2 * math.pi, 0).to(device),
    ]
    for lev in range(1, 4):
        cbs.append(build_codebook(2, 0.0, math.pi / 2, lev).to(device))
    return cbs


def run_experiment(
    n_samples: int,
    seed: int,
    device: torch.device,
) -> dict:
    k_path = DATA_DIR / "K_qwen2_sample.pt"
    if not k_path.is_file():
        raise FileNotFoundError(f"Missing {k_path} — run scripts/extract_kv_vectors.py first")

    try:
        K = torch.load(k_path, map_location="cpu", weights_only=True)
    except TypeError:
        K = torch.load(k_path, map_location="cpu")
    K = K.float()
    d = K.shape[1]
    if d > HEAD_DIM:
        K = K[:, :HEAD_DIM]
        d = HEAD_DIM
    elif d < HEAD_DIM:
        K = torch.nn.functional.pad(K, (0, HEAD_DIM - d))
    K = K.to(device)

    R = make_rotation_matrix(HEAD_DIM, seed=seed).to(device)
    codebooks = build_default_codebooks(device)

    N = min(n_samples, K.shape[0])
    rows = K[:N]

    polar_err = []
    q4_err = []
    polar_dot = []
    q4_dot = []

    rng = torch.Generator(device=device)
    rng.manual_seed(seed + 1)

    for i in range(N):
        x = rows[i]
        y = x @ R.T
        angles, r8 = polar_encode_levels(y)
        idx = quantize_angles(angles, codebooks)
        ang_hat = angles_from_indices(idx, codebooks)
        r8_hat = quantize_radii_fp16(r8)
        y_hat = polar_decode_levels(ang_hat, r8_hat)
        x_polar = y_hat @ R

        x_q4 = q4_0_block_quantize(x)

        polar_err.append((x - x_polar).norm() / (x.norm() + 1e-12))
        q4_err.append((x - x_q4).norm() / (x.norm() + 1e-12))

        queries = torch.randn(10, HEAD_DIM, generator=rng, device=device)
        queries = queries / (queries.norm(dim=1, keepdim=True) + 1e-12)
        true_d = queries @ x
        polar_dot.append((queries @ x_polar - true_d).abs().mean())
        q4_dot.append((queries @ x_q4 - true_d).abs().mean())

    pe = torch.stack(polar_err).mean().item()
    qe = torch.stack(q4_err).mean().item()
    pd = torch.stack(polar_dot).mean().item()
    qd = torch.stack(q4_dot).mean().item()

    ratio = F16_VECTOR_BITS / POLAR_TOTAL_BITS

    # User handoff geometry: 48 layers, 8 kv heads, 128 head, 32K, 2 bytes f16 K+V
    n_layer = 48
    n_kv = 8
    hd = 128
    ctx = 32768
    kv_f16_mib = n_layer * n_kv * hd * ctx * 2 * 2 / (1024**2)
    kv_polar_mib = kv_f16_mib / ratio
    kv_q4_mib = kv_f16_mib / 4.0

    weights_mib = 8148.0
    buffer_mib = 307.0
    vram_total = 24575.0
    vram_kv_budget = vram_total - weights_mib - buffer_mib

    results = {
        "date": "2026-04-07",
        "polar_reconstruction_error_mean": pe,
        "q4_reconstruction_error_mean": qe,
        "polar_dot_error_mean": pd,
        "q4_dot_error_mean": qd,
        "compression_ratio_polar_nominal": ratio,
        "head_dim": HEAD_DIM,
        "n_vectors_evaluated": N,
        "kv_f16_32k_mib": kv_f16_mib,
        "kv_polar_32k_mib_est": kv_polar_mib,
        "kv_q4_32k_mib_est": kv_q4_mib,
        "vram_kv_budget_mib_est": vram_kv_budget,
        "simultaneous_states_f16_est": vram_kv_budget / kv_f16_mib,
        "simultaneous_states_polar_est": vram_kv_budget / kv_polar_mib,
        "simultaneous_states_q4_est": vram_kv_budget / kv_q4_mib,
        "vendor_note": "vendor/polar_quant is CUDA kernels; Python matches README 4-level layout",
    }
    return results


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--samples", type=int, default=500)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--cpu", action="store_true", help="Force CPU")
    args = p.parse_args()

    device = torch.device("cpu" if args.cpu or not torch.cuda.is_available() else "cuda")
    try:
        results = run_experiment(args.samples, args.seed, device)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_JSON.write_text(json.dumps(results, indent=2))

    print("\n=== Compression Quality (mean over vectors) ===")
    print(f"  Polar relative L2 error:   {results['polar_reconstruction_error_mean']:.6f}")
    print(f"  q4_0-block relative L2:    {results['q4_reconstruction_error_mean']:.6f}")
    print(f"  Polar dot error (mean |Δ|): {results['polar_dot_error_mean']:.6f}")
    print(f"  q4_0 dot error (mean |Δ|):   {results['q4_dot_error_mean']:.6f}")
    print("\n=== Nominal bit budget (d=128) ===")
    print(f"  f16 vector bits: {F16_VECTOR_BITS}")
    print(f"  Polar record bits (paper layout): {POLAR_TOTAL_BITS}")
    print(f"  Nominal compression vs f16: {results['compression_ratio_polar_nominal']:.3f}x")
    print("\n=== 32K context KV estimates (48L, 8 KV heads, 128 dim) ===")
    print(f"  KV f16 (MiB):   {results['kv_f16_32k_mib']:.1f}")
    print(f"  KV Polar (MiB): {results['kv_polar_32k_mib_est']:.1f}")
    print(f"  KV q4 (MiB):    {results['kv_q4_32k_mib_est']:.1f}")
    print(f"  Simultaneous states (Polar est): {results['simultaneous_states_polar_est']:.2f}")
    print(f"\nWrote {RESULTS_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
