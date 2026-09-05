<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Cross-domain transfer result

Task: `TASK-OPEN-MATH-DISCOVERY-002`  
Worker: `w-e7cd824c02b53f1b`  
Exact public base: `279ba9fa98befe3aee37bfd1a98e4f688d333bd4`  
Hypothesis freeze commit: `a721b416a30c49820bdc4c4ac789782992c25691`

## Result

The frozen correspondence passes and is mathematically exact:

\[
K(a_1,\ldots,a_n)
=
Z(P_n;a_1,\ldots,a_n)
=
\det T_n,
\]

where

- \(K\) is the ordinary continuant;
- \(Z\) is the monomer-dimer matching partition function on the path \(P_n\), with unmatched vertex \(i\) weighted by \(a_i\) and every dimer weighted by \(1\);
- \(T_n\) is tridiagonal with diagonal \(a_i\), superdiagonal \(+1\), and subdiagonal \(-1\).

For the finite simple continued fraction,

\[
[a_1;\ldots;a_n]
=
\frac{K(a_1,\ldots,a_n)}{K(a_2,\ldots,a_n)}.
\]

The useful transfer is the exact cut formula. With \(K(\varnothing)=1\),

\[
\boxed{
K(a_1,\ldots,a_j+t,\ldots,a_n)-K(a_1,\ldots,a_j,\ldots,a_n)
=
t\,K(a_1,\ldots,a_{j-1})K(a_{j+1},\ldots,a_n).
}
\]

Thus if \(2\le j\le n-1\) and the original convergent is \(p/q\), then

\[
p'
=
p+tK(a_1,\ldots,a_{j-1})K(a_{j+1},\ldots,a_n),
\]

\[
q'
=
q+tK(a_2,\ldots,a_{j-1})K(a_{j+1},\ldots,a_n).
\]

This turns an interior continued-fraction perturbation into a product of two local path partition functions on the two components obtained by cutting at vertex \(j\).

## Independent derivation

### Path-matching side

Partition matchings of \(P_n\) according to the final vertex.

- If vertex \(n\) is unmatched, it contributes \(a_n Z(P_{n-1})\).
- If it is matched to vertex \(n-1\), that dimer contributes weight \(1\) and leaves \(P_{n-2}\).

Hence

\[
Z_n=a_nZ_{n-1}+Z_{n-2},
\qquad Z_0=1,\quad Z_1=a_1.
\]

This is exactly the continuant recurrence, so \(Z_n=K_n\).

Now differentiate \(Z_n\) with respect to the monomer weight \(a_j\). A surviving term is precisely a matching in which vertex \(j\) is unmatched. Removing that forced unmatched vertex disconnects the available matching problem into independent left and right paths. Therefore

\[
\frac{\partial K}{\partial a_j}
=
K(a_1,\ldots,a_{j-1})K(a_{j+1},\ldots,a_n).
\]

The matching partition function is multi-affine in every vertex weight, so a finite shift \(a_j\mapsto a_j+t\) has no higher-order term. This gives the boxed cut formula exactly.

### Determinant side

Expanding the signed tridiagonal determinant along its last row gives the same recurrence and initial values, hence \(\det T_n=K_n\).

There is also a direct cofactor proof of the cut derivative: deleting row and column \(j\) from the tridiagonal matrix leaves a block diagonal matrix consisting of the left and right tridiagonal blocks, so the diagonal cofactor factors as the product of the two sub-continuants.

## Frozen held-out evaluation

The deterministic held-out generation rule was committed before evaluation in `HYPOTHESIS_FREEZE.md`.

Observed after the freeze:

- held-out cases: **64**
- exact checks per case: **6**
- total exact checks: **384**
- failures: **0**
- sequence lengths: **5 through 12**
- largest perturbed numerator encountered: **12,560,229,392**
- largest perturbed denominator encountered: **2,038,256,703**
- floating-point arithmetic: **none**

Each case cross-checks:

1. direct continued-fraction recurrence;
2. the cut prediction for numerator and denominator;
3. brute-force path-matching enumeration;
4. an independently coded Bareiss determinant.

Reproduce with:

```bash
python3 -S work/TASK-OPEN-MATH-DISCOVERY-002/w-e7cd824c02b53f1b/verify_transfer.py
```

Expected final first line:

```text
PASS: 64/64 held-out cases; 384/384 exact checks
```

## Literature / novelty boundary

This is a **literature match and reusable structural transfer, not a novelty claim**.

Sources checked after the mathematical freeze:

1. Eric W. Weisstein, “Continuant”, MathWorld. It records the signed tridiagonal determinant, the ordinary continuant recurrence, and the continued-fraction numerator/denominator role. It cites H. S. Wall, *Analytic Theory of Continued Fractions* (1948).
2. *Encyclopedia of Mathematics*, “Continuant”. It records Euler's deletion rule: the continuant is the sum of products obtained by deleting disjoint adjacent pairs. Interpreting deleted adjacent pairs as matched path edges gives exactly the monomer-dimer path model above.
3. İlke Çanakçı and Ralf Schiffler, “Cluster algebras and continued fractions”, *Compositio Mathematica* 154 (2018), DOI `10.1112/S0010437X17007631`. They give a graph-perfect-matching realization of continued fractions using snake graphs and use it to derive continuant identities.
4. Amit Dhurandhar et al., “CoFrGeNet: Continued Fraction Architectures for Language Generation”, ICML 2026 / arXiv:2601.21766. Its appendix explicitly derives the same single-continuant derivative factorization by deleting a diagonal row/column of the tridiagonal determinant and obtaining two blocks.

The exact cut derivative is therefore already explicit in current literature, and the broader continued-fraction/matching correspondence is classical/known. The useful AIMath output here is the frozen three-domain mapping, exact finite-shift form, and reproducible held-out transfer check.

## Boundary

- No publication novelty is asserted.
- No AIMath claim is promoted.
- The 64-case computation is a regression/falsification layer; the universal statement is justified by the recurrence/matching/cofactor argument, not by finite testing.
- The result does not depend on any private AIMath artifact.
