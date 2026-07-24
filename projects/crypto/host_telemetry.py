#!/usr/bin/env python3
import requests, csv
from datetime import datetime
from pathlib import Path

LOG_PATH = Path.home() / "ai-stack/projects/crypto/host_telemetry.csv"
BRIDGE_URL = "http://pve.taileb8c60.ts.net:9998"
FIELDS = ["timestamp","cpu_tctl","gpu0_smbus","gpu1_smbus","nvme_comp","fan2_rpm","fan5_rpm","fan6_rpm"]

def poll():
    r = requests.get(BRIDGE_URL, timeout=5).json()
    k10 = r.get("k10temp-pci-00c3", {})
    nct = r.get("nct6798-isa-0290", {})
    nvme = r.get("nvme-pci-0d00", {})
    return [
        datetime.now().isoformat(),
        k10.get("Tctl", {}).get("temp1_input", 0),
        nct.get("SMBUSMASTER 1", {}).get("temp7_input", 0),
        nct.get("SMBUSMASTER 0", {}).get("temp9_input", 0),
        nvme.get("Composite", {}).get("temp1_input", 0),
        nct.get("fan2", {}).get("fan2_input", 0),
        nct.get("fan5", {}).get("fan5_input", 0),
        nct.get("fan6", {}).get("fan6_input", 0),
    ]

new = not LOG_PATH.exists()
with open(LOG_PATH, "a", newline="") as f:
    w = csv.writer(f)
    if new:
        w.writerow(FIELDS)
    row = poll()
    w.writerow(row)
    print(" | ".join(str(x) for x in row))
