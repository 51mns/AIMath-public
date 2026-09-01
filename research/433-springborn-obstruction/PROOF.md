# Exact obstruction to Springborn companion identification

Public export of the fixed writer proof underlying canonical claim `C-433-SPRINGBORN-OBSTRUCTION`.

## Frozen definitions

The fixed-433 construction defines

\[
w_k=C_0B^k,\qquad
K(w_k)=
\begin{pmatrix}M_k&U_k\\U_k&V_k\end{pmatrix},
\]

with `w_k` the canonical finite regular continued fraction of `M_k/U_k`. Hence

\[
x_k:=\frac{U_k}{M_k}=[0;w_k].
\]

The fixed beginning of `C0` is

\[
(2,1,1,2,2,1,1,2,\mathbf 4,\ldots).
\]

Springborn defines the approximation constant of a rational `x` by

\[
C(x)=\inf_{a/b\in\mathbb Q,\ a/b\ne x} b^2|x-a/b|.
\]

Springborn's Theorem 2.2 states that a rational number is a Markov fraction or a companion of a Markov fraction if and only if its approximation constant is at least `1/3`.

## Proposition

For every integer `k >= 0`,

\[
\boxed{C(U_k/M_k)<1/4}.
\]

Hence `U_k/M_k` is neither a Markov fraction nor a left or right Springborn companion of any Markov fraction. The same exclusion holds for every integer-affine image `\pm U_k/M_k+n`.

## Proof

For all `k`,

\[
x_k=[0;2,1,1,2,2,1,1,2,4,\ldots].
\]

Take the fixed convergent before the displayed partial quotient `4`:

\[
c=[0;2,1,1,2,2,1,1,2]=\frac{75}{194}.
\]

The previous convergent is `29/75`. Write the remaining complete quotient as `t_k`. Since it starts with the positive partial quotient `4` and has further positive terms,

\[
t_k>4.
\]

The standard convergent identity gives

\[
x_k=\frac{75t_k+29}{194t_k+75}.
\]

Since `75*75-29*194=-1`,

\[
194^2\left|x_k-\frac{75}{194}\right|
=\frac{194}{194t_k+75}
<\frac1{t_k}
<\frac14.
\]

The rational `75/194` differs from `x_k`, so it is an admissible competitor in the infimum defining `C(x_k)`. Therefore

\[
C(x_k)
\le 194^2\left|x_k-\frac{75}{194}\right|
<\frac14<\frac13.
\]

Springborn Theorem 2.2 now excludes `x_k` from both classes in that theorem. This holds for every `k`, not merely the cases emitted by the verifier.

The approximation constant is invariant under the integer-affine symmetries used there, `x -> \pm x+n`; hence every such image of `x_k` also has approximation constant below `1/3` and is likewise excluded.

## Boundary

This is a formula-level obstruction to the direct Springborn companion identification and its integer-affine symmetry orbit. It does not assert an unconstrained `PGL_2(Z)` orbit exclusion. Publication novelty is not established.

**Provenance:** writer fixed commit `5130ada104d4c71e68b2b56811210d510d83d831`; independent review fixed commit `24569ada8f0cb233e0edd2af2b61b48cec32863a`.
