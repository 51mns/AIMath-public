# Public result index

This file is a **conservative public index**. It is not a novelty announcement.

Statuses below reflect the private canonical ledger at the public snapshot source commit. A result marked `INDEPENDENTLY_REPRODUCED` has passed AIMath's internal independent-reproduction gate; this does **not** by itself mean the result is new to the mathematical literature.

## Independently reproduced

### Gyoda Conjecture 7.6 — collision at 89

**Claim ID:** `C-GYODA-89`

A number-only form of Gyoda Conjecture 7.6 (v4) is refuted by a collision at value `89`. AIMath also records infinite counterexample classes

```text
m ≡ 5, 14, 15, 24 (mod 30).
```

**Boundary:** project records support author confirmation only for the collision and the `5 (mod 30)` family. The other three residue classes are independently checked inside AIMath, not author-confirmed in the public claim.

### Fixed-433 root-energy family

**Public replay:** `python3 research/fixed-433/reproduce.py`

**Claim ID:** `C-ROOT-433`

A fixed Markov/Cohn ray gives an infinite subsequence with noncanonical root energy at most `4`, establishing an internal obstruction to the route `g(m) -> infinity`.

**Boundary:** this is a mathematical statement about the fixed family; publication novelty is separate.

### Fixed-433 Springborn obstruction

**Claim ID:** `C-433-SPRINGBORN-OBSTRUCTION`

The fixed-433 rational family is excluded from the specified Springborn Markov-fraction / companion orbit under the audited integer-affine framework.

### Fixed-433 existing-theory identification

**Claim ID:** `C-433-EXISTING-THEORY-IDENTIFICATION`

A fixed transformation identifies the family with an existing-theory expression of the form

```text
U_k / M_k = 4/5 - μ((9k+8)/(15k+13)).
```

**Novelty status:** not established.

### B3RCC structural programme

The private canonical ledger contains several independently reproduced B3RCC results, including:

- `C-B3RCC-1`
- `C-B3RCC-RANK-R-CARRY-PATH`
- `C-B3RCC-RANK3-COMPONENT-ATLAS`
- `C-B3RCC-RANK4-PARTIAL-CUBE-BOUNDARY`
- `C-B3RCC-RANK-R-CORE-MASK-REDUCTION`
- `C-B3RCC-RANK3-INTRINSIC-CHARACTERIZATION`
- `C-B3RCC-RANK3-COM-OM-CLASSIFICATION`
- `C-B3RCC-RANK-SATURATION-RIGIDITY`

Highlights include an all-rank carry-path construction, a complete rank-3 component atlas with 24 connected unlabeled types, a rank-4 boundary where universal partial-cube behaviour fails, and a finite core/mask reduction at fixed rank.

**Novelty status:** do not describe these as new/first/novel without a claim-specific primary-source audit.

### Antipodal partial-cube vertex/dimension bounds

Independently reproduced claims include:

- `C-APC-RANK4-VERTEX-DIMENSION-BOUND`
- `C-B3RCC-MOVE-RANK5-IDIM7-BOUND`
- `C-APC-RANK-R-VERTEX-DIMENSION-BOUND`

For rank `r >= 2`, the canonical rank-r bound is recorded in the form

```text
|V(G)| >= 2^r + κ_r + 2^floor(r/2) (d-r-1)
```

for the stated antipodal partial-cube hypotheses and `d >= r+1`, with the canonical definition of `κ_r` kept in the claim package.

**Novelty status:** not established by the status label alone.

### Equiangular lines in R^18 — eta=17 singleton spectral exclusion

**Claim ID:** `C-EQUIANGULAR-R18-ETA17-SINGLETON-EXCLUSION`

A specific hypothetical 59-line Seidel spectrum is excluded by a principal-deletion characteristic-polynomial deck identity.

**Boundary:** this excludes one spectral branch only. It does **not** prove `N(18) <= 58` and does not solve the `N(18)` problem.

### Dittert n=5 — two-zero matching exclusion

**Claim ID:** `C-DITTERT-N5-Z2-MATCHING-EXCLUSION`

No global Dittert maximizer in the audited `n=5` setting has exactly two zeros in distinct rows and distinct columns, up to row/column permutations.

**Boundary:** this is a support-class exclusion, not a solution of Dittert's `n=5` problem.

### Lonely Runner residual-capacity pruning

**Claim ID:** `C-LRC-R2-RESIDUAL-CAPACITY`

A generic safe two-pivot residual-capacity pruning theorem was independently reproduced.

**Boundary:** the associated scaling/performance route was closed because it did not improve the frozen benchmark. This is not an external Lonely Runner frontier improvement.

### Bounded AFES semantics

**Claim ID:** `C-AFES-BOUNDED-SEMANTICS`

A bounded subset of AIMath's formal exact-semantics layer was independently reproduced.

**Boundary:** the accepted scope is narrow and certificate-relative; it should not be read as a general formal-verification theorem.

### Thue–Morse rediscovery

**Claim ID:** `C-THUE-MORSE-REDISCOVERY`

An AIMath discovery pipeline independently rediscovered the known Thue–Morse constant.

**Boundary:** this is evidence for the rediscovery/certification workflow, not a claim of a new mathematical constant.

## Open / not proved

### Local TP2

**Claim ID:** `C-LOCAL-TP2`

Status: `PROOF_CANDIDATE`.

Large exact finite scans support the statement, and several algebraic identities are proved, but the universal theorem is not established. Finite scans are not promoted to an infinite theorem.

## How to read this index

If you want to cite, extend, or challenge a result, use its **Claim ID** and the exact statement in its exported claim package. This index is deliberately shorter than the proof artifacts.
