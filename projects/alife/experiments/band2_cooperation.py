#!/usr/bin/env python3
"""
Band 2 cooperation experiment — symmetric (A) vs asymmetric (B) signal interpretation.

Randomness: os.urandom only (oracle style). No random module, no seeds.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import chromadb

REPO_ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = REPO_ROOT / "reports" / "alife"

CHROMA_HOST = "192.158.1.243"
CHROMA_PORT = 8000
COLLECTION = "alife_lineage"

NUM_AGENTS = 30
NUM_TICKS = 15
COOPERATION_DECISION_THRESHOLD = 0.5
START_RESOURCES = 5.0
GENERATION = 1
EXPERIMENT = "band2_cooperation"


def oracle_random() -> float:
    """Read from kernel entropy pool — hardware noise analog."""
    raw = os.urandom(4)
    value = int.from_bytes(raw, "big") / 0xFFFFFFFF
    return value


def oracle_random_range(low: float, high: float) -> float:
    return low + oracle_random() * (high - low)


def shuffle_ids(ids: list[str]) -> list[str]:
    """Fisher–Yates using oracle_random."""
    out = list(ids)
    n = len(out)
    for i in range(n - 1, 0, -1):
        j = int(oracle_random() * (i + 1))
        out[i], out[j] = out[j], out[i]
    return out


def interpret_signal(true_signal: float, population: str) -> float:
    if population == "A":
        return true_signal
    noise = (oracle_random() - 0.5) * 0.4
    return max(0.0, min(1.0, true_signal + noise))


def build_ring_neighbors(agent_ids: list[str]) -> dict[str, set[str]]:
    """Symmetric 4-regular graph: ring ±1, ±2 after random relabel."""
    n = len(agent_ids)
    if n < 5:
        raise ValueError("Need at least 5 agents for ring+2 topology")
    perm = shuffle_ids(list(agent_ids))
    idx = {perm[i]: i for i in range(n)}
    neighbors: dict[str, set[str]] = {a: set() for a in agent_ids}
    for i in range(n):
        a = perm[i]
        for off in (-2, -1, 1, 2):
            b = perm[(i + off) % n]
            if a != b:
                neighbors[a].add(b)
                neighbors[b].add(a)
    return neighbors


def make_agent(agent_id: str, population: str) -> dict[str, Any]:
    return {
        "id": agent_id,
        "resources": float(START_RESOURCES),
        "signal_strength": 0.0,
        "trust_scores": {},
        "cooperation_count": 0,
        "defection_count": 0,
        "signal_accuracy": 1.0,
        "_abs_error_sum": 0.0,
        "_abs_error_readings": 0,
        "band": 2,
        "fitness": 0.0,
        "generation": GENERATION,
        "population": population,
    }


def init_trust(agent: dict[str, Any], neighbor_ids: set[str]) -> None:
    agent["trust_scores"] = {nid: 0.5 for nid in neighbor_ids}


def clamp_trust(t: float) -> float:
    return max(0.0, min(1.0, t))


def edge_set(neighbors: dict[str, set[str]]) -> set[tuple[str, str]]:
    edges: set[tuple[str, str]] = set()
    for a, nbs in neighbors.items():
        for b in nbs:
            edges.add(tuple(sorted((a, b))))
    return edges


def run_population(
    population: str,
    col: Any,
    run_id: str,
) -> tuple[dict[str, Any], list[str]]:
    agent_ids = [f"{population}_{i:02d}" for i in range(NUM_AGENTS)]
    neighbors_map = build_ring_neighbors(agent_ids)
    agents: dict[str, dict[str, Any]] = {}
    for aid in agent_ids:
        ag = make_agent(aid, population)
        init_trust(ag, neighbors_map[aid])
        agents[aid] = ag

    cooperation_events = 0
    defection_events = 0
    edges = edge_set(neighbors_map)

    for tick in range(1, NUM_TICKS + 1):
        # Step 1 — choose signal and pay cost
        for ag in agents.values():
            sig = oracle_random_range(0.0, 1.0)
            ag["signal_strength"] = sig
            cost = sig * 0.1
            ag["resources"] -= cost

        tick_abs_err_sum = {aid: 0.0 for aid in agent_ids}
        tick_abs_err_n = {aid: 0 for aid in agent_ids}

        # Steps 2–4 — one pass per undirected edge
        for a, b in edges:
            agent_a = agents[a]
            agent_b = agents[b]
            true_sa = agent_a["signal_strength"]
            true_sb = agent_b["signal_strength"]

            interp_b_for_a = interpret_signal(true_sb, population)
            interp_a_for_b = interpret_signal(true_sa, population)

            tick_abs_err_sum[a] += abs(interp_b_for_a - true_sb)
            tick_abs_err_n[a] += 1
            tick_abs_err_sum[b] += abs(interp_a_for_b - true_sa)
            tick_abs_err_n[b] += 1

            trust_a_to_b = agent_a["trust_scores"][b]
            trust_b_to_a = agent_b["trust_scores"][a]

            a_coops = (interp_b_for_a + trust_a_to_b) > COOPERATION_DECISION_THRESHOLD
            b_coops = (interp_a_for_b + trust_b_to_a) > COOPERATION_DECISION_THRESHOLD

            if a_coops and b_coops:
                cooperation_events += 1
                gain = 0.3 * min(true_sa, true_sb)
                agent_a["resources"] += gain
                agent_b["resources"] += gain
                agent_a["trust_scores"][b] = clamp_trust(trust_a_to_b + 0.1)
                agent_b["trust_scores"][a] = clamp_trust(trust_b_to_a + 0.1)
                agent_a["cooperation_count"] += 1
                agent_b["cooperation_count"] += 1
            elif a_coops and not b_coops:
                defection_events += 1
                agent_b["resources"] += 0.2
                agent_a["resources"] -= 0.2
                agent_a["trust_scores"][b] = clamp_trust(trust_a_to_b - 0.3)
                agent_b["defection_count"] += 1
            elif not a_coops and b_coops:
                defection_events += 1
                agent_a["resources"] += 0.2
                agent_b["resources"] -= 0.2
                agent_b["trust_scores"][a] = clamp_trust(trust_b_to_a - 0.3)
                agent_a["defection_count"] += 1
            # else: neutral

        # Rolling signal error → accuracy (1 - mean abs error, clamped)
        for aid in agent_ids:
            ag = agents[aid]
            n_read = tick_abs_err_n[aid]
            if n_read > 0:
                mean_tick_err = tick_abs_err_sum[aid] / n_read
                ag["_abs_error_sum"] += mean_tick_err
                ag["_abs_error_readings"] += 1
            if ag["_abs_error_readings"] > 0:
                mean_err = ag["_abs_error_sum"] / ag["_abs_error_readings"]
                ag["signal_accuracy"] = max(0.0, min(1.0, 1.0 - mean_err))
            else:
                ag["signal_accuracy"] = 1.0

        # Step 5 — resource decay
        for ag in agents.values():
            ag["resources"] -= 0.3

        # Step 6 — fitness
        for ag in agents.values():
            cc = ag["cooperation_count"]
            dc = ag["defection_count"]
            denom = max(1, cc + dc)
            cooperation_rate = cc / denom
            ag["fitness"] = cooperation_rate * ag["signal_accuracy"] * (1.0 + ag["resources"] / 10.0)

        # Chroma batch for this tick
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []
        ts = datetime.now().isoformat()
        for idx, ag in enumerate(agents.values()):
            sig = ag["signal_strength"]
            doc = (
                f"Band2 agent {ag['id']} pop={population} tick={tick}: "
                f"signal={sig:.2f} resources={ag['resources']:.2f} "
                f"coop={ag['cooperation_count']} defect={ag['defection_count']} "
                f"fitness={ag['fitness']:.3f}"
            )
            uid = f"band2_coop_{run_id}_g{GENERATION}_{population}_t{tick}_{idx}_{ag['id']}"
            ids.append(uid)
            documents.append(doc)
            metadatas.append(
                {
                    "experiment": EXPERIMENT,
                    "generation": GENERATION,
                    "population": population,
                    "agent_id": ag["id"],
                    "tick": tick,
                    "signal_strength": float(sig),
                    "resources": float(ag["resources"]),
                    "cooperation_count": int(ag["cooperation_count"]),
                    "defection_count": int(ag["defection_count"]),
                    "fitness": float(ag["fitness"]),
                    "band": 2,
                    "randomness_source": "oracle_urandom",
                    "timestamp": ts,
                }
            )
        col.add(ids=ids, documents=documents, metadatas=metadatas)

    # Band 3 candidates + summary stats
    band3: list[str] = []
    fitnesses: list[float] = []
    accs: list[float] = []
    for aid, ag in agents.items():
        fitnesses.append(ag["fitness"])
        accs.append(ag["signal_accuracy"])
        cc = ag["cooperation_count"]
        dc = ag["defection_count"]
        coop_rate = cc / max(1, cc + dc)
        if coop_rate >= 0.7 and dc <= 2:
            band3.append(aid)

    stable_pairs = 0
    ids_sorted = sorted(agent_ids)
    for i in range(len(ids_sorted)):
        for j in range(i + 1, len(ids_sorted)):
            x, y = ids_sorted[i], ids_sorted[j]
            ta = agents[x]["trust_scores"].get(y)
            tb = agents[y]["trust_scores"].get(x)
            if ta is not None and tb is not None and ta >= 0.5 and tb >= 0.5:
                stable_pairs += 1

    summary = {
        "agent_count": NUM_AGENTS,
        "ticks": NUM_TICKS,
        "mean_fitness": sum(fitnesses) / len(fitnesses) if fitnesses else 0.0,
        "max_fitness": max(fitnesses) if fitnesses else 0.0,
        "cooperation_events": cooperation_events,
        "defection_events": defection_events,
        "mean_signal_accuracy": sum(accs) / len(accs) if accs else 0.0,
        "band3_candidates": band3,
        "stable_cooperative_networks": stable_pairs,
    }
    return summary, band3


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("Connecting to ChromaDB...", flush=True)
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    col = client.get_collection(COLLECTION)
    alife_before = col.count()
    print(f"alife_lineage count before: {alife_before:,}", flush=True)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    summary_a, _ = run_population("A", col, run_id)
    summary_b, _ = run_population("B", col, run_id)

    alife_after = col.count()

    signal_gap = summary_a["mean_signal_accuracy"] - summary_b["mean_signal_accuracy"]

    hypothesis = {
        "A_higher_cooperation_rate": summary_a["cooperation_events"] > summary_b["cooperation_events"],
        "A_lower_defection_rate": summary_a["defection_events"] < summary_b["defection_events"],
        "A_more_band3_candidates": len(summary_a["band3_candidates"]) > len(summary_b["band3_candidates"]),
        "signal_accuracy_gap": signal_gap,
        "hypothesis_supported": False,
    }
    hypothesis["hypothesis_supported"] = all(
        [
            hypothesis["A_higher_cooperation_rate"],
            hypothesis["A_lower_defection_rate"],
            hypothesis["A_more_band3_candidates"],
            signal_gap > 0,
        ]
    )

    out = {
        "experiment": EXPERIMENT,
        "generation": GENERATION,
        "randomness_source": "oracle_urandom",
        "population_A": summary_a,
        "population_B": summary_b,
        "hypothesis_check": hypothesis,
        "alife_lineage_before": alife_before,
        "alife_lineage_after": alife_after,
    }

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = REPORT_DIR / f"band2_generation1_{stamp}.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}", flush=True)
    print(f"alife_lineage count after: {alife_after:,}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise
