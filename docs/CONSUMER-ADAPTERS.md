# Consumer adapters

LATTICE adapters translate only address/reference structure. They do not import consumer payload semantics or authority.

## QSOL-CONTROL

`validate_qsol_control_contract()` checks that CONTROL's public lattice contract agrees with the canonical v1 profile: 27 cells, the exact axis meanings, `storage-only` authority, and no literal geometric claim. The result is a conformance receipt, not a CONTROL payload codec.

```text
CONTROL_ADAPTER != CONTROL_PAYLOAD_CODEC
```

## QSOL-CORPUS

`qsol_corpus_address_reference()` takes an immutable CORPUS `record_id` and an explicit LATTICE address. It emits `qsol-lattice-reference/1` with the CORPUS SHA-256 record ID stored only as `content_ref`.

No conversation text, attachment bytes, provider-private reasoning, or CORPUS authority is copied into LATTICE.

```text
CORPUS_RECORD_ID != LATTICE_ADDRESS
LATTICE_REFERENCE != CORPUS_PAYLOAD
```

## QSOL-ARK

`qsol_ark_recovery_manifest()` emits a recovery-index manifest whose entries contain ARK artifact references plus LATTICE references. LATTICE remains `storage-only`; recovery authority remains explicitly owned by QSOL-ARK.

```text
ARK_RECOVERY_AUTHORITY != LATTICE_AUTHORITY
RECOVERY_INDEX != RECOVERY_PROOF
```

## Conformance

`conformance/consumer-adapters-v1.json` is the language-neutral fixture for all three adapters. `tools/validate_integrations.py` and the unittest suite recompute each expected output.

The adapters are intentionally narrow. If a future consumer needs payload codecs, distributed storage semantics, truth scoring, or evidence ranking, those remain consumer responsibilities and must not be smuggled into LATTICE by calling them an adapter.
