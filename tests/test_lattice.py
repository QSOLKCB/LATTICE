import importlib.util
import unittest
from pathlib import Path

from lattice.core import (
    MAX_RECURSIVE_DEPTH,
    PHI_STRIDE,
    LatticeError,
    address_for_roles,
    describe_address,
    lexicographic_cells,
    parse_address,
    phi_stride_cells,
    traversal_cells,
)

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("lattice_validator", ROOT / "tools" / "validate_lattice.py")
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


class LatticeTests(unittest.TestCase):
    def test_repository_contracts_validate(self):
        report = validator.validate()
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["top_level_cells"], 27)
        self.assertEqual(report["phi_stride"], 17)

    def test_lexicographic_profile_has_exactly_27_unique_cells(self):
        cells = lexicographic_cells()
        self.assertEqual(len(cells), 27)
        self.assertEqual(len(set(cells)), 27)
        self.assertEqual(cells[0], "L[0,0,0]")
        self.assertEqual(cells[-1], "L[2,2,2]")

    def test_phi_stride_visits_every_cell_exactly_once(self):
        cells = phi_stride_cells()
        self.assertEqual(PHI_STRIDE, 17)
        self.assertEqual(len(cells), 27)
        self.assertEqual(set(cells), set(lexicographic_cells()))
        self.assertEqual(cells[0], "L[0,0,0]")
        self.assertEqual(cells[1], "L[1,2,2]")

    def test_role_mapping_is_explicit(self):
        self.assertEqual(address_for_roles("question", "derived", "current"), "L[0,1,0]")
        self.assertEqual(address_for_roles("response", "derived", "current"), "L[1,1,0]")
        self.assertEqual(address_for_roles("evidence", "observed", "recovery"), "L[2,0,2]")

    def test_recursive_address_is_bounded(self):
        address = "/".join(["L[0,0,0]"] * MAX_RECURSIVE_DEPTH)
        self.assertEqual(len(parse_address(address)), MAX_RECURSIVE_DEPTH)
        too_deep = address + "/L[0,0,0]"
        with self.assertRaisesRegex(LatticeError, "depth"):
            parse_address(too_deep)

    def test_invalid_coordinate_fails_closed(self):
        with self.assertRaises(LatticeError):
            parse_address("L[3,0,0]")

    def test_unknown_traversal_fails_closed(self):
        with self.assertRaisesRegex(LatticeError, "unsupported"):
            traversal_cells("qsol.magic-27/9000")

    def test_description_has_no_truth_authority(self):
        desc = describe_address("L[2,0,0]")
        self.assertEqual(desc["authority"], "storage-only")
        self.assertFalse(desc["literal_geometric_claim"])
        self.assertEqual(desc["segments"][0]["information_role"], "evidence")
        self.assertEqual(desc["segments"][0]["epistemic_role"], "observed")


if __name__ == "__main__":
    unittest.main()
