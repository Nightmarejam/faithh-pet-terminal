#!/usr/bin/env python3
import subprocess, csv
from datetime import datetime
from pathlib import Path

LOG_PATH = Path.home() / "ai-stack/projects/crypto/gpu_telemetry.csv"
FIELDS = ["timestamp","temp_c","fan_pct","power_w","vram_mib","core_mhz","mem_mhz"]

def poll():
    r = subprocess.run(
        ["nvidia-smi","--query-gpu=temperature.gpu,fan.speed,power.draw,memory.used,clocks.current.graphics,clocks.current.memory","--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=10)
    return [datetime.now().isoformat()] + [v.strip() for v in r.stdout.strip().split(",")]

new = not LOG_PATH.exists()
with open(LOG_PATH, "a", newline="") as f:
    w = csv.writer(f)
    if new:
        w.writerow(FIELDS)
    row = poll()
    w.writerow(row)
    print(row[0] + " | " + row[1] + "C | " + row[2] + "% | " + row[3] + "W")
