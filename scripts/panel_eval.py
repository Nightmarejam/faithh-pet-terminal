#!/usr/bin/env python3
"""Does advocate/skeptic disagreement predict when a single reader is wrong?

Step 2 of the sequencer. This is the question the whole panel design rests on. If
disagreement does not track error, more readers add cost and nothing else, and the
mediator has nothing real to mediate over.

## What is being measured

Not accuracy. **Detection.** A panel is worth building if disagreement flags the
cases a lone reader gets wrong -- even when neither panel member is itself right.
Observed earlier: on the cooldown claim the advocate said SUPPORTS and the skeptic
said NEUTRAL. Both were wrong (the answer is REFUTES), but they disagreed, and
"do not mark this confirmed" is the correct action. A panel can be useful while
being individually unreliable, which is the entire argument for one.

So the scoring is a detector's, not a judge's:

    true positive   they disagree AND the solo reader was wrong   -> caught it
    false negative  they agree     AND the solo reader was wrong   -> missed it
    false positive  they disagree AND the solo reader was right    -> noise
    true negative   they agree     AND the solo reader was right    -> quiet

The number that decides whether to continue is the false-negative count. A
detector that stays silent on real errors cannot be fixed by adding members --
agreement between biased readers means they share the bias, and a third reader
drawn from the same model shares it too.

## Why both readers get framing C

C is the framing that doubled solo accuracy, and it fails by committing to wrong
verdicts rather than abstaining. Confident errors are precisely what an opposed
reader is supposed to catch, so C is the honest test. Running the panel on a
weaker framing would flatter it.

Bias is applied as a prefix, leaving C's polarity procedure intact. The point is
opposed priors over the same procedure -- not two different tasks.

Usage:
    python3 scripts/panel_eval.py
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from reader_eval import CASES, FRAMINGS, MODEL, VLLM, verdict_of  # noqa: E402

# Opposed priors, same procedure. Deliberately asymmetric in what they are told
# to look for, identical in how they are told to decide.
ROLES = {
    "advocate": "You start from the position that the claim is TRUE and look for "
                "evidence supporting it. State your honest verdict even if it "
                "contradicts your starting position.\n\n",
    "skeptic": "You start from the position that the claim is FALSE and look for "
               "evidence refuting it. State your honest verdict even if it "
               "contradicts your starting position.\n\n",
}


def ask(system: str, user: str, max_tokens: int) -> str:
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "max_tokens": max_tokens, "temperature": 0,
    }).encode()
    req = urllib.request.Request(VLLM, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]


def hedge_score(text: str) -> int:
    """Crude proxy for 'this reader knows it is reaching'.

    The advocate that argued SUPPORTS on refuting evidence wrote "does not
    explicitly state" inside its own justification. That self-report is worth
    more than its verdict, and unlike a logprob it is not saturated -- the
    verdict token came back at p=1.0000 on an answer that was wrong.
    """
    markers = ("does not explicitly", "not explicitly", "insufficient", "unclear",
               "implies", "suggests", "may ", "might ", "could ", "assuming",
               "indirect", "does not directly", "no direct")
    low = text.lower()
    return sum(low.count(m) for m in markers)


def main() -> int:
    f = FRAMINGS["C"]
    tp = fn = fp = tn = 0
    print(f"{'case':52} {'solo':9} {'adv':9} {'skep':9} agree  outcome")
    for c in CASES:
        user = f["user"].format(**c)
        solo = verdict_of(ask(f["system"], user, f["max_tokens"]))
        out = {}
        for role, prefix in ROLES.items():
            t = ask(prefix + f["system"], user, f["max_tokens"])
            out[role] = (verdict_of(t), hedge_score(t))
        adv, skep = out["advocate"], out["skeptic"]
        agree = adv[0] == skep[0]
        solo_wrong = solo != c["gold"]

        if not agree and solo_wrong:
            tp += 1; label = "CAUGHT"
        elif agree and solo_wrong:
            fn += 1; label = "MISSED"
        elif not agree and not solo_wrong:
            fp += 1; label = "noise"
        else:
            tn += 1; label = "quiet"
        print(f"{c['claim'][:52]:52} {solo:9} {adv[0]:9} {skep[0]:9} "
              f"{str(agree):5}  {label}")
        print(f"{'':52} hedge: advocate={adv[1]} skeptic={skep[1]}  gold={c['gold']}")

    n = len(CASES)
    errs = tp + fn
    print(f"\n=== detector ===")
    print(f"  solo reader wrong on {errs}/{n}")
    print(f"  caught by disagreement : {tp}")
    print(f"  MISSED (agreed, wrong) : {fn}   <- the number that decides this")
    print(f"  noise  (disagreed, right): {fp}")
    print(f"  quiet  (agreed, right) : {tn}")
    if errs:
        print(f"  recall {tp}/{errs} = {100*tp//errs}%")
    if fn:
        print("\n  A missed error means both biased readers shared the same "
              "mistake.\n  Adding a third reader from the same model shares it too "
              "-- widen the\n  evidence, not the panel.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
