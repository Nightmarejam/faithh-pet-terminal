"""
Guards for bulk Chroma HTTP indexing: required metadata and post-ingest growth checks.

Import from bulk upsert scripts (e.g. index_staged_nas_sources.py, indexing/index_documents_chromadb.py).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def normalize_source_for_metadata(path: str | Path, repo_root: Path | None) -> str:
    """Prefer repo-relative paths for Chroma metadata ``source`` (census-friendly)."""
    p = Path(path)
    if repo_root is None:
        return str(p)
    try:
        root = repo_root.resolve()
        if p.is_absolute():
            return str(p.resolve().relative_to(root))
        return str((root / p).resolve().relative_to(root))
    except ValueError:
        return str(p)


def validate_bulk_metadata(
    meta: dict[str, Any],
    *,
    keys: tuple[str, ...] = ("domain", "category", "source"),
) -> list[str]:
    """Return list of missing or empty required keys."""
    missing: list[str] = []
    for k in keys:
        v = meta.get(k)
        if v is None or (isinstance(v, str) and not str(v).strip()):
            missing.append(k)
    return missing


def check_post_ingest_growth(
    pre_count: int,
    post_count: int,
    *,
    multiplier: float = 3.0,
    force: bool = False,
    label: str = "collection",
) -> None:
    """
    Abort if the collection grew more than ``multiplier``× in one bulk run (unless force).

    Raises SystemExit on guard trip.
    """
    if pre_count <= 0:
        return
    if post_count > int(pre_count * multiplier):
        msg = (
            f"BULK_INGEST_GUARD: {label} grew {pre_count:,} -> {post_count:,} "
            f"(>{multiplier:g}× pre-count). Pass --force to proceed."
        )
        if not force:
            raise SystemExit(msg)
        print(f"WARNING: {msg} (--force override)")
