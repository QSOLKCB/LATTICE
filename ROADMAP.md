# Roadmap

## Phase 0 — Bootstrap

- [x] Publish the 3×3×3 profile and authority boundaries.
- [x] Implement exact 27-cell generation.
- [x] Implement bounded recursive address parsing.
- [x] Implement role-to-address mapping.
- [x] Implement lexicographic traversal.
- [x] Implement fixed phi-stride traversal.
- [x] Add machine contract, validator, tests and CI.

## Phase 1 — Profile conformance vectors

- [x] Publish canonical ordered 27-cell fixture.
- [x] Publish phi-stride traversal fixture.
- [x] Publish valid/invalid/adversarial recursive-address corpus.
- [x] Verify the same conformance fixture from an independent non-Python implementation.
- [x] Define compact profile fingerprint over profile/traversal/address semantics.
- [x] Fail CI when runtime semantics, manifest fingerprint, or fixture diverge.

Canonical v1 profile fingerprint:

```text
sha256:6e7c4a9a781d552a2b561d334a8435c12efe2908fcd24a0f152935aded555bcf
```

The fingerprint is compatibility evidence only:

```text
FINGERPRINT_MATCH != TRUTH
FINGERPRINT_MATCH != PAYLOAD_IDENTITY
PROFILE_COMPATIBILITY != EPISTEMIC_AUTHORITY
```

## Phase 2 — Migration contract

- [x] Define profile compatibility rules.
- [x] Define migration manifest.
- [x] Preserve old/new address identities.
- [x] Test unknown-major rejection.
- [x] Test additive compatible metadata.

Implemented by `protocol/profile-compatibility.json`, `schema/lattice-migration.schema.json`, `lattice/migration.py`, and migration fixtures/tests. Historical identity is the pair `(profile_id, address)`; migrations derive a target reference and retain the source reference unchanged.

## Phase 3 — Consumer adapters

- [x] QSOL-CONTROL adapter/conformance test.
- [x] QSOL-CORPUS address-reference adapter.
- [x] QSOL-ARK recovery manifest integration.
- [x] Language-neutral JSON conformance fixture.

Adapters are deliberately thin. They do not import CONTROL payload codecs, CORPUS content, or ARK recovery authority into LATTICE.

## Phase 4 — Additional implementations

- [x] JavaScript reference implementation.
- [x] Rust reference implementation.
- [x] Lean specification proving a real traversal invariant.

The JavaScript implementation independently regenerates and hashes the canonical conformance vector. The Rust implementation independently regenerates the same profile/traversal/address semantics and SHA-256 fingerprint using only the Rust standard library, then emits a record compared against the frozen fixture in CI.

The Lean specification is deliberately narrow: it proves that the fixed `17 mod 27` traversal is coprime, has length 27, contains no duplicate indices, and reduces to the exact published index order. It does not formalize cognitive, physical, epistemic, or biological claims. See `docs/FORMAL-INVARIANTS.md`.

## Roadmap completion state

All implementation phases in this roadmap are complete. Future changes are maintenance or explicitly versioned extensions, not silent reinterpretations of v1 semantics.

## Deferred / prohibited-by-default

These are enduring scope boundaries, not unfinished roadmap tasks:

- literal cognitive-coordinate claims;
- truth scoring by lattice position;
- distributed database semantics;
- biological claims from DNA-like codecs owned elsewhere;
- changing stride/profile meaning without a version bump.
