# Why inference does not run on the Gen8

**Decision record** · first written 2026-07-27 · **escalated 2026-07-30**
Referenced by [FAITHH_REDESIGN.md](FAITHH_REDESIGN.md) ("the Gen8 cannot sustain
GPU compute") — this is the evidence behind that sentence.

## The short answer

**It is electrical, not thermal, and not VRAM.** The Gen8's PSU cannot supply the
current transients a GPU draws under sustained compute. The machine loses power
outright — no shutdown sequence, no kernel panic, no OOM.

This is worth stating plainly because the intuitive explanations are both wrong:

| plausible guess | why it is wrong |
|---|---|
| "6 GB VRAM is too small" | The workload fit. It died mid-run, not on allocation. |
| "it overheated" | CPU stayed 40–49 °C with no thermal events logged. |
| "out of memory" | No OOM killer entries; peak RSS was ~2 GB of 31 GB. |

## Evidence

**2026-07-27 — two hard shutdowns, both under sustained GPU load.** iLO IML
recorded `System Power Fault Detected`. One was a BGE embedding benchmark; the
other an ingest run that had written exactly 128 chunks — one `BATCH` constant —
before dying mid-batch. A four-hour CPU-only compile on the same host did **not**
kill it.

**Mechanism.** GPUs draw microsecond current spikes of 2–3× their rated draw. A
12-year-old 150 W PSU with aged capacitors can no longer buffer those, so
over-current protection trips. *Average* draw looks fine throughout, which is why
the PSU self-reports `Ok` and why this is easy to misdiagnose.

**2026-07-30 — it now dies at idle.** Journal ends mid-cron at 02:29:01 UTC with
the same hard-power-loss signature, under only a few HTTP requests and two cron
jobs. Previous boot ended 02:29:01, next began 02:33:59. Nothing GPU-related was
running.

That is an escalation, and it changes the risk model: the PSU should be treated as
**actively failing**, not merely transient-limited. Everything recovered on its own
(chromadb via its restart policy, `faithh-backend` via its systemd unit), but
unplanned power loss during a Chroma write is how stores get corrupted.

*Note: the 2026-07-30 IML has not been read — `ipmitool` needs sudo and the iLO web
UI was not consulted. The hard-power-loss signature is inferred from the abrupt log
truncation, consistent with the two confirmed 2026-07-27 events.*

## Measured: Plex transcoding is not the risk

**2026-07-30**, `scripts/ops/gpu_load_sample.py`, 30 samples across one live transcode:

| | idle | during transcode |
|---|---:|---:|
| encoder (NVENC) | 0% | **100% peak, 34% mean** |
| decoder (NVDEC) | 0% | 20% peak |
| **CUDA cores (sm)** | 0% | **16% peak, 5.2% mean** |
| GPU memory | 565 MB | 1,206 MB |
| SM clock | 210 MHz | 1,860 MHz (of 2,100) |
| temperature | 43 °C | 62 °C |

This confirms what the failure history already suggested: **every power-loss event on
this host followed CUDA compute, never a transcode.** They are different silicon.
Transcoding saturates the fixed-function NVENC block while the CUDA array stays
near-idle at 5% mean; embedding does the opposite and drives the array toward the
board's ceiling.

Two details worth keeping:

- The trace is **bursty** — rows alternate between 100% encoder and 0%. That is the
  transcoder throttle buffer filling and pausing, which is the desirable shape for a
  marginal PSU: short bursts with idle gaps rather than a sustained draw.
- The 16% CUDA peak during transcode is **HDR tone mapping**, which runs as a shader.
  It is the only CUDA component of a Plex transcode. Disabling it would remove that
  load at the cost of washed-out HDR — not recommended, but it is the lever if one is
  ever needed.

Practical consequence: **limiting simultaneous transcodes is not a power mitigation on
this host.** An earlier change set `TranscodeCountLimit=2` on that reasoning; the
reasoning was wrong. The A1000 will exhaust encoder capacity long before transcoding
becomes an electrical problem.

### Power cap

Applied 2026-07-30: `nvidia-smi -pm 1 && nvidia-smi -pl 35` — 35 W of a 50 W default,
persisted by `infra/systemd/nvidia-powercap.service` because nvidia-smi settings reset
on every boot (a manual cap disappears at exactly the moment it matters).

The cap bounds *sustained* draw. The diagnosed failure is microsecond transients, which
a power limit smooths by holding clocks lower rather than eliminating. It reduces risk;
it does not fix the PSU. Note the A1000 reports no `power.draw` telemetry at all, even
with persistence enabled — SM clock is the proxy.

## Consequences

1. **Never run sustained GPU compute on the Gen8.** Embedding, fine-tuning, and
   inference all run on the Windows workstation. Brief Plex transcodes are fine;
   continuous compute is not.
2. **Inference lives on the RTX 3090** under vLLM in WSL2, consumed by the Gen8
   over the tailnet. See [EMBEDDINGS.md](EMBEDDINGS.md) for the embedding half of
   the same split.
3. **The Gen8 is a storage and service host**: Chroma, the FAITHH backend, Plex,
   monitoring. It receives writes; it does not compute.
4. **Assume it can vanish at any moment.** Anything stateful on it needs a restart
   policy (`unless-stopped` for containers, a systemd unit for services) and
   verified backups.

## The mistake this document exists to prevent

On 2026-07-30 an embedding job for 5,302 documentation chunks was very nearly
launched with `FAITHH_EMBED_DEVICE=cuda` **on the Gen8** — precisely the operation
that causes this failure. It was caught before running. The correct invocation
embeds on the workstation and writes over the tailnet:

```bash
CHROMA_HOST=servicebox.taileb8c60.ts.net \
FAITHH_EMBEDDER_MODEL=BAAI/bge-base-en-v1.5 \
FAITHH_EMBED_DEVICE=cuda:1 \
D:/faithh-ingest/venv/Scripts/python.exe scripts/ingest/index_docs.py
```

`cuda:1` is the idle GTX 1080 Ti — the 3090 is normally held by vLLM at 0.90
memory utilization, leaving under 1 GB free.

## Remediation

Replacing the PSU is the fix. Until then the constraint holds, and the idle-crash
behaviour means it holds more tightly than before. A CR2032 for the BIOS battery is
also outstanding.
