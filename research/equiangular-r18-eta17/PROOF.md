# Proof — eta=17 singleton-spectrum Seidel nonexistence

## Theorem

There is no `59 x 59` Seidel matrix with characteristic polynomial

\[
p(x)=(x+5)^{41}(x-9)^6(x-10)(x-11)(x-13)^{10}.
\]

## 1. Principal deletion form

For any order-58 principal deletion `S_i`, Cauchy interlacing forces multiplicities

```text
-5^40, 9^5, 13^9,
```

and four remaining eigenvalues in

```text
[-5,9], [9,10], [10,11], [11,13].
```

Hence

\[
\chi_{S_i}(x)=F(x)Q_i(x),\qquad
F=(x+5)^{40}(x-9)^5(x-13)^9,
\]

where `Q_i` is a monic integral quartic. Trace and trace-square of an order-58 Seidel matrix give

\[
Q_i=x^4-38x^3+532x^2+A_ix+B_i.
\]

## 2. Endpoint deck

Interlacing forces

```text
Q(-5)>=0, Q(9)<=0, Q(10)>=0, Q(11)<=0, Q(13)>=0.
```

For `Q=x^4-38x^3+532x^2+Ax+B` these become

```text
B >=  5A-18675
B <= -9A-21951
B >= -10A-25200
B <= -11A-28435
B >= -13A-34983.
```

Thus

```text
-3249 <= A <= -3235,
```

and the exact integer polygon contains 64 pairs `(A,B)`.

## 3. Type-2 condition leaves one quartic

For an even-order Seidel deletion, the reviewed type-2 condition applies to `chi_{S_i}(x-1)`: writing a monic degree-`n` polynomial as

```text
x^n + a_1 x^(n-1) + ... + a_n,
```

one requires `2^j | a_j` for every coefficient index `j`.

Applying the complete condition to the 64 endpoint candidates leaves exactly

```text
A=-3242, B=7227,
```

so every deletion would have the same residual quartic

\[
Q_0=x^4-38x^3+532x^2-3242x+7227.
\]

It factors as

\[
Q_0=(x-9)(x-11)(x^2-18x+73),
\]

with roots `9-2sqrt(2), 9, 11, 9+2sqrt(2)`, consistent with the required intervals.

## 4. Deck derivative contradiction

For every matrix,

\[
p'(x)=\sum_i\chi_{S_i}(x).
\]

A singleton deck would therefore require

\[
\frac{p'}F=59Q_0.
\]

Exact expansion gives

```text
p'/F = 59x^4-2242x^3+31388x^2-190974x+422985
59Q0 = 59x^4-2242x^3+31388x^2-191278x+426393.
```

Their difference is

\[
\boxed{16(19x-213)\ne0},
\]

a contradiction.

Therefore no Seidel matrix has the proposed spectrum.

## Scope

The spectrum has the correct Seidel first two moments, and if such a matrix existed then `I+S/5` would be PSD of rank 18. The proof nevertheless excludes only this eta=17/simple-11 spectral branch. It does not change the global bound by itself.
