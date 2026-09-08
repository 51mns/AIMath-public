<!--
SPDX-FileCopyrightText: 2026 AIMath contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# TASK-FIXED-433-001 — Button root-pair exact placement audit

- Worker: `w-5b0eefedca755036`
- Exact public base: `279ba9fa98befe3aee37bfd1a98e4f688d333bd4`
- Search date: 2026-09-04
- Branch: `research/TASK-FIXED-433-001/w-5b0eefedca755036`
- Classification: **SOURCE_BACKED_PARTIAL_EXACT_MATCH / FACTOR5_GAP_UNRESOLVED**
- Publication novelty: **NOT_ESTABLISHED**
- Canonical claim promotion/demotion: **NONE**

## Frozen question

The accepted public AIMath theorem gives, for every `k >= 0`,

\[
\frac{U_k}{M_k}=\frac45-\mu\!\left(\frac{9k+8}{15k+13}\right).
\]

Writing

\[
\mu\!\left(\frac{9k+8}{15k+13}\right)=\frac{p_k}{M_k},
\]

its equivalent representative identities include

\[
r_k=M_k-p_k,
\qquad
U_k=r_k-\frac{M_k}{5},
\qquad
5p_k+5U_k=4M_k.
\]

This audit asks which part of that chain is already explicit, up to an exact change of representative, in J. O. Button's 2001 primary source.

## Primary source and access boundary

J. O. Button, *Markoff Numbers, Principal Ideals and Continued Fraction Expansions*, Journal of Number Theory 87 (2001), 77–95, DOI `10.1006/jnth.2000.2578`.

Oxford University Research Archive exposes the publisher/version-of-record PDF. In this runtime the direct PDF renderer returned a cache miss, so a visual screenshot audit was not available. The publisher PDF's indexed text was nevertheless source-local enough to recover the relevant formulas and page locations. Search/render failure is not used as negative evidence.

The newly recovered source-local points are:

1. **p.84:** the indexed source shows **Corollary 6** and the transition to the Markoff triple `(a,b,c)` and associated principal ideals. This corrects the loose “Lemmas 6–7” label in an earlier work-in-progress description.
2. **p.85, Theorem 7:** for a Markoff triple `(a,b,c)`, choose `alpha` inverse to `a (mod c)` and set
   \[
   x=3c-2b\alpha
   \]
   modulo `2c`; this is an admissible root of `x^2 = D (mod 4c)` and defines the Hermite representative of `C_+`. The theorem states that `C_+^2` is principal.
3. **p.86, Lemma 8:** the indexed publisher text exposes the full ideal-squaring formula, including `d=gcd(a,b)`, Bezout data, `A=a^2/d^2`, and the corresponding `B` expression. This closes the formula-access gap recorded by the earlier Button audit.
4. **p.87:** after normalising `c < x <= 3c-1`, Button constructs the alternative representative `x'` obtained by swapping `a,b` and explicitly derives
   \[
   \boxed{x+x'=4c}
   \]
   outside the singular golden-ratio case.

The fixed-433 ray is not the singular case.

## Exact all-k correspondence with the AIMath root pair

For the fixed AIMath ray use

\[
(a,b,c)=(433,Y_k,M_k).
\]

The accepted fixed-433 data give a Markoff triple and pairwise invertibility modulo `M_k`. Button's p.85 representative satisfies

\[
x\equiv3c-2b a^{-1}\pmod{2c}.
\]

Because this ray has odd `c`, and Button's p.87 normalisation gives `c<x<3c`, define

\[
t=\frac{x-c}{2},\qquad 0<t<c.
\]

Modulo `c`,

\[
t\equiv-b a^{-1}\pmod c.
\]

The Markoff equation

\[
a^2+b^2+c^2=3abc
\]

reduces modulo `c` to

\[
a^2+b^2\equiv0\pmod c.
\]

Since `a` and `b` are units modulo `c`, division by `ab` gives

\[
a b^{-1}+b a^{-1}\equiv0\pmod c,
\]

hence

\[
-b a^{-1}\equiv a b^{-1}\pmod c.
\]

For `a=433`, `b=Y_k`, the canonical AIMath representative is

\[
r_k\equiv433Y_k^{-1}=a b^{-1}\pmod{M_k},
\qquad 0\le r_k<M_k.
\]

Both `t` and `r_k` lie in the same representative interval, so

\[
\boxed{t=r_k}.
\]

Now let `x'` be Button's swapped representative and

\[
t'=\frac{x'-c}{2}.
\]

Button's p.87 identity `x+x'=4c` gives

\[
t+t'=c.
\]

The accepted AIMath/source bridge already gives `r_k=M_k-p_k`, therefore

\[
\boxed{t'=p_k}.
\]

Equivalently, Button's two Hermite representatives encode the exact pair

\[
\boxed{
 x_k=M_k+2r_k,
 \qquad
 x'_k=M_k+2p_k,
 \qquad
 x_k+x'_k=4M_k.
}
\]

Thus the complementary representative mechanism

\[
\boxed{r_k=M_k-p_k}
\]

has an exact primary-source placement in Button 2001 after the explicit affine reparameterisation `t=(x-c)/2`.

This is an all-`k` algebraic identification, not an inference from finite examples.

## What Button does not yet place in this audit

The remaining AIMath step is

\[
\boxed{U_k=r_k-\frac{M_k}{5}},
\]

or equivalently

\[
\boxed{p_k+U_k=\frac{4M_k}{5}}.
\]

Button explicitly warns on p.85 that a composite `c` may admit many possible root representatives. The surrounding ideal theory and later factorisation arguments are therefore relevant background, but the bounded source-local audit did **not** locate an explicit fixed factor-5 representative shift

\[
r\longmapsto r-c/5,
\]

a displayed `4/5` affine map, or an equivalent identity identifying Button's additional roots with the fixed AIMath continuant `U_k`.

Targeted checks included the p.84–88 theorem/lemma window and source-index searches for `4/5`, `1/5`, `c/5`, factor-5 language, the root formula, and the relevant ideal representatives. Non-detection is **not** converted into a novelty claim.

## Exact finite regression

`button_fixed433_exact_overlap.py` independently checks `k=0..10` with arbitrary-precision integer arithmetic. For every tested row it verifies:

- `(433,Y_k,M_k)` satisfies the Markoff equation;
- Button's p.85 `x` and swapped `x'` are reconstructed exactly;
- `x+x'=4M_k`;
- `(x-M_k)/2=r_k`;
- `(x'-M_k)/2=p_k`;
- separately, the accepted AIMath relation `U_k=r_k-M_k/5`.

These rows are regression fingerprints only; the universal Button-to-`(r,p)` correspondence is the modular argument above.

## Verdict

**Source-backed exact prior match:** Button 2001 already encodes the fixed-ray complementary pair `(r_k,p_k)` through its two Hermite/root representatives after `t=(x-M_k)/2`.

**Still bounded unresolved:** the factor-5 CRT shift from `r_k` to `U_k`, equivalently the full map `R_5(z)=4/5-z`, was not located explicitly in the audited Button source window.

Therefore the correct placement is not “no overlap”. It is:

> **exact prior placement of the root-pair complement layer, with the fixed factor-5 shift still unresolved.**

Publication novelty remains **NOT_ESTABLISHED**. No canonical claim level is changed by this worker result.
