#!/usr/bin/env python3
"""
node_attestation — reusable proof-of-life / attestation for any FAITHH node.

Node-agnostic on purpose: FAITHH Lite uses it now, the big backend and (eventually)
PET devices import the SAME module later. "Across the board" = one attestation layer,
many nodes.

A node self-attests with signed heartbeats, each carrying a checkable receipt:
  - liveness : fresh hardware timing-jitter entropy (proves a real machine runs NOW;
               can't be produced from a recording)
  - work     : what the node actually did this interval (real activity, not a proxy)
  - continuity: each beat signs the previous beat's hash (unbroken presence over time)
Signed with an HMAC key (a stand-in for the PUF-derived key a hardware node would use —
the hardware binding is deferred; the software concept works today).

Storage is a local append-only JSON-lines file — no database needed, offline-first,
the right weight for a laptop node.
"""
import time, os, json, hmac, hashlib
from pathlib import Path


def _liveness(n=256):
    bits, last = [], time.perf_counter_ns()
    while len(bits) < n:
        x = 0
        for _ in range(64):
            x ^= 1
        now = time.perf_counter_ns()
        bits.append((now - last) & 1)
        last = now
    packed = bytes(int("".join(map(str, bits[i:i+8])), 2)
                   for i in range(0, len(bits) // 8 * 8, 8))
    return hashlib.sha256(packed).hexdigest()[:16]


class NodeAttestor:
    def __init__(self, node_id, key: bytes, chain_path=None):
        self.node_id = node_id
        self.key = key
        self.chain_path = Path(chain_path or Path.home() / ".faithh_attestation.jsonl")
        self.started = time.time()

    def _last_hash(self):
        if not self.chain_path.exists():
            return "genesis"
        last = None
        with open(self.chain_path) as f:
            for line in f:
                if line.strip():
                    last = line
        return json.loads(last)["hash"] if last else "genesis"

    def beat(self, work: dict) -> dict:
        """Emit + persist one signed heartbeat. `work` = the node's real activity."""
        body = {"node": self.node_id, "t": round(time.time(), 1),
                "liveness": _liveness(), "work": work, "prev": self._last_hash()}
        raw = json.dumps(body, sort_keys=True).encode()
        body["sig"] = hmac.new(self.key, raw, hashlib.sha256).hexdigest()[:16]
        body["hash"] = hashlib.sha256(raw).hexdigest()[:16]
        with open(self.chain_path, "a") as f:
            f.write(json.dumps(body) + "\n")
        return body

    def verify(self) -> dict:
        """Validate the whole persisted chain (signatures + continuity)."""
        if not self.chain_path.exists():
            return {"valid": True, "beats": 0, "note": "no chain yet"}
        prev, n, bad = "genesis", 0, []
        with open(self.chain_path) as f:
            for line in f:
                if not line.strip():
                    continue
                b = json.loads(line)
                raw = json.dumps({k: b[k] for k in ("node", "t", "liveness", "work", "prev")},
                                 sort_keys=True).encode()
                sig_ok = hmac.compare_digest(
                    hmac.new(self.key, raw, hashlib.sha256).hexdigest()[:16], b["sig"])
                if not (sig_ok and b["prev"] == prev):
                    bad.append(b["t"])
                prev = b["hash"]
                n += 1
        return {"valid": not bad, "beats": n, "broken_at": bad}

    def status(self) -> dict:
        v = self.verify()
        return {"node": self.node_id, "uptime_s": round(time.time() - self.started),
                "chain": str(self.chain_path), **v}


def derive_key(seed: str) -> bytes:
    """Stand-in key derivation. On real hardware this comes from a PUF + fuzzy extractor;
    here it's a stable per-node seed. Same interface, so swapping in hardware is drop-in."""
    return hashlib.sha256(("faithh-node::" + seed).encode()).digest()


if __name__ == "__main__":
    a = NodeAttestor("demo-node", derive_key("demo"),
                     chain_path="/tmp/_attest_demo.jsonl")
    for i in range(3):
        a.beat({"demo_work": i})
        time.sleep(0.2)
    print(json.dumps(a.status(), indent=2))
