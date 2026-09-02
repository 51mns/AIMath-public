<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# TASK-FIXED-433-001 — bounded primary-source literature audit

- Public base: `71547cb5d757afaace54b558f2d0a4a49fad5656`
- Worker: `w-f29341f2a4973b71`
- Task: `TASK-FIXED-433-001`
- Campaign: `CAM-FIXED-433`
- Scope: primary-source placement of the accepted fixed affine identification only
- Outcome: **BOUNDED UNRESOLVED COMPARISON**
- Novelty effect: **NONE / NOT ESTABLISHED**

## Frozen target

The accepted public package `research/433-existing-theory-identification/PROOF.md` proves

\[
\frac{U_k}{M_k}=\frac45-\mu\!\left(\frac{9k+8}{15k+13}\right),
\]

or, writing the Markov fraction as `p_k/M_k`,

\[
5p_k=4M_k-5U_k,
\qquad
U_k=r_k-\frac{M_k}{5}.
\]

The question in this task is not whether that identity is valid; it is already an accepted public AIMath premise. The question is whether the same transformation or representative identity is explicit in prior primary literature.

## New access result: Button 2001 is now retrievable

The pre-existing public `LITERATURE_MAP.md` records that the body of J. O. Button's 2001 paper had not been retrieved during the frozen private audit. That access statement is no longer current as an operational fact.

Oxford University Research Archive now exposes a publisher-version record and file for:

J. O. Button, *Markoff Numbers, Principal Ideals and Continued Fraction Expansions*, Journal of Number Theory 87 (2001), 77–95, DOI `10.1006/jnth.2000.2578`.

Primary-source record:

- https://ora.ox.ac.uk/objects/uuid:fc6f3446-4389-41e2-9cb4-d75505137821
- publisher-version file listed by ORA: `1-s2.0-S0022314X00925782-main.pdf`

The searchable publisher text is sufficiently exposed to recover source-local statements from the article. In particular:

- around p.81, Lemma 4 records standard continued-fraction facts for quadratic irrationals and the paper then specializes to `D=9c^2-4`;
- around p.85, Button chooses a modular inverse of `a` modulo `c`, constructs a representative of the form `x=3c-2b*alpha`, verifies `x^2 ≡ D (mod 4c)`, and Theorem 7 identifies the associated ideal `C_+` whose square is principal.

Thus Button 2001 contains a genuinely relevant **modular-representative construction**, not merely generic continued-fraction background.

## Exact-match comparison

The Button construction and the AIMath fixed-433 identity are nearby in subject but are not the same formula in the material located by this bounded audit.

| AIMath target | Button 2001 material located | Exact match located? |
|---|---|---|
| `U_k/M_k = 4/5 - mu(t_k)` | ideal/continued-fraction equivalence and modular representatives for `D=9c^2-4` | no |
| `5p_k = 4M_k - 5U_k` | congruence representative built from a Markoff triple and an inverse modulo `c` | no |
| `U_k = r_k - M_k/5` | modular root/ideal representative framework | no |
| fixed factor-5 CRT sign flip on the 433 ray | general factorisation/ideal-class machinery | no explicit fixed-433/factor-5 identity located |

The bounded search used the exact article title together with combinations of `4/5`, `c/5`, `5p`, `4M`, `433`, `factor 5`, `square root -1`, `mod c`, and continued-fraction/root terminology. These searches recovered Button's nearby ideal/congruence formulas but did not surface the frozen AIMath affine relation or an obvious algebraically identical specialization.

## Important limitation

This is **not** an exhaustive page-by-page historical-priority audit. In this research runtime the ORA record and search-indexed publisher text were accessible, but the PDF renderer/download path returned a cache/fetch failure, so a complete visual inspection of every page was not possible here.

Therefore the correct conclusion is deliberately asymmetric:

1. the old statement “Button's article body could not be retrieved” should not be used as a present-day access blocker;
2. Button contains a relevant modular representative construction that future comparison should cite;
3. this bounded audit did **not locate** the exact `4/5-x`, `5p=4M-5U`, or `U=r-M/5` identity;
4. failure to locate it does **not** prove that Button or earlier literature lacks an equivalent formulation;
5. publication novelty remains `NOT_ESTABLISHED`.

## Best next source check

If publication-level placement is worth another lane, the next check should be a human/full-PDF page-by-page comparison of Button 2001, especially the ideal representatives surrounding Lemmas 5–8 and Theorem 7, against the fixed-433 specialization. Only after that should the search expand backward through Button 1998, Cassels/Cohn, and forward through papers citing Button for congruence representatives.

## Source boundary

Primary sources directly used in this bounded audit:

1. Button 2001 publisher-version record/text via Oxford University Research Archive, DOI `10.1006/jnth.2000.2578`.
2. The accepted public AIMath fixed-identification package at the exact public base above.

Secondary/citing material was used only to navigate terminology and was not used to establish novelty or the mathematical identity.
