<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# AFRD post-signal novelty / reduction audit

This audit is dormant until a frozen candidate passes the predeclared held-out utility gate.

## Order of operations

1. Freeze candidate hashes, hidden-result hashes, evaluator version, and resource accounting.
2. Search primary literature and authoritative implementations using terms derived from the frozen candidate's actual state/operation/invariant structure.
3. Ask a separate AI/reviewer to reduce `X(N)` to known arithmetic, algorithmic, probabilistic, coding, representation, or optimisation constructions without assuming the candidate is new.
4. Perform symbolic simplification and exact small-instance equivalence tests.
5. Compare candidate invariants and updates against known gcd/Fermat/Pollard/ECM/sieve/representation families and any newly located closer prior work.
6. Run adversarial controls: generator swap, temporal holdout, factor-label removal, representation randomisation, reversible re-encoding control, and matched-compute raw-`N` control.
7. Extract any human-readable lemma separately from engineering performance.
8. Only after all above may a novelty audit state more than `NOT_ESTABLISHED`.

## Verdict vocabulary

- `KNOWN_REDUCTION`: candidate is materially equivalent to a known construction under an explicit map.
- `CLOSE_PRIOR_ART`: close literature exists but exact equivalence is unresolved.
- `USEFUL_ENGINEERING_REPRESENTATION`: held-out utility survives, but no new-mathematics claim is made.
- `MATHEMATICAL_LEMMA_CANDIDATE`: an exact lemma has been extracted; independent proof review still required.
- `NOVELTY_NOT_ESTABLISHED`: default unless a sufficiently broad primary-source audit supports a narrower statement.

A finite benchmark result never upgrades an infinite/asymptotic theorem. A writer does not self-award independent reproduction.
