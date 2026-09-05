<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Local TP2 continuant gap-cone reduction

**Claim ID:** `C-LOCAL-TP2-GAP-CONE-REDUCTION`
**Canonical level:** `INDEPENDENTLY_REPRODUCED`

A scoped, all-depth structural reduction extracted from the Local TP2 campaign:

```text
Farey-recursive continued fraction
  -> uniform transfer splice M_t = M_r^T Q M_s^T
  -> all-depth positive boundary gap cone
  -> subtraction-free S_v and D_v
```

The exact frozen statement is [`STATEMENT.md`](STATEMENT.md).

## Important boundary

This is **not** Local TP2.

`C-LOCAL-TP2` remains `PROOF_CANDIDATE` with `public_evidence: PARTIAL`. This package
does not establish the strict adjacent determinant `F_v(n) > 0`, and does not
construct a common coefficient/`H`-grade planar network for `S_v` and `D_v`.

It also records a bounded no-go: the direct raw-gap LGV architecture fails at the
root because `det(M_{1/3} - M_{1/2}) = -(x+1)^2`, so the raw positive gap matrix
cannot itself be a nonnegative planar path matrix. That closes one architecture, not
the problem.

## Reproduce

```bash
python3 reviews/local-tp2/continuant_gap_cone_independent_check.py
```

The finite control covers a bounded Farey range and is a reproduction aid. The
all-depth content rests on the written induction reviewed in
[`../../reviews/local-tp2/CONTINUANT_GAP_CONE_INDEPENDENT_REVIEW_2026-09-05.md`](../../reviews/local-tp2/CONTINUANT_GAP_CONE_INDEPENDENT_REVIEW_2026-09-05.md).

## Review independence

The registered review is graded `I2`, not `I3`. The reviewer is the same model family
as the writer lane and read the writer material before freezing its derivation, so
errors may be correlated. `reviews/local-tp2/REVIEW.yml` records those limitations
explicitly. A cross-family independent review would materially strengthen this claim.
