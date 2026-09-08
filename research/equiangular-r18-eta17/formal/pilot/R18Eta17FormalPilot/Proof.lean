-- SPDX-FileCopyrightText: 2026 AIMath contributors
-- SPDX-License-Identifier: CC-BY-4.0

import R18Eta17FormalPilot.Statement

namespace AIMath.R18Eta17

/-- The two reconstructed deck polynomials already disagree at `x = 0`. -/
theorem deckMismatchAtZero : ratioEval 0 ≠ fiftyNineQ0Eval 0 := by
  decide

/-- Therefore the reconstructed deck identity cannot hold for every integer. -/
theorem deckIdentityImpossible : DeckIdentityImpossible := by
  intro h
  exact deckMismatchAtZero (h 0)

end AIMath.R18Eta17
