# B3RCC / antipodal partial-cube campaign

This directory is the public, privacy-safe evidence map for the accepted B3RCC/APC campaign at private canonical snapshot `c8e61e0e398f540bc8c5de79663398d689f37473`.

The campaign is mathematically successful but currently on **portfolio HOLD**. Accepted results remain reusable; next-rank enumeration is not automatically justified.

## Strongest theorem

`C-APC-RANK-R-VERTEX-DIMENSION-BOUND` (`INDEPENDENTLY_REPRODUCED`): for every antipodal partial cube `G` with `rho(G)=r>=2` and `idim(G)=d>=r+1`, define

```text
q_r = 2^floor(r/2)
kappa_r = binom(r,r/2)                    if r is even
          2 binom(r-1,(r-1)/2)             if r is odd.
```

Then

```text
|V(G)| >= 2^r + kappa_r + q_r(d-r-1).
```

See `APC_ALL_RANK_THEOREM.md` and the independent review under `reviews/b3rcc-apc/`.

## Accepted B3RCC structural claims

See `B3RCC_THEOREMS.md` for exact public statements and proof/provenance summaries for:

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

## Campaign status

`CAMPAIGN_CLOSEOUT.md` explains why this successful theme is held rather than automatically extended. Publication novelty/historical priority are not established merely by the internal claim levels.
