# Runbook — system review

**Living document.** Run this end to end when you want to know the system is sound,
before adding capability, or after a period of heavy change.

It is ordered so each phase produces the evidence the next one needs. Skipping ahead
is the failure mode: every bug found on 2026-07-30 was hidden behind an earlier one,
and each looked complete until the layer beneath it was fixed.

**Exit criterion:** the observer reports 8/8 clean, *and* every phase below has been
run rather than assumed.

---

## Phase 0 — Automated baseline (2 minutes)

```bash
python scripts/ops/observer_report.py
```

Read-only. Exit 0 clean, 1 warnings, 2 critical. Do not proceed past a critical —
particularly **deploy-drift**, which means the running process is not the code on
disk and every subsequent observation is about the wrong build.

| check | what a failure means |
|---|---|
| `dimension` | embedder and collection disagree; retrieval is ungrounded |
| `deploy-drift` | you are testing code that is not running |
| `feedback-loop` | model output is being indexed as fact again |
| `doc-currency` | a document asserts something verified false |
| `reach:gen8->vllm` | inference unavailable; the link that matters, not localhost |

---

## Phase 1 — Is the running system the intended system?

```bash
ssh servicebox "systemctl show faithh-backend -p ActiveEnterTimestamp --value"
ssh servicebox "stat -c %y ~/ai-stack/faithh_professional_backend_fixed.py"
cd ~/repos/faithh-pet-terminal && git status --short && git log --oneline -3
ssh servicebox "cd ~/ai-stack && git log --oneline -1 && git status --short"
```

Three copies exist — your working tree, `origin/main`, and the Gen8 checkout — and
they drift independently. The Gen8 currently carries hand-copied files, so its git
status is expected to be dirty; what matters is that the *deployed file* is not newer
than the running process.

---

## Phase 2 — Storage truth

```bash
ssh servicebox "cd ~/ai-stack && ./venv/bin/python - <<'PY'
import chromadb
c = chromadb.HttpClient(host='localhost', port=8000)
for col in sorted(x if isinstance(x,str) else x.name for x in c.list_collections()):
    h = c.get_collection(col); pk = h.peek(limit=1); e = pk.get('embeddings')
    dim = len(e[0]) if e is not None and len(e) and e[0] is not None else None
    print(f'{col:<32}{h.count():>9,}  dim={dim}')
PY"
```

Every collection the live embedder queries must be **768-dim**. Others may exist at
384 (telemetry, gated rows) provided nothing queries them with the BGE embedder.

Before deleting any collection, prove the content is retrievable elsewhere:

```bash
python scripts/ingest/measure_overlap.py --source <legacy> --sample 400
```

Titles and ids cannot answer this — collections chunk differently, so they never line
up even for identical conversations. A title-based estimate once said 86% covered when
the true figure was 83.5%, with ~9,250 genuinely unique documents.

---

## Phase 3 — Documentation currency

```bash
python scripts/docs/audit_doc_currency.py --severity high
```

Target: **0 high-severity**. Then read the medium/low output with judgement — it is
advisory, not a checklist.

When a verified fact changes, **add a rule** rather than fixing documents one by one.
The rule is what catches the next occurrence.

Two distinctions this audit encodes, both learned by getting them wrong:

- **Records are not stale.** A dated audit or completion report describes what was
  true when written. Dates in filenames mark snapshots (AGENTS.md §8).
- **Not every old value is wrong.** `all-MiniLM-L6-v2` is still correct for
  `auto_metadata_tagger.py`; only KB ingest and query must be BGE. Check context
  before "fixing" working code.

---

## Phase 4 — Retrieval quality

Ask questions whose correct answer you already know, and read the metadata, not just
the prose:

```bash
curl -s --max-time 200 -X POST http://servicebox.taileb8c60.ts.net:5557/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Why did we move inference to the 3090 instead of the Gen8?"}' \
  | python -c "import json,sys; d=json.load(sys.stdin); print(d['best_distance'], d['integrations_used']); [print(' ', (s.get('metadata') or {}).get('path'), s.get('distance')) for s in (d.get('rag_results') or [])[:3]]"
```

Check, in order:

1. **`best_distance`** — under 0.60, and *never exactly 1.0*
2. **Which sources ranked** — a curated doc should outrank a chat transcript
3. **No `live_conversation`** in the sources — model output must not ground answers
4. **Does the answer match the document it cites?** It once cited the right document
   and gave the wrong reason, because only one chunk of seven was retrieved

Then vary the question. **A metric that never moves is not a measurement** — three
separate constants (`best_distance` 1.0, `convergence` 0.5, provider health) each
looked like data for weeks.

---

## Phase 5 — Derived artifacts

Chips are **derived from the corpus** and hold no document references, so changing
documents cannot break a link — but it does make centroids describe a corpus that no
longer exists.

```bash
ssh servicebox "cd ~/ai-stack && ./venv/bin/python -c \"
import json, collections
d = json.load(open('ml/output/consolidated_chips.json'))
t = collections.Counter()
for c in d['chips']:
    for k, v in (c.get('categories') or {}).items(): t[k] += v
print('chips built from', format(sum(t.values()), ','), 'docs:', t.most_common(4))\""
```

Compare that total against the live collection size. As of 2026-07-30 the chips were
built from 32,526 documents (96% chat exports) against a 63,733-document corpus, with
**zero** documentation chunks represented — so the ML topic readout describes an older,
chat-dominated system. Rebuild chips after any material corpus change.

---

## Phase 6 — Host and service health

```bash
ssh servicebox "uptime -p; systemctl is-active faithh-backend; docker ps --format '{{.Names}} {{.Status}}'"
wsl -e bash -lc "systemctl is-active vllm; nvidia-smi --query-gpu=index,memory.used --format=csv,noheader"
```

Expect the 3090 near 23 GB when vLLM is loaded. The Gen8 loses power under sustained
GPU load and, since 2026-07-30, at idle as well — treat unexplained reboots as
hardware, not software
([GEN8_POWER_CONSTRAINT.md](../architecture/GEN8_POWER_CONSTRAINT.md)).

If WSL is down, vLLM is down: the VM is torn down shortly after the last session
exits, and the hidden keepalive (`C:\Users\fez_8\bin\wsl-keepalive.vbs`, launched by
the `WSL-Keepalive` logon task) is what holds it.

---

## Phase 7 — Write it down

Anything found becomes one of:

- a **rule** in `audit_doc_currency.py`, if a document could assert it again
- a **check** in `observer_report.py`, if the system could re-enter the state
- a **decision** in `decisions_log.json` with rationale, if a choice was made
- an **ADR** in `docs/architecture/`, if it changes how the system is understood

A finding that produces none of these will be rediscovered.

---

## What "spotless" means

Not "no problems". It means:

1. Observer 8/8, doc audit 0 high-severity
2. Every metric verified to **move** when its input changes
3. Every collection's dimension matches whatever queries it
4. Derived artifacts rebuilt against the current corpus
5. Every finding written into a rule, a check, or a decision

Known-and-recorded beats unknown-and-clean. The Gen8 PSU is failing and that is not
spotless — but it is understood, documented, and worked around, which is the
achievable goal.
