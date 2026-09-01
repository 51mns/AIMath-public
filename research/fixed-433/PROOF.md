# Proof of the fixed-433 family

This document proves universal algebraic identities. The accompanying first-three
case computation is a consistency check and is not used to infer universality.

Put `A=1299` and `T=A^3-3A=2191930002`.

## 1. Markov ray and subsequence

The seed `(5,29,433)` satisfies

\[
5^2+29^2+433^2=3\cdot5\cdot29\cdot433.
\]

Mutation of the coordinate opposite 433 replaces consecutive ray entries
`x_(n-1),x_n` by

\[
x_{n+1}=3\cdot433x_n-x_{n-1}=1299x_n-x_{n-1}.
\]

Therefore every `(433,x_n,x_(n+1))` is a Markov triple. Since
`x_1>x_0>0` and `1299>2`, induction gives `x_(n+1)>x_n`; hence the subsequence
`M_k=x_(2+3k)` is infinite and has distinct members.

The transfer matrix of the one-step recurrence has determinant one and trace
`A`. Cayley-Hamilton applied to its cube gives, for both
`y_k=x_(1+3k)` and `M_k=x_(2+3k)`,

\[
z_{k+2}=Tz_{k+1}-z_k. \tag{1}
\]

## 2. Continued-fraction word for every k

Let `P=C0 + B[:6]`. Direct inspection of the fixed 30-entry word gives

\[
P_i=P_{23-i\pmod {30}}\qquad(0\le i<30). \tag{2}
\]

Also `B=P[24:]+P[:24]`. Thus `w_k=C0 B^k` is the prefix of the
bi-infinite 30-periodic word `P` having length `24+30k`. For an index `i` in
this prefix, its reflected index is `23+30k-i`, which is congruent to `23-i`
modulo 30. Equation (2) therefore proves that every `w_k` is a palindrome.

Every digit is in `{1,2,3,4}`, every word contains 4, and the last digit is 2.
The last condition makes this the unique canonical finite regular continued
fraction rather than its alternative terminal-one expansion.

For `K(a)=[[a,1],[1,0]]`, exact multiplication gives

\[
K(B)=
\begin{pmatrix}
1909460541&738203752\\
730644200&282469461
\end{pmatrix},
\]

whose determinant is one and trace is `T`. Therefore every entry of
`K(C0)K(B)^k` satisfies (1). Its top-left entries for `k=0,1` are respectively

```text
48928105
107246981290506205
```

which equal `x_2,x_5`. Hence recurrence (1) proves its top-left entry equals
`M_k` for every `k`.

The continuant identity says the bottom-left entry is the denominator of the
convergent. Palindromicity makes that entry equal to the top-right entry `U_k`,
so `[w_k]=M_k/U_k`. Therefore

\[
E_{M_k}(U_k)=\max(w_k)=4. \tag{3}
\]

## 3. Square-root identity

Each `K(a)` is symmetric. Because `w_k` is a palindrome, its matrix product is
symmetric:

\[
K(w_k)=\begin{pmatrix}M_k&U_k\\U_k&V_k\end{pmatrix}.
\]

The word length `24+30k` is even, while `det K(a)=-1`; hence

\[
M_kV_k-U_k^2=1.
\]

It follows for every `k` that

\[
U_k^2\equiv-1\pmod {M_k}. \tag{4}
\]

## 4. Direct exclusion of both canonical roots

Set `y_k=x_(1+3k)`. The Markov equation and pairwise coprimality below show that

\[
r_k\equiv433y_k^{-1}\pmod {M_k}
\]

is a root of `-1`; the repository definition designates
`{r_k,M_k-r_k}` as the canonical pair.

First, recurrence (1) modulo 25, with the first two values, gives

\[
M_k\equiv5\pmod {25},\qquad y_k\equiv16\pmod {25}. \tag{5}
\]

Thus `N_k=M_k/5` is an integer, `N_k>866`, and `y_k=1 (mod 5)`.
Modulo 433, `T=0`, so (1) makes the nonzero residues of `M_k` alternate as
`404,428,29,5,...`. Thus 433 does not divide `M_k` or `N_k`.

The top row of `K(C0)` is `(0,2)` modulo 5 and

\[
K(B)\equiv\begin{pmatrix}1&2\\0&1\end{pmatrix}\pmod5.
\]

Consequently

\[
U_k\equiv2\pmod5. \tag{6}
\]

All three sequences `y_k,M_k,U_k` satisfy (1). Exact substitution at `k=0,1`
therefore proves the all-`k` linear identity

\[
2165y_k=362421M_k-937445U_k. \tag{7}
\]

Multiply (7) by `U_k`, use `U_k^2=M_kV_k-1`, and divide by 5:

\[
433y_kU_k
=N_k(362421U_k-937445V_k)+187489.
\]

Since `187489=433^2` and 433 is invertible modulo `N_k`,

\[
y_kU_k\equiv433\pmod {N_k}. \tag{8}
\]

The Markov identity modulo `M_k` gives
`433^2+y_k^2=0 (mod M_k)`. Also `gcd(y_k,M_k)=1`: a common divisor would,
by the Markov identity, divide `433^2`, but the ray residues modulo the prime
433 are nonzero. Hence `r_k` is defined and `r_k^2=-1 (mod M_k)`.

Now exclude both possibilities:

- If `U_k=r_k (mod M_k)`, multiplication by `y_k` and reduction modulo 5
  would give `2=3 (mod 5)` by (5), (6), and `433=3 (mod 5)`, impossible.
- If `U_k=-r_k (mod M_k)`, reduction modulo `N_k` would give
  `433=-433 (mod N_k)` by (8), so `N_k` would divide 866. But `N_k>866`,
  impossible.

Thus `U_k` differs from both members of the designated canonical pair for every
`k`. Combining this with (3) and (4) proves `g(M_k)<=4`.

## Claim consequence and limit

The infinite distinct sequence disproves the assertion that `g(m)` tends to
infinity along all sufficiently large composite Markov numbers for which `g` is
defined. It does not prove that `g` is globally bounded and does not close every
possible structural use of root energy.
