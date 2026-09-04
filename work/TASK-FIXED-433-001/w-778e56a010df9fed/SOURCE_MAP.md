<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Source map

Exact public base: `279ba9fa98befe3aee37bfd1a98e4f688d333bd4`  
Worker: `w-778e56a010df9fed`

| Source | Source-local statement | AIMath correspondence | Verdict |
|---|---|---|---|
| Drézet--Le Potier, 1985, printed p.194 | `mu(E)=c1/r`; exceptional bundle determined by slope; rank is least positive denominator | If source slope is `p_k/M_k`, then rank `M_k`, Chern numerator `p_k` | **Exact normalization match** |
| Drézet--Le Potier, 1985, printed p.195, Theorem A / definition of `epsilon` | exceptional slopes are `epsilon(D)`; `epsilon(-rho)=-epsilon(rho)`, `epsilon(rho+n)=epsilon(rho)+n`, `n in Z` | Standard symmetry group has only integral translation | **Boundary for `4/5-x`** |
| Veselov, arXiv:2501.06779v2, Section 3, Theorem 3.1 | exceptional slopes on `P^2` coincide with all Markov fractions | `p_k/M_k` is exactly an exceptional-bundle slope | **Exact same-object placement** |
| Veselov, immediately after Theorem 3.1 | tensor by `O(n)` and dual preserve exceptionality; slope set invariant under `Aff_1(Z)` | `E^vee tensor O(1)` sends `p/M` to `(M-p)/M` | **Standard part of AIMath map explained** |
| Perling, arXiv:2210.12982v1, Section 3.1 before Lemma 3.1 | Markoff weights square to `-1` modulo corresponding Markoff number; Rudakov identifies weights with first Chern classes and weight/Markoff ratios with slopes | modular-root numerators have a known exceptional-bundle/Chern interpretation | **Close structural precedent; normalization caution** |
| Bounded factor-5 query envelope | no source-local hit for `U=r-M/5`, `5p+5U=4M`, or `4/5-p/M` | residual factor-5 shift remains unplaced in this envelope | **Unresolved; not novelty evidence** |

## Exact derived placement

Let `E_k` be the exceptional bundle with

`rank(E_k)=M_k`, `c1(E_k)=p_k`, `mu(E_k)=p_k/M_k`.

Set

`F_k = E_k^vee tensor O(1)`.

Then

`rank(F_k)=M_k`, `c1(F_k)=M_k-p_k=r_k`, hence

\[
\mu(F_k)=\frac{r_k}{M_k}.
\]

Using the accepted AIMath relation `U_k=r_k-M_k/5`,

\[
\boxed{U_k/M_k=\mu(F_k)-1/5}.
\]

Thus the fixed transformation decomposes as

\[
p/M \xrightarrow{E^\vee\otimes O(1)} 1-p/M
\xrightarrow{-1/5} 4/5-p/M.
\]

Only the first arrow belongs to the standard exceptional-bundle integer-affine symmetry described in the primary sources.

## Primary URLs

- Drézet--Le Potier PDF: https://www.numdam.org/article/ASENS_1985_4_18_2_193_0.pdf
- DOI record: https://doi.org/10.24033/asens.1489
- Veselov PDF: https://arxiv.org/pdf/2501.06779
- Perling PDF: https://arxiv.org/pdf/2210.12982

Publication novelty: **`NOT_ESTABLISHED`**.
