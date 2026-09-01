# Proof — Dittert n=5 two-zero matching exclusion

## Theorem

No global Dittert maximizer in `K_5` has, up to row and column permutations, exactly two zeros in distinct rows and distinct columns.

## 1. Canonical symmetrised form

For the exact two-matching-zero pattern, fixed-pattern symmetrisation reduces any putative global maximizer to

```text
A = [ 0  a  b  b  b ]
    [ c  0  d  d  d ]
    [ e  f  g  g  g ]
    [ e  f  g  g  g ]
    [ e  f  g  g  g ]
```

with all seven parameters positive.

The zero-entry KKT comparison gives

```text
3(d-b)(f-e) >= (a+c)g > 0.
```

The support automorphism swapping rows `1<->2` and columns `1<->2` reverses both differences, so without loss of generality

```text
d>b,  f>e.
```

## 2. Symmetry coordinates

Set

```text
u=(a+c)/2,  x=(c-a)/2
v=(b+d)/2,  y=(d-b)/2
w=(e+f)/2,  z=(f-e)/2
G=g.
```

Then positivity and the chosen chamber give

```text
u>|x|, v>y>0, w>z>0, G>0,
```

and the KKT inequality becomes

```text
uG <= 6yz.                         (K)
```

Define

```text
S=2w+3G,   T=2v+3G,
A_w=S^3-6G^2w,
A_v=T^3-6G^2v,
B_w=S^3-4G(w^2-z^2),
B_v=T^3-4G(v^2-y^2).
```

At a global maximizer, positive-entry stationarity at the symmetric `b/d` and `e/f` positions gives, after exact permanent expansion,

```text
A_w x = 6G^2 z u - 3y B_w,         (1)
A_v x = 3z B_v - 6G^2 y u.         (2)
```

Only these two positive-entry equalities are needed.

## 3. Strict positivity estimates

Exact expansion gives

```text
A_w = 8w^3+36Gw^2+48G^2w+27G^3 > 0,
A_v = 8v^3+36Gv^2+48G^2v+27G^3 > 0.
```

Also

```text
B_w-12Gz^2
 = 8w^3+24Gw^2+54G^2w+27G^3+8G(w^2-z^2) > 0,
```

because `w>z>0`; similarly

```text
B_v-12Gy^2
 = 8v^3+24Gv^2+54G^2v+27G^3+8G(v^2-y^2) > 0.
```

Thus

```text
B_w>12Gz^2,  B_v>12Gy^2.           (P)
```

## 4. Contradiction

From `(K)`,

```text
6G^2 z u <= 36G y z^2 = 3y(12Gz^2).
```

Using `(1)` and `(P)`,

```text
A_w x <= 3y(12Gz^2-B_w) < 0.
```

Since `A_w>0`, this forces

```text
x<0.
```

Likewise `(K)` gives

```text
6G^2 y u <= 36G y^2 z = 3z(12Gy^2),
```

and `(2)` gives

```text
A_v x >= 3z(B_v-12Gy^2) > 0.
```

Since `A_v>0`, this forces

```text
x>0.
```

Contradiction. Hence the support class contains no global maximizer.

## Load-bearing nature of the KKT chamber

The exact control

```text
v=w=1, y=z=1/2, G=1, x=0, u=61
```

can satisfy the two odd stationarity certificate expressions while

```text
uG-6yz = 119/2 > 0.
```

Thus the two stationarity identities are not tautologically inconsistent; the zero-entry KKT information is genuinely load-bearing.

## Scope

The argument excludes exactly the two-zero matching support orbit. Other zero patterns and the full `n=5` conjecture are outside this theorem.
