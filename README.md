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

## Hard boundaries

```text
GEOMETRY != TRUTH
POSITION != IMPORTANCE
CELL != AUTHORITY
STORED != TRUE
MEMORY != EVIDENCE
TRAVERSAL != PHYSICAL_LAW
LATTICE_REFERENCE != CONTENT_ID
```

"Sierpinski-derived" is a design/profile name. This repository does not claim the memory structure is a literal physical fractal, cognitive anatomy, or empirical model of the universe.

## Reference implementation

Python 3.11+, standard library only:

```python
from lattice import address_for_roles, phi_stride_cells

print(address_for_roles("response", "derived", "current"))
# L[1,1,0]

print(phi_stride_cells()[:3])
```

Validation:

```bash
python3 tools/validate_lattice.py
python3 -m unittest discover -s tests -v
```

## Relationship to CONTROL

QSOL-CONTROL may use this profile for memory references and may define reversible projections such as DNA/codon encodings over a traversal. Those payload codecs remain CONTROL contracts; LATTICE owns the reusable structural address/traversal semantics.

## License

MPL-2.0.
