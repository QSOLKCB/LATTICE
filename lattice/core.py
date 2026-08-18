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

SEGMENT_PATTERN = r"L\[[0-2],[0-2],[0-2]\]"
CANONICAL_SEGMENT_LENGTH = len("L[0,0,0]")


def address_pattern(max_depth: int = MAX_RECURSIVE_DEPTH) -> str:
    """Return the canonical regex body for a bounded recursive address."""
    if type(max_depth) is not int or not 1 <= max_depth <= MAX_RECURSIVE_DEPTH:
        raise LatticeValidationError(f"max_depth must be 1..{MAX_RECURSIVE_DEPTH}")
    return rf"{SEGMENT_PATTERN}(?:/{SEGMENT_PATTERN}){{0,{max_depth - 1}}}"


def max_address_length(max_depth: int = MAX_RECURSIVE_DEPTH) -> int:
    """Return the longest canonical address in characters for max_depth."""
    if type(max_depth) is not int or not 1 <= max_depth <= MAX_RECURSIVE_DEPTH:
        raise LatticeValidationError(f"max_depth must be 1..{MAX_RECURSIVE_DEPTH}")
    return max_depth * CANONICAL_SEGMENT_LENGTH + (max_depth - 1)


ADDRESS_PATTERN = address_pattern()
MAX_ADDRESS_LENGTH = max_address_length()
_ADDRESS_RE = re.compile(rf"^{ADDRESS_PATTERN}$")
_SEGMENT_RE = re.compile(r"^L\[([0-2]),([0-2]),([0-2])\]$")

INFORMATION_ROLES = {"question": 0, "response": 1, "evidence": 2}
EPISTEMIC_ROLES = {"observed": 0, "derived": 1, "unresolved": 2}
TEMPORAL_ROLES = {"current": 0, "historical": 1, "recovery": 2}

INFORMATION_VALUES = {value: key for key, value in INFORMATION_ROLES.items()}
EPISTEMIC_VALUES = {value: key for key, value in EPISTEMIC_ROLES.items()}
TEMPORAL_VALUES = {value: key for key, value in TEMPORAL_ROLES.items()}


class LatticeError(ValueError):
    """Base error for LATTICE protocol failures."""


class LatticeParseError(LatticeError):
    """Raised when untrusted address text violates the canonical grammar."""


class LatticeValidationError(LatticeError):
    """Raised when profile, traversal, or reference validation fails."""


def lexicographic_cells() -> tuple[str, ...]:
    """Return exactly 27 top-level cells in canonical coordinate order."""
    cells = tuple(
        f"L[{x},{y},{z}]"
        for x in range(3)
        for y in range(3)
        for z in range(3)
    )
    if len(cells) != TOP_LEVEL_CELL_COUNT or len(set(cells)) != TOP_LEVEL_CELL_COUNT:
        raise LatticeValidationError("canonical profile must contain exactly 27 unique cells")
    return cells


def phi_stride_cells() -> tuple[str, ...]:
    """Return the fixed integer phi-derived traversal over all 27 cells."""
    if math.gcd(PHI_STRIDE, TOP_LEVEL_CELL_COUNT) != 1:
        raise LatticeValidationError("phi stride must be coprime with the cell count")
    cells = lexicographic_cells()
    order = tuple(
        cells[(step * PHI_STRIDE) % TOP_LEVEL_CELL_COUNT]
        for step in range(TOP_LEVEL_CELL_COUNT)
    )
    if len(set(order)) != TOP_LEVEL_CELL_COUNT:
        raise LatticeValidationError("phi traversal must visit every cell exactly once")
    return order


def traversal_cells(traversal_id: str) -> tuple[str, ...]:
    """Resolve a known versioned traversal ID and reject unknown IDs."""
    if traversal_id == LEXICOGRAPHIC_TRAVERSAL:
        return lexicographic_cells()
    if traversal_id == PHI_STRIDE_TRAVERSAL:
        return phi_stride_cells()
    raise LatticeValidationError(f"unsupported traversal: {traversal_id}")


def address_for_roles(information: str, epistemic: str, temporal: str) -> str:
    """Map named role values to one canonical top-level address."""
    try:
        x = INFORMATION_ROLES[information]
        y = EPISTEMIC_ROLES[epistemic]
        z = TEMPORAL_ROLES[temporal]
    except KeyError as exc:
        raise LatticeValidationError(f"unknown lattice role: {exc.args[0]}") from exc
    return f"L[{x},{y},{z}]"


def parse_address(
    address: str,
    *,
    max_depth: int = MAX_RECURSIVE_DEPTH,
) -> tuple[tuple[int, int, int], ...]:
    """Parse untrusted address text using the canonical bounded grammar."""
    if not isinstance(address, str) or not address:
        raise LatticeParseError("address must be a non-empty string")
    if type(max_depth) is not int or not 1 <= max_depth <= MAX_RECURSIVE_DEPTH:
        raise LatticeValidationError(f"max_depth must be 1..{MAX_RECURSIVE_DEPTH}")
    if address.count("/") + 1 > max_depth:
        raise LatticeParseError("address exceeds recursive depth limit")
    if len(address) > max_address_length(max_depth):
        raise LatticeParseError("address exceeds canonical length limit")

    # Structural syntax has one source of truth: address_pattern(max_depth).
    pattern = _ADDRESS_RE if max_depth == MAX_RECURSIVE_DEPTH else re.compile(
        rf"^{address_pattern(max_depth)}$"
    )
    if pattern.fullmatch(address) is None:
        if _ADDRESS_RE.fullmatch(address) is not None:
            raise LatticeParseError("address exceeds recursive depth limit")
        raise LatticeParseError("invalid lattice address")

    coordinates: list[tuple[int, int, int]] = []
    for segment in address.split("/"):
        match = _SEGMENT_RE.fullmatch(segment)
        if match is None:
            raise LatticeParseError("invalid lattice address")
        coordinates.append(tuple(int(part) for part in match.groups()))
    return tuple(coordinates)


def describe_address(address: str) -> dict[str, Any]:
    """Return inspectable role semantics for every validated address segment."""
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
    """Return whether address satisfies the canonical bounded grammar."""
    try:
        parse_address(address)
    except LatticeError:
        return False
    return True
