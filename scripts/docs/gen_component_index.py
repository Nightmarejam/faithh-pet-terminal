#!/usr/bin/env python3
"""Generate a component index for FAITHH from the source itself.

    python scripts/docs/gen_component_index.py > docs/architecture/COMPONENT_INDEX.md

Why generated rather than written: this repo accumulated four overlapping,
partially-stale architecture maps (BACKEND_STRUCTURE_OVERVIEW, dependency_map,
CAPABILITY_MAP, ACTIVE_VS_LEGACY_SCRIPT_MAP), each covering a slice and none
current. A hand-maintained index of ~70 modules drifts the moment anyone adds a
file. Regenerate this after structural changes and it is true by construction.

For each module it reports:
  * the first line of its docstring (what it does)
  * who imports it (reverse dependencies, resolved across the repo)
  * whether it is reachable from the canonical backend entrypoint

That last column is the useful one: it separates wired-in code from orphans.
"""
from __future__ import annotations

import ast
import pathlib
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
ENTRY = "faithh_professional_backend_fixed.py"
SCAN_DIRS = ["backend", "app/services", "app/providers", "app/analytics", "services", "modules"]
SKIP_PARTS = {".git", "node_modules", "venv", ".venv", "archive", "__pycache__", "experiments"}


def modules(include_inits: bool = False) -> list[pathlib.Path]:
    """Modules to index. `include_inits` is used when building the import graph:
    package __init__.py files re-export submodules, so skipping them made
    anything imported *through* a package look orphaned (this misclassified
    app/services/alife_parasitic_integration_final.py as dead when the real
    __init__.py imports it)."""
    out = []
    for d in SCAN_DIRS:
        p = ROOT / d
        if not p.exists():
            continue
        for f in sorted(p.rglob("*.py")):
            if any(s in f.parts for s in SKIP_PARTS):
                continue
            if f.name == "__init__.py" and not include_inits:
                continue
            out.append(f)
    for f in sorted(ROOT.glob("*.py")):
        if f.name != ENTRY:
            out.append(f)
    return out


def summary(path: pathlib.Path) -> str:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return "**(does not parse — see the Python 3.10 notes in AGENTS.md)**"
    doc = ast.get_docstring(tree)
    if not doc:
        return "_(no docstring)_"
    line = doc.strip().splitlines()[0].strip()
    # Strip the repetitive "FAITHH " prefix most modules carry
    for pre in ("FAITHH ", "FAITHH-"):
        if line.startswith(pre):
            line = line[len(pre):]
    return line[:110]


def imports_of(path: pathlib.Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return set()
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                names.add(a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom) and n.module:
            names.add(n.module)
            names.add(n.module.split(".")[-1])
    return names


def key(path: pathlib.Path) -> str:
    return path.stem


def main() -> int:
    # Write the file directly rather than relying on shell redirection: on Windows
    # the console codepage mangles em-dashes into mojibake on the way out.
    out_path = None
    argv = sys.argv[1:]
    if argv and argv[0] not in ("-", "--stdout"):
        out_path = pathlib.Path(argv[0])
    buf: list[str] = []
    global print  # noqa: PLW0603
    _real_print = print

    def print(*a, **k):  # noqa: A001
        buf.append(" ".join(str(x) for x in a))

    rc = _build()
    text = "\n".join(buf) + "\n"
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8", newline="\n")
        _real_print(f"wrote {out_path} ({len(buf)} lines)")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        _real_print(text, end="")
    return rc


def _build() -> int:
    mods = modules()
    entry = ROOT / ENTRY

    # reverse dependency map: module stem -> set of files importing it
    users: dict[str, set[str]] = defaultdict(set)
    # Scan __init__.py too — they re-export, and their imports are real edges.
    all_files = modules(include_inits=True) + ([entry] if entry.exists() else [])
    stems = {key(m) for m in mods}
    for f in all_files:
        rel = f.relative_to(ROOT).as_posix()
        for imported in imports_of(f):
            if imported in stems:
                users[imported].add(rel)

    entry_imports = imports_of(entry) if entry.exists() else set()

    print("# FAITHH Component Index")
    print()
    print("**Generated** by `scripts/docs/gen_component_index.py` — do not hand-edit.")
    print("Regenerate after adding or removing modules; it reads the source, so it")
    print("cannot drift the way a written map does.")
    print()
    print(f"Canonical entrypoint: `{ENTRY}`")
    print()
    print("`reachable` = imported by the entrypoint directly, or by something it imports.")
    print("Modules with no importer are candidates for archiving.")
    print()

    # transitive reachability from the entrypoint
    reachable, frontier = set(), set(entry_imports)
    by_stem = {key(m): m for m in mods}
    while frontier:
        nxt = set()
        for s in frontier:
            if s in reachable or s not in by_stem:
                continue
            reachable.add(s)
            nxt |= imports_of(by_stem[s]) & set(by_stem)
        frontier = nxt - reachable

    groups: dict[str, list[pathlib.Path]] = defaultdict(list)
    for m in mods:
        rel = m.relative_to(ROOT).as_posix()
        groups[rel.rsplit("/", 1)[0] if "/" in rel else "(root)"].append(m)

    orphans = []
    for grp in sorted(groups):
        print(f"## `{grp}/`" if grp != "(root)" else "## repo root")
        print()
        print("| module | what it does | used by | reachable |")
        print("|---|---|---|---|")
        for m in sorted(groups[grp]):
            st = key(m)
            u = sorted(users.get(st, set()))
            if not u:
                orphans.append(m.relative_to(ROOT).as_posix())
            shown = ", ".join(f"`{x.split('/')[-1]}`" for x in u[:3]) or "—"
            if len(u) > 3:
                shown += f" +{len(u)-3}"
            mark = "yes" if st in reachable else "—"
            print(f"| `{m.name}` | {summary(m)} | {shown} | {mark} |")
        print()

    if orphans:
        print("## Nothing imports these")
        print()
        print("Not necessarily dead — some are standalone scripts or entrypoints — but")
        print("each should either be documented as such or moved to `archive/`.")
        print()
        for o in sorted(orphans):
            print(f"- `{o}`")
        print()

    html = sorted(p for p in ROOT.glob("*.html"))
    if html:
        print("## Frontend")
        print()
        print("| file | size | served from |")
        print("|---|---|---|")
        served = entry.read_text(encoding="utf-8", errors="replace") if entry.exists() else ""
        for h in html:
            hint = "referenced by the backend" if h.name in served else "not referenced in the entrypoint"
            print(f"| `{h.name}` | {h.stat().st_size // 1024} KB | {hint} |")
        print()

    print(f"_{len(mods)} modules indexed, {len(reachable)} reachable from the entrypoint, {len(orphans)} unreferenced._")
    return 0


if __name__ == "__main__":
    sys.exit(main())
