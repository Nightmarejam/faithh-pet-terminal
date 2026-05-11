# System Transparency Implementation Checklist

Last updated: 2026-03-31  
Scope: Windows host + WSL + NAS + Gen8 + FAITHH indexing pipeline

---

## 0) Success Criteria (Definition of Done)

- You can answer, in under 2 minutes:
  - "Why is this task slow right now?"
  - "Which storage path/device is bottlenecking?"
  - "What data is indexed vs not indexed for governance/ALife?"
- You have repeatable baselines for:
  - local disk throughput
  - external drive throughput
  - NAS read/write throughput
  - embedding/indexing throughput
- Governance + ALife indexing pipeline can run from a written runbook (no ad-hoc guessing).

---

## 1) Host Monitoring Baseline (Windows + WSL + NAS + Gen8)

### 1.1 Windows host telemetry (primary bottleneck visibility)

- Install/use:
  - Performance Monitor (built-in)
  - Task Manager Performance tab
  - Resource Monitor (`resmon`)
  - Optional: Grafana Agent / Telegraf / Prometheus node exporter for Windows

- Track these counters at 5s intervals:
  - `PhysicalDisk(*)\\Disk Read Bytes/sec`
  - `PhysicalDisk(*)\\Disk Write Bytes/sec`
  - `PhysicalDisk(*)\\Avg. Disk sec/Read`
  - `PhysicalDisk(*)\\Avg. Disk sec/Write`
  - `PhysicalDisk(*)\\Current Disk Queue Length`
  - `Processor(_Total)\\% Processor Time`
  - `Memory\\Available MBytes`
  - `Network Interface(*)\\Bytes Total/sec`

- Output target:
  - `C:\monitoring\perf-logs\` (CSV or BLG exports)

### 1.2 WSL telemetry (backend + indexing process visibility)

- Install:
  - `sysstat` (`iostat`, `pidstat`)
  - `iotop` (if available)

- Baseline commands:
  - `iostat -x 2 30`
  - `pidstat -d -r -u 2 30`
  - `free -h`
  - `df -h`

- Save outputs to:
  - `/home/jonat/ai-stack/reports/perf/wsl/`

### 1.3 NAS telemetry

- Capture:
  - disk utilization and latency (per volume)
  - SMB/NFS throughput
  - CPU/RAM

- Minimum check:
  - NAS dashboard screenshots + exported logs for each benchmark run

### 1.4 Gen8 telemetry

- Capture:
  - ChromaDB process CPU/RAM
  - network in/out
  - disk I/O where Chroma data lives

- Verify endpoints during runs:
  - Chroma heartbeat/health
  - collection count before/after indexing

---

## 2) Storage Throughput Truth Tests (Repeatable)

Run each test with monitoring active.

### 2.1 Local NVMe baseline

- Read/write test file (10GB+), record MB/s and latency.
- Run 3 passes and keep median.

### 2.2 External drive baseline (each drive)

- Test sequential read/write and random small-file behavior.
- Record:
  - filesystem type
  - USB/SATA controller path
  - cable/port used
  - observed MB/s and latency

### 2.3 NAS baseline

- Copy large single-file and mixed small-file sets.
- Measure both directions:
  - Windows -> NAS
  - NAS -> Windows

### 2.4 Interpretation thresholds

- If queue length spikes with high active time and low MB/s -> storage bottleneck.
- If disk is fine but network saturates -> transport bottleneck.
- If both are fine but indexing slow -> embedding CPU bottleneck.

---

## 3) File Inventory and Classification (Windows + NAS)

Goal: full visibility before reorganizing anything.

### 3.1 Inventory schema

For each file capture:
- `path`
- `size_bytes`
- `modified_at`
- `extension`
- `hash` (for duplicate detection; optional staged)
- `source_host` (`windows` / `nas`)
- `domain_guess` (`governance`, `alife`, `constella`, `business`, `other`)

### 3.2 Output targets

- Windows inventory:
  - `/home/jonat/ai-stack/reports/inventory/windows_inventory.csv`
- NAS inventory:
  - `/home/jonat/ai-stack/reports/inventory/nas_inventory.csv`
- Combined:
  - `/home/jonat/ai-stack/reports/inventory/combined_inventory.csv`

### 3.3 Classification pass

- Build one reviewed subset for indexing candidates:
  - `reports/inventory/index_candidates_governance_alife.csv`
- Mark each candidate:
  - `include_for_index` (`yes/no`)
  - `target_domain`
  - `target_source_type`
  - `sensitivity` (`public/internal/private`)

---

## 4) Governance + ALife Data Pipeline (Pre-seed for scenarios)

### 4.1 Canonical target domains

- `constella_constitutional`
- `alife`
- `faithh_core` (high-signal memory/state)

### 4.2 Source priorities

Priority 1:
- constitutional frameworks
- governance research docs
- ALife findings/summaries
- experiment result JSONs with clear outcomes

Priority 2:
- curated discussion summaries (not raw chat dumps)

Avoid by default:
- raw stack traces
- raw JSON blobs with no semantic summary
- mixed/noisy conversation exports without filtering

### 4.3 Pre-index checklist

- File exists and readable
- Domain + source_type assigned
- document_type assigned
- sensitive content policy checked
- dedupe check by file hash/title/id

### 4.4 Index run protocol

1. Run Chroma health audit:
   - `python3 scripts/audit_chroma_health.py`
2. Run targeted index script(s)
3. Re-run health audit
4. Spot-check retrieval with 5 governance and 5 ALife queries
5. Save run summary in:
   - `reports/index_runs/YYYY-MM-DD_run_summary.md`

---

## 5) CPU-Only Embedding Operations (Until T1000)

- Keep embeddings standardized:
  - model: `all-MiniLM-L6-v2`
  - dimension: `384`
- Force CPU path for indexing scripts where needed:
  - `CUDA_VISIBLE_DEVICES=""`
- Schedule large index jobs off-peak.
- Batch size tuning:
  - small enough to avoid memory spikes
  - large enough to keep throughput stable

---

## 6) Weekly Operating Cadence

### Daily (5-10 min)
- check backend health + Chroma count
- watch active disk/network load during heavy tasks

### Weekly (30-45 min)
- run inventory delta (new/changed files)
- run `audit_chroma_health.py`
- review top retrieval misses/drift

### Bi-weekly
- governance + ALife candidate curation batch
- one controlled index session with summary report

---

## 7) Immediate Next Execution (This Session)

**Precondition for NAS-backed work, candidate generation, and indexing:** Gates A, B (including B-win where applicable), and C in `reports/index_runs/2026-03-31_week1_device_baseline.md` must **pass** before any step that exports from the canonical NAS mount, builds indexing candidates from that export, or runs an index session. If a gate fails, stop at folder/baseline-only steps (1–3) until the baseline doc is updated.

1. Create output folders:
   - `reports/perf/wsl`
   - `reports/perf/windows`
   - `reports/perf/nas`
   - `reports/inventory`
   - `reports/index_runs`
2. Capture one WSL baseline (`iostat`, `pidstat`, `df`, `free`).
3. Capture one Windows disk/network baseline during a file copy.
4. **Precondition:** Week‑1 gates pass. Export first Windows + NAS file inventories to CSV.
5. **Precondition:** Week‑1 gates pass. Produce first `index_candidates_governance_alife.csv`.
6. **Precondition:** Week‑1 gates pass. Run one curated governance/ALife index session and log run summary.

---

## 8) Week 1 — device identity, Plex/Plexamp assumptions, reliability gates

Canonical write-up: `reports/index_runs/2026-03-31_week1_device_baseline.md` (captured 2026-03-31).

- **Identity:** Re-verify quarterly with `hostname` / `uname -a` on WSL, `ssh nas "hostname && uname -a"`, and Chroma `GET http://192.158.1.243:8000/api/v2/heartbeat` from WSL.
- **Plex / Plexamp (SSoT):** Single table with `UNVERIFIED:<TOKEN>` placeholders and verification commands is §2 of that report—do not duplicate paths here.
- **Gates:** Before indexing or NAS staging runs, apply health, WSL access, **Gate B-win (native Windows / PowerShell via interop)**, and ingest readiness in that report.
