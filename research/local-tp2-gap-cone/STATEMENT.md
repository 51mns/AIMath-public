<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Frozen statement — Local TP2 continuant gap-cone reduction

**Claim ID:** `C-LOCAL-TP2-GAP-CONE-REDUCTION`
**Source research head:** `0f2d9f6fb7f3331ad289cc949b1191d7cbb2fb0a`
**Source Task:** `TASK-LOCAL-TP2-CONTINUANT-LGV-001`

This claim is deliberately **narrower than `C-LOCAL-TP2`**. It fixes only the
structural reduction that survived independent review, so that the reduction can
be reused as a load-bearing premise without any part of Local TP2 itself being
treated as proved.

## Setting

Write `x = q + q^{-1}`. For a reduced Farey parameter `p/q`, let `G_{p/q}` be the
corresponding deformed squared Markov polynomial, obtained as the numerator of the
Farey-recursive finite continued fraction of Definition 3.1 of
Bittmann–Jouteur–Kantarcı Oğuz–Molander–Yıldırım, *A Mirror deformation of Markov
Numbers*, arXiv:2602.14802v1.

Let `A(z) = [[z,1],[1,0]]`, `J = [[1,0],[1,-1]]`, and

```text
Q = A(3x+2) J = [[3(x+1), -1], [1, 0]].
```

For a canonical Farey vertex `v` with boundary/mediant data in the usual notation,
write `C_v`, `U_v`, `V_v`, `H_v`, `K_v`, and set

```text
S_v = U_v - C_v,
D_v = V_v - U_v.
```

## Statement

The following hold **at every canonical Farey vertex**, i.e. at all depth.

**(T1) Uniform splice.** For interior Farey triples `t = r ⊕ s`,
`M_t = M_r^T Q M_s^T`, and with the virtual boundary matrices `M_0`, `M_1` the same
formula covers both boundary recursions and the root.

**(T2) Invariants.** `det M_t = 1` and the skew `σ(M) = M_12 - M_21` satisfies
`σ(M_t) = x`. Consequently every difference of two matrices occurring on a Farey
edge is symmetric.

**(T3) Positivity of `Z_t`.** `Z_t = Q M_t^T ≥ 0` coefficientwise.

**(T4) Boundary gap cone.** With the cone `{Δ : Δ ≥ 0 and QΔ ≥ 0}` (coefficientwise,
for symmetric `Δ`), every Farey boundary gap `M_t - M_r`, `M_t - M_s` lies in the
cone, propagated by the interior mediant induction.

**(T5) Extreme `1/n` chain.** On the extreme-left chain, `B_{n+1} = R_0 B_n` where
`R_0 = M_0^T Q`; this uses the fixed-skew invariant of (T2) to cancel the
antisymmetric parts, and is **not** a consequence of the boundary recursion alone.
With `P_0 = 1`, `P_1 = ρ = 2x+3`, `P_{j+1} = ρ P_j - P_{j-1}`,

```text
B_n = (x+1) [[P_{n-1}, P_{n-2}], [P_{n-2}, P_{n-3}]],
P_n = Σ_{k=0}^{n} binom(n+k+1, n-k) (2x+1)^k ≥ 0,
```

and `m P_j - P_{j-1} = P_{j+1} + x P_j ≥ 0` with `m = 3(x+1)`, so `Q B_n ≥ 0`.

**(T6) Degree rank.** `deg_x G_{p/q} = p + q - 1`.

**(T7) Oriented `D_v` factorisation.** With `L`, `R` the two child mutations,
`R - L = (B - A)[3(x+1)C + 1 - x]` exactly, and the canonical orientation supplied
by (T6) and Farey interval genealogy gives

```text
D_v = (H_v - K_v) [3(x+1) C_v + 1 - x],
```

in which the first factor is the upper-left entry of a cone-positive edge gap and
the second factor is coefficientwise positive.

**(T8) Subtraction-free consequence.** Therefore

```text
S_v ∈ Z_{≥0}[x]   and   D_v ∈ Z_{≥0}[x]
```

at every canonical vertex, with no finite-depth inference.

**(T9) Root raw-gap LGV obstruction.** At the root-left edge,

```text
Δ = M_{1/3} - M_{1/2},
det Δ = (x+1)^2 [4(x+1)(x+2) - (2x+3)^2] = -(x+1)^2.
```

Hence the raw positive `2×2` gap matrix cannot itself be an ordinary
two-source/two-sink planar path matrix with nonnegative weights in the standard
noncrossing order. This is a bounded route obstruction, **not** a counterexample to
Local TP2.

## Explicitly not claimed

- `C-LOCAL-TP2` itself. It remains `PROOF_CANDIDATE` with `public_evidence: PARTIAL`.
- The strict adjacent determinant `F_v(n) = H(D_v)[n+1] H(S_v)[n] - H(D_v)[n] H(S_v)[n+1] > 0`.
- Any common coefficient/`H`-grade planar network realising `S_v` and `D_v` together.
- Publication novelty for any of (T1)–(T9).
- Any continuation or campaign decision.

## Evidence

- Writer derivation: `work/TASK-LOCAL-TP2-CONTINUANT-LGV-001/w-4e8c1d7a9b3f6021/RESULT.md`
- Independent review: `reviews/local-tp2/CONTINUANT_GAP_CONE_INDEPENDENT_REVIEW_2026-09-05.md`
- Independent finite control: `reviews/local-tp2/continuant_gap_cone_independent_check.py`

```bash
python3 reviews/local-tp2/continuant_gap_cone_independent_check.py
```

The finite control is a reproduction aid for a bounded Farey range. The all-depth
content of (T1)–(T9) rests on the written induction, not on that script.
