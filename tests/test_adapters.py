import json
import unittest
from pathlib import Path

from lattice.adapters import (
    qsol_ark_recovery_manifest,
    qsol_corpus_address_reference,
    validate_qsol_control_contract,
)
from lattice.core import LatticeValidationError

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "conformance" / "consumer-adapters-v1.json"


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_qsol_control_contract_conforms(self):
        case = self.fixture["qsol_control"]
        self.assertEqual(validate_qsol_control_contract(case["input"]), case["expected"])

    def test_qsol_control_semantic_drift_fails_closed(self):
        case = json.loads(json.dumps(self.fixture["qsol_control"]["input"]))
        case["axes"]["y"]["values"]["0"] = "true"
        with self.assertRaisesRegex(LatticeValidationError, "semantic mismatch"):
            validate_qsol_control_contract(case)

    def test_qsol_corpus_record_becomes_payload_free_reference(self):
        case = self.fixture["qsol_corpus"]
        actual = qsol_corpus_address_reference(case["input"], case["address"])
        self.assertEqual(actual, case["expected"])
        self.assertNotIn("payload", actual)
        self.assertEqual(actual["content_ref"], case["input"]["record_id"])

    def test_qsol_ark_recovery_manifest_preserves_authority_boundary(self):
        case = self.fixture["qsol_ark"]
        actual = qsol_ark_recovery_manifest(case["input"])
        self.assertEqual(actual, case["expected"])
        self.assertEqual(actual["lattice_authority"], "storage-only")
        self.assertEqual(actual["recovery_authority"], "QSOL-ARK")

    def test_qsol_ark_rejects_unknown_stage(self):
        entry = dict(self.fixture["qsol_ark"]["input"][0])
        entry["recovery_stage"] = "stage.99.magic"
        with self.assertRaisesRegex(LatticeValidationError, "unsupported QSOL-ARK recovery stage"):
            qsol_ark_recovery_manifest([entry])


if __name__ == "__main__":
    unittest.main()
