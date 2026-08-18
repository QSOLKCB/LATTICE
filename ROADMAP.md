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
- [ ] Verify the same conformance fixture from an independent non-Python implementation.
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

- [ ] Define profile compatibility rules.
- [ ] Define migration manifest.
- [ ] Preserve old/new address identities.
- [ ] Test unknown-major rejection.
- [ ] Test additive compatible metadata.

## Phase 3 — Consumer adapters

- [ ] QSOL-CONTROL adapter/conformance test.
- [ ] QSOL-CORPUS address-reference adapter.
- [ ] QSOL-ARK recovery manifest integration.
- [x] Language-neutral JSON conformance fixture.

## Phase 4 — Additional implementations

- [ ] JavaScript reference implementation.
- [ ] Rust reference implementation if useful.
- [ ] Lean specification only if it proves a real invariant rather than decorating the repo with theorem-prover confetti.

## Deferred / prohibited-by-default

- literal cognitive-coordinate claims;
- truth scoring by lattice position;
- distributed database semantics;
- biological claims from DNA-like codecs owned elsewhere;
- changing stride/profile meaning without a version bump.
