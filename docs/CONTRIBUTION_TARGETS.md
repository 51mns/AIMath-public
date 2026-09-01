# Public contribution targets

This page tells an external contributor what can actually move AIMath forward. Read `FAILED_ROUTES.md` before starting a proof route.

## High-value contribution types

Across all areas, useful contributions include:

- an independent proof or a simpler alternative proof of a listed claim;
- a concrete counterexample to a proof candidate;
- an independent reproduction failure with exact inputs/environment;
- a primary-source literature match or stronger theorem that changes the novelty/importance assessment;
- a genuinely new structural lemma that crosses a documented HOLD/reopen condition;
- a minimal exact verifier or negative control that improves reproducibility without copying the writer implementation.

## Local TP2 — universal proof remains open

Current public status: `PROOF_CANDIDATE`.

Exact target: prove or refute the adjacent determinant inequality in `research/local-tp2/STATEMENT.md`, including its terminal index and degree orientation.

Already known:

- substantial finite exact evidence is positive;
- several proof architectures are blocked/no-go and recorded in `FAILED_ROUTES.md`;
- finite depth alone cannot prove the universal statement.

What would count as progress:

- a new theorem-native recurrence/positivity mechanism covering all Farey depth;
- a valid counterexample under the exact frozen orientation;
- a source theorem that directly implies the frozen determinant inequality.

Do not reopen merely by increasing denominator bound, quotient ansatz degree or a previously closed far-minor architecture.

## Equiangular lines in R^18

Accepted public result: the eta=17/simple-11 singleton spectrum is impossible.

What is **not** proved: nonexistence of every hypothetical 59-line system or `N(18)<=58`.

Useful contributions:

- independently verify the public deck argument;
- find a different general obstruction that applies beyond the excluded singleton spectrum;
- provide a primary-source theorem that collapses multiple remaining spectral possibilities at once.

Do not cite private/unmerged experimental branches as canonical results.

## Dittert n=5

Accepted public result: the exact two-zero matching support orbit is excluded.

What is **not** proved: the full `n=5` conjecture.

Useful contributions:

- an independent alternative proof of the support-class exclusion;
- a new structural argument covering a genuinely broader zero-pattern class;
- source-backed reductions that close more than one residual support type at once.

Do not infer exclusion of other zero patterns from the public Z2 theorem.

## B3RCC / antipodal partial cubes

The campaign is currently `PORTFOLIO_HOLD`, despite several accepted theorems.

Read `research/b3rcc-apc/CAMPAIGN_CLOSEOUT.md` before starting new work.

A reopen-quality contribution would provide:

- a concrete external APC family with an independently proved vertex cap that makes the all-rank bound load-bearing;
- a source-backed local-to-global theorem connecting high minimum degree to order/isometric dimension;
- another explicit external problem that genuinely requires the all-rank bound;
- a materially new mechanism not reducible to “enumerate the next rank”.

Broad rank-6/rank-7 enumeration by itself is not a priority.

## Gyoda 89

The number-only v4 collision and four mathematical residue classes are public and reproducible.

Useful contributions:

- primary-source/historical comparison establishing whether the exact four-class extension appeared elsewhere;
- analysis of stronger position-aware reformulations without conflating them with the refuted number-only statement;
- independent verification of the recurrence/family argument.

Raw author correspondence is not needed and should not be requested for mathematical verification.

## Fixed-433 / Springborn

The fixed-433 obstruction and exact existing-theory identification are public packages.

Useful contributions are mainly literature/placement work:

- determine whether the fixed affine transformation or CRT representative identity appears explicitly in prior literature;
- supply a stronger classification that subsumes the public result;
- independently verify source normalization and formula correspondence.

Do not claim novelty from the current bounded audit.

## Lonely Runner R2

The generic two-pivot residual-capacity theorem is accepted, but the measured scaling route is closed as `NO_GO_FOR_SCALING`.

Useful contributions:

- a mathematically different pruning mechanism with a credible bounded benchmark advantage;
- a theoretical compression that preserves R2 safety but changes its cost model substantially;
- a literature match for the generic two-pivot set-cover bound.

Simply escalating to R3/R4/R5 without a new complexity argument is not a priority.

## AFES

The narrow bounded semantic claim is accepted. Strict scalar canonical encoding remains a proof candidate because of the documented bool/int edge.

A focused contribution can:

- repair strict integer-vs-boolean scalar validation at every rational-valued entry point;
- add boolean negative controls;
- independently re-review only that repaired scalar/canonicality surface.

Do not broaden this into claims of total equality, total nonzero recognition or full field closure.

## Review standard for proposed promotions

Any contribution intended to change a claim level should make it possible for a separate reviewer to reproduce the mathematical reasoning without trusting the contributor's conclusion or generated output. See `EVIDENCE_POLICY.md` and `CONTRIBUTING.md`.
