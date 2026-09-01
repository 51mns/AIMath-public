# Exact fixed-transformation identification

Public export of the accepted proof underlying `C-433-EXISTING-THEORY-IDENTIFICATION`.

## Theorem

For every integer `k >= 0`,

\[
\boxed{\frac{U_k}{M_k}=\frac45-\mu\!\left(\frac{9k+8}{15k+13}\right)}.
\]

Write

\[
\mu\!\left(\frac{9k+8}{15k+13}\right)=\frac{p_k}{M_k}.
\]

Then equivalently

\[
\boxed{5p_k=4M_k-5U_k}.
\]

## 1. Source-defined Farey/Cohn ray

Let

\[
s=\frac35,\qquad t_0=\frac23,\qquad t_{n+1}=s\oplus t_n.
\]

Induction on the Farey mediant gives

\[
\boxed{t_n=\frac{3n+2}{5n+3}}.
\]

For the reviewed `a=0` Cohn normalization,

\[
S=C_s(0)=\begin{pmatrix}179&433\\463&1120\end{pmatrix},\qquad
C_0=C_{t_0}(0)=\begin{pmatrix}12&29\\31&75\end{pmatrix}.
\]

Along this fixed ray,

\[
\boxed{C_{t_n}(0)=S^nC_0}.
\]

Since

\[
\det S=1,\qquad \operatorname{tr}S=1299,
\]

Cayley--Hamilton gives entrywise

\[
z_{n+2}=1299z_{n+1}-z_n.
\]

For the top-right entries `q_n`,

\[
q_0=29,\qquad q_1=37666.
\]

These are exactly the initial data of the fixed AIMath recurrence, so uniqueness gives

\[
\boxed{q_n=x_n}.
\]

Therefore at `n=2+3k`,

\[
q_{2+3k}=M_k,\qquad t_{2+3k}=\frac{9k+8}{15k+13}.
\]

Hence the source Markov fraction has the same denominator:

\[
\mu(t_{2+3k})=\frac{p_k}{M_k}.
\]

## 2. The source numerator and canonical modular root

Put

\[
Y_k=x_{1+3k}.
\]

The reviewed cross-determinant identity on the oriented local Markov-fraction triple gives

\[
\boxed{p_{1+3k}M_k-p_kY_k=433}.
\]

Modulo `M_k`,

\[
-p_kY_k\equiv433\pmod{M_k}.
\]

The fixed AIMath root representative is

\[
r_k\equiv433Y_k^{-1}\pmod{M_k},\qquad 0\le r_k<M_k.
\]

Thus

\[
r_k\equiv-p_k\pmod{M_k}.
\]

The reviewed source normalization places the Markov fraction in the fundamental domain `0<p_k/M_k<1/2`, so the fixed representative is

\[
\boxed{r_k=M_k-p_k}.
\]

## 3. Factor-5 CRT sign flip

The accepted fixed-433 identities give

\[
M_k\equiv5\pmod{25},\qquad Y_k\equiv1\pmod5,\qquad U_k\equiv2\pmod5,
\]

and, with `N_k=M_k/5`,

\[
Y_kU_k\equiv433\pmod{N_k}.
\]

Reducing the root relation modulo `N_k` and using invertibility of `Y_k` gives

\[
U_k\equiv r_k\pmod{N_k}.
\]

Also `N_k\equiv1 (mod 5)` and `r_k\equiv3 (mod 5)`, hence

\[
r_k-N_k\equiv2\equiv U_k\pmod5.
\]

Because `gcd(5,N_k)=1`, CRT yields

\[
U_k\equiv r_k-N_k\pmod{M_k}.
\]

The representative ranges are decisive: `r_k>M_k/2`, so

\[
0<r_k-N_k<M_k,
\]

and the continuant construction has `0<U_k<M_k`. Therefore

\[
\boxed{U_k=r_k-\frac{M_k}{5}}.
\]

Using `r_k=M_k-p_k`,

\[
U_k=M_k-p_k-\frac{M_k}{5}=\frac{4M_k}{5}-p_k,
\]

so

\[
\boxed{5p_k=4M_k-5U_k},
\]

and division by `M_k` proves the theorem.

## 4. Transformation boundary

Define

\[
R_5(x)=\frac45-x.
\]

Then

\[
R_5(U_k/M_k)=\mu((9k+8)/(15k+13)).
\]

A projective matrix is

\[
\begin{pmatrix}-5&4\\0&5\end{pmatrix},\qquad\det=-25.
\]

Thus `R_5` lies in `PGL_2(Q)` but not in `PGL_2(Z)`. This is exactly why the identification does not contradict the separate Springborn integer-affine obstruction.

## 5. Finite exact controls

The public verifier checks `k=0..10` with exact arithmetic, including:

- continuant `M_k,U_k,V_k`;
- Farey label `(9k+8)/(15k+13)`;
- source Cohn matrix and numerator `p_k`;
- the cross determinant `433`;
- `r_k=M_k-p_k`;
- `U_k=r_k-M_k/5`;
- `5p_k=4M_k-5U_k`;
- the fixed Möbius orbit.

These are finite fingerprints only. The universal argument is Sections 1--3.

## Scope

This does not say `U_k/M_k` itself is a Springborn Markov fraction or companion; the separate obstruction says it is not. It does not attribute an unverified formula to inaccessible literature and does not establish publication novelty.

**Provenance:** writer fixed commit `423a4a1cae9efa52d97240f5bae21ecad1bae19c`; independent review fixed commit `cd098e8ad4f6c69bbe6bfa6a134dfda3e8aa41e6`.
