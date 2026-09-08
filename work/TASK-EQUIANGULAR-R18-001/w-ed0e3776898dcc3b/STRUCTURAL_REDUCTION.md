<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# TASK-EQUIANGULAR-R18-001 — uniform 59-line spectral reduction

## Provenance and scope

- Task: `TASK-EQUIANGULAR-R18-001`
- Worker: `w-ed0e3776898dcc3b`
- Canonical lock activation commit: `ba61d1d7acbda8712cc447d19e45969e72e5fcfa`
- Research branch: `research/TASK-EQUIANGULAR-R18-001/w-ed0e3776898dcc3b`
- Public accepted premise: `C-EQUIANGULAR-R18-ETA17-SINGLETON-EXCLUSION`
- Outcome class: `STRUCTURAL_REDUCTION`
- Claim promotion: **none**
- Publication novelty: **NOT_ESTABLISHED**

The goal is not to enumerate one more `eta` case.  The result below applies to every
hypothetical 59-line spectral branch in the public `R^18` campaign after the standard
common-angle `1/5` Seidel reduction.

## Source theorem used

The load-bearing external input is Gary Greaves' *Montreal Lectures*,
Lemmas 2.19--2.21:

- for odd integer `kappa`, `Char_{S-kappa I}(x)` is weakly type 2;
- type-2 / weak-type-2 behaviour factors as stated in Lemma 2.20;
- Lemma 2.21 forces repeated eigenvalues when a Seidel system is close to the
  relative-bound regime.

Source:
<https://grwgrvs.github.io/talks/Montreal_Lectures.pdf>

For the dimension-18 frontier, Greaves--Syatriadi prove `N(18) <= 59`:
<https://doi.org/10.1016/j.jcta.2023.105812>

The current 57-line constructions and the `57--59` frontier are also recorded in the
recent dimension-18 literature.  No search-absence argument is used as novelty evidence.

## Theorem — uniform degree-17 reduction

Let `S` be the Seidel matrix of a hypothetical system of 59 equiangular lines in
`R^18` with common angle `1/5`.  Then

\[
\boxed{
\operatorname{Char}_S(x)
=
(x+5)^{41}(x-11)\phi(x)
}
\]

for a monic integer polynomial `phi` of degree 17.

Define

\[
g(y)=\phi(y+11).
\]

Then `g` is monic, integral, real-rooted, weakly type 2, and if its roots are
`y_1,...,y_17`, then

\[
\boxed{
\sum_i y_i=7,\qquad
\sum_i y_i^2=65.
}
\]

Consequently,

\[
\boxed{
g(y)=y^{17}-7y^{16}-8y^{15}+\cdots .
}
\]

Moreover its constant term obeys the three-value gate

\[
\boxed{
g(0)\in\{-65536,0,65536\}.
}
\]

Thus every hypothetical 59-line spectrum lies in one of only two structural regimes:

1. `g(0)=0`, in which case `11` has multiplicity at least two in `Char_S`;
2. `g(0)=+/-65536`, in which case the forced `11` is simple and
   `|phi(11)|=65536`.

This is a common gate for all remaining spectral branches; it is not an exclusion of
one isolated next case.

## Proof

For the `1/5` Seidel representation, `I+S/5` is positive semidefinite of rank at most
18.  Hence the smallest Seidel eigenvalue is `lambda_0=-5` with multiplicity at least

\[
59-18=41.
\]

Apply Greaves' Lemma 2.21 with

\[
n=59,\qquad d=18,\qquad \lambda_0=-5.
\]

The closest odd integer to

\[
\frac{(d-n)\lambda_0}{d}
=
\frac{205}{18}
\]

is

\[
\kappa=11.
\]

The exact residual square budget is

\[
\begin{aligned}
R
&=n(n-1)-\lambda_0^2(n-d)
  +2\kappa\lambda_0(n-d)+d\kappa^2\\
&=65.
\end{aligned}
\]

For odd order the threshold in Lemma 2.21 is the least positive integer `eta` such
that

\[
\eta 4^{(\eta-1)/\eta}>65.
\]

No floating-point comparison is needed.  Raising both sides to the positive integer
power `eta` gives the exact integer test

\[
\eta^\eta 4^{\eta-1}>65^\eta.
\]

Direct integer comparison gives

\[
17^{17}4^{16}\le 65^{17},
\qquad
18^{18}4^{17}>65^{18},
\]

so `theta=18`.  Lemma 2.21 therefore forces

\[
(x+5)^{41}(x-11)^{18+1-18}
=
(x+5)^{41}(x-11)
\]

as a factor, with a residual monic integer polynomial `phi` of degree 17.

After removing exactly 41 copies of `-5`, the other 18 eigenvalues have, from
`tr(S)=0` and `tr(S^2)=59*58`,

\[
\sum \lambda_i=205,
\qquad
\sum \lambda_i^2=2397.
\]

Remove one forced eigenvalue `11` and write each of the remaining 17 eigenvalues as
`11+y_i`.  Then

\[
\sum y_i
=
205-18\cdot11
=
7
\]

and

\[
\sum y_i^2
=
2397-11^2-2\cdot11(205-11)+17\cdot11^2
=
65.
\]

Newton's identity gives

\[
e_2
=
\frac{(\sum y_i)^2-\sum y_i^2}{2}
=
-8,
\]

which gives the displayed top coefficients of `g`.

For weak type 2, Greaves' Lemma 2.19 gives

\[
\operatorname{Char}_{S-11I}(y)
=
(y+16)^{41} y\, g(y)
\]

weakly type 2.  The factor `(y+16)^41 y` is type 2, so Lemma 2.20 forces `g`
itself to be weakly type 2.

Because `g` has degree 17, weak type 2 implies

\[
2^{16}\mid g(0).
\]

Also

\[
|g(0)|^2
=
\prod_{i=1}^{17} y_i^2
\le
\left(\frac{\sum_i y_i^2}{17}\right)^{17}
=
\left(\frac{65}{17}\right)^{17}
\]

by AM--GM.  Exact integer arithmetic gives

\[
65^{17}<2^{34}17^{17},
\]

hence

\[
|g(0)|<2^{17}.
\]

The only multiples of `2^16` in that open interval are

\[
-2^{16},\quad 0,\quad 2^{16},
\]

which proves the three-value gate.

## Regression against the accepted eta=17 branch

The accepted public eta=17 spectrum has

\[
\phi(x)=(x-9)^6(x-10)(x-13)^{10}.
\]

Therefore

\[
g(y)=(y+2)^6(y+1)(y-2)^{10}.
\]

Its constant term is

\[
g(0)=+65536.
\]

The product of its 17 roots is `-65536`; the sign differs because the degree is odd.
This explicit sign distinction is checked in the verifier.

## What this does and does not establish

Established:

- every hypothetical public-campaign 59-line spectrum contains an eigenvalue `11`;
- every such spectrum reduces to one degree-17 monic integral real-rooted weak-type-2
  polynomial with fixed first two non-leading coefficients;
- its terminal constant has only three possible values;
- the result is exact and applies simultaneously to all remaining spectral branches.

Not established:

- `N(18) <= 58`;
- nonexistence of all 59-line systems;
- publication novelty of this specialization or of the terminal-product trichotomy;
- any unexported/private eta-branch classification;
- independent reproduction of this worker's derivation.

The next useful attack should exploit the three terminal regimes together with a
principal-deletion/deck identity or another theorem-level constraint.  Blindly extending a
finite coefficient enumeration is intentionally not done here.
