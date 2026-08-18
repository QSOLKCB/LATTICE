#!/usr/bin/env python3
"""Dependency-free validator for QSOL LATTICE."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lattice.core import (
    ADDRESS_PATTERN,
    MAX_ADDRESS_LENGTH,
    MAX_RECURSIVE_DEPTH,
    PHI_STRIDE,
    PROFILE_ID,
    LatticeError,
    LatticeValidationError,
    describe_address,
    lexicographic_cells,
    parse_address,
    phi_stride_cells,
)

PYTHON_MM = re.compile(r"^[0-9]+\.[0-9]+$")
SHA_REF = re.compile(r"^sha256:[0-9a-f]{64}$")
REFERENCE_PROTOCOL = "qsol-lattice-reference/1"
REFERENCE_REQUIRED_KEYS = {"protocol", "profile_id", "address", "authority"}
REFERENCE_OPTIONAL_KEYS = {"content_ref", "note"}
REFERENCE_ALLOWED_KEYS = REFERENCE_REQUIRED_KEYS | REFERENCE_OPTIONAL_KEYS


def fail(message: str) -> LatticeValidationError:
    """Create one deterministic validator error type."""
    return LatticeValidationError(message)


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object and normalize parse/type failures."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise fail(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise fail(f"{path}: must contain an object")
    return value


def require_file(relative: Any, field: str) -> Path:
    """Resolve a required repository file path without raw dict exceptions."""
    if not isinstance(relative, str) or not relative:
        raise fail(f"{field} missing or invalid")
    path = ROOT / relative
    if not path.is_file():
        raise fail(f"missing required file: {relative}")
    return path


def require_mapping(value: Any, field: str) -> dict[str, Any]:
    """Require a JSON object with a deterministic error."""
    if not isinstance(value, dict):
        raise fail(f"{field} missing or invalid")
    return value


def validate_reference(value: dict[str, Any]) -> None:
    """Validate a payload-free, authority-free LATTICE reference."""
    if not isinstance(value, dict):
        raise fail("reference must be an object")

    missing = REFERENCE_REQUIRED_KEYS - set(value)
    if missing:
        raise fail(f"reference missing fields: {sorted(missing)}")

    unexpected = set(value) - REFERENCE_ALLOWED_KEYS
    if unexpected:
        raise fail(f"reference contains unsupported fields: {sorted(unexpected)}")

    if value.get("protocol") != REFERENCE_PROTOCOL:
        raise fail("reference protocol mismatch")
    if value.get("profile_id") != PROFILE_ID:
        raise fail("unsupported lattice profile")

    address = value.get("address")
    try:
        parse_address(address)
    except LatticeError as exc:
        raise fail(str(exc)) from exc

    if value.get("authority") != "storage-only":
        raise fail("lattice references cannot claim epistemic authority")

    content_ref = value.get("content_ref")
    if content_ref is not None and (
        not isinstance(content_ref, str) or SHA_REF.fullmatch(content_ref) is None
    ):
        raise fail("content_ref must be null or sha256 reference")

    note = value.get("note")
    if note is not None and (not isinstance(note, str) or len(note) > 2048):
        raise fail("note must be a string of at most 2048 characters")


def validate() -> dict[str, Any]:
    """Validate repository, profile, schema, machine contract, and fixtures."""
    manifest = load_json(ROOT / "manifest.json")
    if manifest.get("protocol") != "QSOL-LATTICE/0.1":
        raise fail("manifest protocol mismatch")
    if manifest.get("verb") != "REMEMBERS" or manifest.get("authority") != "storage-only":
        raise fail("LATTICE role/authority mismatch")
    if manifest.get("profile") != PROFILE_ID:
        raise fail("manifest profile mismatch")
    if (
        manifest.get("top_level_cells") != 27
        or manifest.get("literal_geometric_claim") is not False
    ):
        raise fail("manifest geometry contract mismatch")
    if manifest.get("max_recursive_depth") != MAX_RECURSIVE_DEPTH:
        raise fail("recursive depth contract mismatch")
    if manifest.get("max_address_length") != MAX_ADDRESS_LENGTH:
        raise fail("address length contract mismatch")
    if manifest.get("address_pattern") != ADDRESS_PATTERN:
        raise fail("address pattern contract mismatch")

    validation = require_mapping(manifest.get("validation"), "manifest.validation")
    minimum = validation.get("python_minimum")
    if not isinstance(minimum, str) or PYTHON_MM.fullmatch(minimum) is None:
        raise fail("manifest.validation.python_minimum missing or invalid")
    required_version = tuple(int(part) for part in minimum.split("."))
    if sys.version_info[:2] < required_version:
        raise fail(f"requires Python >= {minimum}")

    required_paths = {
        "license": manifest.get("license"),
        "machine_entrypoint": manifest.get("machine_entrypoint"),
        "architecture": manifest.get("architecture"),
        "roadmap": manifest.get("roadmap"),
        "security": manifest.get("security"),
        "profile_contract": manifest.get("profile_contract"),
        "reference_runtime": manifest.get("reference_runtime"),
        "validation.workflow": validation.get("workflow"),
    }
    for field, relative in required_paths.items():
        require_file(relative, field)
    require_file("README.md", "README.md")
    require_file("AGENTS.md", "AGENTS.md")

    profile_path = require_file(manifest.get("profile_contract"), "profile_contract")
    profile = load_json(profile_path)
    if profile.get("profile_id") != PROFILE_ID or profile.get("top_level_cell_count") != 27:
        raise fail("profile contract mismatch")
    if profile.get("literal_geometric_claim") is not False:
        raise fail("profile must remain logical, not literal")
    if profile.get("max_recursive_depth") != MAX_RECURSIVE_DEPTH:
        raise fail("profile recursive depth drift")
    address_contract = require_mapping(profile.get("address"), "profile.address")
    if address_contract.get("pattern") != ADDRESS_PATTERN:
        raise fail("profile address pattern drift")
    if address_contract.get("max_length") != MAX_ADDRESS_LENGTH:
        raise fail("profile address length drift")

    axes = require_mapping(profile.get("axes"), "profile.axes")
    if set(axes) != {"x", "y", "z"}:
        raise fail("profile must define x/y/z axes")
    for name, axis_value in axes.items():
        axis = require_mapping(axis_value, f"profile.axes.{name}")
        values = require_mapping(axis.get("values"), f"profile.axes.{name}.values")
        if set(values) != {"0", "1", "2"}:
            raise fail("each axis must define ternary values 0/1/2")

    traversals = require_mapping(profile.get("traversals"), "profile.traversals")
    phi = require_mapping(
        traversals.get("qsol.phi-stride-27/1"),
        "profile.traversals.qsol.phi-stride-27/1",
    )
    if phi.get("stride") != PHI_STRIDE or phi.get("modulus") != 27:
        raise fail("phi traversal parameter drift")

    cells = lexicographic_cells()
    phi_cells = phi_stride_cells()
    if len(cells) != 27 or len(set(cells)) != 27:
        raise fail("lexicographic traversal is not a 27-cell bijection")
    if len(phi_cells) != 27 or set(phi_cells) != set(cells):
        raise fail("phi traversal is not a 27-cell bijection")

    schemas = require_mapping(manifest.get("schemas"), "manifest.schemas")
    schema_path = require_file(schemas.get("address_reference"), "schemas.address_reference")
    schema = load_json(schema_path)
    json_schema = require_mapping(manifest.get("json_schema"), "manifest.json_schema")
    if schema.get("$schema") != json_schema.get("draft") or not schema.get("$id"):
        raise fail("address schema declaration mismatch")
    if schema.get("additionalProperties") is not False:
        raise fail("lattice-reference schema must reject additional properties")
    properties = require_mapping(schema.get("properties"), "schema.properties")
    address_schema = require_mapping(properties.get("address"), "schema.properties.address")
    if address_schema.get("pattern") != f"^{ADDRESS_PATTERN}$":
        raise fail("schema address pattern drift")
    if address_schema.get("maxLength") != MAX_ADDRESS_LENGTH:
        raise fail("schema address length drift")

    examples = require_mapping(manifest.get("schema_examples"), "manifest.schema_examples")
    valid_path = require_file(examples.get("valid"), "schema_examples.valid")
    invalid_path = require_file(examples.get("invalid"), "schema_examples.invalid")
    validate_reference(load_json(valid_path))
    try:
        validate_reference(load_json(invalid_path))
    except LatticeValidationError:
        pass
    else:
        raise fail("invalid lattice fixture unexpectedly passed")

    adversarial_path = require_file(
        examples.get("adversarial_addresses"),
        "schema_examples.adversarial_addresses",
    )
    try:
        adversarial = json.loads(adversarial_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise fail(f"adversarial address fixture invalid: {exc}") from exc
    if not isinstance(adversarial, list) or not adversarial:
        raise fail("adversarial address fixture must be a non-empty array")
    for case in adversarial:
        if not isinstance(case, dict) or not isinstance(case.get("address"), str):
            raise fail("adversarial address fixture row invalid")
        try:
            parse_address(case["address"])
        except LatticeError:
            continue
        raise fail(f"adversarial address unexpectedly accepted: {case.get('name', 'unnamed')}")

    machine = load_json(ROOT / "README4AI.md")
    if machine.get("profile") != PROFILE_ID or machine.get("literal_geometric_claim") is not False:
        raise fail("machine profile contract mismatch")
    if machine.get("address_pattern") != ADDRESS_PATTERN:
        raise fail("machine address pattern drift")
    if machine.get("max_recursive_depth") != MAX_RECURSIVE_DEPTH:
        raise fail("machine recursive depth drift")
    if machine.get("max_address_length") != MAX_ADDRESS_LENGTH:
        raise fail("machine address length drift")

    sample = describe_address("L[2,0,1]/L[1,1,0]")
    if sample["authority"] != "storage-only" or sample["depth"] != 2:
        raise fail("reference runtime description mismatch")

    return {
        "protocol": manifest["protocol"],
        "status": "valid",
        "profile": PROFILE_ID,
        "top_level_cells": len(cells),
        "phi_stride": PHI_STRIDE,
        "max_recursive_depth": MAX_RECURSIVE_DEPTH,
        "max_address_length": MAX_ADDRESS_LENGTH,
        "address_pattern": ADDRESS_PATTERN,
    }


def main(argv: list[str] | None = None) -> int:
    """Run repository or single-reference validation with structured output."""
    parser = argparse.ArgumentParser(description="Validate QSOL LATTICE contracts.")
    parser.add_argument(
        "--reference",
        type=Path,
        help="validate one lattice-reference JSON object instead of the whole repository",
    )
    args = parser.parse_args(argv)

    try:
        if args.reference is not None:
            validate_reference(load_json(args.reference))
            report = {
                "protocol": REFERENCE_PROTOCOL,
                "status": "valid",
                "reference": str(args.reference),
            }
        else:
            report = validate()
    except (LatticeError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        error = {
            "status": "error",
            "error_type": type(exc).__name__,
            "message": str(exc),
        }
        print(json.dumps(error, sort_keys=True), file=sys.stderr)
        return 1

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
