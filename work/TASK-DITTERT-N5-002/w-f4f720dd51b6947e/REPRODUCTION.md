<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# TASK-DITTERT-N5-002 — independent Z2 reproduction attempt

## Scope and independence

Task: `TASK-DITTERT-N5-002`.

Public base: `71547cb5d757afaace54b558f2d0a4a49fad5656`.

Worker: `w-f4f720dd51b6947e`.

Frozen target statement: up to independent row and column permutations, a global Dittert maximizer in `K_5` cannot have exactly two zero entries in distinct rows and distinct columns.

This attempt was derived without reading `research/dittert-n5-z2/PROOF.md` or importing writer code/generated logs. Before the derivation was frozen, the worker read only the public claim metadata/README and standard Dittert/Hwang background. In particular, the reduction below uses the same-zero-pattern averaging and first-order maximizer conditions quoted in Udayan–Somasundaram, *Special Matrices* 12 (2024), DOI `10.1515/spma-2024-0006`, and in Cheon–Wanless, *Linear Algebra Appl.* 436 (2012), 791–801.

## Canonical seven-parameter face

Place the two zeros at `(1,1)` and `(2,2)`. Rows 3,4,5 have the same zero pattern, and columns 3,4,5 have the same zero pattern. Hwang averaging therefore allows a hypothetical global maximizer to be replaced, without losing global maximality, by

\[
A=\begin{pmatrix}
0&a&b&b&b\\
c&0&d&d&d\\
e&f&g&g&g\\
e&f&g&g&g\\
e&f&g&g&g
\end{pmatrix},
\qquad a,b,c,d,e,f,g>0,
\]

with

\[
a+c+3(b+d+e+f)+9g=5.
\]

The row sums are

\[
r_1=a+3b,\quad r_2=c+3d,\quad r_3=r_4=r_5=e+f+3g,
\]

and the column sums are

\[
s_1=c+3e,\quad s_2=a+3f,\quad s_3=s_4=s_5=b+d+3g.
\]

For

\[
\phi_{ij}(A)=\prod_{k\ne i}r_k+\prod_{\ell\ne j}s_\ell-\operatorname{per}A(i\mid j),
\]

Hwang's first-order condition gives `phi_ij = phi(A)` on positive entries and `phi_ij <= phi(A)` on zero entries.

## Exact chamber lemma

The four permanent minors needed below are

\[
\operatorname{per}A(1\mid1)=18dfg^2,
\]

\[
\operatorname{per}A(1\mid2)=6g^2(cg+3de),
\]

\[
\operatorname{per}A(2\mid2)=18beg^2,
\]

\[
\operatorname{per}A(2\mid1)=6g^2(ag+3bf).
\]

Since `(1,1)` is zero and `(1,2)` is positive,

\[
\phi_{11}-\phi_{12}
=(s_2-s_1)s_3^3+6g^2\bigl(cg+3d(e-f)\bigr)\le0.
\]

Since `(2,2)` is zero and `(2,1)` is positive,

\[
\phi_{22}-\phi_{21}
=(s_1-s_2)s_3^3+6g^2\bigl(ag+3b(f-e)\bigr)\le0.
\]

Adding cancels the entire column-product term and yields

\[
6g^2\left((a+c)g+3(d-b)(e-f)\right)\le0.
\]

Because `a,c,g>0`, every hypothetical maximizer in this exact two-zero support class must satisfy the strict chamber condition

\[
\boxed{(d-b)(e-f)<0}.
\]

The transpose-dual comparison, using `(1,1)` versus `(2,1)` and `(2,2)` versus `(1,2)`, gives the same identity after the row-product terms cancel. This is an internal negative-control/cross-check of the orientation.

## Additional stationary cycle equations

All seven nonzero parameter classes are positive. Therefore the positive-entry stationarity equations also imply the two row/column-sum-free cycle identities

\[
\phi_{12}+\phi_{33}-\phi_{13}-\phi_{32}=0,
\]

\[
\phi_{21}+\phi_{33}-\phi_{23}-\phi_{31}=0.
\]

The row/column-product parts cancel, so these reduce purely to permanent-minor equations:

\[
\operatorname{per}A(1\mid2)+\operatorname{per}A(3\mid3)
-\operatorname{per}A(1\mid3)-\operatorname{per}A(3\mid2)=0,
\]

\[
\operatorname{per}A(2\mid1)+\operatorname{per}A(3\mid3)
-\operatorname{per}A(2\mid3)-\operatorname{per}A(3\mid1)=0.
\]

These are a compact exact elimination target for a future completion: any complete independent proof only needs to show that the full positive-entry stationary system is incompatible with the strict chamber `(d-b)(e-f)<0` (or otherwise exclude the remaining chamber).

## Numerical reconnaissance, not evidence for the theorem

As a discovery check only, solving the full seven-variable interior stationary equations numerically from many positive starts produced one positive stationary point, invariant under the natural transpose/swap symmetries:

- `a=c≈0.29155449`,
- `b=d=e=f≈0.23614850`,
- `g≈0.17590100`.

It has row and column sums numerically equal to 1, but it violates the strict chamber because `(d-b)(e-f)=0`; direct evaluation also gives both zero-entry derivatives larger than the common positive-entry derivative. This numerical observation is **not** used as a uniqueness proof and is not a load-bearing part of the result.

## Outcome and boundary

Outcome: `STRUCTURAL_REDUCTION / INCONCLUSIVE`.

Proved here: the exact seven-parameter reduction plus the strict necessary chamber `(d-b)(e-f)<0`, with a transpose-dual check and two compact stationary cycle equations.

Not proved here: incompatibility of the complete stationary system with that chamber. Therefore this contribution does **not** independently reproduce the full public Z2 exclusion and does not change the public claim level.

The next minimal step is exact elimination or a sign argument for the positive-entry stationarity equations restricted to `(d-b)(e-f)<0`; reading the existing AIMath proof should be deferred until that derivation is frozen if method independence is still desired.
