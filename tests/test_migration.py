import json
import unittest
from copy import deepcopy
from pathlib import Path

from lattice.core import PROFILE_ID, LatticeValidationError
from lattice.migration import (
    MAX_MIGRATION_MAPPINGS,
    current_profile_descriptor,
    migrate_reference,
    validate_migration_manifest,
    validate_profile_descriptor,
)

ROOT = Path(__file__).resolve().parents[1]


def _three_segment_address(index: int) -> str:
    cells = [
        f"L[{x},{y},{z}]"
        for x in range(3)
        for y in range(3)
        for z in range(3)
    ]
    digits = []
    value = index
    for _ in range(3):
        digits.append(value % 27)
        value //= 27
    return "/".join(cells[digit] for digit in reversed(digits))


class MigrationTests(unittest.TestCase):
    def test_exact_profile_is_compatible(self):
        report = validate_profile_descriptor(current_profile_descriptor())
        self.assertEqual(report["status"], "compatible")
        self.assertEqual(report["compatibility"], "exact")

    def test_additive_metadata_is_compatible(self):
        descriptor = current_profile_descriptor(
            {"description": "consumer-only description", "labels": ["stable", "v1"]}
        )
        report = validate_profile_descriptor(descriptor)
        self.assertEqual(report["compatibility"], "additive-metadata")

    def test_unknown_major_is_rejected(self):
        descriptor = current_profile_descriptor()
        descriptor["profile_id"] = PROFILE_ID.rsplit("/", 1)[0] + "/2"
        with self.assertRaisesRegex(LatticeValidationError, "unsupported profile major"):
            validate_profile_descriptor(descriptor)

    def test_changed_semantic_fingerprint_is_rejected(self):
        descriptor = current_profile_descriptor()
        descriptor["profile_fingerprint"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(LatticeValidationError, "semantic fingerprint"):
            validate_profile_descriptor(descriptor)

    def test_valid_migration_fixture_preserves_old_and_new_identity(self):
        manifest = json.loads(
            (ROOT / "examples" / "migration.valid.json").read_text(encoding="utf-8")
        )
        report = validate_migration_manifest(manifest)
        self.assertEqual(report["status"], "valid")

        reference = {
            "protocol": "qsol-lattice-reference/1",
            "profile_id": PROFILE_ID,
            "address": "L[2,0,2]",
            "content_ref": "sha256:" + "a" * 64,
            "authority": "storage-only",
        }
        before = deepcopy(reference)
        migrated = migrate_reference(reference, manifest)
        self.assertEqual(reference, before)
        self.assertEqual(migrated["source_reference"], before)
        self.assertEqual(migrated["target_reference"], before)
        self.assertEqual(
            migrated["source_identity"],
            {"profile_id": PROFILE_ID, "address": "L[2,0,2]"},
        )
        self.assertEqual(migrated["source_identity"], migrated["target_identity"])

    def test_unknown_major_migration_fixture_fails_closed(self):
        manifest = json.loads(
            (ROOT / "examples" / "migration.unknown-major.invalid.json").read_text(
                encoding="utf-8"
            )
        )
        with self.assertRaisesRegex(LatticeValidationError, "unsupported profile major"):
            validate_migration_manifest(manifest)

    def test_mapping_count_limit_matches_published_schema(self):
        manifest = json.loads(
            (ROOT / "examples" / "migration.valid.json").read_text(encoding="utf-8")
        )
        manifest["mappings"] = [
            {
                "source_address": _three_segment_address(index),
                "target_address": _three_segment_address(index),
            }
            for index in range(MAX_MIGRATION_MAPPINGS + 1)
        ]
        with self.assertRaisesRegex(LatticeValidationError, "mappings exceed limit"):
            validate_migration_manifest(manifest)

    def test_schema_enumerates_supported_profile_descriptor_pair(self):
        schema = json.loads(
            (ROOT / "schema" / "lattice-migration.schema.json").read_text(encoding="utf-8")
        )
        descriptor = schema["$defs"]["profileDescriptor"]
        variants = descriptor.get("oneOf")
        self.assertEqual(len(variants), 1)
        properties = variants[0]["properties"]
        self.assertEqual(properties["profile_id"]["const"], PROFILE_ID)
        self.assertEqual(
            properties["profile_fingerprint"]["const"],
            current_profile_descriptor()["profile_fingerprint"],
        )


if __name__ == "__main__":
    unittest.main()
