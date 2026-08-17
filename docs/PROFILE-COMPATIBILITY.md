# Profile compatibility

LATTICE profile IDs are part of the meaning of an address.

## Rules

- Unknown major profile versions fail closed.
- A traversal rule change requires a new traversal/profile version.
- Axis value meaning changes require a new major profile.
- Additive descriptive metadata may be introduced compatibly when it does not reinterpret existing addresses.
- Historical records retain their original profile ID and address.
- Migration creates a new derived reference and preserves lineage to the old reference.

```text
MIGRATION != SILENT_REWRITE
NEW_PROFILE != NEW_TRUTH
```

Consumers may support several profile versions simultaneously. They must not guess how an unknown profile maps onto a known one.
