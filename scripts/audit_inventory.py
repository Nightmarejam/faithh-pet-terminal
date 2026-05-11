#!/usr/bin/env python3
"""Generate repo inventory with hashes and inferred types."""
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

BINARY_EXTS = {
    "png", "jpg", "jpeg", "gif", "ico", "svg", "pdf", "docx", "pptx", "xlsx",
    "zip", "gz", "bz2", "xz", "tar", "7z", "db", "sqlite", "sqlite3", "odt",
    "ods", "odp", "mp3", "mp4", "mov", "avi", "wav",
}

DOC_EXTS = {
    "md", "txt", "rst", "docx", "pdf", "pptx", "doc", "rtf", "odt", "ods", "odp",
}

CONFIG_EXTS = {
    "yml", "yaml", "json", "toml", "ini", "cfg", "conf", "env", "config",
    "modelfile",
}

UI_EXTS = {
    "html", "htm", "css", "js", "svg", "ico", "png", "jpg", "jpeg", "gif",
}

SCRIPT_EXTS = {
    "sh", "bash", "zsh", "fish", "bat", "ps1",
}

PYTHON_EXTS = {"py"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def infer_type(ext: str, path: Path) -> str:
    ext = ext.lower()
    if ext in PYTHON_EXTS:
        return "python"
    if ext in DOC_EXTS:
        return "doc"
    if ext in CONFIG_EXTS:
        return "config"
    if ext in UI_EXTS:
        return "ui"
    if ext in SCRIPT_EXTS:
        return "script"
    # Heuristic for executable scripts without extension
    if not ext:
        try:
            with path.open("rb") as f:
                head = f.read(128)
            if head.startswith(b"#!/"):
                return "script"
        except OSError:
            pass
    return "other"


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip .git
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            yield Path(dirpath) / name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output).resolve()

    records = []
    for path in sorted(iter_files(root)):
        if output == path:
            # Avoid hashing the output while generating it.
            continue
        rel = path.relative_to(root).as_posix()
        stat = path.stat()
        ext = path.suffix[1:].lower() if path.suffix else ""
        record = {
            "path": rel,
            "size": stat.st_size,
            "sha256": sha256_file(path),
            "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "extension": ext,
            "inferred_type": infer_type(ext, path),
        }
        records.append(record)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, sort_keys=False)
        f.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
