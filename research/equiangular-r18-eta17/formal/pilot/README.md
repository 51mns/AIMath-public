# R18 eta17 formal-proof pilot

This pilot tests the formal-proof policy on an already `INDEPENDENTLY_REPRODUCED` AIMath claim without changing its mathematical level or claiming that the full Seidel-matrix theorem has been formalised.

## Formalised scope

The accepted Python verifier reconstructs two exact integer polynomials at the final characteristic-polynomial deck gate:

- the quotient `p'/F`, with coefficients `[59, -2242, 31388, -190974, 422985]` in descending order;
- `59 Q0`, with coefficients `[59, -2242, 31388, -191278, 426393]` in descending order.

The Lean pilot freezes these as integer-valued polynomial expressions and proves that they cannot be identical, since they already disagree at `x = 0`.

## Explicit trust boundary

Lean does **not** yet prove:

- the existence or completeness of the 64 endpoint candidates;
- the type-2 divisibility filter;
- uniqueness of `Q0`;
- derivation of the quotient coefficients from `p'/F`;
- the Seidel spectral/deletion lemmas that make polynomial identity necessary;
- the full claim that no `59 x 59` Seidel matrix has the frozen spectrum.

Those remain covered by the existing exact verifier and independent mathematical review. Therefore this pilot is a kernel-checked **subtheorem**, not `KERNEL_PASS` for the whole Claim.

## Frozen statement / candidate proof

- `R18Eta17FormalPilot/Statement.lean` contains definitions and the frozen proposition only.
- `R18Eta17FormalPilot/Proof.lean` imports that statement and supplies the proof.
- `R18Eta17FormalPilot/FinalCheck.lean` reports the axioms of the final theorem.
- `theorems/THM-EQUIANGULAR-R18-ETA17-DECK-MISMATCH.json` records theorem-DAG/evidence metadata.

Toolchain for the pilot check: Lean `4.33.1`, Lean core only, no Mathlib.

The branch-level pilot verifier additionally runs the Lean kernel build, axiom audit, `leanchecker`, and `nanoda`. The temporary branch workflow is not intended to become part of public `main` merely to run this experiment.
