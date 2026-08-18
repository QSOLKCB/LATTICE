import json
import unittest
from pathlib import Path

from lattice.conformance import canonical_json_bytes, conformance_record, profile_fingerprint

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "conformance" / "profile-v1.json"
EXPECTED = "sha256:6e7c4a9a781d552a2b561d334a8435c12efe2908fcd24a0f152935aded555bcf"


class ConformanceTests(unittest.TestCase):
    def test_runtime_matches_canonical_fixture_exactly(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(conformance_record(), fixture)

    def test_profile_fingerprint_is_pinned(self):
        self.assertEqual(profile_fingerprint(), EXPECTED)

    def test_canonical_json_bytes_recipe_is_pinned(self):
        self.assertEqual(
            canonical_json_bytes({"z": 2, "a": "φ", "nested": {"b": 1, "a": 0}}),
            b'{"a":"\xcf\x86","nested":{"a":0,"b":1},"z":2}',
        )

    def test_fixture_has_two_27_cell_bijections(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        lex = fixture["lexicographic_cells"]
        phi = fixture["phi_stride_cells"]
        self.assertEqual(len(lex), 27)
        self.assertEqual(len(set(lex)), 27)
        self.assertEqual(len(phi), 27)
        self.assertEqual(len(set(phi)), 27)
        self.assertEqual(set(phi), set(lex))

    def test_fingerprint_changes_if_semantics_change(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(fixture["fingerprint"], EXPECTED)
        mutated = dict(fixture)
        mutated["phi_stride"] = 16
        self.assertNotEqual(mutated, conformance_record())


if __name__ == "__main__":
    unittest.main()
