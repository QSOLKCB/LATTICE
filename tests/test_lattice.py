import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from lattice.core import (
    ADDRESS_PATTERN,
    MAX_ADDRESS_LENGTH,
    MAX_RECURSIVE_DEPTH,
    PHI_STRIDE,
    LatticeParseError,
    LatticeValidationError,
    address_for_roles,
    describe_address,
    lexicographic_cells,
    parse_address,
    phi_stride_cells,
    traversal_cells,
)

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "lattice_validator",
    ROOT / "tools" / "validate_lattice.py",
)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


class LatticeTests(unittest.TestCase):
    def test_repository_contracts_validate(self):
        report = validator.validate()
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["top_level_cells"], 27)
        self.assertEqual(report["phi_stride"], 17)
        self.assertEqual(report["address_pattern"], ADDRESS_PATTERN)
        self.assertEqual(report["max_address_length"], MAX_ADDRESS_LENGTH)

    def test_lexicographic_profile_has_exactly_27_unique_cells(self):
        cells = lexicographic_cells()
        self.assertEqual(len(cells), 27)
        self.assertEqual(len(set(cells)), 27)
        self.assertEqual(cells[0], "L[0,0,0]")
        self.assertEqual(cells[-1], "L[2,2,2]")

    def test_all_top_level_addresses_round_trip(self):
        for cell in lexicographic_cells():
            parsed = parse_address(cell)
            self.assertEqual(len(parsed), 1)
            x, y, z = parsed[0]
            self.assertEqual(cell, f"L[{x},{y},{z}]")

    def test_phi_stride_visits_every_cell_exactly_once(self):
        indices = tuple((PHI_STRIDE * n) % 27 for n in range(27))
        self.assertEqual(PHI_STRIDE, 17)
        self.assertEqual(len(indices), 27)
        self.assertEqual(len(set(indices)), 27)
        self.assertEqual(set(indices), set(range(27)))

        cells = phi_stride_cells()
        self.assertEqual(len(cells), 27)
        self.assertEqual(set(cells), set(lexicographic_cells()))
        self.assertEqual(cells[0], "L[0,0,0]")
        self.assertEqual(cells[1], "L[1,2,2]")

    def test_role_mapping_is_explicit(self):
        self.assertEqual(
            address_for_roles("question", "derived", "current"),
            "L[0,1,0]",
        )
        self.assertEqual(
            address_for_roles("response", "derived", "current"),
            "L[1,1,0]",
        )
        self.assertEqual(
            address_for_roles("evidence", "observed", "recovery"),
            "L[2,0,2]",
        )

    def test_recursive_address_is_bounded(self):
        address = "/".join(["L[0,0,0]"] * MAX_RECURSIVE_DEPTH)
        self.assertEqual(len(address), MAX_ADDRESS_LENGTH)
        self.assertEqual(len(parse_address(address)), MAX_RECURSIVE_DEPTH)

        too_deep = address + "/L[0,0,0]"
        with self.assertRaisesRegex(LatticeParseError, "depth"):
            parse_address(too_deep)

        two_segments = "L[0,0,0]/L[1,1,1]"
        with self.assertRaisesRegex(LatticeParseError, "depth"):
            parse_address(two_segments, max_depth=1)

    def test_untrusted_parser_rejects_adversarial_input(self):
        malicious = (
            "L[3,0,0]",
            "L[0,0,0]\x00",
            "L[0,0,0]\n",
            "L[0,0,0]%2FL[1,1,1]",
            "../L[0,0,0]",
            r"L[0,0,0]\/L[1,1,1]",
            "L[0,0,0]//L[1,1,1]",
            "L[0,0,0]/../L[1,1,1]",
            "Ｌ[0,0,0]",
            "L[0,0,0]" + "A" * 10000,
        )
        for address in malicious:
            with self.subTest(address=repr(address)):
                with self.assertRaises(LatticeParseError):
                    parse_address(address)

    def test_unknown_traversal_fails_closed(self):
        with self.assertRaisesRegex(LatticeValidationError, "unsupported traversal"):
            traversal_cells("qsol.magic-27/9000")

    def test_description_has_no_truth_authority(self):
        desc = describe_address("L[2,0,0]")
        self.assertEqual(desc["authority"], "storage-only")
        self.assertFalse(desc["literal_geometric_claim"])
        self.assertEqual(desc["segments"][0]["information_role"], "evidence")
        self.assertEqual(desc["segments"][0]["epistemic_role"], "observed")

    def test_reference_rejects_unknown_profile(self):
        fixture = validator.load_json(ROOT / "examples" / "lattice-reference.valid.json")
        fixture["profile_id"] = "qsol-unknown/99"
        with self.assertRaisesRegex(LatticeValidationError, "unsupported lattice profile"):
            validator.validate_reference(fixture)

    def test_reference_rejects_payload_and_authority_like_extras(self):
        fixture = validator.load_json(ROOT / "examples" / "lattice-reference.valid.json")
        for key, value in (
            ("payload", {"secret": "not a lattice concern"}),
            ("confidence", 1.0),
            ("truth_score", 1),
        ):
            candidate = dict(fixture)
            candidate[key] = value
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    LatticeValidationError,
                    "unsupported fields",
                ):
                    validator.validate_reference(candidate)

    def test_cli_invalid_reference_is_structured_and_nonzero(self):
        fixture = validator.load_json(ROOT / "examples" / "lattice-reference.valid.json")
        fixture["payload"] = {"no": "payloads"}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "invalid.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "tools/validate_lattice.py", "--reference", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 1)
        error = json.loads(result.stderr.strip().splitlines()[-1])
        self.assertEqual(error["status"], "error")
        self.assertEqual(error["error_type"], "LatticeValidationError")

    def test_cli_valid_reference_is_structured_and_zero(self):
        result = subprocess.run(
            [
                sys.executable,
                "tools/validate_lattice.py",
                "--reference",
                "examples/lattice-reference.valid.json",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "valid")


if __name__ == "__main__":
    unittest.main()
