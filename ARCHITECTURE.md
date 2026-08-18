# Architecture

```text
                      CONTENT / RECORD ID
                              |
                              | independent reference
                              v
                    +-------------------+
                    |      LATTICE      |
                    |     REMEMBERS     |
                    |     STRUCTURE     |
                    +---------+---------+
                              |
                  +-----------+-----------+
                  |                       |
                  v                       v
            ROLE ADDRESS              TRAVERSAL
             L[x,y,z]           lexicographic / phi-stride
                  |                       |
                  +-----------+-----------+
                              |
                              v
                    VERSIONED PROFILE ID
```

## Cell semantics

The profile is a product of three explicit ternary axes:

```text
X information : question / response / evidence
Y epistemic   : observed / derived / unresolved
Z temporal    : current / historical / recovery
```

This makes each top-level address inspectable rather than opaque.

## Recursive addresses

A record may reference a bounded nested structural path:

```text
L[2,0,1]/L[1,1,0]
```

Recursion is structural refinement only. It does not increase authority or imply physical nesting.

## Traversal layer

Traversal determines an order over the 27 top-level cells. It does not change their meanings.

- `qsol.lexicographic-27/1`: canonical coordinate generation order.
- `qsol.phi-stride-27/1`: fixed modular stride 17 over the lexicographic list.

## Compatibility

Profile/traversal IDs are part of meaning. Consumers must fail closed on unknown major profile versions rather than guessing.

Migration creates new references/projections while preserving the old profile/address identity. Historical addresses are never silently reinterpreted.

## Repository boundaries

- `QSOL-CONTROL`: operational machinery, retrieval, reversible payload projections.
- `QSOL-CORPUS`: private persistent interaction content and Collections.
- `LATTICE`: public structural profile/address/traversal semantics.
- `QSOL-ARK`: preservation/recovery boundary.
