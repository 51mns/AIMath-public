# Independent review — Gyoda 89 collision and family mechanism

**Canonical claim:** `C-GYODA-89`  
**Accepted private evidence commit:** `ffedc04af3a0dd951fa1b700dcbcd47c9901407a`  
**Decision:** `PASS_WITH_FIXES` on the historical bundle; mathematical core accepted and canonical level is `INDEPENDENTLY_REPRODUCED`.

## Independently reproduced mathematics

A separately implemented audit reproduced:

- the fixed `89` collision;
- the generalized Cohn matrices and determinant-one checks;
- generalized Markov equation witnesses;
- the recurrence `a_(m+1)=3a_m-a_(m-1)` with `a_1=2,a_2=5`;
- the exact affine law `n_(2/3)=10k+29`;
- the modulo-10 state period `30`;
- the four residue classes `m ≡ 5,14,15,24 (mod 30)`;
- direct exact representatives from every residue class.

The review explicitly separated the universal recurrence/state-cycle proof from finite checks.

## Fixed 89 witness

The independent matrix reconstruction gives

```text
C_1/5 = [[767,293],[89,34]]
C_2/3 = [[759,307],[89,36]]
det = 1, 1
lower-left = 89, 89
```

with exact generalized-Markov-equation witnesses for both labels.

## Family result

The recurrence modulo 10 has exactly the equality-compatible classes

```text
5, 14, 15, 24 (mod 30).
```

The review checked the state-cycle mechanism symbolically/exactly and also checked multiple concrete representatives as controls.

## Historical-bundle qualifications

The old research bundle mixed several workflow claims with the mathematics. The independent audit therefore qualified claims about blind discovery, same-instance provenance and historical raw-byte reproduction. In particular, the frozen search bound coincided with the first known collision frontier, so the safe description is **deterministic blind-style replay**, not proof of a prospectively blind discovery protocol.

Those workflow qualifications do not invalidate the mathematical collision or family proof.

## Author-confirmation boundary

The repository project record supports author confirmation for the `89` collision and the `5 mod 30` family. Raw correspondence was not retrieved and is intentionally not exported. The `14,15,24` classes are independently reproduced mathematical extensions only.

## Scope

The public result concerns the number-only form of the written conjecture. No claim is made against a stronger position-aware reformulation.
