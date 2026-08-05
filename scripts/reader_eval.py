#!/usr/bin/env python3
"""Measure how evidence framing changes reader accuracy. Step 1 of the sequencer.

The sequencer is the last thing to build, not the first. A mediator over readers
that are wrong is a precisely-quantified wrong answer, and precision reads as
trustworthiness -- strictly worse than a coarse honest one. So before any
aggregation logic exists, establish how good a single reader is and what makes it
better.

## Why these cases

Every claim below was settled empirically during the 2026-08-04 session, by
running the command and reading the output -- not by argument. That matters: an
eval set written from memory encodes the same blind spots as the system under
test. Each `why` field names the measurement that decided it.

The set is deliberately REFUTES-heavy. A reader that answers NEUTRAL to
everything scores 0% here, which is the exact failure observed in practice: asked
whether a successful mid-cooldown add refuted "the cooldown blocks adding",
qwen2.5-14b answered NEUTRAL with p=1.0000. Saturated and wrong. A set balanced
toward SUPPORTS would have scored that reader as adequate.

## Why framing is the first variable

The readers did not fail for lack of capability. They failed because evidence
arrived as raw timestamps with the inference left implicit -- `updated_at
05:05:22` means nothing unless you know it should be compared to the add at
05:04:30. Framing A reproduces that. B asks for reasoning before the verdict. C
additionally forces an explicit polarity check, because the measured failure mode
is topical agreement masking logical contradiction (contradictory pairs scored
0.84-0.95 cosine; genuine agreement scored 0.50).

Usage:
    python3 scripts/reader_eval.py                 # all framings
    python3 scripts/reader_eval.py --framing B
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request

VLLM = "http://desktop-iifeikl.taileb8c60.ts.net:8000/v1/chat/completions"
MODEL = "qwen2.5-14b"

CASES = [
    {
        "claim": "The TorBox cooldown blocks adding torrents.",
        "evidence": "A Radarr grab was submitted at 05:04:30 while cooldown_until "
                    "was in the future. It succeeded and received provider id "
                    "69390653. The account then reported updated_at 05:05:22 and "
                    "cooldown_until 05:05:22 on the following day.",
        "gold": "REFUTES",
        "why": "the add completed during the cooldown, so it cannot be a block",
    },
    {
        "claim": "vLLM on the RTX 3090 is serving FAITHH inference.",
        "evidence": "POST /api/chat on the live backend returned "
                    'provider="vLLM (RTX 3090)" and model_used="qwen2.5-14b".',
        "gold": "SUPPORTS",
        "why": "the backend names the provider that served the request",
    },
    {
        # Reworded 2026-08-04. The original read "can distinguish a contradiction
        # from an agreement", which is defensible either way: the scores ARE
        # separable, just inverted, so a reader answering SUPPORTS was not wrong.
        # Labeling that SUPPORTS would teach the reader that
        # technically-separable-but-backwards counts as working -- the exact
        # reasoning failure the arbiter exists to catch. The ordering claim below
        # has no reading under which it holds.
        "claim": "Cosine similarity scores agreeing statements higher than "
                "contradicting ones.",
        "evidence": "Using BAAI/bge-base-en-v1.5: three directly contradictory "
                    "sentence pairs scored 0.8439, 0.8965 and 0.9515. A pair that "
                    "genuinely agreed scored 0.5010. An unrelated pair scored 0.5007.",
        "gold": "REFUTES",
        "why": "agreement scored 0.5010 while contradictions scored 0.84-0.95, so "
               "the ordering is inverted",
    },
    {
        "claim": "Ollama is installed and running on the Gen8.",
        "evidence": "`command -v ollama` produced no output on that host, and "
                    "curl to http://127.0.0.1:11434/api/tags returned "
                    "'Connection refused'.",
        "gold": "REFUTES",
        "why": "no binary and nothing listening",
    },
    {
        "claim": "The parked TorBox queue drains on its own while Sonarr keeps "
                "grabbing new releases.",
        "evidence": "The queue held 211 items, all created 2026-08-01, and was "
                    "still exactly 211 three days later. cooldown_until is "
                    "measured 24 hours from the most recent successful add.",
        "gold": "REFUTES",
        "why": "nothing drained over three days, and each new grab restarts the "
               "window",
    },
    {
        # Rewritten 2026-08-04, twice over. The original evidence ended "It is a
        # pure function from conversation text to a tiered entry" -- an assertion,
        # not an observation, which handed the reader its answer. Replaced with a
        # measurement.
        #
        # The claim was also narrowed. Running the test surfaced what the code
        # search had missed: extract.py takes --date, defaulting to
        # date.today().isoformat(), so the same conversation extracted tomorrow
        # yields a different entry. The unqualified claim is false. It is the tier
        # decision that is deterministic, and that is what repair re-derivation
        # actually depends on.
        "claim": "extract.py's tier decision is deterministic.",
        "evidence": "choose_tier was run three times over the same three inputs. "
                    "The SHA-256 of its output was 6c2b54cca53c0300 on all three "
                    "runs.",
        "gold": "SUPPORTS",
        "why": "identical input produced byte-identical output across repeated runs",
    },
]

FRAMINGS = {
    # Reproduces how the readers were actually called when they failed.
    "A": {
        "system": "Answer with exactly one word: SUPPORTS, REFUTES, or NEUTRAL.",
        "user": "Evidence: {evidence}\nClaim: {claim}",
        "max_tokens": 4,
    },
    # Reasoning before the verdict: the failing cases all needed one inference
    # step, and a single-token answer leaves no room to take it.
    "B": {
        "system": "You judge whether the evidence supports or refutes the claim. "
                  "Reason in at most three sentences, then end with a final line "
                  "exactly of the form 'VERDICT: SUPPORTS' or 'VERDICT: REFUTES' "
                  "or 'VERDICT: NEUTRAL'.",
        "user": "Evidence: {evidence}\nClaim: {claim}",
        "max_tokens": 200,
    },
    # Forces the polarity question to be asked out loud. NEUTRAL is given an
    # explicit, narrow definition because the observed failure was NEUTRAL used as
    # a hedge on evidence that decided the question.
    "C": {
        "system": "You judge a claim against evidence.\n"
                  "Step 1: state what the claim asserts, and what its negation "
                  "would assert.\n"
                  "Step 2: state which of those two the evidence is consistent "
                  "with.\n"
                  "Step 3: answer. Use NEUTRAL only if the evidence is genuinely "
                  "silent on the question -- not merely indirect. If the evidence "
                  "settles the question by one inference step, that is not "
                  "NEUTRAL.\n"
                  "End with a final line exactly of the form 'VERDICT: SUPPORTS' "
                  "or 'VERDICT: REFUTES' or 'VERDICT: NEUTRAL'.",
        "user": "Evidence: {evidence}\nClaim: {claim}",
        "max_tokens": 300,
    },
}


def ask(system: str, user: str, max_tokens: int) -> str:
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "max_tokens": max_tokens,
        "temperature": 0,
    }).encode()
    req = urllib.request.Request(VLLM, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]


def verdict_of(text: str) -> str:
    """Last explicit VERDICT wins; fall back to a bare word for framing A."""
    hits = re.findall(r"VERDICT:\s*(SUPPORTS|REFUTES|NEUTRAL)", text.upper())
    if hits:
        return hits[-1]
    words = re.findall(r"\b(SUPPORTS|REFUTES|NEUTRAL)\b", text.upper())
    return words[-1] if words else "UNPARSED"


def main() -> int:
    only = None
    if "--framing" in sys.argv:
        only = sys.argv[sys.argv.index("--framing") + 1].upper()

    scores: dict[str, int] = {}
    for name, f in FRAMINGS.items():
        if only and name != only:
            continue
        print(f"\n=== framing {name} ===")
        correct = 0
        for c in CASES:
            out = ask(f["system"], f["user"].format(**c), f["max_tokens"])
            got = verdict_of(out)
            hit = got == c["gold"]
            correct += hit
            print(f"  {'PASS' if hit else 'FAIL'}  got={got:9} want={c['gold']:9} "
                  f"{c['claim'][:52]}")
            if not hit:
                print(f"        gold rationale: {c['why']}")
        scores[name] = correct
        print(f"  -> {correct}/{len(CASES)}")

    print("\n=== summary ===")
    for name, n in scores.items():
        print(f"  framing {name}: {n}/{len(CASES)}  ({100*n//len(CASES)}%)")
    # A reader at or below all-NEUTRAL is not usable as a panel member; the panel
    # can only aggregate signal that individual readers actually produce.
    floor = sum(1 for c in CASES if c["gold"] == "NEUTRAL")
    print(f"  all-NEUTRAL baseline: {floor}/{len(CASES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
