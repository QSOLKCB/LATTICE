# Security

LATTICE contains no credentials and is intended to remain safe for public use. Its security concerns are mostly **parser confinement, resource bounds, and authority containment**.

## Untrusted addresses

Treat every external lattice address as untrusted input.

Implementations must:

- reject malformed syntax;
- reject coordinates outside `0..2`;
- reject empty path segments;
- enforce the declared recursion-depth limit;
- avoid evaluating address text as code;
- never use an unvalidated address directly as a filesystem path.

## Resource bounds

Recursive addresses are capped at eight segments in the bootstrap profile. Consumers may adopt stricter local limits but must not silently reinterpret longer addresses.

## Authority containment

A malicious or malformed record must not gain authority by choosing a special coordinate.

```text
CELL != AUTHORITY
POSITION != IMPORTANCE
GEOMETRY != TRUTH
```

## Traversal parameters

Traversal IDs and parameters are versioned protocol data. Consumers must validate the fixed stride/modulus for known profiles and fail closed when they do not match.

The phi-stride traversal is not an encryption mechanism and provides no confidentiality.

## Payload boundary

LATTICE does not own arbitrary payload deserialization. Consumers should store content IDs/references separately and validate their own payload formats.
