# Financial Data Intake (AI-assisted)

**Purpose:** Guided conversation to gather partnership / small-business figures for Power BI, producing CSVs and CPA flags — without replacing a CPA.

**Canonical prompt file:** [`prompts/financial_intake_v1.txt`](../../prompts/financial_intake_v1.txt) (copy the block between `----- SYSTEM PROMPT` and `----- END SYSTEM PROMPT -----`).

**Related:** [TOMCAT_DASHBOARD.md](../business/TOMCAT_DASHBOARD.md), [PORTFOLIO_OVERVIEW.md](../business/PORTFOLIO_OVERVIEW.md).

---

## Tomorrow’s session — quick checklist

1. **Open** `prompts/financial_intake_v1.txt` and copy the **system prompt** block only (not the `#` header lines unless your UI allows them).
2. **Choose channel:**
   - **Claude (cloud):** New Project → paste into project instructions → start chat; or paste prompt + “act as this assistant.”
   - **FAITHH (local):** New chat → set system / personality context from the same block → use your preferred local model (e.g. `qwen25-grounded:latest` if configured).
3. **Run a dry run** on your own numbers (e.g. Tom Cat Sound) once before a client session — note any questions that feel slow or confusing.
4. **Power BI:** After CSVs exist, follow your runbook steps **manually** so you still own the dashboard for next year.
5. **Boundaries:** AI = structure, math checks, formatting, flags. Human/CPA = COGS vs OpEx judgment, commingling, tax positions.

---

## Three deployment options

| Option | Where | Best for |
|--------|--------|----------|
| **A — Claude** | claude.ai / Project instructions | Fastest test, no repo setup |
| **B — FAITHH** | Local stack + prompt file | Sensitive client data stays on your machine |
| **C — Future** | Small Flask POST + HTML form | Client-facing without installing AI tools |

---

## Workflow zones (why this isn’t “full automation”)

- **AI zone:** One-question flow, confirmations, running totals internally, CSV layout, CPA flag capture, plain-English recap.
- **Human zone:** What belongs in which bucket, narrative for the CPA, any legal/tax call.
- **Learning zone:** The client learns categories by answering; the **review gate** (confirm summary before file generation) is the main learning beat.

---

## Output artifacts (after client confirms review summary)

| Artifact | Role |
|----------|------|
| `financials.csv` | Revenue, COGS, derived lines, OpEx, net |
| `members.csv` | Names, ownership decimals, roles |
| `k1_allocations.csv` | Allocated loss/share (rounded dollars) |
| CPA block | Everything flagged during intake |

---

## Template variables (when you customize)

| Variable | Default | Customize to |
|----------|---------|----------------|
| Entity examples | LLC, partnership | Add S-corp, sole prop as needed |
| Large purchase flag threshold | $500 | Match client scale |
| CPA language | “flag for CPA review” | “your accountant” / “tax preparer” |
| Deliverable format | CSV | JSON / Excel later if needed |

---

## Version history

| Version | Date | Notes |
|---------|------|--------|
| 1.0 | 2026-04-03 | Initial generalized template (Tom Cat Sound 2024 intake design); Form 1065–oriented partnership flow |

---

## Changelog in repo

When you change the prompt, bump the version line in `prompts/financial_intake_v1.txt` and add a row to the table above.
