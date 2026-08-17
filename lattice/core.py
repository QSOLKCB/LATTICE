#!/usr/bin/env python3
"""Dependency-free reference implementation for QSOL LATTICE."""

from __future__ import annotations

import math
import re
from typing import Any

PROFILE_ID = "qsol-3x3x3-sierpinski-derived-memory/1"
LEXICOGRAPHIC_TRAVERSAL = "qsol.lexicographic-27/1"
PHI_STRIDE_TRAVERSAL = "qsol.phi-stride-27/1"
PHI_STRIDE = 17
TOP_LEVEL_CELL_COUNT = 27
MAX_RECURSIVE_DEPTH = 8

ADDRESS_PATTERN = r"L\[[0-2],[0-2],[0-2]\](?:/L\[[0-2],[0-2],[0-2]\]){0,7}"
_ADDRESS_RE = re.compile(rf"^{ADDRESS_PATTERN}$")
_SEGMENT_RE = re.compile(r"^L\[([0-2]),([0-2]),([0-2])\]$")

INFORMATION_ROLES = {"question": 0, "response": 1, "evidence": 2}
EPISTEMIC_ROLES = {"observed": 0, "derived": 1, "unresolved": 2}
TEMPORAL_ROLES = {"current": 0, "historical": 1, "recovery": 2}

INFORMATION_VALUES = {value: key for key, value in INFORMATION_ROLES.items()}
EPISTEMIC_VALUES = {value: key for key, value in EPISTEMIC_ROLES.items()}
TEMPORAL_VALUES = {value: key for key, value in TEMPORAL_ROLES.items()}


class LatticeError(ValueError):
    """Raised when a LATTICE profile/address invariant is violated."""


def lexicographic_cells() -> tuple[str, ...]:
    """Return exactly 27 top-level cells in canonical coordinate order."""
    cells = tuple(
        f"L[{x},{y},{z}]"
        for x in range(3)
        for y in range(3)
        for z in range(3)
    )
    if len(cells) != TOP_LEVEL_CELL_COUNT or len(set(cells)) != TOP_LEVEL_CELL_COUNT:
        raise LatticeError("canonical profile must contain exactly 27 unique cells")
    return cells


def phi_stride_cells() -> tuple[str, ...]:
    """Return the fixed integer phi-derived traversal over all 27 cells."""
    if math.gcd(PHI_STRIDE, TOP_LEVEL_CELL_COUNT) != 1:
        raise LatticeError("phi stride must be coprime with the cell count")
    cells = lexicographic_cells()
    order = tuple(
        cells[(step * PHI_STRIDE) % TOP_LEVEL_CELL_COUNT]
        for step in range(TOP_LEVEL_CELL_COUNT)
    )
    if len(set(order)) != TOP_LEVEL_CELL_COUNT:
        raise LatticeError("phi traversal must visit every cell exactly once")
    return order


def traversal_cells(traversal_id: str) -> tuple[str, ...]:
    """Resolve a known versioned traversal ID."""
    if traversal_id == LEXICOGRAPHIC_TRAVERSAL:
        return lexicographic_cells()
    if traversal_id == PHI_STRIDE_TRAVERSAL:
        return phi_stride_cells()
    raise LatticeError(f"unsupported traversal: {traversal_id}")


def address_for_roles(information: str, epistemic: str, temporal: str) -> str:
    """Map named role values to one canonical top-level address."""
    try:
        x = INFORMATION_ROLES[information]
        y = EPISTEMIC_ROLES[epistemic]
        z = TEMPORAL_ROLES[temporal]
    except KeyError as exc:
        raise LatticeError(f"unknown lattice role: {exc.args[0]}") from exc
    return f"L[{x},{y},{z}]"


def parse_address(address: str, *, max_depth: int = MAX_RECURSIVE_DEPTH) -> tuple[tuple[int, int, int], ...]:
    """Parse a bounded top-level/recursive lattice address."""
    if not isinstance(address, str) or not address:
        raise LatticeError("address must be a non-empty string")
    if not isinstance(max_depth, int) or not 1 <= max_depth <= MAX_RECURSIVE_DEPTH:
        raise LatticeError(f"max_depth must be 1..{MAX_RECURSIVE_DEPTH}")

    segments = address.split("/")
    if len(segments) > max_depth:
        raise LatticeError("address exceeds recursive depth limit")

    coordinates: list[tuple[int, int, int]] = []
    for segment in segments:
        match = _SEGMENT_RE.fullmatch(segment)
        if match is None:
            raise LatticeError(f"invalid lattice address segment: {segment!r}")
        coordinates.append(tuple(int(part) for part in match.groups()))
    return tuple(coordinates)


def describe_address(address: str) -> dict[str, Any]:
    """Return inspectable role semantics for every address segment."""
    parsed = parse_address(address)
    segments = []
    for depth, (x, y, z) in enumerate(parsed):
        segments.append(
            {
                "depth": depth,
                "address": f"L[{x},{y},{z}]",
                "information_role": INFORMATION_VALUES[x],
                "epistemic_role": EPISTEMIC_VALUES[y],
                "temporal_role": TEMPORAL_VALUES[z],
            }
        )
    return {
        "profile": PROFILE_ID,
        "address": address,
        "depth": len(parsed),
        "segments": segments,
        "authority": "storage-only",
        "literal_geometric_claim": False,
    }


def is_valid_address(address: str) -> bool:
    """Boolean helper for callers that do not need error detail."""
    try:
        parse_address(address)
    except LatticeError:
        return False
    return True
