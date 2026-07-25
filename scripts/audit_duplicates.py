#!/usr/bin/env python3
"""Find exact and near-duplicates after whitespace normalization."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

TEXT_EXTS = {
    "py", "md", "txt", "rst", "yml", "yaml", "json", "toml", "ini", "cfg", "conf",
    "env", "html", "htm", "css", "js", "sh", "bash", "zsh", "fish", "bat", "ps1",
}

MAX_TEXT_BYTES = 500_000

INCLUDE_PREFIXES = {
    "backend/",
    "scripts/",
    "frontend/",
    "active/",
    "legacy/",
    "docs/",
    "tests/",
    "knowledge_base/",
    "parity/",
}


def is_text_file(path: Path, ext: str) -> bool:
    if ext in TEXT_EXTS:
        return True
    try:
        with path.open("rb") as f:
            sample = f.read(4096)
        sample.decode("utf-8")
        return True
    except Exception:
        return False


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def simhash64(tokens) -> int:
    vec = [0] * 64
    for token in tokens:
        h = hashlib.sha1(token.encode("utf-8")).digest()
        v = int.from_bytes(h[:8], "big")
        for i in range(64):
            bit = (v >> i) & 1
            vec[i] += 1 if bit else -1
    out = 0
    for i, score in enumerate(vec):
        if score >= 0:
            out |= 1 << i
    return out


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def canonical_candidate(paths):
    def score(path: str) -> tuple:
        lowered = path.lower()
        penalties = [
            "/archive/", "/docs/archive/", "/legacy/", "/backup", "/backups/", "/old/",
            "/snapshots/", "/parity/", "/generated/", "/reports/",
        ]
        penalty = sum(1 for p in penalties if p in lowered)
        depth = lowered.count("/")
        return (penalty, depth, len(lowered), lowered)
    return sorted(paths, key=score)[0]


def load_inventory(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def band_keys(sig: int):
    return [
        (sig >> 48) & 0xFFFF,
        (sig >> 32) & 0xFFFF,
        (sig >> 16) & 0xFFFF,
        sig & 0xFFFF,
    ]


def should_scan_near(path: str) -> bool:
    if "/" not in path:
        return True
    return any(path.startswith(prefix) for prefix in INCLUDE_PREFIXES)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    inventory = load_inventory(Path(args.inventory))

    sha_groups = {}
    for rec in inventory:
        sha_groups.setdefault(rec["sha256"], []).append(rec["path"])

    exact_dupes = []
    for sha, paths in sha_groups.items():
        if len(paths) > 1:
            exact_dupes.append({
                "sha256": sha,
                "paths": sorted(paths),
                "canonical": canonical_candidate(paths),
            })

    # Near-duplicates (subset for performance)
    candidates = []
    for rec in inventory:
        if not should_scan_near(rec["path"]):
            continue
        path = root / rec["path"]
        if not path.is_file():
            continue
        if rec["size"] > MAX_TEXT_BYTES:
            continue
        ext = rec["extension"]
        if not is_text_file(path, ext):
            continue
        candidates.append((rec["path"], ext, rec["size"]))

    signatures = {}
    lengths = {}

    for rel_path, ext, _size in candidates:
        path = root / rel_path
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        norm = normalize_text(text)
        if not norm:
            continue
        lengths[rel_path] = len(norm)
        tokens = norm.split()
        signatures[rel_path] = simhash64(tokens[:2000])

    buckets = {}
    for rel_path, ext, _size in candidates:
        if rel_path not in signatures:
            continue
        sig = signatures[rel_path]
        for band in band_keys(sig):
            buckets.setdefault((ext, band), []).append(rel_path)

    near_dupes = []
    seen_pairs = set()
    normalized_cache = {}

    for (ext, band), paths in buckets.items():
        if len(paths) < 2:
            continue
        paths = sorted(set(paths))
        for i, a in enumerate(paths):
            for b in paths[i + 1:]:
                pair_key = (a, b)
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)
                la = lengths.get(a)
                lb = lengths.get(b)
                if not la or not lb:
                    continue
                if min(la, lb) / max(la, lb) < 0.98:
                    continue
                if hamming(signatures[a], signatures[b]) > 3:
                    continue
                if a not in normalized_cache:
                    try:
                        normalized_cache[a] = normalize_text((root / a).read_text(encoding="utf-8"))
                    except UnicodeDecodeError:
                        continue
                if b not in normalized_cache:
                    try:
                        normalized_cache[b] = normalize_text((root / b).read_text(encoding="utf-8"))
                    except UnicodeDecodeError:
                        continue
                ratio = difflib.SequenceMatcher(None, normalized_cache[a], normalized_cache[b]).ratio()
                if ratio >= 0.92:
                    near_dupes.append({
                        "similarity": round(ratio, 4),
                        "paths": [a, b],
                        "canonical": canonical_candidate([a, b]),
                    })

    data = {
        "parameters": {
            "max_text_bytes": MAX_TEXT_BYTES,
            "similarity_threshold": 0.92,
            "simhash_hamming_max": 3,
            "length_ratio_min": 0.98,
            "near_duplicate_include_prefixes": sorted(INCLUDE_PREFIXES),
        },
        "exact_duplicates": sorted(exact_dupes, key=lambda d: d["canonical"]),
        "near_duplicates": sorted(near_dupes, key=lambda d: (-d["similarity"], d["canonical"])),
    }

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=False)
        f.write("\n")

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    with output_md.open("w", encoding="utf-8") as f:
        f.write("# Duplicates Report\n\n")
        f.write("## Exact duplicates (byte-identical)\n")
        if not data["exact_duplicates"]:
            f.write("\n- None found\n")
        else:
            f.write("\n")
            for group in data["exact_duplicates"]:
                f.write(f"- Canonical: `{group['canonical']}`\n")
                for path in group["paths"]:
                    f.write(f"  - `{path}`\n")
        f.write("\n## Near duplicates (normalized whitespace, similarity >= 0.92)\n")
        f.write("\nDetection limits: text files <= 500KB, UTF-8 decodable, prefixes limited to core dirs.\n")
        if not data["near_duplicates"]:
            f.write("\n- None found\n")
        else:
            f.write("\n")
            for group in data["near_duplicates"]:
                f.write(f"- Similarity: {group['similarity']} | Canonical: `{group['canonical']}`\n")
                for path in group["paths"]:
                    f.write(f"  - `{path}`\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
