# Profile compatibility

LATTICE profile IDs are part of the meaning of an address. The historical identity of an address is the ordered pair `(profile_id, address)`.

## Executable rules

The canonical machine-readable policy is `protocol/profile-compatibility.json`; the dependency-free implementation is `lattice/migration.py`.

- Unknown major profile versions are rejected rather than guessed.
- Unknown profile families or aliases are rejected even when they reuse a known major number.
- Unknown traversal IDs are rejected rather than mapped to a local default.
- A traversal rule change requires a new traversal/profile version.
- Axis value meaning changes require a new major profile.
- Address syntax or escape-semantics changes require a new profile/reference version.
- A semantic fingerprint change cannot be hidden behind the existing profile ID.
- Additive descriptive metadata is compatible only inside the non-semantic `metadata` namespace and only while the profile ID and semantic fingerprint remain unchanged.
- Historical records retain their original profile ID and address.
- Migration creates a derived target reference while preserving the complete source reference and source identity.

```text
MIGRATION != SILENT_REWRITE
NEW_PROFILE != NEW_TRUTH
PROFILE_COMPATIBILITY != EPISTEMIC_AUTHORITY
ADDRESS_IDENTITY = PROFILE_ID + ADDRESS
```

Consumers may support several profile versions simultaneously. They must not guess how an unknown profile maps onto a known one.

## Migration manifest

`qsol-lattice-migration/1` records source and target profile descriptors, an explicit migration mode, optional address mappings, and mandatory `preserve_source_identity=true`.

`identity` mode is allowed only when source and target profile IDs and fingerprints are identical. Any listed address mapping must also be identity-preserving. `explicit-map` mode requires explicit source-to-target address mappings and never rewrites the source reference in place.

The current repository has one implemented profile major, so migrations to an unknown future major fail closed. The invalid fixture `examples/migration.unknown-major.invalid.json` permanently tests that boundary.

## Additive metadata

The fixture `examples/migration.valid.json` demonstrates a metadata-only compatibility event. The target descriptor contains new descriptive metadata while retaining the exact v1 profile ID and fingerprint. This is compatible because metadata does not participate in address semantics.

Adding a field outside the declared metadata namespace, changing a fingerprinted semantic field, or changing profile meaning without a version bump is not a compatible metadata addition.
