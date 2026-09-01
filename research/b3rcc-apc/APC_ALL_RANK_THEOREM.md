# All-rank antipodal partial-cube vertex/dimension bound

**Claim ID:** `C-APC-RANK-R-VERTEX-DIMENSION-BOUND`  
**Canonical level:** `INDEPENDENTLY_REPRODUCED`

## Theorem

Let `G` be an antipodal partial cube with

```text
rho(G) = r >= 2
idim(G) = d >= r+1.
```

Define

```text
q_r = 2^floor(r/2)
```

and

```text
kappa_r = binom(r,r/2)                     if r is even,
          2 binom(r-1,(r-1)/2)              if r is odd.
```

Then

\[
\boxed{|V(G)|\ge 2^r+\kappa_r+q_r(d-r-1)}.
\]

For `r=4`, this is exactly `|V(G)|>=4d+2`.

## Proof surface

### A. Side-rank lemma

Consider an antipodal expansion of a rank-`r` APC base `H`, with isometric covering sides `H1,H2` and `H2=-H1`.

Choose an `r`-coordinate shattered set `S` in `H`, and let `P=proj_S(H1)`. Antipodality and the cover imply

```text
P union complement(P) = Q_r,
```

hence `|P|>=2^(r-1)`.

If `VCdim(P)<=floor(r/2)-1`, the Sauer--Shelah bound is strictly below `2^(r-1)` (checking even and odd `r` separately), contradiction. Because `H1` is isometric in `H`, distinct ambient Theta classes do not merge in `H1`; inherited shattered coordinates therefore inject into intrinsic Theta coordinates of `H1`. Thus

```text
VCdim(P) <= rho(H1),
```

so

\[
\boxed{\rho(H_1)\ge\lfloor r/2\rfloor}.
\]

### B. Later-overlap lemma

For the exact inverse-expansion halfspace setting, the accepted affine-partial-cube machinery identifies

```text
K = H1 intersect H2 = A(H1),
```

where `A(F)` is the affine-antipode set. The independently reviewed bound

```text
|A(F)| >= 2^rho(F)
```

combined with the side-rank lemma gives

\[
\boxed{|K|\ge2^{\lfloor r/2\rfloor}=q_r}.
\]

### C. First reverse expansion from `Q_r`

Let `X=H1\H2`. No pair in `X` can have Hamming distance `r`, since such a pair would be antipodal and contradict exclusivity. No pair can have distance `r-1`, because one endpoint would then be adjacent to the antipode of the other, creating a forbidden edge between the exclusive sides.

Therefore

```text
diam_Hamming(X) <= r-2.
```

Kleitman's binary diameter theorem gives the exact maximum size `B(r,r-2)` of such an anticode. Since

```text
Q_r = X disjoint_union K disjoint_union (-X),
```

we have

```text
|K| >= 2^r - 2 B(r,r-2) = kappa_r,
```

with the displayed even/odd closed forms.

### D. Expansion-chain sum

Because `rho(G)=r`, a Theta-contraction sequence takes `G` to `Q_r`. Refine to elementary one-Theta contractions. Each elementary contraction decreases isometric dimension by exactly one, so there are exactly `d-r` contractions. Every intermediate graph remains an APC of rank exactly `r`.

Reverse the chain. The first expansion from `Q_r` adds at least `kappa_r` vertices; each of the remaining `d-r-1` expansions adds at least `q_r` vertices. Starting from `|V(Q_r)|=2^r`,

```text
|V(G)| >= 2^r + kappa_r + q_r(d-r-1).
```

This proves the theorem.

## Exact control values

The reviewed arithmetic controls give:

```text
r=3: |V(G)| >= 2d+4
r=4: |V(G)| >= 4d+2
r=5: |V(G)| >= 4d+20
r=6: |V(G)| >= 8d+28.
```

Finite controls support the algebra only; no finite enumeration is used to infer the all-rank theorem.

## Scope boundary

This theorem does not prove a general minimum-degree theorem, `APC=OM`, `APC=COM`, a Las-Vergnas conjecture, all-rank sharpness/equality classification, or any move-rank-6 B3RCC theorem.

Publication novelty is not established by mathematical acceptance. A bounded audit found no exact match in its checked scope and classified the combination conservatively; historical priority remains open.

**Provenance:** writer fixed `49e14900478fd97be6c0a52ad4982af010a472a8`; independent Phase-1 freeze `49743fff5c494314076b861a4c8045b4a27cd673`; final independent review `9d71e3dc530d1fbd1cd7922ba2f48d315b048866`; canonical intake `2205edc61dbbb3b260acc230b57d02d8aec9f9bd`.
