#!/usr/bin/env python3
"""Trace local Python imports from entrypoints using AST."""
import argparse
import ast
import json
from pathlib import Path


def resolve_module(root: Path, base_file: Path, module: str, level: int):
    base_dir = base_file.parent
    if level > 0:
        for _ in range(level):
            base_dir = base_dir.parent
        if module:
            mod_path = Path(*module.split("."))
            candidate = base_dir / mod_path
        else:
            candidate = base_dir
    else:
        candidate = root / Path(*module.split("."))

    if candidate.with_suffix(".py").exists():
        return candidate.with_suffix(".py")
    if candidate.is_dir() and (candidate / "__init__.py").exists():
        return candidate / "__init__.py"
    return None


def parse_imports(path: Path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, 0))
        elif isinstance(node, ast.ImportFrom):
            imports.append((node.module or "", node.level))
    return imports


def build_graph(root: Path, entrypoints):
    graph = {}
    queue = [Path(p).resolve() for p in entrypoints]
    seen = set()
    while queue:
        current = queue.pop(0)
        if current in seen or not current.exists():
            continue
        seen.add(current)
        rel = current.relative_to(root).as_posix()
        graph[rel] = []
        for module, level in parse_imports(current):
            resolved = resolve_module(root, current, module, level)
            if resolved and resolved.exists():
                rel_resolved = resolved.relative_to(root).as_posix()
                graph[rel].append(rel_resolved)
                if resolved not in seen:
                    queue.append(resolved)
    return graph


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--entrypoint", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    graph = build_graph(root, args.entrypoint)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, sort_keys=False)
        f.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
