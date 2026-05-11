# Seeded Model Training Parameters

Last updated: 2026-03-31

## Purpose

Define a reproducible training parameter framework for reporting ALife-seeded governance model findings.

## Stage Gate

Use this checkpoint before training:

- Data ingestion stable across two consecutive cycles.
- Retrieval drift within guardrails for governance/alife/constella classes.
- At least one seeded batch comparison completed.

## Recommended Initial Recipe (specialized mini-model)

- Method: QLoRA
- Base model class: 7B to 14B instruct model
- Sequence length: 2048
- Epochs: 3
- Learning rate: 2e-4
- LR schedule: cosine
- Warmup ratio: 0.05
- LoRA rank (`r`): 16
- LoRA alpha: 16
- Batch size: 1
- Gradient accumulation: 8
- Eval cadence: every 25 steps
- Early stop patience: 4 eval windows

## Evaluation Protocol (reportable)

- Heldout loss curve over time
- Grounded answer rate (must cite or align with indexed evidence)
- Unsupported claim rate (target: downward trend)
- Governance retrieval precision@5
- ALife mechanism alignment score
- Constella synthesis consistency check

## Minimum Evidence Before Public Findings

- Seeded batch runs: 15+
- Distinct seeded scenarios: 5+
- Validation queries per class (governance/alife/constella): 12+
- At least one ablation (with/without seeded governance data)

## Reproducibility Requirements

- Save exact dataset version paths
- Save train/val/test split files
- Save training hyperparameters JSON
- Save run logs and final checkpoint metadata
- Save post-training retrieval validation report

## Artifact Paths

- Seeded batch reports: `reports/index_runs/alife_seeded_batch_*.json`
- Exported corpus: `ml/training_data/seeded_batches/seeded_batch_corpus_*.jsonl`
- Split definitions: `ml/training_data/seeded_batches/seeded_batch_corpus_*_splits.json`
- Parameter snapshot: `ml/training_data/seeded_batches/seeded_batch_params_*.json`

## Causal Seed Sweep Gate (Generation Five)

Before using ALife A/B contrast as training signal, run a seed sweep to avoid
overfitting on one lucky seed.

- Script: `scripts/run_gen5_seed_sweep.py`
- Purpose: estimate sign-lock stability for key effects across many paired seeds
- Default run: 20 seeds, no Chroma writes (fast gate check)

Example:

```bash
cd /home/jonat/ai-stack && source venv/bin/activate
python3 scripts/run_gen5_seed_sweep.py --seeds 20 --seed-start 505001
```

Gate recommendation:

- Use >= 20 seeds for initial confidence.
- Mark "causal contrast lock" as provisional only if:
  - `pop_a_better_survival_rate >= 0.70`
  - `pop_a_lower_depletion_rate >= 0.70`
- If below threshold, continue tuning policy/noise assumptions before feeding this
  signal into model training.

## Model-Build Paths: What It Takes

### Path A (Recommended): Specialized 7B-or-less experts via fine-tuning

This is practical on your hardware and directly aligned to ecosystem experts.

- Method: QLoRA/LoRA adapters on 3B/7B instruct bases
- Typical hardware:
  - 3B: 1x 12-24GB VRAM GPU
  - 7B QLoRA: 1x 24GB VRAM GPU (your RTX 3090 is viable)
- Data target per specialist:
  - Minimum useful: 10k-50k high-quality instruction examples
  - Stronger specialization: 50k-250k curated examples
- Runtime expectation:
  - Hours to a couple of days per run depending on sequence length and eval cadence
- Best use:
  - Domain-specialist agents (governance, infra, ledger, ALife) in single or parallel routing

### Path B: Full fine-tune (all weights) for 7B

Possible, but significantly heavier than LoRA.

- Hardware: multi-GPU setup (commonly 4-8x 80GB class accelerators for efficient training)
- Operational burden: higher failure/debug cost, storage, checkpoint management
- Recommendation: only after LoRA experts clearly plateau

### Path C: From-scratch pretraining (hard mode)

Technically possible, economically expensive.

- Data:
  - Needs large, deduplicated token corpora (billions of tokens)
  - Strong data engineering and filtering pipeline required
- Compute:
  - 1B model: still substantial cluster-scale compute
  - 3B-7B models: typically data-center class budgets
- Infra:
  - Distributed training stack, fault tolerance, checkpoint orchestration
  - Rigorous eval/ablation framework to avoid expensive blind runs
- Reality check:
  - For ecosystem expertise, curated fine-tuning usually beats from-scratch ROI

## Practical Plan for Your Ecosystem Experts

1. Build/refresh seeded corpora and run causal seed sweep gate.
2. Train 3B specialist first (faster iteration), then 7B for final quality.
3. Keep one general backbone + multiple specialist adapters.
4. Route queries by domain tag and confidence, with fallback to generalist.
5. Promote adapters only when they beat baseline on grounded answer rate and unsupported-claim rate.
