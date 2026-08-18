#!/usr/bin/env python3
"""Thin consumer adapters that preserve LATTICE's storage-only authority boundary."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from .conformance import profile_fingerprint
from .core import (
    EPISTEMIC_VALUES,
    INFORMATION_VALUES,
    PROFILE_ID,
    TEMPORAL_VALUES,
    LatticeError,
    LatticeValidationError,
    parse_address,
)

CONTROL_ADAPTER_PROTOCOL = "qsol-lattice-control-adapter/1"
ARK_RECOVERY_PROTOCOL = "qsol-ark-lattice-recovery/1"
REFERENCE_PROTOCOL = "qsol-lattice-reference/1"
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_ARK_STAGES = {
    "stage.0.integrity",
    "stage.1.identity",
    "stage.2.terminology",
    "stage.3.epistemic",
    "stage.4.reproduce",
    "stage.5.contradictions",
    "stage.6.reconstruct",
    "stage.7.report",
}


def _fail(message: str) -> LatticeValidationError:
    return LatticeValidationError(message)


def _axis_values(values: Mapping[int, str]) -> dict[str, str]:
    return {str(index): values[index] for index in range(3)}


def validate_qsol_control_contract(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the public QSOL-CONTROL lattice contract against LATTICE v1."""
    if not isinstance(value, Mapping):
        raise _fail("QSOL-CONTROL lattice contract must be an object")
    if value.get("type") != "qsol-control-lattice-contract":
        raise _fail("QSOL-CONTROL lattice contract type mismatch")
    if value.get("protocol") != PROFILE_ID:
        raise _fail("QSOL-CONTROL lattice profile mismatch")
    version = value.get("version")
    if type(version) is not int or version != 1:
        raise _fail("QSOL-CONTROL lattice contract version mismatch")
    if value.get("authority") != "storage-only":
        raise _fail("QSOL-CONTROL lattice authority mismatch")
    if value.get("top_level_cell_count") != 27:
        raise _fail("QSOL-CONTROL lattice cell count mismatch")
    if value.get("literal_geometric_claim") is not False:
        raise _fail("QSOL-CONTROL must not make a literal geometric claim")

    axes = value.get("axes")
    if not isinstance(axes, Mapping) or set(axes) != {"x", "y", "z"}:
        raise _fail("QSOL-CONTROL lattice axes mismatch")
    expected = {
        "x": ("information_role", _axis_values(INFORMATION_VALUES)),
        "y": ("epistemic_role", _axis_values(EPISTEMIC_VALUES)),
        "z": ("temporal_role", _axis_values(TEMPORAL_VALUES)),
    }
    for key, (name, values) in expected.items():
        axis = axes.get(key)
        if not isinstance(axis, Mapping):
            raise _fail(f"QSOL-CONTROL axis {key} missing or invalid")
        if axis.get("name") != name or axis.get("values") != values:
            raise _fail(f"QSOL-CONTROL axis {key} semantic mismatch")

    return {
        "protocol": CONTROL_ADAPTER_PROTOCOL,
        "consumer": "QSOL-CONTROL",
        "status": "conformant",
        "profile_id": PROFILE_ID,
        "profile_fingerprint": profile_fingerprint(),
        "authority": "storage-only",
    }


def qsol_corpus_address_reference(
    record: Mapping[str, Any],
    address: str,
    *,
    note: str | None = None,
) -> dict[str, Any]:
    """Project a CORPUS immutable record ID into a payload-free LATTICE reference."""
    if not isinstance(record, Mapping):
        raise _fail("QSOL-CORPUS record must be an object")
    record_id = record.get("record_id")
    if not isinstance(record_id, str) or _SHA256_RE.fullmatch(record_id) is None:
        raise _fail("QSOL-CORPUS record_id must be a sha256 reference")
    authority = record.get("authority")
    if authority is not None and not isinstance(authority, str):
        raise _fail("QSOL-CORPUS authority must be absent or the string 'none'")
    if authority not in {None, "none"}:
        raise _fail("QSOL-CORPUS adapter cannot import authority claims")
    try:
        parse_address(address)
    except LatticeError as exc:
        raise _fail(str(exc)) from exc
    if note is not None and (not isinstance(note, str) or len(note) > 2048):
        raise _fail("note must be a string of at most 2048 characters")

    reference: dict[str, Any] = {
        "protocol": REFERENCE_PROTOCOL,
        "profile_id": PROFILE_ID,
        "address": address,
        "content_ref": record_id,
        "authority": "storage-only",
    }
    if note is not None:
        reference["note"] = note
    return reference


def qsol_ark_recovery_manifest(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Build a LATTICE-indexed ARK recovery manifest without claiming recovery authority."""
    if isinstance(entries, (str, bytes)) or not isinstance(entries, Sequence):
        raise _fail("QSOL-ARK recovery entries must be an array")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise _fail("QSOL-ARK recovery entry must be an object")
        if set(entry) != {"artifact_ref", "address", "recovery_stage"}:
            raise _fail("QSOL-ARK recovery entries require artifact_ref, address, recovery_stage")
        artifact_ref = entry.get("artifact_ref")
        if not isinstance(artifact_ref, str) or _SHA256_RE.fullmatch(artifact_ref) is None:
            raise _fail("QSOL-ARK artifact_ref must be a sha256 reference")
        if artifact_ref in seen:
            raise _fail("QSOL-ARK artifact_ref values must be unique")
        seen.add(artifact_ref)
        address = entry.get("address")
        try:
            parse_address(address)
        except LatticeError as exc:
            raise _fail(str(exc)) from exc
        stage = entry.get("recovery_stage")
        if not isinstance(stage, str):
            raise _fail("QSOL-ARK recovery_stage must be a string")
        if stage not in _ARK_STAGES:
            raise _fail("unsupported QSOL-ARK recovery stage")
        normalized.append(
            {
                "artifact_ref": artifact_ref,
                "recovery_stage": stage,
                "lattice_reference": {
                    "protocol": REFERENCE_PROTOCOL,
                    "profile_id": PROFILE_ID,
                    "address": address,
                    "content_ref": artifact_ref,
                    "authority": "storage-only",
                },
            }
        )

    return {
        "protocol": ARK_RECOVERY_PROTOCOL,
        "lattice_profile": PROFILE_ID,
        "lattice_profile_fingerprint": profile_fingerprint(),
        "lattice_authority": "storage-only",
        "recovery_authority": "QSOL-ARK",
        "entries": normalized,
    }
