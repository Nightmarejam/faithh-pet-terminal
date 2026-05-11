#!/usr/bin/env python3
"""
Resolve the on-disk GGUF blob path for an Ollama model (same weights llama-server uses).

Ollama stores manifests as files with *four* path segments under models/manifests/
(host/namespace/model/tag), matching server/manifest.go Glob("*/*/*/*").

Roots: $OLLAMA_MODELS, ~/.ollama, /usr/share/ollama/.ollama, WSL /mnt/c/Users/*/.ollama,
and /mnt/c/Users/*/AppData/Local/Ollama.

If the model is not on disk, we query GET /api/tags (OLLAMA_HOST, default http://127.0.0.1:11434)
and print which names the server actually has — often the requested tag/name is missing.

Usage:
  python3 scripts/resolve_ollama_gguf.py [model_ref]
  model_ref default: qwen25-grounded-gen5-delta:latest (FAITHH / KV bench; override if absent)
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


MODEL_MEDIA = "application/vnd.ollama.image.model"


def _add_root(out: list[Path], seen: set[str], raw: str | None) -> None:
    if not raw or raw in seen:
        return
    seen.add(raw)
    p = Path(raw).expanduser()
    try:
        p = p.resolve()
    except OSError:
        return
    if p.is_dir():
        out.append(p)


def roots() -> list[Path]:
    out: list[Path] = []
    seen: set[str] = set()
    _add_root(out, seen, os.environ.get("OLLAMA_MODELS"))
    _add_root(out, seen, str(Path.home() / ".ollama"))
    _add_root(out, seen, "/usr/share/ollama/.ollama")

    mnt = Path("/mnt/c/Users")
    if mnt.is_dir():
        skip = {"Public", "All Users", "Default", "Default User"}
        try:
            for user in mnt.iterdir():
                if not user.is_dir() or user.name in skip:
                    continue
                _add_root(out, seen, str(user / ".ollama"))
                _add_root(out, seen, str(user / "AppData" / "Local" / "Ollama"))
                _add_root(out, seen, str(user / "AppData" / "Roaming" / "Ollama"))
        except (OSError, PermissionError):
            pass

    return out


def ollama_root_from_manifest(manifest: Path) -> Path | None:
    m = manifest.resolve()
    for anc in m.parents:
        if (anc / "models" / "blobs").is_dir() and (anc / "models" / "manifests").is_dir():
            return anc
    return None


def normalize_from_field(path_str: str) -> Path:
    """Turn Windows paths and 'from' manifest entries into a WSL-friendly Path."""
    s = path_str.strip().replace("\\", "/")
    if len(s) > 2 and s[1] == ":" and s[0].isalpha():
        drive = s[0].lower()
        rest = Path(s[2:].strip("/"))
        return Path(f"/mnt/{drive}") / rest
    return Path(s)


def digest_to_blob(root: Path, digest: str) -> Path:
    if ":" in digest:
        _, _, hexpart = digest.partition(":")
    else:
        hexpart = digest
    return root / "models" / "blobs" / f"sha256-{hexpart}"


def blob_from_manifest(manifest: Path) -> Path | None:
    root = ollama_root_from_manifest(manifest)
    if root is None:
        return None
    try:
        raw = manifest.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return None
    layers = data.get("layers") or []
    for layer in layers:
        if layer.get("mediaType") != MODEL_MEDIA:
            continue
        frm = layer.get("from")
        if frm:
            for candidate in (Path(frm), normalize_from_field(frm)):
                try:
                    if candidate.is_file() and candidate.stat().st_size > 0:
                        return candidate.resolve()
                except OSError:
                    continue
        d = layer.get("digest")
        if not d:
            continue
        blob = digest_to_blob(root, d)
        try:
            if blob.is_file() and blob.stat().st_size > 0:
                return blob.resolve()
        except OSError:
            continue
    return None


def iter_four_part_manifests(manifests_dir: Path) -> list[Path]:
    """Same shape as Ollama's filepath.Glob(manifests, \"*\", \"*\", \"*\", \"*\"): files only, depth 4."""
    found: list[Path] = []
    if not manifests_dir.is_dir():
        return found
    try:
        for p in manifests_dir.rglob("*"):
            try:
                if not p.is_file():
                    continue
                rel = p.relative_to(manifests_dir)
            except ValueError:
                continue
            if len(rel.parts) == 4:
                found.append(p)
    except OSError:
        pass
    return found


def manifest_matches(manifest: Path, manifests_dir: Path, name: str, tag: str) -> bool:
    try:
        rel = manifest.relative_to(manifests_dir)
    except ValueError:
        return False
    if len(rel.parts) != 4:
        return False
    _host, _ns, mname, mtag = rel.parts
    return mname.casefold() == name.casefold() and mtag.casefold() == tag.casefold()


def manifest_path(root: Path, name: str, tag: str) -> Path:
    return (
        root
        / "models"
        / "manifests"
        / "registry.ollama.ai"
        / "library"
        / name
        / tag
    )


def iter_candidate_manifests(root: Path, name: str, tag: str) -> list[Path]:
    """Ordered: exact registry file, glob, then full Ollama-style four-part scan (casefold)."""
    found: list[Path] = []
    seen: set[str] = set()

    def add(p: Path) -> None:
        k = str(p.resolve())
        if k not in seen and p.is_file():
            seen.add(k)
            found.append(p)

    exact = manifest_path(root, name, tag)
    add(exact)

    mdir = root / "models" / "manifests"
    if not mdir.is_dir():
        return found

    try:
        for p in sorted(mdir.glob(f"**/library/{name}/{tag}")):
            add(p)
    except OSError:
        pass

    # Case / host / layout drift (e.g. NTFS paths): scan all four-part manifests.
    for p in iter_four_part_manifests(mdir):
        if manifest_matches(p, mdir, name, tag):
            add(p)

    # Tag fallback: no path match yet; library dir may omit a file literally named "latest".
    lib = mdir / "registry.ollama.ai" / "library" / name
    if lib.is_dir():
        try:
            if tag == "latest":
                alt = lib / "latest"
                if alt.is_file():
                    add(alt)
                else:
                    files = sorted(
                        [c for c in lib.iterdir() if c.is_file()],
                        key=lambda x: x.stat().st_mtime,
                        reverse=True,
                    )
                    if files:
                        add(files[0])
            else:
                spec = lib / tag
                if spec.is_file():
                    add(spec)
        except OSError:
            pass

    return found


def resolve(model_ref: str) -> Path | None:
    name, _, tag = model_ref.partition(":")
    if not tag:
        tag = "latest"

    for root in roots():
        for man in iter_candidate_manifests(root, name, tag):
            got = blob_from_manifest(man)
            if got is not None:
                return got
    return None


def api_list_model_names(timeout: float = 5.0) -> list[str]:
    base = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").strip().rstrip("/")
    if not base.startswith("http"):
        base = "http://" + base
    url = f"{base}/api/tags"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, OSError):
        return []
    names: list[str] = []
    for m in data.get("models") or []:
        n = m.get("name") or m.get("model")
        if n:
            names.append(n)
    return names


def main() -> int:
    ref = sys.argv[1] if len(sys.argv) > 1 else "qwen25-grounded-gen5-delta:latest"
    p = resolve(ref)
    if p is not None:
        print(p)
        return 0

    rlist = roots()
    api_names = api_list_model_names()
    stem = ref.partition(":")[0]

    print("Could not resolve GGUF for %r." % (ref,), file=sys.stderr)
    print("  Searched roots: %s" % (", ".join(str(r) for r in rlist) or "(none)",), file=sys.stderr)

    if api_names:
        print("  Models reported by %s/api/tags: %s" % (
            os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").strip().rstrip("/") or "http://127.0.0.1:11434",
            ", ".join(api_names),
        ), file=sys.stderr)
        if ref not in api_names and not any(n.split(":")[0].casefold() == stem.casefold() for n in api_names):
            print(
                "  That name is not installed on this daemon (wrong OLLAMA_HOST, or model was removed).",
                file=sys.stderr,
            )
            print(
                "  If you ran `ollama delete` earlier, manifests/blobs may be gone — `ollama pull %s` restores it."
                % (stem,),
                file=sys.stderr,
            )
            print("  Or benchmark a model you have: e.g. OLLAMA_MODEL_REF=deepseek-r1:32b (heavy) or pull a 14B.", file=sys.stderr)
            print("  Or pass a file: GGUF_PATH=/path/to/model.gguf bash scripts/run_llama_kv_cache_benchmark.sh", file=sys.stderr)
    else:
        print(
            "  Could not reach Ollama HTTP API (set OLLAMA_HOST if the daemon is elsewhere).",
            file=sys.stderr,
        )

    print(
        "  Disk hints: ensure models/manifests and models/blobs exist under a root; on Windows",
        file=sys.stderr,
    )
    print(
        "  set OLLAMA_MODELS to that folder's parent (.ollama), then re-run.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
