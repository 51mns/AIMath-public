# Gyoda Conjecture 7.6 — collision at 89

**Claim ID:** `C-GYODA-89`  
**Canonical level:** `INDEPENDENTLY_REPRODUCED`  
**Private canonical snapshot:** `c8e61e0e398f540bc8c5de79663398d689f37473`

This package exports the mathematics and exact checks for the written **number-only** form of Gyoda Conjecture 7.6 in arXiv:2512.04547v4.

The first audited collision is

```text
(k1,k2,k3) = (0,0,6)
sigma = (3,1,2)
labels = 1/5 and 2/3
n_(1/5) = n_(2/3) = 89
```

The accepted independent audit also proves infinite collision classes

```text
m ≡ 5, 14, 15, 24 (mod 30).
```

## Reproduce

```bash
python3 research/gyoda-89/reproduce.py
```

All arithmetic is exact integer arithmetic.

## Important boundary

The project record supports author confirmation only for the `89` collision and the `m ≡ 5 (mod 30)` family. Raw correspondence is deliberately not public and is not used as independent mathematical evidence. The additional `14,15,24` residue classes are independently checked AIMath extensions, not author-confirmed claims.

The result refutes the conjecture **as written in terms of equality of the generalized Markov numbers alone**. It does not claim to refute a stronger position-aware revision involving the associated position labels.

The historical discovery archive and private chat material are intentionally not exported.
