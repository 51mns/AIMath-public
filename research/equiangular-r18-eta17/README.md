# Equiangular lines in R^18 — eta=17 singleton spectral exclusion

**Claim ID:** `C-EQUIANGULAR-R18-ETA17-SINGLETON-EXCLUSION`  
**Canonical level:** `INDEPENDENTLY_REPRODUCED`

There is no `59 x 59` Seidel matrix with characteristic polynomial

```text
(x+5)^41 (x-9)^6 (x-10)(x-11)(x-13)^10.
```

Consequently the `eta=17 / simple-eigenvalue-11` branch of a hypothetical 59-line equiangular system in `R^18` is empty.

## Reproduce

```bash
python3 research/equiangular-r18-eta17/verify.py
```

The public checker uses exact Python integer arithmetic only. It reconstructs the 64 endpoint-feasible principal-deletion quartics, applies the complete type-2 coefficient divisibility test, finds the unique quartic, and verifies the characteristic-polynomial deck contradiction.

## Boundary

This excludes one spectral branch only. It does **not** prove `N(18)<=58`, does not exclude every 59-line configuration, and does not establish publication novelty.

Writer fixed commit: `2b61a27c37d87934c765688140cbd15cc8050440`. Independent Phase-1: `1d5100b713e36f58bbee917da9d255d6b0c72a7b`. Final independent review: `1f5d19f617ee9187216c51cc69a6bf5f2e750520`.
