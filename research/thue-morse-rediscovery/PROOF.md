# Exact identification

Let

```text
t_n = popcount(n) mod 2,
epsilon_n = (-1)^t_n = 1-2t_n.
```

The finite binary-product identity is

\[
\prod_{k=0}^{K-1}(1-x^{2^k})
=\sum_{n=0}^{2^K-1}\epsilon_n x^n.
\]

This follows directly by expanding the product: choosing a subset of powers `2^k` produces each integer `0<=n<2^K` exactly once via its binary expansion, with sign `(-1)^{popcount(n)}`.

At `x=1/2`, letting `K->infinity` gives the absolutely convergent identity

\[
P:=\prod_{k\ge0}(1-2^{-2^k})
=\sum_{n\ge0}\frac{\epsilon_n}{2^n}.
\]

Since `t_n=(1-epsilon_n)/2`,

\[
\begin{aligned}
C
&=\sum_{n\ge0}\frac{t_n}{2^{n+1}}\\
&=\sum_{n\ge0}\frac{1-\epsilon_n}{2^{n+2}}\\
&=\frac12-\frac14P.
\end{aligned}
\]

The binary series definition is exactly the standard definition of the Thue–Morse constant, so the identification is definition-level rather than decimal matching.

## Exact tail certificate

For the prefix through `n=N-1`,

\[
0\le C-C_N
=\sum_{n\ge N}\frac{t_n}{2^{n+1}}
\le\sum_{n\ge N}\frac1{2^{n+1}}
=2^{-N}.
\]

Thus arbitrarily many digits can be certified by exact dyadic arithmetic.
