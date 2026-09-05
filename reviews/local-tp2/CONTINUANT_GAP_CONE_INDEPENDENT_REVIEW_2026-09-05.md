<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Local TP2 continuant gap-cone independent mathematical review

Date: 2026-09-05  
Campaign: `CAM-LOCAL-TP2`  
Task under review: `TASK-LOCAL-TP2-CONTINUANT-LGV-001`  
Exact writer research head: `0f2d9f6fb7f3331ad289cc949b1191d7cbb2fb0a`  
Writer artifact reviewed: `work/TASK-LOCAL-TP2-CONTINUANT-LGV-001/w-4e8c1d7a9b3f6021/RESULT.md`  
Public main at review start after lock release: `35363613c829f25afc4ead099e0286917287bdfe`

## Decision

**PASS for the scoped theorem-like structural reduction, with explicit proof clarifications recorded below.**

I independently rederived the three load-bearing pieces requested for review:

1. the all-depth Farey boundary gap-cone induction;
2. the exceptional extreme-left `1/n` chain;
3. the exact `D_v` factorisation together with the degree orientation needed to make its first factor a positive boundary gap.

I also independently checked the root determinant obstruction to using the raw positive gap matrix itself as an ordinary nonnegative planar LGV path matrix.

This review does **not** prove `C-LOCAL-TP2`. It does not construct the missing common coefficient-grade network, does not prove the strict adjacent `H` minor, and does not change claim or Campaign state. Its PASS is only for using the gap-cone / subtraction-free `S_v,D_v` reduction as a scoped mathematical premise.

Two points are compressed in the writer note and should be made explicit before the reduction is reused as load-bearing prose:

- `B_{n+1}=R B_n` on the extreme `1/n` chain uses the fixed-skew invariant to cancel transpose terms; it does not follow from the boundary recursion alone.
- the orientation in the `D_v` factorisation is justified uniformly by the exact degree rank `deg_x G_{p/q}=p+q-1` and the Farey interval genealogy.

Both missing explanations admit short all-depth proofs, supplied below; I found no mathematical contradiction in the scoped result.

## Independence disclosure

This was a separate review session, but it is **not** statistically independent evidence merely because it used a separate session.

- The reviewer is GPT-5.6 Sol, the same model family recorded for the writer lane.
- The public writer `RESULT.md` and `splice_verifier.py` were read before this review derivation was completely frozen, so this was not a blind derivation.
- The writer verifier was not imported or executed as review evidence.
- A separate finite checker was written from scratch from the primary-source Farey continued-fraction recursion and is committed as `reviews/local-tp2/continuant_gap_cone_independent_check.py`.
- The universal PASS below rests on written algebra/induction, not on that finite checker.

Accordingly, this is an independent mathematical review in the Village workflow sense, with correlated-model/context limitations explicitly retained.

## 1. Primary-source object map

The external recursion was checked directly against Bittmann--Jouteur--Kantarcı Oğuz--Molander--Yıldırım, *A Mirror deformation of Markov Numbers*, arXiv:2602.14802v1, Definition 3.1.

After writing `x=q+q^{-1}`, the four source cases are exactly:

- root: `[2x+2,x+2]`;
- `r=0`: `[2x+2,1,b_n-1,b_{n-1},...,b_1]`;
- `s=1`: `[a_l,...,a_1,3x+2,x+2]`;
- interior: `[a_l,...,a_1,3x+2,1,b_n-1,b_{n-1},...,b_1]`.

The same source states that the numerator is the corresponding deformed squared Markov polynomial. Thus the transfer-matrix object map used by the writer matches the primary recursion.

Set

```text
A(z) = [z 1]
       [1 0],

J = [1  0]
    [1 -1],

Q = A(3x+2) J
  = [3(x+1) -1]
    [1         0].
```

Direct multiplication gives

```text
A(1) A(z-1) = J A(z).
```

Since reversing a word transposes its transfer matrix, the source recursion gives

```text
M_t = M_r^T Q M_s^T
```

for interior Farey triples. The virtual boundary matrices

```text
M_0 = [ 1 0]
      [-x 1],

M_1 = [x+2 x+1]
      [ 1    1]
```

satisfy

```text
M_0^T Q = A(2x+2)J,
Q M_1^T = A(3x+2)A(x+2),
```

so the same formula covers the two boundary recursions and the root.

## 2. Determinant and fixed-skew invariant

All virtual matrices and `Q` have determinant one. Therefore the uniform splice recursively gives

```text
det M_t = 1
```

at every Farey vertex.

Define

```text
sigma(M) = M_12 - M_21.
```

Directly,

```text
sigma(M_0)=sigma(M_1)=sigma(M_1/2)=x.
```

The following elementary 2x2 lemma gives an all-depth proof of the fixed skew without importing the writer conclusion.

Let

```text
T = A^T Q B^T,
```

with `det A = det B = 1`. A direct expansion gives

```text
sigma(A^T Q T^T) = sigma(B),
sigma(T^T Q B^T) = sigma(A).
```

These are exactly the left- and right-mediant recursions. Starting from the root interval, interval induction therefore yields

```text
sigma(M_t)=x
```

for every genuine Farey vertex. Hence every difference of two genuine/virtual matrices occurring on a Farey edge is symmetric. This supplies the symmetry hypothesis used by the cone argument.

## 3. Positivity of `Z_t = Q M_t^T`

The primary word recursion also gives the required all-depth entry positivity directly in `x`.

The root entries lie in `Z_{>=0}[x]`. At each recursive step all entries are inherited/reversed except for fixed positive entries and one term `b_n-1`. The first and last entries of every canonical word have constant term at least 2 by an immediate Farey-tree induction, so `b_n-1` is still coefficientwise nonnegative. Thus every continued-fraction entry belongs to `Z_{>=0}[x]`.

Write

```text
M_t = [N P]
      [R I]
```

and let `a` be the last continued-fraction entry. Removing the final `A(a)` factor gives

```text
N = a P + P_prev,
R = a I + I_prev.
```

With `m=3(x+1)`, the last entry has nonnegative coefficients and constant at least 2, hence

```text
m a - 1 >= 0
```

coefficientwise. Therefore

```text
mN-P = (ma-1)P + m P_prev >= 0,
mR-I = (ma-1)I + m I_prev >= 0.
```

Together with `N,R>=0`, this proves

```text
Z_t = Q M_t^T >= 0
```

coefficientwise at every depth.

## 4. Interior gap-cone induction

For a symmetric polynomial matrix `Delta`, use the cone

```text
Delta >= 0,
Q Delta >= 0
```

coefficientwise.

For `t=r⊕s`, suppose the two boundary gaps

```text
Delta_r=M_t-M_r,
Delta_s=M_t-M_s
```

lie in the cone. For the left child `ell=r⊕t`, symmetry gives

```text
M_ell-M_t
 = M_r^T Q (M_t-M_s)^T
 = M_r^T (Q Delta_s),
```

and hence

```text
Q(M_ell-M_t)=Z_r(Q Delta_s).
```

When `r!=0`, both factors are coefficientwise nonnegative. The other left boundary gap is the sum of this new cone element and `Delta_r`.

For the right child `u=t⊕s`,

```text
M_u-M_t = Delta_r Z_s,
Q(M_u-M_t)=(Q Delta_r)Z_s,
```

so the same closure holds, including `s=1` because `Z_1=Q M_1^T>=0`.

The root gaps are directly cone-positive. Thus every branch not repeatedly touching the exceptional virtual left endpoint `0` is covered by this interior induction. The remaining extreme-left chain is handled next.

## 5. Extreme `1/n` chain

Let

```text
R_0 = M_0^T Q
    = [rho -1]
      [ 1   0],

rho=2x+3,
```

and

```text
B_n=M_(1/n)-M_(1/(n-1)),   n>=3.
```

The boundary formula is

```text
M_(1/(n+1)) = R_0 M_(1/n)^T.
```

The writer states `B_(n+1)=R_0 B_n`. The missing one-line justification is the fixed-skew invariant. Indeed

```text
B_(n+1)-R_0 B_n
 = R_0[(M_n^T-M_n)+(M_(n-1)-M_(n-1)^T)]
 = 0,
```

because every `M_j` has the same skew `x`, so the two antisymmetric parts cancel.

Define

```text
P_0=1,
P_1=rho,
P_(j+1)=rho P_j-P_(j-1).
```

The exact root-left gap is the `n=3` base case, and multiplication by `R_0` gives by induction

```text
B_n=(x+1)
    [P_(n-1) P_(n-2)]
    [P_(n-2) P_(n-3)].
```

The generating function is

```text
sum_(j>=0) P_j t^j
 = 1/(1-rho t+t^2)
 = 1/((1-t)^2-(2x+1)t),
```

so coefficient extraction gives

```text
P_n = sum_(k=0)^n binom(n+k+1,n-k)(2x+1)^k.
```

Hence every `P_n` is coefficientwise nonnegative. Finally, since `m-rho=x`,

```text
mP_j-P_(j-1)=P_(j+1)+xP_j>=0,
```

which proves `Q B_n>=0`. The other gap to the virtual endpoint is a sum of earlier cone gaps. Therefore the extreme-left chain genuinely closes the all-depth cone induction.

## 6. Consequence for `S_v`

Each canonical lower-degree child `U_v` is one of the two Farey children of `C_v`. The child-parent matrix gap is cone-positive, so its upper-left entry is coefficientwise nonnegative. Therefore

```text
S_v=U_v-C_v in Z_{>=0}[x]
```

at every canonical vertex.

No finite-depth inference is used here.

## 7. `D_v` factorisation and its orientation

For a Farey triple with boundary polynomials

```text
A=G_r, B=G_s, C=G_t,
```

the two child mutation formulas are

```text
L=3(x+1)AC-x(A+C)-B,
R=3(x+1)BC-x(B+C)-A.
```

Subtracting directly gives

```text
R-L=(B-A)[3(x+1)C+1-x].
```

The algebraic factorisation is exact. What must additionally be checked is that canonical degree orientation makes the first factor a positive previously established edge gap.

Define, for a reduced Farey parameter `p/q`,

```text
delta(p/q)=p+q-1.
```

The initial objects satisfy

```text
deg_x G_0=0=delta(0),
deg_x G_1=1=delta(1),
deg_x G_(1/2)=2=delta(1/2).
```

If `t=r⊕s`, the mutation creating `r⊕t` has leading degree

```text
deg G_r + deg G_t + 1.
```

For `r!=0` this leading term strictly dominates the subtraction terms. For the only zero-degree boundary case `r=0`, the leading coefficient from `3(x+1)G_rG_t-xG_t` is still `2` times the leading coefficient of `G_t`, so it cannot cancel. The same argument holds on the right. Therefore Farey-tree induction gives

```text
deg_x G_(p/q)=p+q-1
```

at all depths.

Consequently,

```text
deg G_(t⊕s)-deg G_(r⊕t)=deg G_s-deg G_r.
```

So the higher-degree child is attached to the higher-degree boundary exactly as required.

Moreover, every non-root Farey interval is produced by subdividing a previous interval: one endpoint is a newly created mediant and the other is one of its parents. Since the mediant degree equals the sum of the two parent degrees plus one, it is the higher-degree endpoint. Thus the oriented difference

```text
H_v-K_v
```

is precisely the upper-left entry of a previously proved cone-positive edge gap. For the initial interval `(0,1)`, the difference is separately `G_1-G_0=x+1>=0`.

Therefore the canonical orientation gives

```text
D_v=(H_v-K_v)[3(x+1)C_v+1-x].
```

The second factor is coefficientwise positive: if `C_v=sum c_j x^j` with `c_j>=0` and `c_0>=1`, then its constant coefficient is `3c_0+1`, its `x` coefficient is `3(c_0+c_1)-1>=2`, and all higher coefficients are nonnegative (with a positive new leading coefficient). Hence

```text
D_v in Z_{>=0}[x]
```

for every canonical vertex.

## 8. Direct raw-gap LGV obstruction

At the root-left edge, direct recomputation gives

```text
Delta=M_(1/3)-M_(1/2)
     = [4(x+1)^2(x+2)  (x+1)(2x+3)]
       [(x+1)(2x+3)    x+1          ].
```

Its determinant is

```text
det Delta
=(x+1)^2[4(x+1)(x+2)-(2x+3)^2]
=-(x+1)^2.
```

Thus the raw positive 2x2 gap matrix cannot itself be an ordinary two-source/two-sink planar path matrix with nonnegative weights in the standard noncrossing order. This is a valid bounded route obstruction only; it is not a counterexample to Local TP2.

## 9. Independent finite negative control

The companion script reimplements the primary-source word recursion and exact polynomial arithmetic without importing the writer verifier.

Command:

```bash
python3 reviews/local-tp2/continuant_gap_cone_independent_check.py
```

Expected output:

```text
PASS
farey_vertices=127
cone_edge_checks=254
d_factor_checks=127
extreme_chain_n=3..8
root_gap_det=-(x+1)^2
```

This finite replay checks transfer identities, fixed skew, the degree rank, cone inequalities, `D_v` factorisation/orientation, several extreme-chain cases, and the root determinant obstruction. It is a debugging/reproduction aid only and is not used to infer the all-depth claims.

## 10. Review boundary

Accepted by this review:

- uniform transfer splice from the primary continued-fraction recursion;
- determinant-one and fixed-skew invariants;
- all-depth boundary gap-cone induction;
- the extreme-left `1/n` chain after making its skew-cancellation step explicit;
- universal subtraction-free `S_v`;
- exact oriented factorisation and universal subtraction-free `D_v`;
- root no-go for the direct raw-gap LGV architecture.

Not accepted/proved by this review:

- a common coefficient/`H`-grade planar network for `S_v,D_v`;
- the strict adjacent determinant `F_v(n)>0`;
- `C-LOCAL-TP2` itself;
- publication novelty;
- any continuation decision after the terminal Task.

The remaining mathematical bottleneck is therefore still the one identified by #85: a refined common marked/coefficient-grade embedding or switching theorem. The gap-cone reduction itself is mathematically sound within the reviewed scope, but a fresh post-outcome Evaluation / continuation decision is still required before allocating another Local TP2 research Task.
