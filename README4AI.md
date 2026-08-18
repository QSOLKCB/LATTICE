{
  "protocol": "QSOL-LATTICE/0.1",
  "role": "logical-memory-structure",
  "verb": "REMEMBERS",
  "authority": "storage-only",
  "profile": "qsol-3x3x3-sierpinski-derived-memory/1",
  "profile_fingerprint": "sha256:6e7c4a9a781d552a2b561d334a8435c12efe2908fcd24a0f152935aded555bcf",
  "conformance_fixture": "conformance/profile-v1.json",
  "conformance_runtime": "lattice/conformance.py",
  "profile_compatibility_contract": "protocol/profile-compatibility.json",
  "migration_runtime": "lattice/migration.py",
  "migration_schema": "schema/lattice-migration.schema.json",
  "migration_fixture": "examples/migration.valid.json",
  "adapter_runtime": "lattice/adapters.py",
  "consumer_conformance_fixture": "conformance/consumer-adapters-v1.json",
  "javascript_reference": "implementations/javascript/lattice.js",
  "javascript_conformance_command": "node implementations/javascript/verify_conformance.js",
  "top_level_cells": 27,
  "fingerprint_serialization": {
    "input": "conformance_payload_without_fingerprint",
    "encoding": "UTF-8",
    "object_key_order": "lexicographic sort_keys=true",
    "separators": [",", ":"],
    "ensure_ascii": false,
    "allow_nan": false,
    "terminal_newline": false,
    "hash": "SHA-256"
  },
  "literal_geometric_claim": false,
  "address_grammar": "L[x,y,z](/L[x,y,z])*",
  "address_pattern": "L\\[[0-2],[0-2],[0-2]\\](?:/L\\[[0-2],[0-2],[0-2]\\]){0,7}",
  "address_escaping": "none",
  "max_recursive_depth": 8,
  "max_address_length": 71,
  "traversals": {
    "qsol.lexicographic-27/1": {
      "kind": "lexicographic",
      "cell_count": 27
    },
    "qsol.phi-stride-27/1": {
      "kind": "fixed-modular-stride",
      "stride": 17,
      "modulus": 27,
      "rule": "cell_index(n)=(17*n) mod 27"
    }
  },
  "compatibility": {
    "unknown_major": "reject",
    "same_profile_same_fingerprint": "compatible",
    "additive_non_semantic_metadata": "compatible",
    "semantic_fingerprint_change": "version-bump-required",
    "historical_identity": "preserve-profile-id-plus-address",
    "silent_rewrite": false
  },
  "consumer_adapters": {
    "QSOL-CONTROL": "validate external lattice contract only",
    "QSOL-CORPUS": "map immutable record_id to content_ref plus explicit lattice address",
    "QSOL-ARK": "build recovery indexing manifest while leaving recovery authority in ARK"
  },
  "boundaries": [
    "GEOMETRY != TRUTH",
    "POSITION != IMPORTANCE",
    "CELL != AUTHORITY",
    "STORED != TRUE",
    "MEMORY != EVIDENCE",
    "TRAVERSAL != PHYSICAL_LAW",
    "LATTICE_REFERENCE != CONTENT_ID",
    "LATTICE_REFERENCE != PAYLOAD",
    "FINGERPRINT_MATCH != TRUTH",
    "PROFILE_COMPATIBILITY != EPISTEMIC_AUTHORITY",
    "MIGRATION != SILENT_REWRITE",
    "ADDRESS_IDENTITY = PROFILE_ID + ADDRESS",
    "CONTROL_ADAPTER != CONTROL_PAYLOAD_CODEC",
    "ARK_RECOVERY_AUTHORITY != LATTICE_AUTHORITY"
  ]
}
