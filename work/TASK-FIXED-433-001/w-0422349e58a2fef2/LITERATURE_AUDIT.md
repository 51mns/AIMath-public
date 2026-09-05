<!--
SPDX-FileCopyrightText: 2026 AIMath contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# TASK-FIXED-433-001 — bounded primary-source placement

- Worker: `w-0422349e58a2fef2`
- Public base: `71547cb5d757afaace54b558f2d0a4a49fad5656`
- Search date: 2026-09-02
- Current PR: `#27`
- Outcome: **BOUNDED_UNRESOLVED_WITH_CLOSE_PRECEDENT**
- Novelty: **NOT_ESTABLISHED**
- Truth-layer effect: **NONE**

Detailed per-source adjudication is in `SOURCE_MAP.md`. Exact search inputs, access failures and the stop rule are frozen in `SEARCH_LOG.md`.

## Frozen question

The accepted AIMath public proof gives, for every `k >= 0`,

\[
\frac{U_k}{M_k}=\frac45-\mu\!\left(\frac{9k+8}{15k+13}\right).
\]

If

\[
\mu\!\left(\frac{9k+8}{15k+13}\right)=\frac{p_k}{M_k},
\]

then equivalently

\[
5p_k+5U_k=4M_k,
\qquad
U_k=r_k-\frac{M_k}{5}.
\]

This literature task asks where the fixed rational-affine map

\[
R_5(x)=\frac45-x
\]

or an algebraically equivalent fixed-433 representative identity sits in prior primary literature. It does not re-prove the AIMath theorem.

## Scope separation from PR #26

Parallel PR `#26` is Button-centered: it removes an old access blocker for Button 2001 and inspects the modular representative / Theorem 7 neighbourhood.

This continuation deliberately did **not** make Button 2001 its main work. The new search moved backward into Markoff/Cassels/Cohn/Baragar, then through Bombieri, Springborn, Button-citing downstream work, and Veselov's Cohn-index framework. The earlier Button result is retained only as context.

## Main result of the expanded placement

The source neighbourhood separates into two layers.

### Layer A — classical Markoff forms, triples, ideals and words

Markoff 1879 starts from indefinite binary quadratic forms and their minima. Cassels' Markoff-chain treatment and Cohn's modular/geodesic/primitive-word programme belong to this classical object layer. Baragar 1996 gives an especially concrete bridge to the ideal-theoretic side: for fixed Markoff number `m`, the Markoff equation is rewritten as

\[
x^2+y^2-3mxy=-m^2
\]

and then as a norm equation in the real quadratic order of discriminant `9m^2-4`.

This is structurally close to the later Button ideal/representative construction, but its exact objects are Markoff-triple coordinates, quadratic-order elements and principal ideals — not Springborn's Markov-fraction numerator `p_k` and not the fixed-433 numerator `U_k`.

Consequently these sources provide ancestry and nearby algebra, not an exact `R_5` match in the material that was inspectable here.

Cassels/Cohn body-level access remained incomplete for several primary items; those rows are classified `ACCESS_LIMITED` in `SOURCE_MAP.md`, not as negative prior-art findings.

### Layer B — the same Markov-fraction object

The strongest normalization boundary comes from Springborn 2024 and Veselov 2026 because they work directly with the same Markov-fraction object `mu(t)`.

Springborn states that the approximation constant is invariant under the integer-affine action

\[
x\longmapsto \pm x+n,\qquad n\in\mathbb Z,
\]

in equation (4). On p.157 the Markov-fraction subtree in `[1/2,1]` is obtained from `[0,1/2]` by the reflection

\[
x\longmapsto 1-x,
\]

and integer translates supply the other unit intervals. Definition 2.1, equations (6)–(7), separately defines the companion sequences.

Veselov then gives the direct Cohn-index bridge. With

\[
C_t(a)=\begin{pmatrix}a_t&m_t\\c_t&3m_t-a_t\end{pmatrix},
\qquad
I_t(a)=\frac{a_t}{m_t},
\]

Theorem 3.1, equation (14), states

\[
\mu(t)=I_t(0).
\]

The same passage identifies `[0,1/2]` as a fundamental domain for the group acting by `x -> +/-x+m`, `m in Z`.

This is a useful exact placement: AIMath's map is not merely one of those displayed standard symmetries, because its translation part is `4/5`, not an integer. In the accepted AIMath language, this is consistent with `R_5` lying in `PGL_2(Q)` but not `PGL_2(Z)`.

This does **not** establish publication novelty. A source may encode the same fixed-433 identity through a different representative, normalization, ideal, word or matrix relation without displaying the map as a canonical affine symmetry.

## Bombieri 2007

Bombieri's publisher record confirms that the article develops Markoff's badly-approximable-number theorem using classical continued fractions and Harvey Cohn's free-group word method for the periods of Markov irrationals.

The current runtime did not expose enough of the article body for an equation-by-equation comparison with `R_5`. Bombieri is therefore retained as a strong framework source with an explicit access boundary, not as a checked nonmatch.

## Button-citing downstream control: Srinivasan 2009

Srinivasan works with discriminant

\[
d=9c^2-4
\]

and ambiguous binary quadratic-form classes / associated ideals for a fixed Markoff number `c`. The article explicitly cites Button 2001 as an existing uniqueness criterion near p.769.

This later primary source confirms that Button's ideal/form machinery continued to be used in the Markoff uniqueness problem, but it does not identify Button's representative with Springborn's Markov-fraction numerator or with AIMath's `(5p_k,5U_k)` pair in the inspected passages.

Thus the downstream lineage remains **near but on a different object**.

## Earlier Button result retained, not re-audited

The first phase of PR #27 found a close constant-`4` relation in Button's quadratic-order representative construction and an exact finite diagnostic showing that, for `k=0,1,2`, Button's unordered representative pair is not AIMath's unordered scaled pair `(5p_k,5U_k)`, although both pairs sum to `4M_k`.

That result remains a finite diagnostic and a different-object distinction. It is not promoted to an all-`k` non-identification theorem and was not the main research target of this continuation.

The exact checker remains:

```bash
python3 work/TASK-FIXED-433-001/w-0422349e58a2fef2/button_overlap_check.py
```

## Decision

The expanded bounded primary-source audit supports the following placement and no stronger one:

> The fixed-433 identity sits inside a classical Markoff lineage of forms, triples, real-quadratic ideals, continued fractions and Cohn words/matrices. The older inspectable sources are generally on different mathematical objects. Springborn and Veselov reach the same Markov-fraction object and give an exact integer-affine normalization/Cohn-index framework, but the displayed standard action is `x -> +/-x+n`, not `x -> 4/5-x`. Within the frozen source/query envelope, an exact prior primary-source statement equivalent to AIMath's fixed `R_5` map was not located.

This is a **bounded unresolved prior-art placement with close precedents**, not a novelty determination.

Accordingly:

- `novelty = NOT_ESTABLISHED` remains unchanged;
- no canonical claim level changes;
- no author/prior-art priority claim is made;
- search failure is not converted into novelty;
- access-limited Cassels/Cohn/Bombieri items remain open historical-priority gaps rather than negative evidence.
