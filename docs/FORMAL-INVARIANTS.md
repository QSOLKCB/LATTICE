# Formal invariants

LATTICE uses formal methods only where they prove a protocol invariant that matters to interoperability.

## Lean scope

`implementations/lean/Lattice.lean` proves concrete properties of the canonical top-level traversal `qsol.phi-stride-27/1`:

1. `Nat.gcd 17 27 = 1`;
2. the generated traversal has length 27;
3. the generated traversal contains no duplicate indices;
4. the algorithm reduces to the exact published canonical order.

Together, the length and no-duplicate results establish the operational invariant needed by the protocol: the 27-step traversal does not revisit a top-level cell before completing the cycle.

The Lean file is intentionally small and pinned by `lean-toolchain`. It does not formalize truth, cognition, evidence authority, physical geometry, or any biological interpretation.

```text
THEOREM_ABOUT_TRAVERSAL != THEOREM_ABOUT_TRUTH
FORMALIZED_GEOMETRY != PHYSICAL_GEOMETRY
POSITION != EPISTEMIC_AUTHORITY
```

## Rust scope

`implementations/rust/lattice.rs` is a standard-library-only systems-language reference implementation. It independently regenerates:

- the 27 lexicographic cells;
- the fixed `17 mod 27` traversal;
- bounded recursive-address parsing;
- the canonical JSON conformance payload;
- SHA-256 for the canonical v1 profile fingerprint.

`tools/verify_rust_conformance.py` compiles the Rust unit tests and executable with the pinned Rust toolchain, then compares the emitted JSON record with `conformance/profile-v1.json`.

## Verification

The repository CI executes both additional implementations. A change is not considered roadmap-complete if either the Rust record diverges from the frozen fixture or the Lean invariant file fails kernel checking.
