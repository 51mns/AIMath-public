# Local TP2 exact finite baseline

This file records finite evidence only. It is **not** an infinite proof.

The canonical private ledger records historical exact scans with:

- no counterexample through denominator `120`;
- minimum positive oriented adjacent determinant `24` in that recorded scan.

A later historical computation extended the no-oriented-negative observation further, but the public claim level remains `PROOF_CANDIDATE` regardless of finite depth.

## Correct interpretation

A finite scan can falsify the universal statement if it finds a valid negative determinant. A finite scan that finds none cannot prove the all-depth theorem.

The exact candidate is the statement in `STATEMENT.md`, including:

- degree-oriented children `U_v,V_v`;
- indices starting at `0`;
- the strict terminal determinant at `n=deg_x(S_v)`;
- explicit zero extension after the support.

Any future public scanner should emit enough data to re-check those conventions, not merely a count of positive/negative samples.

## Reopen boundary

Increasing the denominator/depth bound alone is not currently a preferred proof route. The current Local TP2 campaign is on `HOLD` until a materially new structural mechanism appears.
