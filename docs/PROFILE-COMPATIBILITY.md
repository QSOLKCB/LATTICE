# Profile compatibility

LATTICE profile IDs are part of the meaning of an address.

## Rules

- Unknown major profile versions are rejected rather than guessed.
- Unknown traversal IDs are rejected rather than mapped to a local default.
- A traversal rule change requires a new traversal/profile version.
- Axis value meaning changes require a new major profile.
- Address syntax or escape semantics changes require a new profile/reference version.
- Additive descriptive metadata may be introduced compatibly only when it does not reinterpret existing addresses.
- Historical records retain their original profile ID and address.
- Migration creates a new derived reference and preserves lineage to the old reference.

```text
MIGRATION != SILENT_REWRITE
NEW_PROFILE != NEW_TRUTH
```

Consumers may support several profile versions simultaneously. They must not guess how an unknown profile maps onto a known one.

## Migration example

A future profile must use a new profile ID instead of changing the meaning of `qsol-3x3x3-sierpinski-derived-memory/1`. Migration tooling may emit a new reference plus lineage metadata in the consumer repository; it must preserve the historical reference unchanged.
