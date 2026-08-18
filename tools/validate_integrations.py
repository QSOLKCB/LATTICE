#!/usr/bin/env python3
"""Validate migration, adapters, and additional implementation contracts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lattice.adapters import (
    qsol_ark_recovery_manifest,
    qsol_corpus_address_reference,
    validate_qsol_control_contract,
)
from lattice.conformance import profile_fingerprint
from lattice.core import PROFILE_ID, LatticeValidationError
from lattice.migration import (
    MAX_MIGRATION_MAPPINGS,
    PROFILE_DESCRIPTOR_PROTOCOL,
    current_profile_descriptor,
    validate_migration_manifest,
    validate_profile_descriptor,
)

EXPECTED_RUST_TOOLCHAIN = "1.96.1"
EXPECTED_LEAN_TOOLCHAIN = "leanprover/lean4:v4.30.0"


def load_json(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LatticeValidationError(f"{relative}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise LatticeValidationError(f"{relative}: must contain an object")
    return value


def require_file(relative: Any, field: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise LatticeValidationError(f"{field} missing or invalid")
    path = ROOT / relative
    if not path.is_file():
        raise LatticeValidationError(f"{field} missing file: {relative}")
    return path


def validate() -> dict[str, Any]:
    manifest = load_json("manifest.json")
    contract_path = manifest.get("profile_compatibility_contract")
    migration_schema = manifest.get("migration_schema")
    migration_fixture = manifest.get("migration_fixture")
    consumer_fixture = manifest.get("consumer_conformance_fixture")
    javascript_runtime = manifest.get("javascript_reference")
    javascript_validator = manifest.get("javascript_conformance_command")
    rust_runtime = manifest.get("rust_reference")
    rust_validator = manifest.get("rust_conformance_command")
    lean_specification = manifest.get("lean_specification")
    lean_toolchain_file = manifest.get("lean_toolchain_file")
    lean_validator = manifest.get("lean_verification_command")
    formal_invariants = manifest.get("formal_invariants")

    for field, relative in {
        "profile_compatibility_contract": contract_path,
        "migration_schema": migration_schema,
        "migration_fixture": migration_fixture,
        "consumer_conformance_fixture": consumer_fixture,
        "javascript_reference": javascript_runtime,
        "rust_reference": rust_runtime,
        "lean_specification": lean_specification,
        "lean_toolchain_file": lean_toolchain_file,
        "formal_invariants": formal_invariants,
    }.items():
        require_file(relative, field)

    if javascript_validator != "node implementations/javascript/verify_conformance.js":
        raise LatticeValidationError("javascript conformance command drift")
    if rust_validator != "python3 tools/verify_rust_conformance.py":
        raise LatticeValidationError("rust conformance command drift")
    if manifest.get("rust_toolchain") != EXPECTED_RUST_TOOLCHAIN:
        raise LatticeValidationError("rust toolchain drift")
    if lean_validator != "lean implementations/lean/Lattice.lean":
        raise LatticeValidationError("lean verification command drift")
    if manifest.get("lean_toolchain") != EXPECTED_LEAN_TOOLCHAIN:
        raise LatticeValidationError("lean toolchain drift")
    lean_toolchain_text = require_file(lean_toolchain_file, "lean_toolchain_file").read_text(
        encoding="utf-8"
    ).strip()
    if lean_toolchain_text != EXPECTED_LEAN_TOOLCHAIN:
        raise LatticeValidationError("lean-toolchain file drift")

    additional = manifest.get("additional_implementations")
    if additional != {
        "javascript": "conformance-reference",
        "rust": "stdlib-only-conformance-reference",
        "lean": "traversal-invariant-specification",
    }:
        raise LatticeValidationError("additional implementation registry drift")

    contract = load_json(contract_path)
    if contract.get("protocol") != "qsol-lattice-profile-compatibility/1":
        raise LatticeValidationError("profile compatibility protocol mismatch")
    current = contract.get("current_profile")
    if current != current_profile_descriptor():
        raise LatticeValidationError("profile compatibility current descriptor drift")
    rules = contract.get("rules")
    if not isinstance(rules, dict):
        raise LatticeValidationError("profile compatibility rules missing")
    expected_rules = {
        "unknown_major": "reject",
        "additive_non_semantic_metadata": "compatible",
        "historical_identity": "preserve-profile-id-plus-address",
        "migration": "explicit-derived-reference-only",
    }
    for key, expected in expected_rules.items():
        if rules.get(key) != expected:
            raise LatticeValidationError(f"profile compatibility rule drift: {key}")

    schema = load_json(migration_schema)
    if schema.get("$schema") != manifest.get("json_schema", {}).get("draft"):
        raise LatticeValidationError("migration schema draft mismatch")
    if schema.get("additionalProperties") is not False:
        raise LatticeValidationError("migration schema must reject additional properties")

    definitions = schema.get("$defs")
    if not isinstance(definitions, dict):
        raise LatticeValidationError("migration schema definitions missing")
    descriptor_schema = definitions.get("profileDescriptor")
    if not isinstance(descriptor_schema, dict):
        raise LatticeValidationError("migration profile descriptor schema missing")
    variants = descriptor_schema.get("oneOf")
    if not isinstance(variants, list) or len(variants) != 1:
        raise LatticeValidationError("migration schema must enumerate supported profile descriptors")
    variant = variants[0]
    if not isinstance(variant, dict) or not isinstance(variant.get("properties"), dict):
        raise LatticeValidationError("migration supported profile descriptor invalid")
    supported = variant["properties"]
    if supported.get("profile_id", {}).get("const") != PROFILE_ID:
        raise LatticeValidationError("migration schema supported profile id drift")
    if supported.get("profile_fingerprint", {}).get("const") != profile_fingerprint():
        raise LatticeValidationError("migration schema supported profile fingerprint drift")

    properties = schema.get("properties")
    if not isinstance(properties, dict):
        raise LatticeValidationError("migration schema properties missing")
    mappings_schema = properties.get("mappings")
    if not isinstance(mappings_schema, dict):
        raise LatticeValidationError("migration mappings schema missing")
    if mappings_schema.get("maxItems") != MAX_MIGRATION_MAPPINGS:
        raise LatticeValidationError("migration mapping limit drift")

    migration = load_json(migration_fixture)
    migration_report = validate_migration_manifest(migration)
    if migration_report["status"] != "valid":
        raise LatticeValidationError("migration fixture did not validate")

    invalid = load_json("examples/migration.unknown-major.invalid.json")
    try:
        validate_migration_manifest(invalid)
    except LatticeValidationError as exc:
        if "unsupported profile major" not in str(exc):
            raise
    else:
        raise LatticeValidationError("unknown-major migration unexpectedly passed")

    additive = current_profile_descriptor(
        {"description": "compatible descriptive metadata", "consumer_hint": "optional"}
    )
    additive_report = validate_profile_descriptor(additive)
    if additive_report.get("compatibility") != "additive-metadata":
        raise LatticeValidationError("additive metadata compatibility drift")

    fixture = load_json(consumer_fixture)
    if fixture.get("protocol") != "qsol-lattice-consumer-conformance/1":
        raise LatticeValidationError("consumer conformance protocol mismatch")
    control = fixture.get("qsol_control")
    corpus = fixture.get("qsol_corpus")
    ark = fixture.get("qsol_ark")
    if not all(isinstance(case, dict) for case in (control, corpus, ark)):
        raise LatticeValidationError("consumer conformance cases missing")
    if validate_qsol_control_contract(control["input"]) != control["expected"]:
        raise LatticeValidationError("QSOL-CONTROL adapter fixture drift")
    if qsol_corpus_address_reference(corpus["input"], corpus["address"]) != corpus["expected"]:
        raise LatticeValidationError("QSOL-CORPUS adapter fixture drift")
    if qsol_ark_recovery_manifest(ark["input"]) != ark["expected"]:
        raise LatticeValidationError("QSOL-ARK adapter fixture drift")

    roadmap = require_file(manifest.get("roadmap"), "roadmap").read_text(encoding="utf-8")
    if "- [ ]" in roadmap:
        raise LatticeValidationError("roadmap contains unfinished implementation checkbox")
    if "All implementation phases in this roadmap are complete." not in roadmap:
        raise LatticeValidationError("roadmap completion declaration missing")

    return {
        "status": "valid",
        "profile_id": PROFILE_ID,
        "profile_descriptor_protocol": PROFILE_DESCRIPTOR_PROTOCOL,
        "profile_fingerprint": profile_fingerprint(),
        "migration_contract": "valid",
        "consumer_adapters": ["QSOL-CONTROL", "QSOL-CORPUS", "QSOL-ARK"],
        "javascript_reference": javascript_runtime,
        "rust_reference": rust_runtime,
        "rust_toolchain": EXPECTED_RUST_TOOLCHAIN,
        "lean_specification": lean_specification,
        "lean_toolchain": EXPECTED_LEAN_TOOLCHAIN,
        "roadmap": "complete",
    }


if __name__ == "__main__":
    try:
        report = validate()
    except (LatticeValidationError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {"status": "error", "error_type": type(exc).__name__, "message": str(exc)},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        raise SystemExit(1)
    print(json.dumps(report, indent=2, sort_keys=True))
