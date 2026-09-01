# Fixed-433 / existing-theory identification

**Claim ID:** `C-433-EXISTING-THEORY-IDENTIFICATION`  
**Canonical level:** `INDEPENDENTLY_REPRODUCED`  
**Private canonical snapshot:** `c8e61e0e398f540bc8c5de79663398d689f37473`

For every `k >= 0`, AIMath identifies the fixed-433 rational exactly as

\[
\frac{U_k}{M_k}=\frac45-\mu\!\left(\frac{9k+8}{15k+13}\right),
\]

where `mu(t)` is the reviewed Springborn/Veselov Markov-fraction normalization.
Equivalently, if `mu((9k+8)/(15k+13))=p_k/M_k`, then

\[
5p_k=4M_k-5U_k.
\]

The public proof also records the equivalent modular-root identity

\[
U_k=r_k-M_k/5,\qquad r_k=M_k-p_k.
\]

This is an all-`k` structural proof, not a fit to finite data.

## Reproduce

```bash
python3 research/433-existing-theory-identification/reproduce.py
```

The finite checker uses exact integer/Fraction arithmetic. Its finite rows are regression fingerprints only; the universal proof is in `PROOF.md`.

## Boundary

The reflection `R_5(x)=4/5-x` is a fixed rational affine map in `PGL_2(Q)`, not an integer-affine symmetry and not a `PGL_2(Z)` map. This is compatible with `C-433-SPRINGBORN-OBSTRUCTION`.

Publication novelty is **NOT ESTABLISHED**. No author correspondence is used or exported.
