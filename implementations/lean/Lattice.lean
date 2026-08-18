import Std

namespace QSOL.Lattice

/-- The exact integer index traversal used by `qsol.phi-stride-27/1`. -/
def phiOrder : List Nat :=
  (List.range 27).map (fun n => (17 * n) % 27)

/-- The published stride and modulus are coprime. -/
theorem phiStrideCoprime : Nat.gcd 17 27 = 1 := by
  decide

/-- The traversal has exactly one entry for each top-level lattice cell. -/
theorem phiOrderLength : phiOrder.length = 27 := by
  decide

/-- No top-level index repeats before the 27-step traversal completes. -/
theorem phiOrderNodup : phiOrder.Nodup := by
  decide

/-- The formalized algorithm reduces to the canonical published index order. -/
theorem phiOrderExact :
    phiOrder =
      [0, 17, 7, 24, 14, 4, 21, 11, 1, 18, 8, 25, 15, 5,
       22, 12, 2, 19, 9, 26, 16, 6, 23, 13, 3, 20, 10] := by
  decide

end QSOL.Lattice
