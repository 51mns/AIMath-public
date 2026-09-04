<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# TASK-LOCAL-TP2-REFRESH-001 — continuant / LGV route triage

Worker: `w-2282a212672dc6bf`  
Worker branch: `research/TASK-LOCAL-TP2-REFRESH-001/w-2282a212672dc6bf`  
Exact public base: `a1b0243423bbc6da08e514e37597feb987163e2d`  
Private snapshot named by the public campaign: `c8e61e0e398f540bc8c5de79663398d689f37473`

## Decision

**Outcome candidate: `STRUCTURAL_REDUCTION`.**

A materially different Local-TP2 proof architecture exists that is not a degree/depth enlargement of the recorded QW3, quotient, fixed-local wedge/Jacobi, F-only descent, or far-minor finite-dimensional ansatz routes.

The candidate route is:

```text
deformed squared Markov polynomial
  -> Farey-recursive continued fraction
  -> continuant / weighted path model
  -> degree-lifted common planar network for S_v and D_v
  -> LGV 2x2 minor
  -> F_v(n) > 0
```

This worker does **not** claim that the common planar network has been constructed for all Farey vertices. The result is a route-quality structural reduction and a sharply bounded next gate, not a proof of `C-LOCAL-TP2` and not a campaign reopen decision.

## Frozen target

The canonical target remains exactly

```text
F_v(n)
= H(D_v)[n+1] H(S_v)[n]
- H(D_v)[n]   H(S_v)[n+1] > 0
```

for every valid canonical Farey vertex `v` and `0 <= n <= deg_x(S_v)`, including the terminal zero-extension index. No stronger all-column TP2, PF2, log-concavity, or ratio statement is introduced.

## New external structural hook

Primary source inspected:

- Léa Bittmann, Perrine Jouteur, Ezgi Kantarcı Oğuz, Melody Molander, Emine Yıldırım, *A Mirror deformation of Markov Numbers*, arXiv:2602.14802v1 (16 Feb 2026), <https://arxiv.org/abs/2602.14802>.

The proof-relevant facts actually used for this triage are narrow:

1. Section 3.1, Definition 3.1 recursively attaches a finite continued fraction `F_t^+(q)` to every Farey parameter `t`.
2. Immediately after the definition, the paper states (via its cited Corollary 7.11 of Gyoda--Maruyama--Sato) that the numerator of `F_t^+(q)` is precisely the corresponding deformed squared Markov polynomial `M_t(q)`.
3. The entries in these continued fractions are Laurent polynomials with positive integer coefficients in the positivity argument for Theorem 2.2.
4. Independently, Section 4 gives the factorization `M_t(q)=m_t(q)m_t(q^{-1})` and a mirror mutation. This factorization is useful auxiliary structure, but global coefficient positivity of the mirror factors themselves is only Conjecture 6.2, so this worker does **not** use mirror-factor positivity as a premise.

Upstream source named by Bittmann et al. for the generalized-Markov continued-fraction construction:

- Yasuaki Gyoda, Shuhei Maruyama, Yusuke Sato, *SL(2,Z)-matrixizations of generalized Markov numbers*, arXiv:2407.08203v3, <https://arxiv.org/abs/2407.08203>.

A later proof lane should freeze the exact upstream proposition/corollary text before treating that dependency as load-bearing.

## Why this is not a recorded failed route

The public failed-route ledger closes these recorded mechanisms in scope:

- QW3 individual-sign propagation;
- all-pair quotient diagnostic / quotient structural reduction;
- `FM-REC2-AFFINE`;
- `FM-PAIRKERNEL-SYMD2`;
- earlier Candidate-B/direct-Route-W, fixed-local wedge/Jacobi, and F-only descent without a materially new ingredient.

The present route changes the proof object. It does not posit a finite recurrence for the determinant profile and does not try to propagate the sign of `F_v` through the old mutation state. Instead it attempts to realize the four entries of the target determinant as path sums in **one compatible planar network**, so positivity would come from a combinatorial minor interpretation.

The word `Jacobi` in the old failed-route name is not by itself a conflict: this proposal is not a new local determinant identity. Its load-bearing obligation is a global path-matrix realization tied to the Farey-recursive continuant.

## Exact LGV gate

For each valid `v` and each `0 <= n <= deg_x(S_v)`, construct an acyclic weighted planar network `N_{v,n}` with two ordered sources `s_D,s_S` and two ordered sinks `t_n,t_{n+1}` such that its path matrix is exactly

```text
P_{v,n} = [ H(D_v)[n+1]  H(D_v)[n]   ]
          [ H(S_v)[n+1]  H(S_v)[n]   ]
```

or the row/column ordering equivalent that has determinant `F_v(n)` with the frozen positive orientation.

Then the Lindstrom--Gessel--Viennot mechanism gives

```text
det(P_{v,n}) = weighted sum of compatible nonintersecting 2-path families.
```

Hence the target follows if both of the following are proved:

- all edge weights are nonnegative;
- for every frozen index, at least one admissible nonintersecting 2-path family has strictly positive weight.

This also handles the terminal index without division, because `H(S_v)[deg(S_v)+1]=0` is represented as absence of the corresponding path family rather than as a ratio.

## Degree-lift lemma available for the next gate

There is a generic exact construction that explains why coefficient extraction is not itself the hard part.

If a finite acyclic network has edge weights in `Z_{>=0}[q,q^{-1}]`, replace a Laurent-polynomial edge

```text
w_e(q) = sum_k c_k q^k
```

by transitions on an additional integer degree coordinate: from `(u,d)` to `(v,d+k)` with multiplicity/weight `c_k`. After a uniform exponent shift if desired, path sums to degree layer `d` are exactly coefficients of the original generating-function path sum.

Therefore a continuant path model for `M_t(q)` can be lifted coefficientwise without introducing subtraction. The unresolved issue is **simultaneous compatible planarity for the differences `S_v=U_v-C_v` and `D_v=V_v-U_v`**, not coefficient extraction itself.

The next proof lane should not spend its budget rediscovering this degree-lift observation; it should attack the simultaneous-difference network directly.

## Concrete next subproblem

Freeze one generic interior Farey triple `(r,s,t)` with `t=r⊕s`. Using Definition 3.1's recursive continued-fraction words, write the two canonical children as continuants built from the parent words. Derive exact splice identities for

```text
S_v = U_v - C_v,
D_v = V_v - U_v.
```

The desired outcome is a subtraction-free representation of both differences as path sums sharing the same ordered source/sink geometry after degree lift.

### PASS

A symbolic all-word identity gives a common compatible planar network and proves at least one positive nonintersecting family for every adjacent coefficient index.

### PARTIAL

A subtraction-free continuant formula for both `S_v` and `D_v` is obtained, but common-network compatibility or strictness remains unresolved. This is still reusable structural progress and should be frozen narrowly.

### KILL / HOLD

The exact generic splice forces sign-cancelling terms that cannot be represented in a common nonnegative path network, or a canonical vertex supplies a counterexample to the proposed common-network invariant. Record that obstruction; do not respond by increasing finite depth or ansatz degree.

## Mirror-factor route is secondary only

Bittmann et al. show the squared object factors as `m_t(q)m_t(q^{-1})`. This makes every coefficient profile of `M_t` an autocorrelation-type quantity of a mirror factor. That may eventually give a second route through correlation kernels.

However Conjecture 6.2 in the same paper explicitly leaves positivity of all mirror-deformed Markov polynomial coefficients open. Therefore a proof that assumes global mirror-factor positivity would merely exchange Local TP2 for another unproved statement. It is not authorized as the primary successor.

## Root sanity fixture

The exact root data used to guard orientation are

```text
C = 2x^2 + 6x + 5
U = 4x^3 + 18x^2 + 26x + 13
V = 6x^4 + 34x^3 + 74x^2 + 74x + 29
```

which give

```text
H(S) = [40, 32, 16, 4]
H(D) = [164, 138, 80, 30, 6]
F    = [272, 352, 160, 24].
```

A separate exact symbolic session reproduced these integers. The committed pure-Python `root_fixture.py` is a dependency-free replay artifact for this one fixture only; remote blob read-back at the time of this note was `68fe323fe56ce172c6aea214fe086be710af6114`.

## Claim and novelty boundary

- `C-LOCAL-TP2` remains `PROOF_CANDIDATE`.
- No counterexample was found or claimed.
- No universal proof is claimed.
- The Local-TP2 campaign remains `HOLD` until human/portfolio governance accepts a successor task under the reopen condition.
- This worker does not claim publication novelty for the Local-TP2 statement or for the proposed use of continuants/LGV.
- The external papers are used as structural dependencies, not as evidence that the exact AIMath determinant inequality was previously proved.

## Proposed successor payload

A portfolio/director successor should be narrowly titled along the lines of:

`Local TP2 continuant-splice common-network gate`

and own a fresh path distinct from this triage workspace. It should prohibit old QW3/quotient/far-minor enlargement and stop after the generic splice/common-network question is decided. A separate independent review is still required before any theorem promotion.
