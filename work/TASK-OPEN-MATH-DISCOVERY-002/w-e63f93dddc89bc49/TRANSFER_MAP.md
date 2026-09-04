<!--
SPDX-FileCopyrightText: 2026 AIMath contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# Continued fractions ↔ matching partition functions

## Fixed scope

Task: `TASK-OPEN-MATH-DISCOVERY-002`  
Worker: `w-e63f93dddc89bc49`  
Exact public base: `279ba9fa98befe3aee37bfd1a98e4f688d333bd4`

This lane tests one explicit cross-domain transfer between:

1. finite simple continued fractions / Euler continuants;
2. matchings on a caterpillar graph, compressed to a weighted monomer–dimer model on its backbone path;
3. 2×2 transfer matrices.

The result is a **literature match with a reusable exact transfer**, not a novelty claim.

## 1. State mapping

Let

\[
a=(a_1,\ldots,a_n), \qquad a_i\in\mathbb Z_{>0}.
\]

Define the continuant

\[
K(\varnothing)=1,\qquad K(a_1)=a_1,
\]

\[
K(a_1,\ldots,a_n)
=
a_nK(a_1,\ldots,a_{n-1})+K(a_1,\ldots,a_{n-2}).
\]

The corresponding finite continued fraction is

\[
[a_1;\ldots,a_n]
=
\frac{K(a_1,\ldots,a_n)}
     {K(a_2,\ldots,a_n)}.
\]

Now form a path \(P_n\) with backbone vertices \(1,\ldots,n\).
Give vertex \(i\) monomer weight \(a_i\) and every backbone dimer weight \(1\).
For a matching \(M\) of the path define

\[
w(M)=\prod_{i\text{ unmatched by }M}a_i,
\qquad
Z(a)=\sum_{M} w(M).
\]

Then

\[
\boxed{Z(a)=K(a)}.
\]

### Why the matching model is the right graph object

Condition on the last backbone vertex.

- If it is not paired to \(n-1\), it contributes \(a_n Z(a_1,\ldots,a_{n-1})\).
- If edge \((n-1,n)\) is present, the remaining contribution is
  \(Z(a_1,\ldots,a_{n-2})\).

So \(Z\) has exactly the continuant recurrence and initial values.

For integer \(a_i\), this weighted path is the collapsed form of Hosoya's
caterpillar \(C_n(a_1,\ldots,a_n)\): attach \(a_i-1\) leaves to backbone
vertex \(i\).  Whenever the backbone does not match vertex \(i\), there are
exactly \(a_i\) local choices (no pendant edge, or one of its \(a_i-1\)
pendant edges); if a backbone edge matches \(i\), there is one local choice.
Thus summing over pendant choices gives the monomer weight \(a_i\).

Hence the state map is

\[
(a_1,\ldots,a_n)
\longleftrightarrow
C_n(a_1,\ldots,a_n)
\longleftrightarrow
P_n\text{ with monomer weights }a_i.
\]

## 2. Operation mapping

Appending a partial quotient \(b\),

\[
(a_1,\ldots,a_n)\mapsto(a_1,\ldots,a_n,b),
\]

is exactly the graph operation "attach one new weighted vertex of monomer
weight \(b\) to the right end of the backbone".

The common update is

\[
K_{n+1}=bK_n+K_{n-1},
\qquad
Z_{n+1}=bZ_n+Z_{n-1}.
\]

It is also encoded by

\[
M(b)=
\begin{pmatrix}
b&1\\
1&0
\end{pmatrix},
\]

with

\[
M(a_1)\cdots M(a_n)
=
\begin{pmatrix}
p_n&p_{n-1}\\
q_n&q_{n-1}
\end{pmatrix},
\]

where \(p_n/q_n=[a_1;\ldots,a_n]\).
Since \(\det M(b)=-1\),

\[
p_nq_{n-1}-p_{n-1}q_n=(-1)^n.
\]

## 3. Reusable transferred lemma: exact coordinate sensitivity

The graph model makes a useful factorisation immediate.

Change one partial quotient by a positive integer \(t\):

\[
a_j\mapsto a_j+t.
\]

Only matching terms in which backbone vertex \(j\) is not covered by a
backbone dimer receive the extra \(t\). Removing that unmatched vertex
splits the path into two independent components, hence

\[
\boxed{
K(a_1,\ldots,a_j+t,\ldots,a_n)-K(a_1,\ldots,a_n)
=
t\,K(a_1,\ldots,a_{j-1})K(a_{j+1},\ldots,a_n).
}
\]

Let

\[
x=[a_1;\ldots,a_n]=p/q,
\]

and let \(x'=p'/q'\) be the continued fraction after the same change.
Put

\[
S=K(a_{j+1},\ldots,a_n),
\]

with \(K(\varnothing)=1\). Then

\[
\boxed{
x'-x
=
\frac{(-1)^{j-1}tS^2}{qq'}.
}
\]

### Proof

Set

\[
A=K(a_1,\ldots,a_{j-1}),
\qquad
C=K(a_2,\ldots,a_{j-1}),
\]

with the empty-prefix conventions \(A=1,C=0\) when \(j=1\).

The matching-cut identity gives

\[
p'=p+tAS,\qquad q'=q+tCS.
\]

Factor the transfer matrix before position \(j\):

\[
M(a_1)\cdots M(a_{j-1})
=
\begin{pmatrix}
A&A_-\\
C&C_-
\end{pmatrix}.
\]

Its determinant is \((-1)^{j-1}\). The suffix product shows

\[
\binom pq
=
\begin{pmatrix}
A&A_-\\
C&C_-
\end{pmatrix}
\binom{K(a_j,\ldots,a_n)}{S},
\]

so

\[
Aq-Cp=(AC_- - CA_-)S=(-1)^{j-1}S.
\]

Therefore

\[
x'-x
=
\frac{(p+tAS)q-p(q+tCS)}{qq'}
=
\frac{tS(Aq-Cp)}{qq'}
=
\frac{(-1)^{j-1}tS^2}{qq'}.
\]

Consequences:

- increasing an odd-position partial quotient increases the value;
- increasing an even-position partial quotient decreases it;
- the exact response magnitude is controlled by the square of the suffix
  matching partition function.

This is an actual transferred invariant/lemma, not merely a visual analogy.

## 4. Held-out protocol

The theorem statements above were fixed before generation of the held-out
cases.

Implementation-freeze seed:

`AIMath-TASK-OPEN-MATH-DISCOVERY-002-w-e63f93dddc89bc49-v1`

Sanity/train envelope:

- every word of lengths 1..5;
- digits 1..4;
- every coordinate;
- perturbations \(t=1,2\).

Pre-frozen held-out envelope:

- 128 SHA-256-derived deterministic cases;
- lengths 6..12, disjoint from training lengths;
- digits 1..25;
- a deterministic changed coordinate;
- \(t=1,\ldots,9\).

The verifier independently evaluates the matching partition function by
enumerating edge subsets rather than calling the continuant recurrence.

Observed:

```text
PASS
train_words=1364
train_perturbations=12744
held_out_cases=128
held_out_length_range=6..12
held_out_digit_range=1..25
negative_control_dimer_weight_2=FAIL_AS_EXPECTED
negative_control_prefix_denominator_failures=3/3
held_out_digest=adaf08e035fe55a2e4ac980b01db997572f164d58178751d60e8561e30157a1e
```

Negative controls deliberately break the mapping:

1. changing dimer weight from 1 to 2 already destroys the continuant identity;
2. replacing the suffix continuant denominator by the prefix continuant fails
   on all three frozen controls.

## 5. Literature boundary

The core correspondence is not new.

- Haruo Hosoya, *Continuant, caterpillar, and topological index Z. Fastest
  algorithm for degrading a continued fraction*, Natural Science Report,
  Ochanomizu University 58(1), 15–28 (2007), explicitly identifies Euler's
  continuant with the Z-index / total-matching count of the associated
  caterpillar.
- Puri, Dhurandhar, Pedapati, Shanmugam, Wei and Varshney,
  *CoFrNets: Interpretable Neural Architecture Inspired by Continued
  Fractions*, NeurIPS 2021, Supplement Lemma 2, gives the coordinate
  derivative of the continuant ratio:
  \[
  \frac{\partial}{\partial a_j}[a_1;\ldots,a_n]
  =
  (-1)^{j-1}
  \left(\frac{K(a_{j+1},\ldots,a_n)}
  {K(a_2,\ldots,a_n)}\right)^2
  \]
  after translating indexing conventions.

The exact finite-\(t\) identity above is consistent with that derivative and
follows routinely from the same continuant/transfer-matrix machinery.
This bounded search did **not** establish publication novelty for the
finite-difference presentation or for the matching-cut proof.

Publication novelty: **NOT_ESTABLISHED**.

## 6. Outcome

Classification:

**LITERATURE_MATCH / REUSABLE_STRUCTURAL_TRANSFER**

What survived the task gate:

- explicit state map: continued-fraction word ↔ caterpillar / weighted path;
- explicit operation map: append partial quotient ↔ extend path;
- invariant map: continuant ↔ matching partition function;
- held-out exact prediction: 128/128;
- reusable lemma: exact coordinate sensitivity via graph cut;
- negative controls: both fail as intended.

No universal claim is inferred from finite tests; the universal statements
above are proved algebraically/combinatorially. No novelty or Truth Layer
promotion is requested.
