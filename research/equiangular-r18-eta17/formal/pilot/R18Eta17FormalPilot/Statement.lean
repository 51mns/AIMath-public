-- SPDX-FileCopyrightText: 2026 AIMath contributors
-- SPDX-License-Identifier: CC0-1.0

namespace AIMath.R18Eta17

/--
The exact quotient polynomial `p'/F` reconstructed by the accepted Python
verifier, evaluated at an integer `x`. Coefficients are low-trust inputs to
this formal pilot: their derivation from the Seidel/deck argument remains
outside Lean in this phase.
-/
def ratioEval (x : Int) : Int :=
  59 * x^4 - 2242 * x^3 + 31388 * x^2 - 190974 * x + 422985

/--
The exact polynomial `59 * Q₀` reconstructed by the accepted Python verifier,
evaluated at an integer `x`.
-/
def fiftyNineQ0Eval (x : Int) : Int :=
  59 * x^4 - 2242 * x^3 + 31388 * x^2 - 191278 * x + 426393

/--
Frozen formal pilot target: the two reconstructed integer polynomials are not
identical as functions on `Int`.

This is only the final deck-mismatch bridge. It does not formalise the
derivation of the candidate quartic, the type-2 filter, the Seidel matrix
hypotheses, or the implication from the full spectral problem to this bridge.
-/
def DeckIdentityImpossible : Prop :=
  ¬ ∀ x : Int, ratioEval x = fiftyNineQ0Eval x

end AIMath.R18Eta17
