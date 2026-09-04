<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Validation

Environment:

- Python: 3.13.5
- OS/kernel: Linux 6.18.35 x86_64
- External Python dependencies: none

Commands and observed results:

```text
python3 -S gen_a_reference.py
PASS: GEN-A deterministic demo
2165177653 34739 62327
2013490027 37549 53623
1554197077 35089 44293
2737339351 49177 55663

python3 -S afrd_metrics.py
PASS: AFRD metric reference tests

python3 -S verify_afrd_contract.py
PASS: AFRD E0 contract invariants
visible_training=12288
hidden_total=7424
hidden_splits=H0_INTERPOLATION:1536,H1_SCALE:1152,H2_BALANCE:1152,H3_ARITHMETIC:1024,H4_GENERATOR:1536,H5_TEMPORAL:1024
```

All three commands exited with code 0.

The reference code checks contract mechanics only. It does not establish a factorisation theorem, a useful representation, novelty, or independent reproduction.
