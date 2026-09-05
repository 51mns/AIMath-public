<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# TASK-LOCAL-TP2-CONTINUANT-LGV-001 — continuant gap-cone reduction

Worker: `w-4e8c1d7a9b3f6021`  
Task: `TASK-LOCAL-TP2-CONTINUANT-LGV-001`  
Exact acquisition base: `ffdb21ca682b9f834a08c9860bfa3147c9395950`  
Lock activation main: `d0a1781084f6579531a1f98c1f892a1d9eb33f95`

## Decision

**Outcome candidate: `STRUCTURAL_REDUCTION` / PARTIAL.**

The bounded gate produced a genuine all-depth algebraic reduction, but it did not construct the final common coefficient-grade planar network required to prove `C-LOCAL-TP2`.

The main positive result is:

1. the Farey-recursive continued-fraction splice admits a uniform 2x2 transfer-matrix formula;
2. all Farey boundary gap matrices satisfy a subtraction-free cone invariant;
3. this implies subtraction-free all-depth `x`-polynomial formulas for both canonical differences

```text
S_v = U_v - C_v,
D_v = V_v - U_v;
```

4. however, the most direct idea of using the positive 2x2 continuant gap matrix itself as an LGV path matrix is impossible already at the root, because that matrix has determinant `-(x+1)^2`.

Thus Gate 1 passes, while the direct Gate-2 embedding is killed. A more refined marked/coefficient-grade common embedding or switching theorem would still be needed for the frozen strict adjacent determinant.

This result does **not** prove or refute Local TP2.

## Frozen target

The canonical target remains

```text
F_v(n)
= H(D_v)[n+1] H(S_v)[n]
- H(D_v)[n]   H(S_v)[n+1] > 0
```

for every canonical Farey vertex `v` and every

```text
0 <= n <= deg_x(S_v),
```

including the terminal zero-extension index.

No stronger all-column TP2, PF2, log-concavity, or ratio theorem is asserted here.

## 1. Continuant matrix convention

For a continued-fraction entry `z`, write

```text
A(z) = [ z  1 ]
       [ 1  0 ].
```

For a word `w=[a_1,...,a_k]`, put

```text
M(w) = A(a_1) ... A(a_k).
```

Its upper-left entry is the continuant numerator. For the canonical Farey word attached to `t`, write `M_t=M(w_t)` and `G_t=(M_t)_{11}`.

The external continued-fraction construction used by the refresh lane attaches such a positive Laurent/polynomial word to every Farey parameter, with numerator equal to the deformed squared Markov polynomial. The argument below uses only that frozen recursion and elementary 2x2 matrix algebra.

## 2. The splice collapses to one fixed matrix

Set

```text
J = [ 1  0 ]
    [ 1 -1 ]
```

and note the exact identity

```text
A(1) A(z-1) = J A(z).
```

Let

```text
m = 3(x+1),
Q = A(3x+2) J
  = [ m -1 ]
    [ 1  0 ].
```

Because every `A(z)` is symmetric, reversing a continued-fraction word transposes its transfer matrix. Therefore the generic interior Farey splice from Definition 3.1 becomes

```text
M_t = M_r^T Q M_s^T
```

whenever `t=r⊕s`.

The two boundary recursions can be absorbed into the same formula by introducing virtual matrices

```text
M_0 = [ 1  0 ]
      [-x  1 ],

M_1 = [x+2 x+1]
      [ 1    1 ].
```

Indeed,

```text
M_0^T Q = A(2x+2) J,
Q M_1^T = A(3x+2) A(x+2),
```

so the uniform identity

```text
M_t = M_r^T Q M_s^T
```

holds for all Farey triples, including the root and the two extreme boundary chains.

For the root this gives

```text
M_(1/2)
= [2x^2+6x+5  2x+2]
  [x+2          1    ],
```

so the upper-left entry agrees with the frozen root polynomial.

## 3. Fixed skew and positive right transfer

Write

```text
M_t = [N_t P_t]
      [R_t I_t].
```

For every genuine Farey vertex, the standard generalized-Markov matrixization gives the fixed skew relation

```text
P_t - R_t = x.
```

Equivalently, all genuine `M_t` have the same skew-symmetric part. Hence any difference of two genuine Farey matrices is symmetric.

Define

```text
Z_t = Q M_t^T
    = [m N_t - P_t   m R_t - I_t]
      [N_t           R_t          ].
```

All entries of `M_t` are coefficientwise nonnegative because they are continuants in positive continued-fraction entries.

The entries of `Z_t` are also coefficientwise nonnegative. For example, if the last continued-fraction entry is `a`, the continuant recurrence gives

```text
N_t = a P_t + P_prev,
R_t = a I_t + I_prev,
```

and therefore

```text
m N_t - P_t = (m a - 1) P_t + m P_prev,
m R_t - I_t = (m a - 1) I_t + m I_prev.
```

The canonical entries have positive integer coefficients and constant term at least 1; in the canonical words used here, `m a - 1` is coefficientwise nonnegative. Thus `Z_t >= 0` coefficientwise.

## 4. The Farey boundary gap cone

For a symmetric polynomial 2x2 matrix `Delta`, define the cone condition

```text
Delta >= 0 coefficientwise,
Q Delta >= 0 coefficientwise.
```

### Interior propagation

Assume `t=r⊕s` and both parent-side boundary gaps are in the cone:

```text
Delta_r = M_t - M_r,
Delta_s = M_t - M_s.
```

Let the left child be `ell=r⊕t`. Using the uniform splice formula and symmetry of the gaps,

```text
M_ell - M_t
= M_r^T Q (M_t-M_s)^T
= M_r^T (Q Delta_s).
```

Both factors on the right are coefficientwise nonnegative, so the new gap is coefficientwise nonnegative. Moreover

```text
Q(M_ell-M_t)
= (Q M_r^T)(Q Delta_s)
= Z_r (Q Delta_s),
```

which is also coefficientwise nonnegative. Hence `M_ell-M_t` is in the cone. The other boundary gap

```text
M_ell-M_r = (M_ell-M_t) + (M_t-M_r)
```

is a sum of cone elements.

For the right child `u=t⊕s`, similarly

```text
M_u - M_t = Delta_r Z_s,
Q(M_u-M_t) = (Q Delta_r) Z_s,
```

so both right-child boundary gaps remain in the cone.

Thus the cone propagates throughout every interior branch.

### Extreme left boundary

The virtual matrix `M_0` itself is not coefficientwise nonnegative, so the chain `1/n` needs a separate exact argument rather than being hidden inside the interior induction.

Put

```text
R = M_0^T Q
  = [rho -1]
    [ 1   0],

rho = 2x+3.
```

Let

```text
B_n = M_(1/n) - M_(1/(n-1)).
```

The boundary recursion gives

```text
B_(n+1) = R B_n.
```

Define `P_0=1`, `P_1=rho`,

```text
P_(j+1) = rho P_j - P_(j-1).
```

The first gap yields, and induction preserves,

```text
B_n
= (x+1)
  [P_(n-1) P_(n-2)]
  [P_(n-2) P_(n-3)].
```

The apparent subtraction in the recurrence does not create coefficient signs. Indeed

```text
sum_(j>=0) P_j t^j
= 1 / (1-rho t+t^2)
= 1 / ((1-t)^2-(2x+1)t),
```

so explicitly

```text
P_n
= sum_(k=0)^n binom(n+k+1,n-k) (2x+1)^k,
```

which is coefficientwise nonnegative.

Furthermore

```text
m P_j - P_(j-1)
= P_(j+1) + x P_j >= 0,
```

so `Q B_n` is also coefficientwise nonnegative. Hence the extreme-left boundary gaps satisfy the same cone condition. The right virtual boundary has both `M_1>=0` and `Q M_1^T>=0`, and the root gaps can be checked directly, so the induction seeds every Farey interval.

### Gap-cone conclusion

For every canonical Farey triple `r<t<s`, both boundary differences

```text
M_t-M_r,
M_t-M_s
```

are symmetric cone elements. In particular, the upper-left entry of every degree-oriented parent-to-child gap is a subtraction-free polynomial in `x`.

This is an all-depth written induction, not an inference from the finite verifier.

## 5. Consequence for S_v

The lower-degree child `U_v` is one of the two Farey children of `C_v=G_t`. Therefore

```text
S_v = U_v-C_v
```

is exactly the upper-left entry of a cone-positive child/parent gap matrix. Consequently

```text
S_v in Z_{>=0}[x]
```

for every canonical Farey vertex, with an explicit subtraction-free continuant/gap representation supplied by the induction above.

This closes the first half of Gate 1.

## 6. Exact factorization for D_v

For a Farey triple with boundary polynomials

```text
A=G_r, B=G_s, C=G_t,
```

the two child mutation formulas are

```text
L = 3(x+1) A C - x(A+C) - B,
R = 3(x+1) B C - x(B+C) - A.
```

Subtracting gives the exact factorization

```text
R-L
= (B-A) [3(x+1)C + 1 - x].
```

The higher-degree child is attached to the higher-degree Farey boundary, so after the canonical degree orientation, if `H_v` and `K_v` denote respectively the higher- and lower-degree boundary polynomials, then

```text
D_v
= (H_v-K_v) [3(x+1)C_v + 1 - x].
```

The first factor `H_v-K_v` is the upper-left entry of a boundary gap from the cone theorem, hence coefficientwise nonnegative. The second factor is coefficientwise positive because `C_v` is coefficientwise nonnegative with positive constant term, while the only explicit subtraction is the single `-x` against the positive `3(x+1)C_v` contribution.

Therefore

```text
D_v in Z_{>=0}[x]
```

for every canonical Farey vertex, again with an all-depth subtraction-free factorization.

Thus **Gate 1 passes for both `S_v` and `D_v`.**

## 7. Direct gap-matrix LGV architecture is impossible

The gap-cone theorem does **not** automatically provide the common planar network required by the Task.

At the root-left edge, the exact gap matrix is

```text
Delta
= M_(1/3) - M_(1/2)
= [4(x+1)^2(x+2)   (x+1)(2x+3)]
  [(x+1)(2x+3)     x+1           ].
```

Every entry is coefficientwise nonnegative, but

```text
det(Delta) = -(x+1)^2.
```

A 2-source/2-sink planar network path matrix with nonnegative weights and the usual noncrossing source/sink order has nonnegative determinant by the LGV mechanism. Therefore `Delta` itself cannot be that positive planar path matrix.

This gives an exact bounded no-go:

> The most direct architecture “take the positive 2x2 continuant gap matrix, degree-lift it, and use it as the common LGV path matrix” is impossible already at the root.

This obstruction is **not** a counterexample to Local TP2, and it does not rule out a more refined common network whose path matrix is built from the `H`-coefficient families rather than directly from the raw continuant gap matrix.

## 8. What remains

The residual core is now narrower than at Task start.

Already established in this lane:

```text
Farey continued-fraction recursion
 -> uniform transfer matrix M_t=M_r^T Q M_s^T
 -> all-depth positive gap cone
 -> subtraction-free S_v
 -> exact subtraction-free factorization of D_v.
```

Still missing:

```text
S_v,D_v subtraction-free x-objects
 -> one compatible coefficient/H-grade common network or marked switching theorem
 -> LGV/cancellation at the frozen adjacent H minor
 -> strict positive family for every n, including terminal index.
```

The separate literature lane already found that ordinary weight-preserving snake/fence skein machinery does not supply the required one-unit marked exponent-grade transfer. The present algebraic reduction therefore identifies that marked/graded compatibility as the precise remaining mathematical bottleneck rather than merely saying “find a network.”

## 9. Exact finite verifier and negative control

`splice_verifier.py` independently checks the algebraic formulas on a finite generated Farey tree and includes the root negative control.

A successful replay prints

```text
PASS
farey_words=511
subtraction_free_sibling_checks=127
finite_local_tp2_sanity_checks=127
direct_gap_network_obstruction=det(M_1/3-M_1/2)=-(x+1)^2
```

The finite Local-TP2 checks in that program are sanity checks only. They are not used to justify the all-depth gap-cone induction and cannot prove the frozen universal theorem.

The verifier also reproduces the frozen root profiles

```text
H(S) = [40, 32, 16, 4]
H(D) = [164, 138, 80, 30, 6]
F    = [272, 352, 160, 24].
```

## Claim / review boundary

- `C-LOCAL-TP2` remains `PROOF_CANDIDATE`.
- No universal proof of `F_v(n)>0` is claimed.
- No counterexample to Local TP2 is claimed.
- The new all-depth gap-cone/subtraction-free reduction is theorem-like internal mathematics and should be independently reviewed before it is used as a load-bearing successor premise.
- Failure of the direct gap-matrix LGV architecture is a bounded route obstruction only.
- Because the Campaign was reopened for exactly this bounded Task, a fresh continuation decision is required after this terminal Outcome rather than silently extending the lane.
