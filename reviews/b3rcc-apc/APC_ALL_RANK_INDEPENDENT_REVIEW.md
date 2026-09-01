# Independent review — APC all-rank vertex/dimension theorem

**Writer target:** `49e14900478fd97be6c0a52ad4982af010a472a8`  
**Phase-1 independent derivation freeze:** `49743fff5c494314076b861a4c8045b4a27cd673`  
**Final reviewer:** `9d71e3dc530d1fbd1cd7922ba2f48d315b048866`  
**Verdict:** `PASS`

Phase 1 was fixed before the writer theorem proof was opened. The reviewer independently reproduced the all-rank theorem.

## Gate results

- **Side rank:** PASS. From an `r`-coordinate shattered set, complement cover gives at least half of `Q_r`; Sauer--Shelah forces `VCdim>=floor(r/2)`. Isometry prevents ambient Theta coordinates from merging inside the expansion side, so this lower-bounds intrinsic rank.
- **Affine overlap:** PASS. The exact expansion overlap equals the affine-antipode set; `|A(F)|>=2^rho(F)` gives overlap at least `2^floor(r/2)`.
- **First `Q_r` expansion:** PASS. The exclusive part is a Hamming anticode of diameter at most `r-2`; Kleitman's theorem yields the exact `kappa_r` penalty.
- **Contraction/expansion chain:** PASS. An elementary Theta contraction removes exactly one isometric coordinate. A rank-`r`, idim-`d` APC therefore reverses from `Q_r` through exactly `d-r` antipodal expansions, all of rank `r`.
- **All-rank bound:** PASS.
- **Rank-4 recovery:** PASS; the formula reduces to `4d+2`.
- **Scope firewall:** PASS.

The final accepted theorem is

```text
|V(G)| >= 2^r + kappa_r + 2^floor(r/2)(d-r-1)
```

under the exact hypotheses `rho(G)=r>=2`, `idim(G)=d>=r+1`.

## Exact controls

The independent checker exhaustively verifies small complement-cover and anticode claims for `r=2,3,4`, and checks the closed-form arithmetic through `r=20`. These are supporting controls, not the infinite proof.

## Boundary

The review does not establish a minimum-degree theorem, Las-Vergnas, `APC=OM/COM`, sharpness/equality classification, or publication novelty. No next-rank B3RCC work is authorized by this theorem alone.
