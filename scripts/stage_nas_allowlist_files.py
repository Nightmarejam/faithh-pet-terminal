#!/usr/bin/env python3
"""
Stage approved NAS allowlist files into local canonical intake roots.

This uses SSH + remote cat for safe copy without deleting/moving NAS files.
"""

from __future__ import annotations

import argparse
import csv
import json
import shlex
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath


ALLOWED_SCOPES = frozenset({"governance", "alife", "constella"})
VOLUME_PREFIX = PurePosixPath("/volume1")


def nas_relative_subpath(remote_path: str) -> PurePosixPath:
    """
    Map a NAS absolute path to a safe relative subpath under the scope import folder
    (mirrors move-plan intent: preserve directory shape under /volume1).
    """
    raw = remote_path.strip()
    p = PurePosixPath(raw)
    if not p.is_absolute():
        p = PurePosixPath("/") / p
    try:
        rel = p.relative_to(VOLUME_PREFIX)
    except ValueError:
        rel = PurePosixPath(*p.parts[1:]) if len(p.parts) > 1 else PurePosixPath(p.name)

    safe_parts: list[str] = []
    for seg in rel.parts:
        if seg == ".":
            safe_parts.append("__dot__")
        elif seg == "..":
            safe_parts.append("__dotdot__")
        else:
            cleaned = seg.replace("\x00", "")
            if not cleaned:
                cleaned = "_empty_"
            safe_parts.append(cleaned)
    return PurePosixPath(*safe_parts) if safe_parts else PurePosixPath("_root")


def scope_intake_subdir(scope: str) -> str:
    if scope == "governance":
        return "governance_sources"
    if scope == "alife":
        return "alife_sources"
    return "constella_sources"


def local_target(scope: str, src_path: str, root: Path) -> Path:
    rel = nas_relative_subpath(src_path)
    base = root / scope_intake_subdir(scope) / "nas_import"
    return base.joinpath(*rel.parts)


def row_passes_policy(row: dict) -> bool:
    if row.get("domain_group") == "personal":
        return False
    if row.get("review_status") != "approved":
        return False
    if row.get("ingestion_scope") not in ALLOWED_SCOPES:
        return False
    if row.get("sensitivity") == "private":
        return False
    return True


def fetch_file_via_ssh(ssh_host: str, remote_path: str, local_path: Path) -> tuple[bool, str]:
    """
    Return (ok, stderr_or_empty).

    One remote shell command with POSIX-safe quoting so paths with spaces and
    metacharacters are not split (ssh with separate argv is not portable across sshd configs).
    """
    local_path.parent.mkdir(parents=True, exist_ok=True)
    remote_cmd = f"cat -- {shlex.quote(remote_path)}"
    proc = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", ssh_host, remote_cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    err = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
    if proc.returncode != 0:
        return False, err or f"ssh_cat_exit_{proc.returncode}"
    local_path.write_bytes(proc.stdout)
    return True, ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage NAS allowlist files locally")
    parser.add_argument(
        "--allowlist",
        default="/home/jonat/ai-stack/reports/inventory/nas_ingest_allowlist.csv",
    )
    parser.add_argument(
        "--intake-root",
        default="/home/jonat/ai-stack/docs/data",
    )
    parser.add_argument("--ssh-host", default="nas")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Replace existing destination files (default: skip existing)",
    )
    parser.add_argument(
        "--manifest",
        default="",
        help="Write run manifest JSON here (default: reports/index_runs/nas_stage_manifest_<UTC>.json)",
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=[".md", ".txt", ".json", ".yaml", ".yml", ".csv"],
        help="Only stage these extensions for initial ingestion safety",
    )
    args = parser.parse_args()

    allow = Path(args.allowlist)
    if not allow.exists():
        raise FileNotFoundError(allow)
    intake_root = Path(args.intake_root).resolve()
    allowed_exts = {e.lower() for e in args.extensions}

    now = datetime.now(UTC)
    manifest_path = (
        Path(args.manifest)
        if args.manifest
        else Path("reports/index_runs")
        / f"nas_stage_manifest_{now.strftime('%Y%m%d_%H%M%S')}.json"
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(allow.open("r", encoding="utf-8")))
    counters: Counter[str] = Counter()
    file_records: list[dict[str, str]] = []

    hit_limit = False

    for row in rows:
        src = row.get("path", "").strip()
        scope = (row.get("ingestion_scope") or "").strip()

        if not row_passes_policy(row):
            counters["skipped_policy"] += 1
            file_records.append(
                {
                    "source": src,
                    "action": "skipped_policy",
                    "ingestion_scope": scope,
                }
            )
            continue

        ext = Path(src).suffix.lower()
        if ext not in allowed_exts:
            counters["skipped_extension"] += 1
            file_records.append(
                {
                    "source": src,
                    "action": "skipped_extension",
                    "ingestion_scope": scope,
                    "extension": ext,
                }
            )
            continue

        if counters["staged"] >= args.limit:
            hit_limit = True
            counters["skipped_limit"] += 1
            file_records.append(
                {
                    "source": src,
                    "action": "skipped_limit",
                    "ingestion_scope": scope,
                }
            )
            continue

        dst = local_target(scope, src, intake_root)
        rel_under_intake = dst.resolve().relative_to(intake_root)

        if dst.exists() and not args.overwrite:
            counters["skipped_destination_exists"] += 1
            file_records.append(
                {
                    "source": src,
                    "action": "skipped_destination_exists",
                    "local_path": str(rel_under_intake),
                    "ingestion_scope": scope,
                }
            )
            continue

        ok, err = fetch_file_via_ssh(args.ssh_host, src, dst)
        if ok:
            counters["staged"] += 1
            file_records.append(
                {
                    "source": src,
                    "action": "staged",
                    "local_path": str(rel_under_intake),
                    "ingestion_scope": scope,
                }
            )
        else:
            counters["fetch_failed"] += 1
            file_records.append(
                {
                    "source": src,
                    "action": "fetch_failed",
                    "local_path": str(rel_under_intake),
                    "ingestion_scope": scope,
                    "detail": err[:500] if err else "",
                }
            )

    manifest = {
        "timestamp_utc": now.isoformat(),
        "allowlist_path": str(allow),
        "intake_root": str(intake_root),
        "ssh_host": args.ssh_host,
        "overwrite": args.overwrite,
        "extension_allowlist": sorted(allowed_exts),
        "staging_limit": args.limit,
        "hit_limit": hit_limit,
        "policy_enforced_at_staging": {
            "domain_group_not_personal": True,
            "review_status_eq_approved": True,
            "ingestion_scope_in": sorted(ALLOWED_SCOPES),
            "sensitivity_not_private": True,
        },
        "counters": {
            "rows_in_allowlist_csv": len(rows),
            "staged": counters.get("staged", 0),
            "fetch_failed": counters.get("fetch_failed", 0),
            "skipped_extension": counters.get("skipped_extension", 0),
            "skipped_policy": counters.get("skipped_policy", 0),
            "skipped_destination_exists": counters.get("skipped_destination_exists", 0),
            "skipped_limit": counters.get("skipped_limit", 0),
        },
        "files": file_records,
    }

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Staged: {counters['staged']}")
    print(f"Failed: {counters['fetch_failed']}")
    print(f"Skipped_extension: {counters['skipped_extension']}")
    print(f"Skipped_policy: {counters['skipped_policy']}")
    print(f"Skipped_destination_exists: {counters['skipped_destination_exists']}")
    print(f"Skipped_limit: {counters['skipped_limit']}")
    print(f"Intake root: {intake_root}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
