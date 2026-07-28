# Broken maintenance scripts, archived 2026-07-28

Both fail to parse and nothing imports either. Archived rather than repaired
because the breakage is structural, not cosmetic.

**`genomic_experiments_enhancer.py`** — truncated. The triple-quoted template
opened at line 1117 never closes; the file simply ends at 1142. It is also the
generator that produced the four `experiments/genomic/*_enhanced.py` files, each
of which contained a real newline where `\n` was intended (`print("` followed by
a line break). Those four were repaired in place; this generator would reproduce
the fault if run, so it should be rewritten rather than restored.

**`cleanup_and_backup.py`** — one-off from the "RAG + Memory System Complete"
milestone. The f-string at line 279 terminates early, leaving markdown content
(including a ✅) parsed as code at line 284.

If either is wanted again, rewrite from the intent rather than fixing the text —
in both cases the file no longer says what its author meant.
