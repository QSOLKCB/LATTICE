#!/usr/bin/env python3
"""Versioned profile compatibility and identity-preserving migration helpers."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any, Mapping

from .conformance import profile_fingerprint
from .core import PROFILE_ID, LatticeError, LatticeValidationError, parse_address

PROFILE_DESCRIPTOR_PROTOCOL = "qsol-lattice-profile-descriptor/1"
MIGRATION_PROTOCOL = "qsol-lattice-migration/1"
MIGRATED_REFERENCE_PROTOCOL = "qsol-lattice-migrated-reference/1"
REFERENCE_PROTOCOL = "qsol-lattice-reference/1"
_PROFILE_VERSION_RE = re.compile(r"^(?P<family>.+)/(?P<major>[1-9][0-9]*)$")
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _fail(message: str) -> LatticeValidationError:
    return LatticeValidationError(message)


def profile_family_and_major(profile_id: str) -> tuple[str, int]:
    """Parse the terminal major version from a versioned profile ID."""
    if not isinstance(profile_id, str):
        raise _fail("profile_id must be a string")
    match = _PROFILE_VERSION_RE.fullmatch(profile_id)
    if match is None:
        raise _fail("profile_id must end in /<major>")
    return match.group("family"), int(match.group("major"))


def current_profile_descriptor(metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return a portable descriptor for the implemented profile semantics."""
    descriptor: dict[str, Any] = {
        "protocol": PROFILE_DESCRIPTOR_PROTOCOL,
        "profile_id": PROFILE_ID,
        "profile_fingerprint": profile_fingerprint(),
    }
    if metadata is not None:
        descriptor["metadata"] = deepcopy(dict(metadata))
    return descriptor


def validate_profile_descriptor(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate compatibility while allowing additive non-semantic metadata."""
    if not isinstance(value, Mapping):
        raise _fail("profile descriptor must be an object")
    if value.get("protocol") != PROFILE_DESCRIPTOR_PROTOCOL:
        raise _fail("profile descriptor protocol mismatch")

    profile_id = value.get("profile_id")
    family, major = profile_family_and_major(profile_id)
    current_family, current_major = profile_family_and_major(PROFILE_ID)
    if major != current_major:
        raise _fail(f"unsupported profile major: {major}")
    if family != current_family or profile_id != PROFILE_ID:
        raise _fail("unsupported lattice profile")

    fingerprint = value.get("profile_fingerprint")
    if fingerprint != profile_fingerprint():
        raise _fail("profile semantic fingerprint mismatch")

    metadata = value.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, Mapping):
            raise _fail("profile metadata must be an object")
        try:
            json.dumps(metadata, sort_keys=True, ensure_ascii=False, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise _fail("profile metadata must be finite JSON data") from exc

    unexpected = set(value) - {
        "protocol",
        "profile_id",
        "profile_fingerprint",
        "metadata",
    }
    if unexpected:
        raise _fail(f"profile descriptor contains unsupported fields: {sorted(unexpected)}")

    return {
        "status": "compatible",
        "compatibility": "additive-metadata" if metadata else "exact",
        "profile_id": PROFILE_ID,
        "profile_fingerprint": profile_fingerprint(),
    }


def reference_identity(profile_id: str, address: str) -> dict[str, str]:
    """Return the complete logical identity of one historical address."""
    descriptor = current_profile_descriptor()
    descriptor["profile_id"] = profile_id
    validate_profile_descriptor(descriptor)
    try:
        parse_address(address)
    except LatticeError as exc:
        raise _fail(str(exc)) from exc
    return {"profile_id": profile_id, "address": address}


def _validate_reference(value: Mapping[str, Any]) -> None:
    if not isinstance(value, Mapping):
        raise _fail("reference must be an object")
    allowed = {"protocol", "profile_id", "address", "content_ref", "authority", "note"}
    unexpected = set(value) - allowed
    if unexpected:
        raise _fail(f"reference contains unsupported fields: {sorted(unexpected)}")
    if value.get("protocol") != REFERENCE_PROTOCOL:
        raise _fail("reference protocol mismatch")
    reference_identity(value.get("profile_id"), value.get("address"))
    if value.get("authority") != "storage-only":
        raise _fail("lattice references cannot claim epistemic authority")
    content_ref = value.get("content_ref")
    if content_ref is not None and (
        not isinstance(content_ref, str) or _SHA256_RE.fullmatch(content_ref) is None
    ):
        raise _fail("content_ref must be null or sha256 reference")
    note = value.get("note")
    if note is not None and (not isinstance(note, str) or len(note) > 2048):
        raise _fail("note must be a string of at most 2048 characters")


def validate_migration_manifest(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one explicit profile migration contract."""
    if not isinstance(value, Mapping):
        raise _fail("migration manifest must be an object")
    required = {
        "protocol",
        "migration_id",
        "source_profile",
        "target_profile",
        "mode",
        "preserve_source_identity",
        "mappings",
        "metadata",
    }
    missing = required - set(value)
    if missing:
        raise _fail(f"migration manifest missing fields: {sorted(missing)}")
    unexpected = set(value) - required
    if unexpected:
        raise _fail(f"migration manifest contains unsupported fields: {sorted(unexpected)}")
    if value.get("protocol") != MIGRATION_PROTOCOL:
        raise _fail("migration manifest protocol mismatch")
    migration_id = value.get("migration_id")
    if not isinstance(migration_id, str) or not migration_id or len(migration_id) > 256:
        raise _fail("migration_id must be a non-empty string of at most 256 characters")
    if value.get("preserve_source_identity") is not True:
        raise _fail("migration must preserve source identity")

    source = value.get("source_profile")
    target = value.get("target_profile")
    source_report = validate_profile_descriptor(source)
    target_report = validate_profile_descriptor(target)

    mode = value.get("mode")
    if mode not in {"identity", "explicit-map"}:
        raise _fail("migration mode must be identity or explicit-map")

    mappings = value.get("mappings")
    if not isinstance(mappings, list):
        raise _fail("migration mappings must be an array")
    seen_sources: set[str] = set()
    normalized: list[dict[str, str]] = []
    for row in mappings:
        if not isinstance(row, Mapping) or set(row) != {"source_address", "target_address"}:
            raise _fail("migration mapping rows require source_address and target_address only")
        source_address = row.get("source_address")
        target_address = row.get("target_address")
        reference_identity(source["profile_id"], source_address)
        reference_identity(target["profile_id"], target_address)
        if source_address in seen_sources:
            raise _fail("migration mapping source addresses must be unique")
        seen_sources.add(source_address)
        normalized.append(
            {"source_address": source_address, "target_address": target_address}
        )

    if mode == "identity":
        if source["profile_id"] != target["profile_id"]:
            raise _fail("identity migration requires the same profile_id")
        if source["profile_fingerprint"] != target["profile_fingerprint"]:
            raise _fail("identity migration requires the same profile fingerprint")
        for row in normalized:
            if row["source_address"] != row["target_address"]:
                raise _fail("identity migration cannot change address meaning")
    elif not normalized:
        raise _fail("explicit-map migration requires at least one address mapping")

    metadata = value.get("metadata")
    if not isinstance(metadata, Mapping):
        raise _fail("migration metadata must be an object")
    try:
        json.dumps(metadata, sort_keys=True, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise _fail("migration metadata must be finite JSON data") from exc

    return {
        "status": "valid",
        "migration_id": migration_id,
        "mode": mode,
        "source_profile": source_report["profile_id"],
        "target_profile": target_report["profile_id"],
        "mapping_count": len(normalized),
    }


def migrate_reference(reference: Mapping[str, Any], manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Derive a new reference while retaining immutable source identity."""
    _validate_reference(reference)
    validate_migration_manifest(manifest)

    source_profile = manifest["source_profile"]["profile_id"]
    target_profile = manifest["target_profile"]["profile_id"]
    if reference["profile_id"] != source_profile:
        raise _fail("reference profile does not match migration source profile")

    source_address = reference["address"]
    if manifest["mode"] == "identity":
        target_address = source_address
    else:
        mapping = {
            row["source_address"]: row["target_address"]
            for row in manifest["mappings"]
        }
        try:
            target_address = mapping[source_address]
        except KeyError as exc:
            raise _fail("reference address has no explicit migration mapping") from exc

    source_reference = deepcopy(dict(reference))
    target_reference = deepcopy(dict(reference))
    target_reference["profile_id"] = target_profile
    target_reference["address"] = target_address
    _validate_reference(target_reference)

    return {
        "protocol": MIGRATED_REFERENCE_PROTOCOL,
        "migration_id": manifest["migration_id"],
        "source_identity": reference_identity(source_profile, source_address),
        "target_identity": reference_identity(target_profile, target_address),
        "source_reference": source_reference,
        "target_reference": target_reference,
    }
