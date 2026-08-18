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

## Python style

The repository intentionally keeps runtime and validation dependencies in the standard library. CI therefore uses the deterministic local quality gate rather than adding multiple formatter/linter packages to the protocol surface. Keep Python typed, documented, free of tabs/trailing whitespace, and free of code-evaluation primitives in parser/validator paths.

Payload codecs, semantic search and private corpus content belong in their respective consumer repositories, not here.
