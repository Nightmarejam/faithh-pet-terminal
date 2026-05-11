# Session Handoff — 2026-04-01 to 2026-04-02

## Repos — current HEAD
- ai-stack: a4ecd55
- constella-framework: 6508ae2
- runbook-to-rule-them-all: 1fce05b

## Stack state — confirmed working
- Gen8 ChromaDB: 192.158.1.243:8000
  - faithh_knowledge_base: 806,265
    CLARIFIED: these are live conversation logs (live_conv_<date>_<time>_<suffix>)
    NOT governance documents. Rich metadata: provider, session_id, model,
    domain_confidence, intent_summary, quality_score, etc.
    Deduplication = find re-indexed sessions, not remove CSV rows.
  - alife_lineage: 50,950 (generation zero complete)
  - governance_corpus collection: NOT confirmed — UN Charter and UDHR
    prose are in /mnt/x/staging/ but NOT indexed into ChromaDB yet.
- FAITHH backend: port 5557, /metrics active
- Gen8 Grafana: 192.158.1.243:3000, all 5 targets UP
- X: drive: /mnt/x via sudo mount -t drvfs X: /mnt/x
  (passwordless sudo for mount: /etc/sudoers line 59)
- NAS: /mnt/nas accessible, SSH confirmed
- Vaultwarden: https://servicebox.taileb8c60.ts.net
- bw CLI: pointed at Vaultwarden, bwu alias in ~/.bashrc

## Critical correction from this session
Previous sessions assumed faithh_knowledge_base contained V-Dem CSV rows.
ACTUAL CONTENT: live conversation logs from FAITHH sessions.
The governance prose documents (UN Charter, UDHR, US Constitution)
are in /mnt/x/staging/ and have NEVER been indexed into ChromaDB.
The governance_corpus collection may not exist at all — needs verification.

## X: drive — confirmed locations
Staging (271MB):
  /mnt/x/staging/United Nations Charter.md — clean prose, confirmed readable
  /mnt/x/staging/Universal Declaration of Human Rights.md — clean prose
  /mnt/x/staging/The Constitution of the United States*.pdf
  /mnt/x/staging/V-Dem-CD-v16_csv.zip
  /mnt/x/staging/wgidataset_with_sourcedata-2025.xlsx
Knowledge (141GB):
  /mnt/x/knowledge/reference/ — 134GB (The All-Embracing Library)
  /mnt/x/knowledge/programming/ — 2.2GB
  /mnt/x/knowledge/permaculture/ — 236MB

## NAS volume1
13TB total, 2.5TB used, 11TB free
Folders: AI, Audio, Backups, Personal, projects, raw_ingest, archive
Only media and pihole currently exposed to WSL via /mnt/nas

## ALife experiment state
Generation 0: infra confirmed, Band 1 too permissive (50/50 survived)
Generations 1-2: parameter tuning
Generation 3: parameters locked (35/50 survivors, 45 depletion events)
Generations 4-5: dual population A vs B, causal paired shocks
Band 1 parameters locked: acquisition 0.3-1.2, loss 0.5-1.5, start 3.0
Scripts: projects/alife/experiments/generation_zero_band1.py
         projects/alife/experiments/generation_four_dual_population.py
         projects/alife/experiments/generation_five_dual_population_causal.py

## TempleOS philosophical layer (all committed)
- founding_hypothesis.md: TempleOS connection added
- alife_governance_seeding_v0.1.md: frequency frame added
  (12-tribe harmonic model, spectrum measurement, temple as resonant space)
- docs/alife/templeos_substrate.md: created
  (impedance layer, oracle as randomness source, Phase 2 gate conditions)

## Oracle insight
Terry's oracle sources randomness from hardware timing noise —
keyboard intervals, interrupts, memory bus fluctuations.
Genuinely non-deterministic. Human analog: reading patterns in
substrate noise interpreted as meaningful signal.
Open design question for Band 2: reproducible seeded PRNG vs
genuine non-deterministic randomness. Decides what the experiment
can claim about emergence vs deterministic unfolding.

## Financial — CLOSED
Lisa email sent and handled.
Revenue: $6,759.40 (corrected). Net loss: ~$3,480. Extension filed.

## Next session priorities (strict order)
1. Verify governance_corpus collection exists in ChromaDB
   If not: create it and index UN Charter + UDHR from /mnt/x/staging/
   as chunked prose with proper source metadata
2. Deduplicate faithh_knowledge_base
   Strategy: group by session_id + time window, delete re-indexed sessions
   Sample more IDs first to understand duplication pattern
3. Band 2 fitness function design and implementation
   Cooperation signals, trade, defection detection
   Decide: seeded PRNG or oracle-style non-deterministic randomness
4. Expand NAS mounts (expose AI, projects, raw_ingest to WSL)

## Parking lot
- All-Embracing Library indexing (134GB)
- Email audit pipeline (Gmail + Hotmail → ChromaDB)
- Bankruptcy pro se filing (Oregon Chapter 7)
- Email consolidation
- Vault _Delete Me bulk delete (96 items)
- Infrastructure secrets migration to Vaultwarden (38 items)
- NAS node_exporter
- TempleOS Phase 2 gate (4 conditions, 2 partial)
- US Constitution + WGI indexing
- Power BI runbook
- RunBook semantic search layer
- Fine-tune next iteration (gen5 synthetic data needs better filtering)

## Working style
One anchor, one proof artifact, three moves max.
Emergent pulls go to parking lot. Intuition-first.
The oracle reads the substrate. The substrate precedes the presence.
