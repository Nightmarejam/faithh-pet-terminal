#!/usr/bin/env python3
"""Sample GPU load on the Gen8 while something is running. Read-only.

Written to answer "what does Plex actually cost this server?" with numbers instead of
assumptions. The distinction that matters here is not total GPU utilisation but WHICH
block is busy:

  encoder / decoder   NVENC / NVDEC — fixed-function silicon, used by Plex transcodes.
                      Low, roughly flat power draw.
  sm (CUDA cores)     used by embedding and other compute. This is the load that has
                      preceded every power-loss event on this host
                      (docs/architecture/GEN8_POWER_CONSTRAINT.md).

A transcode showing high encoder and near-zero sm is the safe shape. Embedding shows
the opposite, and that is the workload to keep off this machine.

Run it, then start playback on a client that forces a transcode (pick a lower quality
than the source, or play 4K to a 1080p client).

Usage:
    python scripts/ops/gpu_load_sample.py --seconds 60
    python scripts/ops/gpu_load_sample.py --seconds 120 --interval 2
"""
from __future__ import annotations

import argparse
import subprocess
import sys

FIELDS = "utilization.gpu,utilization.memory,memory.used,clocks.sm,temperature.gpu,power.draw"


def sample(host: str) -> dict | None:
    """One nvidia-smi reading, plus encoder/decoder which need the -q form."""
    try:
        base = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=8", host,
             f"nvidia-smi --query-gpu={FIELDS} --format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=25,
        ).stdout.strip().split(",")
        enc = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=8", host,
             "nvidia-smi -q -d UTILIZATION | grep -A2 -i 'Encoder *:' | head -4"],
            capture_output=True, text=True, timeout=25,
        ).stdout
    except Exception:
        return None
    if len(base) < 6:
        return None

    def num(s, default=0.0):
        s = s.strip()
        try:
            return float(s)
        except ValueError:
            return default

    enc_pct = dec_pct = 0.0
    for line in enc.splitlines():
        if "Encoder" in line and ":" in line:
            enc_pct = num(line.split(":")[1].replace("%", ""))
        elif "Decoder" in line and ":" in line:
            dec_pct = num(line.split(":")[1].replace("%", ""))

    return {
        "sm": num(base[0]), "mem_util": num(base[1]), "mem_mb": num(base[2]),
        "clock": num(base[3]), "temp": num(base[4]),
        # The RTX A1000 does not expose instantaneous power draw at all — it reports
        # [N/A] even with persistence mode enabled and a power cap applied. Verified
        # 2026-07-30 (persistence Enabled, limit 35W, draw still N/A). Use SM clock and
        # utilisation as the proxy; the cap is enforced in hardware regardless of
        # whether the card will tell you what it is drawing.
        "watts": num(base[5], default=-1.0),
        "enc": enc_pct, "dec": dec_pct,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="servicebox")
    ap.add_argument("--seconds", type=int, default=60)
    ap.add_argument("--interval", type=int, default=3)
    args = ap.parse_args()

    print(f"sampling {args.host} every {args.interval}s for {args.seconds}s")
    print(f"{'sm%':>5}{'enc%':>6}{'dec%':>6}{'memMB':>8}{'clkMHz':>8}{'degC':>6}{'W':>7}")
    rows = []
    elapsed = 0
    while elapsed < args.seconds:
        s = sample(args.host)
        if s:
            rows.append(s)
            w = f"{s['watts']:.1f}" if s["watts"] >= 0 else "n/a"
            print(f"{s['sm']:>5.0f}{s['enc']:>6.0f}{s['dec']:>6.0f}"
                  f"{s['mem_mb']:>8.0f}{s['clock']:>8.0f}{s['temp']:>6.0f}{w:>7}")
        else:
            print("  (sample failed)")
        import time
        time.sleep(args.interval)
        elapsed += args.interval

    if not rows:
        print("no samples collected", file=sys.stderr)
        return 1

    def peak(k):
        return max(r[k] for r in rows)

    def mean(k):
        return sum(r[k] for r in rows) / len(rows)

    print(f"\n{len(rows)} samples")
    print(f"  CUDA (sm)   peak {peak('sm'):>5.0f}%   mean {mean('sm'):>5.1f}%")
    print(f"  encoder     peak {peak('enc'):>5.0f}%   mean {mean('enc'):>5.1f}%")
    print(f"  decoder     peak {peak('dec'):>5.0f}%   mean {mean('dec'):>5.1f}%")
    print(f"  memory      peak {peak('mem_mb'):>5.0f} MB")
    print(f"  temperature peak {peak('temp'):>5.0f} C")
    if peak("watts") >= 0:
        print(f"  power       peak {peak('watts'):>5.1f} W  mean {mean('watts'):>5.1f} W")
    else:
        print("  power       not reported by this card (A1000 exposes no draw telemetry,")
        print("              even with persistence mode on) — read SM clock as the proxy:")
        print(f"              clock peak {peak('clock'):>5.0f} MHz of 2100 max")

    print()
    if peak("enc") > 5 and peak("sm") < 30:
        print("  Shape: fixed-function encode, CUDA array mostly idle — the safe profile.")
    elif peak("sm") >= 60:
        print("  Shape: sustained CUDA load. This is the workload that precedes power loss")
        print("         on this host. Move it to the workstation.")
    else:
        print("  Shape: light or idle; re-run while a transcode is actually active.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
