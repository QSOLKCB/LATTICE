# LATTICE

**REMEMBERS STRUCTURE.**

LATTICE is the public, dependency-free reference protocol and implementation for QSOL's logical 3×3×3 memory structure.

It defines **where a record may be structurally referenced**, not whether that record is true, important, authoritative, conscious, or physically located in a geometric object.

```text
QSOL-CONTROL  OPERATES
QSOL-CORPUS   PRESERVES INTERACTION CORPUS
LATTICE       REMEMBERS STRUCTURE
QSOL-ARK      SURVIVES
```

## Profile

Canonical profile:

```text
qsol-3x3x3-sierpinski-derived-memory/1
```

Exactly 27 top-level cells:

```text
L[x,y,z]

x = information role
    0 question
    1 response
    2 evidence

y = epistemic role
    0 observed
    1 derived
    2 unresolved

z = temporal role
    0 current
    1 historical
    2 recovery
```

Examples:

```text
L[0,1,0]  derived/current question
L[1,1,0]  derived/current response
L[2,0,0]  observed/current evidence reference
L[2,0,2]  observed/recovery evidence/recovery reference
```

Bounded recursive addressing is represented as:

```text
L[2,1,0]/L[0,2,1]
```

## Traversals

Two deterministic top-level traversal profiles are implemented:

```text
qsol.lexicographic-27/1
qsol.phi-stride-27/1
```

The optional phi-derived traversal uses the fixed integer protocol constant:

```text
stride = 17
index(n) = (17 * n) mod 27
```

Because `gcd(17,27)=1`, all 27 cells are visited exactly once before repetition. Runtime traversal uses integer arithmetic only.

## Migration contract

Historical address identity is always the pair:

```text
(profile_id, address)
```

Unknown profile majors fail closed. Additive descriptive metadata is compatible only when it does not change the profile ID or semantic fingerprint. Migration emits a derived target reference while retaining the complete source reference and source identity.

See `docs/PROFILE-COMPATIBILITY.md`, `protocol/profile-compatibility.json`, `schema/lattice-migration.schema.json`, and `lattice/migration.py`.

```text
MIGRATION != SILENT_REWRITE
ADDRESS_IDENTITY = PROFILE_ID + ADDRESS
```

## Consumer adapters

`lattice/adapters.py` provides narrow adapters for:

- QSOL-CONTROL lattice-contract conformance;
- QSOL-CORPUS immutable `record_id` to payload-free LATTICE reference projection;
- QSOL-ARK recovery indexing manifests with recovery authority left in ARK.

The frozen language-neutral fixture is `conformance/consumer-adapters-v1.json`.

## Hard boundaries

```text
GEOMETRY != TRUTH
POSITION != IMPORTANCE
CELL != AUTHORITY
STORED != TRUE
MEMORY != EVIDENCE
TRAVERSAL != PHYSICAL_LAW
LATTICE_REFERENCE != CONTENT_ID
PROFILE_COMPATIBILITY != EPISTEMIC_AUTHORITY
CONTROL_ADAPTER != CONTROL_PAYLOAD_CODEC
ARK_RECOVERY_AUTHORITY != LATTICE_AUTHORITY
THEOREM_ABOUT_TRAVERSAL != THEOREM_ABOUT_TRUTH
```

"Sierpinski-derived" is a design/profile name. This repository does not claim the memory structure is a literal physical fractal, cognitive anatomy, or empirical model of the universe.

## Reference implementations

### Python

Python 3.11+, standard library only:

```python
from lattice import address_for_roles, phi_stride_cells

print(address_for_roles("response", "derived", "current"))
# L[1,1,0]

print(phi_stride_cells()[:3])
```

### JavaScript

A dependency-free Node.js implementation independently regenerates the canonical conformance vector and SHA-256 profile fingerprint:

```bash
node implementations/javascript/verify_conformance.js
```

### Rust

A standard-library-only Rust implementation independently regenerates the same 27-cell profile, traversal, strict recursive-address parser, canonical JSON payload, and SHA-256 fingerprint. Its emitted record is compared byte-semantically with the frozen JSON fixture:

```bash
python3 tools/verify_rust_conformance.py
```

The CI verifier pins Rust `1.96.1` rather than following a moving toolchain channel.

### Lean

The Lean specification proves a real protocol invariant rather than mirroring the whole codebase. `implementations/lean/Lattice.lean` proves that the fixed `17 mod 27` traversal is coprime, has length 27, contains no duplicate indices, and reduces to the exact published index order.

```bash
lean implementations/lean/Lattice.lean
```

Lean is pinned by `lean-toolchain`. See `docs/FORMAL-INVARIANTS.md` for the proof boundary.

## Validation

```bash
python3 tools/quality_gate.py
python3 tools/validate_lattice.py
python3 tools/validate_integrations.py
node implementations/javascript/verify_conformance.js
python3 tools/verify_rust_conformance.py
lean implementations/lean/Lattice.lean
python3 -m unittest discover -s tests -v
```

## Roadmap status

All implementation phases in `ROADMAP.md` are complete. The deferred/prohibited-by-default section remains an enduring scope boundary, not unfinished work.

## Relationship to CONTROL

QSOL-CONTROL may use this profile for memory references and may define reversible projections such as DNA/codon encodings over a traversal. Those payload codecs remain CONTROL contracts; LATTICE owns the reusable structural address/traversal semantics.

## License

MPL-2.0.
