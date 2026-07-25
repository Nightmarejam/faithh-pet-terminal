# Inner Monologue Engine (IME)

High-reasoning companion intelligence. The journal's inner voice.

## What This Is

The IME reads accumulated journal entries and synthesizes patterns across
life domains. It is the long-horizon counterpart to FAITHH:

- **FAITHH**: task coherence, project context, immediate memory
- **IME**: reflective synthesis, life pattern recognition, artificial life seed

## Architecture Foundation

- Resonance Transformer Architecture (see harmony/docs/)
- Resonance Gating: refuses premature synthesis until data is sufficient
- Journal-grounded: fed by ml/output/journal/ entries, not task logs

## Current Status

v0.1.0 — Scaffold only. Reads journal entries, evaluates resonance level.
No synthesis capability yet. That comes after 3+ months of journal data.

## Build

```bash
mkdir build && cd build
cmake ..
make
./ime ../ml/output/journal/
```

## Connection to Artificial Life

This is the prototype. The journal entries are the training signal.
The resonance gate prevents hallucinated synthesis.
Over time, the patterns extracted here will become the design principles
for a companion intelligence that exists alongside humans, not just answers questions.
