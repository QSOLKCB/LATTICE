# Security

LATTICE contains no credentials and is intended to remain safe for public use. Its security concerns are mostly **parser confinement, resource bounds, and authority containment**.

## Untrusted addresses

Treat every external lattice address as untrusted input.

Implementations must:

- reject malformed syntax;
- reject coordinates outside `0..2`;
- reject empty path segments;
- reject control characters, percent-encoded separators, path-traversal tokens and escape syntax;
- enforce the declared recursion-depth and address-length limits;
- avoid evaluating address text as code;
- never use an unvalidated address directly as a filesystem path.

The canonical bootstrap grammar has no escape mechanism. A valid segment is exactly `L[x,y,z]` with each coordinate in `0..2`. Recursive segments are separated only by a literal `/`.

## Resource bounds

Recursive addresses are capped at eight segments and 71 characters in the bootstrap profile. Parsing checks those limits before segment conversion. Consumers may adopt stricter local limits but must not silently reinterpret longer addresses.

## Authority containment

A malicious or malformed record must not gain authority by choosing a special coordinate.

```text
CELL != AUTHORITY
POSITION != IMPORTANCE
GEOMETRY != TRUTH
```

## Traversal parameters

Traversal IDs and parameters are versioned protocol data. Consumers must validate the fixed stride/modulus for known profiles and reject inputs when they do not match.

The phi-stride traversal is not an encryption mechanism and provides no confidentiality.

## Payload boundary

LATTICE references are structural metadata, not payload containers. The core reference contract rejects unsupported fields, including consumer-specific payload or authority-like metadata. Consumers should store content IDs/references separately and validate their own payload formats.
