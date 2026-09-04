# Local TP2 refresh triage — grade-refined skein / matching literature

Worker: `w-c7d4f8a21b609e3c`  
Task: `TASK-LOCAL-TP2-REFRESH-001`  
Public base: `a1b0243423bbc6da08e514e37597feb987163e2d`

## Decision

**NO CAMPAIGN REOPEN RECOMMENDED from this bounded triage.**

The submitted direction was to seek a theorem-native refinement of the known weighted-poset / matching skein machinery that controls the Local-TP2 exponent grade after the specialization

```text
k = q + q^(-1).
```

The literature contains substantially multivariate, weight-preserving skein bijections, but the located theorems do not supply the missing adjacent exponent-grade likelihood-ratio sign between the two marked Local-TP2 families.

This task is maintenance/dependency triage only. It does not change `C-LOCAL-TP2`, does not reopen `CAM-LOCAL-TP2`, and makes no novelty claim.

## 1. Public failed-route boundary

The public campaign is on `HOLD`. Its reopen conditions require one of:

- a materially new theorem-native mechanism;
- an external theorem directly implying the frozen statement;
- a valid counterexample.

The public failed-route memory already blocks deeper finite-only continuation and equivalent quotient/QW3/far-minor restatements. This triage therefore did not treat a larger scan, another generic skein iteration, or another finite quotient test as a valid new mechanism.

## 2. Strongest external literature match: snake graph calculus

Canakci--Schiffler, *Snake graph calculus and cluster algebras from surfaces* (arXiv:1209.4617), constructs explicit bijections between perfect matchings of crossing snake graphs and perfect matchings of the resolved graphs.

The relevant point is stronger than cardinality preservation. Their Lemma 6.2 records, on the first resolution branch, preservation of the full matching weight and height monomial:

```text
x(phi_34(P)) y(phi_34(P)) = x(P) y(P).
```

The self-crossing sequel (arXiv:1407.0500) likewise emphasizes that the switching operation is weight-preserving. Thus multivariate monomial-level skein preservation is already known; merely replacing a single scalar weight by many formal coefficient variables is not a new Local-TP2 mechanism.

### Why this still does not imply Local TP2

Local TP2 needs an adjacent exchange of the two **factor grades**:

```text
(T : n,   S : n+1)
   ->
(T : n+1, S : n).
```

If one refines the known matching weight by tagging every monomial unit with its original factor, the standard weight-preserving branch preserves that factor-origin data rather than transferring one unit of exponent grade from one factor to the other. If the origin tag is instead allowed to change when a piece switches between resolved components, that is an additional theorem not supplied by the cited weight-preserving skein result.

Hence the literature match identifies a powerful multivariate resolution theorem, but not the required marked-factor grade transfer.

## 3. Weighted fence-poset skein literature

Banaian--Gyoda, *Cluster algebraic interpretation of generalized Markov numbers and their matrixizations* (arXiv:2507.06900), Proposition 8.4, gives for crossing weighted fence posets

```text
W*(P1) W*(P2)
 = W*(P3) W*(P4)
 + Z_R* Z_s* Z_t* W*(P5) W*(P6).
```

The proof imports a partition `A sqcup B` of order-ideal pairs. The `A` bijection is weight-preserving; the `B` bijection changes the weight by one explicit monomial.

This is exactly the kind of canonical determinant-collapse machinery that can avoid a generic far-minor expansion. However, the theorem controls the total formal weight of an ideal pair. It does not state an adjacent `q`-endpoint refinement after substituting `k=q+q^(-1)`, nor a two-factor grade transfer of the form required above.

Banaian--Huang, *Orderings of Generalized k-Markov Numbers* (arXiv:2604.17445), supplies explicit switching-position / tail-swap constructions in related generalized Markov posets. Those constructions confirm the availability of structural switches, but their stated invariant is again ideal/weight data rather than the Local-TP2 adjacent exponent grade.

## 4. Oriented-poset rank interlacing does not use the required grading

Kantarcı Oğuz, *Oriented posets, Rank Matrices and q-deformed Markov Numbers* (arXiv:2206.05517), develops rank matrices for oriented posets and relates fence rank polynomials to a different q-deformation of Markov numbers. The rank variable records ideal size.

The Local-TP2 `H` grade instead comes from the endpoint exponent after `k=q+q^(-1)`: an object of formal weight `k^e` expands into all `+/-1` words of length `e`, and the grade is the signed endpoint. Ideal-size rank interlacing therefore cannot be silently substituted for the required exponent-endpoint interlacing.

No source found in this bounded search states a theorem transporting the oriented-poset interlacing result to this signed-walk endpoint grading.

## 5. Monomer--dimer / stability literature

Heilmann--Lieb theory gives real-rootedness for the ordinary matching generator, and real-stability / strong-Rayleigh methods imply important negative-dependence and ultra-log-concavity consequences in suitable generating-polynomial settings.

The Local-TP2 requirement is different: it is a cross-family adjacent minor / likelihood-ratio comparison between two marked boundary-condition families, after a signed monomer-colour refinement. No theorem located in this bounded search directly supplies that comparison.

Accordingly, invoking real-rootedness, strong Rayleigh, negative association, or ULC alone would be a harder restatement rather than a proof of the frozen Local-TP2 sign.

## 6. What would count as a genuine reopen mechanism

The search leaves a precise external-theorem target rather than an open-ended request for more computation.

A materially new mechanism would need to prove something equivalent to one of the following.

### Factor-coloured / rank-refined skein theorem

A resolution theorem for the relevant weighted fence/snake objects that tracks two factor grades separately and permits a controlled one-unit exchange under

```text
k = q + q^(-1),
```

so that the crossed endpoint class is injected/cancelled against the desired endpoint class with an explicit positive remainder.

### Marked-family graded switching theorem

A structural switch on the existing common matching object that preserves the two Local-TP2 marked classes while changing their exponent grades by exactly `(+1,-1)` (or gives an equivalent determinant-level cancellation), including strictness.

### External direct sign theorem

A theorem whose hypotheses can be checked on the canonical Local-TP2 objects and whose conclusion is directly the adjacent `H`-profile minor sign. General unimodality, log-concavity, real-rootedness, or total-weight skein positivity is not enough.

## 7. Bounded triage outcome

No located external theorem meets the above threshold. The multivariate snake-graph and weighted-poset results are useful literature matches and clarify the exact missing refinement, but they do not independently satisfy the campaign reopen conditions.

Therefore this worker records:

```text
outcome: NO_REUSABLE_PROGRESS
campaign_reopen: NO
claim_promotion: NONE
recommended_next_action: keep CAM-LOCAL-TP2 on HOLD
reopen_only_if: a theorem/source explicitly controls the signed H/exponent grade,
                or a new canonical identity/counterexample bypasses that grade problem
```

## References checked

- I. Canakci, R. Schiffler, *Snake graph calculus and cluster algebras from surfaces*, arXiv:1209.4617.
- I. Canakci, R. Schiffler, *Snake graph calculus and cluster algebras from surfaces II: Self-crossing snake graphs*, arXiv:1407.0500.
- E. Banaian, Y. Gyoda, *Cluster algebraic interpretation of generalized Markov numbers and their matrixizations*, arXiv:2507.06900.
- E. Banaian, M. Huang, *Orderings of Generalized k-Markov Numbers*, arXiv:2604.17445.
- E. Kantarcı Oğuz, *Oriented posets, Rank Matrices and q-deformed Markov Numbers*, arXiv:2206.05517.
