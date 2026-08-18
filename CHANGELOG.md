# Changelog

## Unreleased

### Added

- Public 3×3×3 logical-memory profile and machine contract.
- Exact 27-cell lexicographic traversal.
- Fixed integer phi-stride traversal (`17 mod 27`).
- Bounded recursive address parser and role-to-address mapping.
- JSON Schema reference contract and fixtures.
- Dependency-free validator, tests and CI.
- Executable profile compatibility rules and identity-preserving migration manifest/runtime.
- Unknown-major rejection and additive non-semantic metadata compatibility tests.
- QSOL-CONTROL contract conformance adapter.
- QSOL-CORPUS immutable record-to-address reference adapter.
- QSOL-ARK recovery indexing manifest adapter with recovery authority retained by ARK.
- Language-neutral consumer-adapter conformance fixture.
- Independent dependency-free JavaScript reference implementation and CI conformance verification.

### Boundaries

- Migration never silently rewrites historical `(profile_id, address)` identity.
- Consumer adapters do not import payload codecs, evidence authority, truth scoring, distributed database semantics, or biological claims into LATTICE.
