#!/usr/bin/env python3
"""Dependency-free validator for QSOL LATTICE."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lattice.core import (
    MAX_RECURSIVE_DEPTH,
    PHI_STRIDE,
    PROFILE_ID,
    LatticeError,
    describe_address,
    lexicographic_cells,
    parse_address,
    phi_stride_cells,
)

PYTHON_MM = re.compile(r"^[0-9]+\.[0-9]+$")
SHA_REF = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def require_file(relative: str) -> None:
    if not (ROOT / relative).is_file():
        raise ValueError(f"missing required file: {relative}")


def validate_reference(value: dict[str, Any]) -> None:
    required = {"protocol", "profile_id", "address", "authority"}
    missing = required - set(value)
    if missing:
        raise ValueError(f"reference missing fields: {sorted(missing)}")
    if value["protocol"] != "qsol-lattice-reference/1":
        raise ValueError("reference protocol mismatch")
    if value["profile_id"] != PROFILE_ID:
        raise ValueError("unsupported lattice profile")
    try:
        parse_address(value["address"])
    except LatticeError as exc:
        raise ValueError(str(exc)) from exc
    if value["authority"] != "storage-only":
        raise ValueError("lattice references cannot claim epistemic authority")
    content_ref = value.get("content_ref")
    if content_ref is not None and (not isinstance(content_ref, str) or SHA_REF.fullmatch(content_ref) is None):
        raise ValueError("content_ref must be null or sha256 reference")


def validate() -> dict[str, Any]:
    manifest = load_json(ROOT / "manifest.json")
    if manifest.get("protocol") != "QSOL-LATTICE/0.1":
        raise ValueError("manifest protocol mismatch")
    if manifest.get("verb") != "REMEMBERS" or manifest.get("authority") != "storage-only":
        raise ValueError("LATTICE role/authority mismatch")
    if manifest.get("profile") != PROFILE_ID:
        raise ValueError("manifest profile mismatch")
    if manifest.get("top_level_cells") != 27 or manifest.get("literal_geometric_claim") is not False:
        raise ValueError("manifest geometry contract mismatch")
    if manifest.get("max_recursive_depth") != MAX_RECURSIVE_DEPTH:
        raise ValueError("recursive depth contract mismatch")

    minimum = manifest["validation"]["python_minimum"]
    if not isinstance(minimum, str) or PYTHON_MM.fullmatch(minimum) is None:
        raise ValueError("python_minimum must use MAJOR.MINOR")
    required_version = tuple(int(part) for part in minimum.split("."))
    if sys.version_info[:2] < required_version:
        raise ValueError(f"requires Python >= {minimum}")

    for path in (
        manifest["license"], manifest["machine_entrypoint"], manifest["architecture"],
        manifest["roadmap"], manifest["security"], manifest["profile_contract"],
        manifest["reference_runtime"], "README.md", "AGENTS.md",
        ".github/workflows/validate.yml",
    ):
        require_file(path)

    profile = load_json(ROOT / manifest["profile_contract"])
    if profile.get("profile_id") != PROFILE_ID or profile.get("top_level_cell_count") != 27:
        raise ValueError("profile contract mismatch")
    if profile.get("literal_geometric_claim") is not False:
        raise ValueError("profile must remain logical, not literal")
    axes = profile.get("axes", {})
    if set(axes) != {"x", "y", "z"}:
        raise ValueError("profile must define x/y/z axes")
    for axis in axes.values():
        if set(axis.get("values", {})) != {"0", "1", "2"}:
            raise ValueError("each axis must define ternary values 0/1/2")
    phi = profile["traversals"]["qsol.phi-stride-27/1"]
    if phi.get("stride") != PHI_STRIDE or phi.get("modulus") != 27:
        raise ValueError("phi traversal parameter drift")

    cells = lexicographic_cells()
    phi_cells = phi_stride_cells()
    if len(cells) != 27 or len(set(cells)) != 27:
        raise ValueError("lexicographic traversal is not a 27-cell bijection")
    if len(phi_cells) != 27 or set(phi_cells) != set(cells):
        raise ValueError("phi traversal is not a 27-cell bijection")

    schema_path = manifest["schemas"]["address_reference"]
    require_file(schema_path)
    schema = load_json(ROOT / schema_path)
    if schema.get("$schema") != manifest["json_schema"]["draft"] or not schema.get("$id"):
        raise ValueError("address schema declaration mismatch")

    valid_path = manifest["schema_examples"]["valid"]
    invalid_path = manifest["schema_examples"]["invalid"]
    require_file(valid_path)
    require_file(invalid_path)
    validate_reference(load_json(ROOT / valid_path))
    try:
        validate_reference(load_json(ROOT / invalid_path))
    except ValueError:
        pass
    else:
        raise ValueError("invalid lattice fixture unexpectedly passed")

    machine = load_json(ROOT / "README4AI.md")
    if machine.get("profile") != PROFILE_ID or machine.get("literal_geometric_claim") is not False:
        raise ValueError("machine profile contract mismatch")

    sample = describe_address("L[2,0,1]/L[1,1,0]")
    if sample["authority"] != "storage-only" or sample["depth"] != 2:
        raise ValueError("reference runtime description mismatch")

    return {
        "protocol": manifest["protocol"],
        "status": "valid",
        "profile": PROFILE_ID,
        "top_level_cells": len(cells),
        "phi_stride": PHI_STRIDE,
        "max_recursive_depth": MAX_RECURSIVE_DEPTH,
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
