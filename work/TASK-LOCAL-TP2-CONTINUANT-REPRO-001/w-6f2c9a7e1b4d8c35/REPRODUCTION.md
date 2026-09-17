<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Local TP2 continuant reduction — adversarial reproduction

Task: `TASK-LOCAL-TP2-CONTINUANT-REPRO-001`  
Worker: `w-6f2c9a7e1b4d8c35`  
Frozen target: `0f2d9f6fb7f3331ad289cc949b1191d7cbb2fb0a`

## Scope boundary

This is an executable / exact-arithmetic reproduction of the finite fixtures and the root obstruction attached to the continuant gap-cone structural reduction. It is **not** an independent all-depth proof of the gap-cone theorem and is **not** a proof of `C-LOCAL-TP2`.

The fresh implementation does not import or call the writer's `splice_verifier.py` or the PR #90 checker. It constructs the finite Farey tree directly from the uniform matrix splice

`M_t = M_r^T Q M_s^T`

starting from the two virtual boundary matrices. Only after this implementation was frozen was the writer verifier read for comparison. The writer verifier independently constructs continued-fraction words and then forms their continuant matrices, so the two executables use materially different finite-generation paths before meeting at the same exact matrix identities.

## Fresh replay

Command:

```bash
python3 work/TASK-LOCAL-TP2-CONTINUANT-REPRO-001/w-6f2c9a7e1b4d8c35/independent_reproduction.py
```

Observed output:

```text
PASS
farey_words=511
subtraction_free_sibling_checks=127
finite_local_tp2_sanity_checks=127
boundary_chain_checks=7
root_HS=[40, 32, 16, 4]
root_HD=[164, 138, 80, 30, 6]
root_F=[272, 352, 160, 24]
direct_gap_network_obstruction=det(M_1/3-M_1/2)=-(x+1)^2
```

## Exact checks reproduced

1. Root transfer matrix:

```text
M_(1/2) = [[2x^2+6x+5, 2x+2], [x+2, 1]].
```

2. A depth-9 finite Farey generation contains exactly `511` genuine vertices.

3. For all `127` vertices through depth 7 whose two children are present in the generated tree, the degree-oriented

```text
S = U-C,
D = V-U
```

have coefficientwise nonnegative ordinary `x` coefficients.

4. The same `127` finite fixtures satisfy the frozen adjacent `H`-minor positivity sanity check. This is finite evidence only.

5. Frozen root profiles are reproduced exactly:

```text
H(S) = [40, 32, 16, 4]
H(D) = [164, 138, 80, 30, 6]
F    = [272, 352, 160, 24].
```

6. The root-left raw gap matrix is reproduced as

```text
Delta = [[4(x+1)^2(x+2), (x+1)(2x+3)],
         [(x+1)(2x+3),   x+1]],
```

with exact determinant

```text
det(Delta) = -(x+1)^2.
```

Thus the direct nonnegative planar-path-matrix architecture is obstructed at the root exactly as reported.

7. As an additional independent boundary check, for `n=3,...,9` the extreme left-chain gaps satisfy the closed form

```text
B_n=(x+1)[[P_(n-1),P_(n-2)],[P_(n-2),P_(n-3)]]
```

with `P_0=1`, `P_1=2x+3`, `P_(j+1)=(2x+3)P_j-P_(j-1)`, and the recurrence `B_(n+1)=R B_n` is exactly verified wherever the next fixture is present.

## Comparison with the frozen writer verifier

After freezing the fresh implementation, the writer's `splice_verifier.py` was inspected. Its published replay target is:

```text
PASS
farey_words=511
subtraction_free_sibling_checks=127
finite_local_tp2_sanity_checks=127
direct_gap_network_obstruction=det(M_1/3-M_1/2)=-(x+1)^2
```

All four reported finite counts / obstruction outputs agree exactly. The frozen root `H(S)`, `H(D)` and `F` profiles also agree exactly.

## Verdict

**REPRODUCTION PASS for the bounded executable / exact-fixture scope.**

What this supports:

- the published finite continuant-splice fixtures are reproducible by a fresh implementation;
- the exact root determinant obstruction is independently reproduced;
- representative extreme-boundary recurrence fixtures are independently reproduced.

What this does not support:

- it does not by itself establish the all-depth gap-cone induction;
- it does not establish a common `H`-grade network or switching theorem;
- it does not prove Local TP2;
- it does not justify further campaign continuation by itself.

Per the human continuation decision, reaching this bounded PASS is a terminal stopping point for this Task. A fresh continuation decision is required before allocating another Local TP2 lane.
