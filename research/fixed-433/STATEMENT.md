# Frozen statement: fixed-433 bounded-energy family

**Claim ID:** `C-ROOT-433`

**Canonical public level:** `INDEPENDENTLY_REPRODUCED`

Define

\[
x_0=29,\qquad x_1=37666,\qquad
x_{n+1}=1299x_n-x_{n-1}\quad(n\ge1)
\]

and

\[
M_k=x_{2+3k}\quad(k\ge0).
\]

Let

```text
C0 = 2,1,1,2,2,1,1,2,4,1,1,3,3,1,1,4,2,1,1,2,2,1,1,2
B  = 2,1,1,1,1,2,2,1,1,2,2,1,1,2,4,1,1,3,3,1,1,4,2,1,1,2,2,1,1,2
```

and `w_k = C0 B^k`. For

\[
K(a)=\begin{pmatrix}a&1\\1&0\end{pmatrix},\qquad
K(w_k)=\begin{pmatrix}M'_k&U_k\\U'_k&V_k\end{pmatrix},
\]

the accepted statement is:

> For every integer `k >= 0`, `M'_k=M_k`, the word `w_k` is the canonical
> finite regular continued fraction of `M_k/U_k`, and `U_k` is neither member
> of the designated canonical root pair
> \[
> \{r_k,M_k-r_k\},\qquad
> r_k\equiv433\,x_{1+3k}^{-1}\pmod {M_k}.
> \]
> Moreover `U_k^2 = -1 (mod M_k)` and `E_{M_k}(U_k)=4`. Consequently
> `g(M_k) <= 4` on an infinite sequence of Markov numbers.

The consequence is only that the proposed `g(m) -> infinity` growth route is
false. It does not assert a global upper bound for `g`, does not settle every
possible root-energy argument, and does not establish publication novelty.
