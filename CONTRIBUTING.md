# Contributing

Keep LATTICE small, deterministic and inspectable.

Before changing a profile, address grammar or traversal:

1. state whether the change is compatible or version-breaking;
2. preserve historical profile IDs;
3. add/update conformance and adversarial tests;
4. prove traversal bijection for any new top-level traversal;
5. keep coordinates, address length and recursion bounded and reject invalid inputs deterministically;
6. do not attach truth/evidence authority to geometry;
7. run `python3 tools/quality_gate.py`, `python3 tools/validate_lattice.py`, and the unittest suite.

## Fingerprint compatibility changes

The v1 profile fingerprint is SHA-256 over the canonical UTF-8 JSON bytes returned by `conformance_payload()` using sorted object keys, compact `,`/`:` separators, direct Unicode (`ensure_ascii=false`), rejected NaN/Infinity, and no terminal newline.

When a change alters any fingerprinted semantic field:

1. decide whether the existing profile ID can remain compatible; never silently change the meaning of an existing versioned profile;
2. update the runtime semantics and conformance fixture together;
3. recompute and pin the new fingerprint in `manifest.json`, `README4AI.md`, the fixture, and tests;
4. record the compatibility/migration consequence in `ROADMAP.md` or the relevant migration document;
5. run the complete quality gate, validator, and tests before publication.

A fingerprint match proves profile-byte compatibility only. It does not prove payload identity, truth, importance, or epistemic authority.

## Python style

The repository intentionally keeps runtime and validation dependencies in the standard library. CI therefore uses the deterministic local quality gate rather than adding multiple formatter/linter packages to the protocol surface. Keep Python typed, documented, free of tabs/trailing whitespace, and free of code-evaluation primitives in parser/validator paths.

Payload codecs, semantic search and private corpus content belong in their respective consumer repositories, not here.
