import json
import unittest
from copy import deepcopy
from pathlib import Path

from lattice.core import PROFILE_ID, LatticeValidationError
from lattice.migration import (
    current_profile_descriptor,
    migrate_reference,
    validate_migration_manifest,
    validate_profile_descriptor,
)

ROOT = Path(__file__).resolve().parents[1]


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


if __name__ == "__main__":
    unittest.main()
