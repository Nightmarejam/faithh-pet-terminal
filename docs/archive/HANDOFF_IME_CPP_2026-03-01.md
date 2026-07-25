# FAITHH Handoff: Inner Monologue Engine — C++ Verification & Scaffold
**Date:** 2026-03-01  
**Written by:** Claude (MCP session)  
**Priority:** Discovery first, build second  
**Archive to:** `docs/archive/` after consumption

See full handoff: HANDOFF_IME_CPP_2026-03-01.md (copy from Claude Desktop outputs)

## Quick Summary
1. Find C++ environment (`find /home/jonat -name "*.cpp"`) — report what exists
2. If none: scaffold `ime/` directory with CMakeLists.txt, resonance_gate, journal_reader
3. Build and run against `ml/output/journal/`
4. Index harmony docs into FAITHH RAG
5. Test FAITHH can answer resonance gating questions from actual docs

## Key Concept
IME ≠ FAITHH. FAITHH = task coherence. IME = reflective synthesis + artificial life seed.
Architecture foundation: projects/constella-framework/harmony/docs/
