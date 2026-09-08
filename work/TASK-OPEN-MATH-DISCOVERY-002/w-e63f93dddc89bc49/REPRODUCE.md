<!--
SPDX-FileCopyrightText: 2026 AIMath contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# Reproduction record

Run from the repository root:

```bash
python3 -S work/TASK-OPEN-MATH-DISCOVERY-002/w-e63f93dddc89bc49/verify_continuant_matching_transfer.py
```

Expected terminal output:

```text
PASS
seed=AIMath-TASK-OPEN-MATH-DISCOVERY-002-w-e63f93dddc89bc49-v1
train_words=1364
train_perturbations=12744
held_out_cases=128
held_out_length_range=6..12
held_out_digit_range=1..25
negative_control_dimer_weight_2=FAIL_AS_EXPECTED
negative_control_prefix_denominator_failures=3/3
held_out_digest=adaf08e035fe55a2e4ac980b01db997572f164d58178751d60e8561e30157a1e
```

Research-session verification used Python standard library only and exited
with status 0 under `python3 -S`.
