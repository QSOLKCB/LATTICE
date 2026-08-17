# AGENTS.md

Machine guidance for LATTICE.

## Role

LATTICE **REMEMBERS STRUCTURE**. It owns versioned logical address/traversal semantics only.

## Hard rules

1. Never treat a lattice cell as truth, authority, confidence, importance or evidence strength.
2. Never infer content identity from position; references and content IDs remain separate.
3. Keep the top-level profile exactly 3×3×3 / 27 cells unless a new MAJOR profile is introduced.
4. Keep traversal IDs versioned. Changing traversal meaning requires a new traversal/profile version.
5. Use integer arithmetic for fixed modular traversals.
6. Reject coordinates outside 0..2.
7. Reject recursive addresses beyond the declared depth limit.
8. Preserve old profile IDs during migrations; never silently reinterpret historical addresses.
9. Do not move CONTROL-specific payload codecs into this repository.
10. Do not attach epistemic authority to the word `Sierpinski`, `phi`, `DNA`, or any other design lineage term.

```text
GEOMETRY != TRUTH
POSITION != IMPORTANCE
CELL != AUTHORITY
MEMORY != EVIDENCE
```
