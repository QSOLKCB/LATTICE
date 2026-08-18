#!/usr/bin/env python3
"""Deterministic stdlib-only quality gate for the small LATTICE Python surface."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOTS = ("lattice", "tools", "tests")
PARSER_FILES = {Path("lattice/core.py"), Path("tools/validate_lattice.py")}
FORBIDDEN_CALLS = {"eval", "exec"}


def python_files() -> list[Path]:
    """Return Python files in deterministic repository-relative order."""
    files: list[Path] = []
    for directory in PYTHON_ROOTS:
        files.extend((ROOT / directory).rglob("*.py"))
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def call_name(node: ast.Call) -> str | None:
    """Resolve the small set of call names relevant to parser safety."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        if isinstance(node.func.value, ast.Name):
            return f"{node.func.value.id}.{node.func.attr}"
    return None


def validate() -> dict[str, object]:
    """Check syntax, whitespace hygiene, and unsafe parser primitives."""
    checked = 0
    for path in python_files():
        relative = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), 1):
            if "\t" in line:
                raise ValueError(f"{relative}:{number}: tab character forbidden")
            if line.rstrip() != line:
                raise ValueError(f"{relative}:{number}: trailing whitespace")
        try:
            tree = ast.parse(text, filename=str(relative))
        except SyntaxError as exc:
            raise ValueError(f"{relative}: syntax error: {exc}") from exc

        if relative in PARSER_FILES:
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = call_name(node)
                if name in FORBIDDEN_CALLS or name == "ast.literal_eval":
                    raise ValueError(f"{relative}:{node.lineno}: unsafe parser primitive {name}")
        checked += 1

    return {
        "status": "valid",
        "python_files": checked,
        "runtime_dependencies": "stdlib-only",
        "unsafe_parser_primitives": "rejected",
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
