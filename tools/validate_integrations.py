#!/usr/bin/env python3
"""Validate migration and consumer-adapter contracts against frozen fixtures."""

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


def load_json(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LatticeValidationError(f"{relative}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise LatticeValidationError(f"{relative}: must contain an object")
    return value


def validate() -> dict[str, Any]:
    manifest = load_json("manifest.json")
    contract_path = manifest.get("profile_compatibility_contract")
    migration_schema = manifest.get("migration_schema")
    migration_fixture = manifest.get("migration_fixture")
    consumer_fixture = manifest.get("consumer_conformance_fixture")
    javascript_runtime = manifest.get("javascript_reference")
    javascript_validator = manifest.get("javascript_conformance_command")
    for field, relative in {
        "profile_compatibility_contract": contract_path,
        "migration_schema": migration_schema,
        "migration_fixture": migration_fixture,
        "consumer_conformance_fixture": consumer_fixture,
        "javascript_reference": javascript_runtime,
    }.items():
        if not isinstance(relative, str) or not (ROOT / relative).is_file():
            raise LatticeValidationError(f"{field} missing or invalid")
    if javascript_validator != "node implementations/javascript/verify_conformance.js":
        raise LatticeValidationError("javascript conformance command drift")

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

    return {
        "status": "valid",
        "profile_id": PROFILE_ID,
        "profile_descriptor_protocol": PROFILE_DESCRIPTOR_PROTOCOL,
        "profile_fingerprint": profile_fingerprint(),
        "migration_contract": "valid",
        "consumer_adapters": ["QSOL-CONTROL", "QSOL-CORPUS", "QSOL-ARK"],
        "javascript_reference": javascript_runtime,
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
