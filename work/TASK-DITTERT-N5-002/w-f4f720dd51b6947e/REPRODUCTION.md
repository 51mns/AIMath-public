<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# TASK-DITTERT-N5-002 — fresh Z2 reproduction

## Scope and independence

Task: `TASK-DITTERT-N5-002`.

Public base at task start: `71547cb5d757afaace54b558f2d0a4a49fad5656`.

Worker: `w-f4f720dd51b6947e`.

Frozen target statement: up to independent row and column permutations, a global Dittert maximizer in `K_5` cannot have exactly two zero entries in distinct rows and distinct columns.

The existing AIMath writer proof `research/dittert-n5-z2/PROOF.md` was not read, and writer code/generated logs were not imported. The public claim README was read before the derivation freeze; therefore this is **not information-blind**: that README already disclosed the high-level skeleton “zero-entry KKT chamber + two positive-entry stationarity equalities give a sign contradiction.” The exact coordinates, identities, factorisations and sign certificates below were derived independently from the frozen statement and published Dittert/Hwang machinery.

The source premises were checked against Cheon–Wanless, *Some results towards the Dittert conjecture on permanents*, Linear Algebra Appl. 436 (2012), 791–801. Their Lemma 3.4 records Hwang's fixed-zero-pattern equalisation, and Lemma 3.6 records the first-order rule

\[
\phi(A)\ge \phi_{ij}(A),
\]

with equality when `a_ij>0`.

## 1. Canonical seven-parameter face

Place the two zeros at `(1,1)` and `(2,2)`. Since rows 3,4,5 have the same zero pattern, and columns 3,4,5 have the same zero pattern, fixed-zero-pattern equalisation allows a hypothetical global maximizer to be replaced, without losing global maximality, by

\[
A=\begin{pmatrix}
0&a&b&b&b\\
c&0&d&d&d\\
e&f&g&g&g\\
e&f&g&g&g\\
e&f&g&g&g
\end{pmatrix},
\qquad a,b,c,d,e,f,g>0,
\]

with

\[
a+c+3(b+d+e+f)+9g=5.
\]

The strict positivity of all seven parameters follows from the target support assumption: these are exactly the two zero entries.

The row sums are

\[
r_1=a+3b,\quad r_2=c+3d,\quad r_3=r_4=r_5=e+f+3g,
\]

and the column sums are

\[
s_1=c+3e,\quad s_2=a+3f,\quad s_3=s_4=s_5=b+d+3g.
\]

For

\[
\phi_{ij}(A)=\prod_{k\ne i}r_k+\prod_{\ell\ne j}s_\ell-\operatorname{per}A(i\mid j),
\]

the first-order maximizer condition gives `phi_ij = phi(A)` on positive entries and `phi_ij <= phi(A)` on zero entries.

## 2. Exact zero-entry chamber

The four permanent minors needed are

\[
\operatorname{per}A(1\mid1)=18dfg^2,
\]

\[
\operatorname{per}A(1\mid2)=6g^2(cg+3de),
\]

\[
\operatorname{per}A(2\mid2)=18beg^2,
\]

\[
\operatorname{per}A(2\mid1)=6g^2(ag+3bf).
\]

Since `(1,1)` is zero and `(1,2)` is positive,

\[
\phi_{11}-\phi_{12}
=(s_2-s_1)s_3^3+6g^2\bigl(cg+3d(e-f)\bigr)\le0.
\]

Since `(2,2)` is zero and `(2,1)` is positive,

\[
\phi_{22}-\phi_{21}
=(s_1-s_2)s_3^3+6g^2\bigl(ag+3b(f-e)\bigr)\le0.
\]

Adding cancels the column-product terms:

\[
6g^2\left((a+c)g+3(d-b)(e-f)\right)\le0.
\]

Introduce mean/antisymmetric coordinates

\[
u=\frac{a+c}{2},\quad
v=\frac{b+d}{2},\quad
w=\frac{e+f}{2},
\]

\[
\alpha=\frac{a-c}{2},\quad
\beta=\frac{d-b}{2},\quad
\gamma=\frac{e-f}{2}.
\]

Then

\[
a=u+\alpha,\ c=u-\alpha,\ b=v-\beta,\ d=v+\beta,
\]

\[
e=w+\gamma,\ f=w-\gamma,
\]

and positivity gives

\[
u>0,\quad v>0,\quad w>0,\quad g>0,
\]

\[
|\alpha|<u,\quad |\beta|<v,\quad |\gamma|<w.
\]

The zero-entry inequality becomes

\[
\boxed{ug+6\beta\gamma\le0}.
\]

In particular `beta*gamma<0`.

The simultaneous permutation exchanging rows 1 and 2 and columns 1 and 2 preserves the support class and the Dittert functional, while sending

\[
(\alpha,\beta,\gamma)\mapsto(-\alpha,-\beta,-\gamma).
\]

Hence, without loss of generality, set

\[
\beta=x>0,\qquad \gamma=-y<0.
\]

Then

\[
0<x<v,\qquad 0<y<w,
\]

and the chamber is

\[
\boxed{H:=6xy-ug\ge0}.
\]

## 3. Two positive-entry stationarity equations

Let

\[
\Phi(A)=\prod_i r_i+\prod_j s_j-\operatorname{per}A.
\]

Define the positive cubic polynomials

\[
P(t)=27g^3+48g^2t+36gt^2+8t^3,
\]

\[
C(t)=27g^3+54g^2t+32gt^2+8t^3.
\]

Because `b=v-beta` occurs in three equal positive entries and `d=v+beta` occurs in three equal positive entries,

\[
\frac{\partial\Phi}{\partial\beta}
=3(\phi_d-\phi_b).
\]

Likewise,

\[
\frac{\partial\Phi}{\partial\gamma}
=3(\phi_e-\phi_f).
\]

All four classes are positive, so positive-entry stationarity requires both derivatives to vanish. Exact expansion gives

\[
0=\frac{\partial\Phi}{\partial\beta}
=6P(w)\alpha-18C(w)\beta-36g^2u\gamma-72g\beta\gamma^2,
\]

\[
0=\frac{\partial\Phi}{\partial\gamma}
=6P(v)\alpha-36g^2u\beta-18C(v)\gamma-72g\beta^2\gamma.
\]

No other positive-entry stationarity equation is needed.

## 4. The beta equation forces alpha > 0

Substitute `beta=x`, `gamma=-y` into the first equation:

\[
6P(w)\alpha
=18\left(C(w)x-2g^2uy+4gxy^2\right).
\]

Write the bracket as

\[
B_+=C(w)x-2g^2uy+4gxy^2.
\]

Using `H=6xy-ug`, the following is an exact identity:

\[
\boxed{
B_+=x\left(C(w)-8gy^2\right)+2gyH.
}
\]

Moreover,

\[
\begin{aligned}
C(w)-8gy^2
={}&27g^3+54g^2w+24gw^2+8w^3\\
&+8g(w-y)(w+y).
\end{aligned}
\]

Every displayed term is nonnegative, and the first four terms are strictly positive because `g,w>0`; also `w-y>0`. Thus

\[
C(w)-8gy^2>0.
\]

Since `x>0`, `g>0`, `y>0`, and `H>=0`, it follows that

\[
B_+>0.
\]

Since `P(w)>0`, the beta-stationarity equation forces

\[
\boxed{\alpha>0}.
\]

## 5. The gamma equation forces alpha < 0

The second stationarity equation becomes

\[
6P(v)\alpha
=18\left(2g^2ux-C(v)y-4gx^2y\right).
\]

Set

\[
B_-=2g^2ux-C(v)y-4gx^2y.
\]

Its negative has the exact decomposition

\[
\boxed{
-B_-=y\left(C(v)-8gx^2\right)+2gxH.
}
\]

Also,

\[
\begin{aligned}
C(v)-8gx^2
={}&27g^3+54g^2v+24gv^2+8v^3\\
&+8g(v-x)(v+x).
\end{aligned}
\]

Again every term is nonnegative and the first four are strictly positive; `v-x>0`. Therefore

\[
C(v)-8gx^2>0,
\]

and hence

\[
-B_->0,
\qquad B_-<0.
\]

Because `P(v)>0`, gamma-stationarity forces

\[
\boxed{\alpha<0}.
\]

## 6. Contradiction and target conclusion

The same real number `alpha=(a-c)/2` cannot be both positive and negative. Therefore there is no positive seven-parameter stationary point satisfying the necessary zero-entry chamber.

Fixed-zero-pattern equalisation says that if a global Dittert maximizer with exactly the two independent zeroes existed, there would be a global maximizer in this seven-parameter form. Such a maximizer would have to satisfy the zero-entry inequalities and all positive-entry stationarity equalities. The contradiction above rules this out.

Therefore:

\[
\boxed{
\text{No global Dittert maximizer in }K_5
\text{ has exactly two zeroes in distinct rows and columns.}
}
\]

This reproduces the frozen `N5-Z2-MATCHING` support-orbit exclusion.

## 7. Verifier boundary

Two executable checks are retained and evaluated separately from the proof.

### Chamber regression checker

`verify_chamber_identity.py` uses exact `Fraction` arithmetic and brute-force permanents on asymmetric fixtures. It is useful regression evidence but finite fixtures alone do not prove the theorem.

### Universal symbolic identity checker

`verify_stationarity_contradiction.py` is the load-bearing algebra checker. It uses only the Python standard library and a small sparse-polynomial implementation. It reconstructs

- all row and column sums,
- the full 5x5 permanent,
- the Dittert functional,
- the formal derivatives with respect to `beta` and `gamma`,
- their equality to `3(phi_d-phi_b)` and `3(phi_e-phi_f)`,
- the zero-entry chamber identity,
- both sign-certificate decompositions,
- both positive `C(t)-8g z^2` decompositions.

The checker compares sparse-polynomial coefficient dictionaries exactly; it does not infer a universal identity from random or finite sample agreement.

Local command:

```bash
python3 work/TASK-DITTERT-N5-002/w-f4f720dd51b6947e/verify_stationarity_contradiction.py
```

Local result:

```text
PASS: exact universal stationarity-contradiction identities
```

Local exit code: `0`.

Verifier SHA-256 before upload:

`1c5dbacbca5fc08a48553ca5ad09dc3b93453b68e9e7966eff3e3c5b20afd630`.

The executable checker verifies the algebraic identities. The mathematical implication from those identities to the theorem is the human sign argument in Sections 4–6; checker success is not treated as theorem acceptance by itself.

## 8. Outcome and evidence boundary

Worker result: **full fresh reproduction of the frozen Z2 exclusion, unreviewed**.

This worker does not change the canonical claim level. The public claim was already `INDEPENDENTLY_REPRODUCED`; this contribution is additional reproduction evidence only after repository CI and any required independent intake.

Independence boundary:

- existing AIMath writer `PROOF.md`: not read;
- existing AIMath writer code: not imported;
- existing AIMath writer generated logs: not imported;
- public README high-level proof skeleton: seen before the derivation freeze, so information-blind I3-style independence is **not** claimed;
- exact derivation and verifier implementation: fresh in this worker lane.

Publication novelty is not assessed and no novelty claim is made.
