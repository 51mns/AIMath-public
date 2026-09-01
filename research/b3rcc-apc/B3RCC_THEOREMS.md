# Accepted B3RCC structural theorems

All claims below have canonical level `INDEPENDENTLY_REPRODUCED` at private snapshot `c8e61e0e398f540bc8c5de79663398d689f37473`. Publication novelty is separate and is not established by these status labels.

## `C-B3RCC-1` — three independent moves have only induced 4- and 6-cycles

Let `r1,r2,r3 in {-1,0,1}^k` be nonzero and Q-linearly independent. On `Q_k={0,1}^k`, join `x,y` when `y-x=+/-r_j`. Every induced cycle has length `4` or `6`.

**Proof core.** Put the moves in a `k x 3` matrix and choose an invertible `3 x 3` coordinate-row minor. Projection to those coordinates is injective on each connected component and reflects move adjacency, so every induced cycle embeds as an induced cycle in a graph on `Q_3`, hence has length at most `8`. Independence forces every move colour to occur equally often with both orientations on a closed walk, so every cycle length is even. A hypothetical induced `C8` would use all of `Q_3`. Exact matching-edge counts force move-support pattern `(1,2,2)`. The two support-2 matchings would have to occupy complementary parity halfcubes on the same coordinate pair, while the support-1 move lies on the remaining coordinate. Every edge then preserves that parity split, making the graph disconnected, contradiction.

Writer `2da4e3714141b96379635e675bf1745d4ee8d9bc`; independent reviewer `acead7660d22da1cc2e0b45c0f1bfdcdfc054410`.

**Boundary:** exactly three independent ternary moves. A four-move induced `C10` control blocks naive relation-count generalisation.

---

## `C-B3RCC-RANK-R-CARRY-PATH` — exact path extremiser

For `r>=1`, define

```text
v_j = (0^(r-j), 1, (-1)^(j-1)),   j=1,...,r.
```

The move matrix is unimodular with determinant `(-1)^(r(r-1)/2)`, and the Boolean-state graph is exactly the path `P_(2^r)`. The edge from binary state `b(n-1)` to `b(n)` has label `1+nu_2(n)`.

**Proof core.** Ordinary binary carry produces every consecutive binary transition. For the binary-value potential `Phi(x)=sum_i 2^(r-i)x_i`, every move has `Phi(v_j)=1`, so every legal signed edge changes value by exactly one. Therefore no shortcut or extra edge exists.

For arbitrary Q-independent integer moves `u_1,...,u_r`, coefficient parity relative to a component base is injective, yielding `|C|<=2^r` and hence `diam(C)<=2^r-1`. The carry family attains equality.

Writer `15b740dab13df7869cf47988078afb715d59ed9a`; reviewer `90db35a7b4f6a408868f07d384e1fbc14d9aa22c`.

---

## `C-B3RCC-RANK3-COMPONENT-ATLAS` — exactly 24 rank-3 graph types

For three nonzero Q-independent ternary moves in arbitrary ambient dimension, every connected component reduces losslessly through an invertible ternary `3 x 3` coordinate minor to a masked finite core on `Q_3`. Omitted coordinates become exact Boolean-legality masks, and every resulting root component is conversely realizable. Exactly `24` connected unlabeled component graph types occur, and every one is a partial cube.

**Reduction proof core.** The same invertible-minor argument used in `C-B3RCC-1` gives componentwise injective projection and adjacency reflection. Every omitted row is an affine function of the three projected coordinates; requiring that coordinate to remain Boolean gives an exact finite legality mask. Thus arbitrary ambient dimension contributes only finite mask constraints over `Q_3`.

**Exact classification record.** The accepted independent reconstruction checked all `19,683` ternary `3 x 3` matrices, `11,808` invertible matrices, `246` labelled core edge masks, `71,568` rooted mask-intersection states, and obtained exactly `24` connected unlabeled all-ambient graph types. Writer and reviewer canonical graph-code sets agree exactly. All 24 pass independent partial-cube checks.

Writer `3281c03bdcdf7700657aa48e8889478e7f9d5b2d`; Phase-1 reviewer freeze `90b95076f0d564bcf105288002064ab3d40606fd`; final reviewer `9354d0d4463e4f42338b9b7184ef9dba6822ff69`.

**Boundary:** classification is rank exactly 3, not arbitrary rank.

---

## `C-B3RCC-RANK4-PARTIAL-CUBE-BOUNDARY` — rank 4 already fails

The universal assertion “every B3RCC component is a partial cube” is false for four independent moves. In minimum possible ambient dimension `k=4`, take

```text
u1 = (0,0,0,1)
u2 = (0,0,1,-1)
u3 = (0,1,-1,0)
u4 = (1,0,-1,1).
```

The move matrix has determinant `1`; the generated graph is one connected `16`-vertex, `18`-edge component and is not a partial cube.

The independent review reproduced two intrinsic obstructions: nontransitivity of the Djoković--Winkler relation and a nonconvex semicube. The exact `k=4` search found `432` non-partial-cube components and three unlabeled failure types, but the explicit witness above alone proves the universal rank-4 assertion false.

Writer `7b03d73bc864c72861dabb21a01e4cd1bc9d1356`; reviewer `edc39182881f0d6a2bca5d645b156335edfb0e53`.

---

## `C-B3RCC-RANK-R-CORE-MASK-REDUCTION` — arbitrary fixed-rank finite core

For every fixed `r>=1`, Q-independent ternary move matrix `R in {-1,0,1}^{k x r}`, and connected Boolean-state component `C`, choose an invertible coordinate-row minor `A`. Projection to those `r` coordinates is injective on `C`, preserves and reflects move adjacency, and identifies `C` with the root component of a finite core on `Q_r` cut out by omitted-coordinate legality constraints of the form

```text
epsilon + b A^{-1}(u-u0) in {0,1}.
```

This is a lossless structural reduction, not merely a size bound. It explains why fixed move rank is intrinsically finite even when ambient dimension is arbitrary.

Writer `ae8f90f4b2db8b8665f0acb8eb94ee1805123871`.

**Boundary:** the theorem does not provide a uniform explicit graph-type list for arbitrary `r`, nor an arbitrary-r partial-cube theorem.

---

## `C-B3RCC-RANK3-INTRINSIC-CHARACTERIZATION`

A connected graph is a rank-3 B3RCC component graph iff it satisfies the reviewed graph-intrinsic I1/I2/I3 predicate: balanced proper 3-edge-colouring with allowed orders `{1,2,3,4,5,6,8}`, the specified six-vertex `F6` exclusion, and the audited eight-vertex involution/colour-class/C4-C6 compatibility conditions.

The proof reconstructs the 7-of-8 lemma, the `F6` obstruction, the small-order classification, the eight-vertex four-orbit lemma and direct realizability. The predicate does not cheat by looking up atlas IDs or canonical graph codes.

Writer `2034e5d133e802ac5f88d1332f7bce0d8685e9bc`; reviewer `2700cc1adef5fb0605c1eacb6a7c6a7741dfcf21`.

---

## `C-B3RCC-RANK3-COM-OM-CLASSIFICATION`

All 24 accepted rank-3 component types are COM tope graphs. Exactly atlas IDs `{1,2,6,16,24}` are antipodal and exactly those five are OM tope graphs, with abstract graph types

```text
K1, K2, C4, C6, Q3.
```

The independent reconstruction used partial-cube geometry, Theta classes, contraction/VC rank, antipodality, convex antipodal subgraphs and gatedness; it did not infer the result from the writer's labels.

Writer `528f658c7155108e110a58dfd3b20bb976713c00`; Phase-1 `5bfc0e2fcba659bb07fa672d12e2aa4a39c43c1f`; final reviewer `9450cfa90fab5ee7fae379c9157ef6e422bf80b1`.

**Boundary:** B3RCC move rank is not identified with OM/COM rank.

---

## `C-B3RCC-RANK-SATURATION-RIGIDITY`

Let `C` be a partial-cube B3RCC component generated by `m` Q-independent integer moves and let `rho` be its intrinsic Theta-contraction / VC rank. Then

```text
rho <= m,
```

and equality `rho=m` forces

```text
C ~= Q_m.
```

**Proof core.** Coefficient-parity injectivity gives `|V(C)|<=2^m`. A contraction sequence to `Q_rho` gives `2^rho<=|V(C)|`, hence `rho<=m`. If `rho=m`, all inequalities are equalities. Any nonempty Theta contraction strictly lowers vertex count, so a contraction sequence from a `2^m`-vertex graph to the equally sized `Q_m` must be empty.

Writer `528f658c7155108e110a58dfd3b20bb976713c00`; reviewer `9450cfa90fab5ee7fae379c9157ef6e422bf80b1`.

---

## `C-B3RCC-MOVE-RANK4-APC-BARRIER`

For a four-move B3RCC component already independently certified to be an antipodal partial cube, rank-saturation gives `rho<=4`; imported generalized-APC results cover `rho<=3`, while `rho=4` forces `Q_4`. Thus move rank 4 contributes no unresolved B3RCC APC sector relative to that imported solved union.

Writer `d2c96133d3a46842592954b980e465d1d78676f0`; reviewer `de43d85e229352c5dee5eda1e0ea3dee910e632b`.

**Boundary:** this does not say every move-rank-4 component is a partial cube or antipodal.

---

## `C-B3RCC-MOVE-RANK5-APC-TARGET-REDUCTION`

For five independent ternary moves, any component that lies in the unresolved imported APC sector must first be independently certified as a partial cube and intrinsically antipodal, and must satisfy

```text
rho = 4,  idim >= 8.
```

Rank saturation removes `rho=5` by forcing `Q_5`; imported solved cases remove `rho<=3` and `idim<=7`.

Writer `d2c96133d3a46842592954b980e465d1d78676f0`; reviewer `de43d85e229352c5dee5eda1e0ea3dee910e632b`.

**Boundary:** necessary-condition reduction only; it is not an existence or emptiness theorem.

---

## `C-B3RCC-CORE-MASK-COMPLEMENT-PAIRING`

For the core-mask legality function

```text
f(u) = epsilon + b A^{-1}(u-u0),
```

define

```text
epsilon* = 1-epsilon-b A^{-1}(1-2u0).
```

Exact algebra gives

```text
1-f(1-u) = epsilon* + b A^{-1}(u-u0).
```

Whenever `epsilon*` is Boolean, core complement sends the legality mask to another legal mask.

Writer `d2c96133d3a46842592954b980e465d1d78676f0`; reviewer `de43d85e229352c5dee5eda1e0ea3dee910e632b`.

**Boundary:** this identity alone does not prove intrinsic antipodality, partial-cube structure or OM/COM status.

---

## `C-B3RCC-MOVE-RANK5-IDIM7-BOUND`

Let `C` be generated by five Q-independent ternary integer moves. If `C` is an antipodal partial cube with intrinsic rank `rho(C)=4`, then

```text
idim(C) <= 7.
```

**Proof core.** Coefficient parity injects `V(C)` into `{0,1}^5`, so `|V(C)|<=32`. If `idim(C)>=8`, the accepted rank-4 APC bound gives `|V(C)|>=4*8+2=34`, contradiction.

Writer `d42ec0ddc9a9e90e70bae0e5d71e3423ffa22fbe`; reviewer `a97bdc3585c2f35ab81ec4a8adc3033a9ce43f7a`.

---

## Publication / continuation boundary

None of the claims above should be described as `NEW`, `FIRST` or historically novel solely because AIMath independently reproduced them. The B3RCC/APC theme is on portfolio HOLD; see `CAMPAIGN_CLOSEOUT.md` before opening next-rank work.
