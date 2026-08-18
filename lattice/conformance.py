#!/usr/bin/env python3
"""Canonical LATTICE conformance vector and compact fingerprint."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .core import (
    LEXICOGRAPHIC_TRAVERSAL,
    MAX_ADDRESS_LENGTH,
    MAX_RECURSIVE_DEPTH,
    PHI_STRIDE,
    PHI_STRIDE_TRAVERSAL,
    PROFILE_ID,
    TOP_LEVEL_CELL_COUNT,
    lexicographic_cells,
    phi_stride_cells,
)

CONFORMANCE_PROTOCOL = "qsol-lattice-conformance/1"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def conformance_payload() -> dict[str, Any]:
    """Return the exact profile semantics included in the v1 fingerprint."""
    return {
        "protocol": CONFORMANCE_PROTOCOL,
        "profile_id": PROFILE_ID,
        "lexicographic_traversal_id": LEXICOGRAPHIC_TRAVERSAL,
        "phi_traversal_id": PHI_STRIDE_TRAVERSAL,
        "phi_stride": PHI_STRIDE,
        "modulus": TOP_LEVEL_CELL_COUNT,
        "max_recursive_depth": MAX_RECURSIVE_DEPTH,
        "max_address_length": MAX_ADDRESS_LENGTH,
        "lexicographic_cells": list(lexicographic_cells()),
        "phi_stride_cells": list(phi_stride_cells()),
    }


def profile_fingerprint() -> str:
    """Return SHA-256 over canonical conformance payload bytes."""
    digest = hashlib.sha256(canonical_json_bytes(conformance_payload())).hexdigest()
    return f"sha256:{digest}"


def conformance_record() -> dict[str, Any]:
    """Return the portable vector with its compact fingerprint."""
    return {"fingerprint": profile_fingerprint(), **conformance_payload()}
