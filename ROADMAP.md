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

- [ ] Publish canonical ordered 27-cell fixture.
- [ ] Publish phi-stride traversal fixture.
- [ ] Publish valid/invalid recursive-address corpus.
- [ ] Add cross-language conformance vectors.
- [ ] Define compact profile fingerprint.

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
- [ ] language-neutral JSON fixtures.

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
