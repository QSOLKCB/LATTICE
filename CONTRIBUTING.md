# Contributing

Keep LATTICE small, deterministic and inspectable.

Before changing a profile, address grammar or traversal:

1. state whether the change is compatible or version-breaking;
2. preserve historical profile IDs;
3. add/update conformance tests;
4. prove traversal bijection for any new top-level traversal;
5. keep coordinates bounded and parsing fail-closed;
6. do not attach truth/evidence authority to geometry;
7. run `python3 tools/validate_lattice.py` and the unittest suite.

Payload codecs, semantic search and private corpus content belong in their respective consumer repositories, not here.
