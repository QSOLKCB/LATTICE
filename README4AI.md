{
  "protocol": "QSOL-LATTICE/0.1",
  "role": "logical-memory-structure",
  "verb": "REMEMBERS",
  "authority": "storage-only",
  "profile": "qsol-3x3x3-sierpinski-derived-memory/1",
  "top_level_cell_count": 27,
  "literal_geometric_claim": false,
  "axes": {
    "x": {"name": "information_role", "values": {"0": "question", "1": "response", "2": "evidence"}},
    "y": {"name": "epistemic_role", "values": {"0": "observed", "1": "derived", "2": "unresolved"}},
    "z": {"name": "temporal_role", "values": {"0": "current", "1": "historical", "2": "recovery"}}
  },
  "address_grammar": "L[x,y,z](\/L[x,y,z])*",
  "max_recursive_depth": 8,
  "traversals": {
    "qsol.lexicographic-27/1": {"kind": "lexicographic", "cell_count": 27},
    "qsol.phi-stride-27/1": {
      "kind": "fixed-modular-stride",
      "stride": 17,
      "modulus": 27,
      "rule": "cell_index(n)=(17*n) mod 27"
    }
  },
  "boundaries": [
    "GEOMETRY != TRUTH",
    "POSITION != IMPORTANCE",
    "CELL != AUTHORITY",
    "STORED != TRUE",
    "MEMORY != EVIDENCE",
    "TRAVERSAL != PHYSICAL_LAW",
    "LATTICE_REFERENCE != CONTENT_ID"
  ]
}
