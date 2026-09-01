# Public result index

This is a **conservative public index**, not a novelty announcement. Statuses reflect private canonical `main` at `c8e61e0e398f540bc8c5de79663398d689f37473`. `INDEPENDENTLY_REPRODUCED` means AIMath has an accepted independent mathematical review; it does not by itself mean a result is new to the literature.

## Independently reproduced

### Gyoda Conjecture 7.6 — collision at 89

**Claim:** `C-GYODA-89`  
**Package:** [`research/gyoda-89/`](../research/gyoda-89/)

The written number-only form of Gyoda Conjecture 7.6 v4 is refuted by the exact collision `n_(1/5)=n_(2/3)=89`. The accepted mathematical extension gives infinite classes

```text
m ≡ 5, 14, 15, 24 (mod 30).
```

Only the collision and `5 mod 30` family are recorded as author-confirmed in the private project record; raw correspondence is intentionally not public. The other three classes are independently reproduced AIMath mathematics. A stronger position-aware reformulation is a different statement.

### Fixed-433 root-energy family

**Claim:** `C-ROOT-433`  
**Package/replay:** [`research/fixed-433/`](../research/fixed-433/) — `python3 research/fixed-433/reproduce.py`

A fixed Markov/Cohn ray has an infinite subsequence with noncanonical root energy at most `4`, refuting the internal subroute `g(m)->infinity` for that family.

### Fixed-433 Springborn obstruction

**Claim:** `C-433-SPRINGBORN-OBSTRUCTION`  
**Package:** [`research/433-springborn-obstruction/`](../research/433-springborn-obstruction/)

For every fixed-433 rational `x_k=U_k/M_k`, the public all-`k` proof gives `C(x_k)<1/4`, excluding the audited Springborn Markov-fraction/companion classes and their integer-affine symmetry orbit. Arbitrary `GL_2(Z)`/`PGL_2(Z)` exclusion is not claimed.

### Fixed-433 existing-theory identification

**Claim:** `C-433-EXISTING-THEORY-IDENTIFICATION`  
**Package:** [`research/433-existing-theory-identification/`](../research/433-existing-theory-identification/)

For all `k>=0`,

```text
U_k/M_k = 4/5 - mu((9k+8)/(15k+13)).
```

The proof identifies the exact Farey/Cohn ray and the factor-5 CRT representative relation. Publication novelty is not established.

### B3RCC structural programme

**Campaign package:** [`research/b3rcc-apc/`](../research/b3rcc-apc/)

Accepted claims documented there include:

- `C-B3RCC-1`
- `C-B3RCC-RANK-R-CARRY-PATH`
- `C-B3RCC-RANK3-COMPONENT-ATLAS`
- `C-B3RCC-RANK4-PARTIAL-CUBE-BOUNDARY`
- `C-B3RCC-RANK-R-CORE-MASK-REDUCTION`
- `C-B3RCC-RANK3-INTRINSIC-CHARACTERIZATION`
- `C-B3RCC-RANK3-COM-OM-CLASSIFICATION`
- `C-B3RCC-RANK-SATURATION-RIGIDITY`
- `C-B3RCC-MOVE-RANK4-APC-BARRIER`
- `C-B3RCC-MOVE-RANK5-APC-TARGET-REDUCTION`
- `C-B3RCC-CORE-MASK-COMPLEMENT-PAIRING`
- `C-B3RCC-MOVE-RANK5-IDIM7-BOUND`

Highlights: induced cycles are exactly length 4/6 for three independent ternary moves; an explicit all-rank family realises `P_(2^r)` and the sharp component diameter `2^r-1`; rank 3 has exactly 24 connected unlabeled component types and all are partial cubes; rank 4 already has an explicit non-partial-cube component; arbitrary fixed rank reduces losslessly to a finite masked core.

The campaign is currently `PORTFOLIO_HOLD`; see its closeout before opening next-rank work.

### Antipodal partial-cube vertex/dimension bound

**Claim:** `C-APC-RANK-R-VERTEX-DIMENSION-BOUND`  
**Package:** [`research/b3rcc-apc/APC_ALL_RANK_THEOREM.md`](../research/b3rcc-apc/APC_ALL_RANK_THEOREM.md)

For `rho(G)=r>=2`, `idim(G)=d>=r+1`,

```text
|V(G)| >= 2^r + kappa_r + 2^floor(r/2)(d-r-1),
```

with the exact even/odd binomial definition of `kappa_r` in the package. At `r=4`, this recovers the separately accepted `C-APC-RANK4-VERTEX-DIMENSION-BOUND`, namely `|V(G)|>=4d+2`.

Historical novelty/priority are not established.

### Equiangular lines in R^18 — eta=17 singleton spectrum

**Claim:** `C-EQUIANGULAR-R18-ETA17-SINGLETON-EXCLUSION`  
**Package/replay:** [`research/equiangular-r18-eta17/`](../research/equiangular-r18-eta17/) — `python3 research/equiangular-r18-eta17/verify.py`

No `59 x 59` Seidel matrix has characteristic polynomial

```text
(x+5)^41 (x-9)^6 (x-10)(x-11)(x-13)^10.
```

The principal-deletion deck is forced to one quartic, but the universal derivative identity fails by `16(19x-213)`. This excludes exactly the eta=17/simple-11 branch; it does **not** prove `N(18)<=58` or solve the full problem.

### Dittert n=5 — two-zero matching exclusion

**Claim:** `C-DITTERT-N5-Z2-MATCHING-EXCLUSION`  
**Package:** [`research/dittert-n5-z2/`](../research/dittert-n5-z2/)

No global `n=5` Dittert maximizer has exactly two zeros in distinct rows and columns, up to independent row/column permutation. The proof uses a KKT chamber inequality and two positive-entry stationarity identities to force both `x<0` and `x>0`.

This is one support-class exclusion, not a solution of the full `n=5` conjecture.

### Lonely Runner two-pivot residual capacity

**Claim:** `C-LRC-R2-RESIDUAL-CAPACITY`  
**Package:** [`research/lonely-runner-r2/`](../research/lonely-runner-r2/)

A generic set-cover theorem gives a safe two-pivot optimistic capacity `R2` with `R2<=R1`; `R2<|U|` safely prunes. A reachable `p=71` LRC branch gives a strict bounded certificate, but the later performance route is `NO_GO_FOR_SCALING`. This does not prove `LRC(13)`.

### Bounded AFES semantics

**Claim:** `C-AFES-BOUNDED-SEMANTICS`  
**Package:** [`research/afes-bounded/`](../research/afes-bounded/)

A bounded exact formalism covering reviewed rational, indexed algebraic-root, alternating-series and recursive operation/certificate cases was independently reproduced.

**Separate open claim:** `C-AFES-STRICT-CANONICAL-ENCODING` remains `PROOF_CANDIDATE` because of the documented Python bool/int scalar edge. No total equality, total nonzero recognition or full field closure is claimed.

### Thue–Morse rediscovery

**Claim:** `C-THUE-MORSE-REDISCOVERY`  
**Package/replay:** [`research/thue-morse-rediscovery/`](../research/thue-morse-rediscovery/) — `python3 research/thue-morse-rediscovery/verify.py`

The pilot binary series is exactly the already-known Thue–Morse constant and has the exact product identity

```text
C = 1/2 - (1/4) product_(k>=0)(1-2^(-2^k)).
```

This is a rediscovery/certification result, not a new constant.

## Open / not proved

### Local TP2

**Claim:** `C-LOCAL-TP2` — `PROOF_CANDIDATE`  
**Public baseline:** [`research/local-tp2/`](../research/local-tp2/)

The exact adjacent-determinant statement, orientation, finite baseline, novelty boundary and old proof-design invariants are public. The universal strict inequality is not proved. Several blocked proof routes are recorded in [`FAILED_ROUTES.md`](FAILED_ROUTES.md).

## Contributing or checking a result

Before starting a new route, read:

1. [`CONTRIBUTION_TARGETS.md`](CONTRIBUTION_TARGETS.md)
2. [`FAILED_ROUTES.md`](FAILED_ROUTES.md)
3. [`EVIDENCE_POLICY.md`](EVIDENCE_POLICY.md)
4. [`CLAIM_LEVELS.md`](CLAIM_LEVELS.md)

If a result is challenged or extended, refer to its Claim ID and exact public package rather than this summary alone.
