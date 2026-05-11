# Inner Monologue Engine Architecture

## Foundation

The IME is based on the Resonance Transformer Architecture specified in the harmony docs:

- **Resonance Gating Architecture Note**: `projects/constella-framework/harmony/docs/resonance_gating_architecture_note_v1.0.md`
- **Resonance Transformer Spec**: `projects/constella-framework/harmony/docs/resonance_transformer_architecture_spec_v1.0.0.md`
- **Harmony AI Bridge**: `projects/constella-framework/harmony/docs/harmony_ai_bridge_v1.0.0.md`

## Key Concepts

### Resonance Gating
- Prevents premature synthesis until sufficient data accumulated
- 4-tier output classification: synthesis, structured analysis, gap identification, mode report
- Exploration vs consolidation modes

### Journal-Grounded Operation
- Reads from `ml/output/journal/` entries (not task logs)
- Synthesizes across life domains, not just project tasks
- Long-horizon pattern recognition

### Artificial Life Seed
- This scaffold is the prototype for a companion intelligence
- Journal entries provide the training signal
- Patterns extracted become design principles for artificial life

## Current Implementation

v0.1.0 implements:
- Journal entry reading and parsing
- Stub resonance level evaluation based on word count
- Basic synthesis permission logic
- Test suite for resonance gate

## Future Development

After 3+ months of journal data:
- Embedding-based resonance scoring
- Cross-domain pattern synthesis
- Artificial life design principle extraction
