<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# TASK-AIMATH-ND-001 outcome — transition-seal pilot

## Frozen scope

This worker tested one bounded AI-native representation family: primitive homogeneous quadratic **transition seals** on adjacent integer values, with coefficient bound 8, learned from two unlabeled training sequences and evaluated against the preregistered direct second-order recurrence baseline.

Public base: `71547cb5d757afaace54b558f2d0a4a49fad5656`  
Worker: `w-5023e0723711`  
Branch: `research/TASK-AIMATH-ND-001/w-5023e0723711`

## Outcome

**Decision: `NO_STRICT_UTILITY_GAIN` (bounded negative result).**

The exact training search found unique canonical primitive seals

- `x^2 - 3xy + y^2 = -5` for training sequence A;
- `x^2 - 5xy + y^2 = -21` for training sequence B.

This suggested the parameterized representation

`Q_c(x,y) = x^2 - cxy + y^2`.

However, equality of consecutive seals factors exactly as

`Q_c(x,y) - Q_c(y,z) = (x-z)(x+z-cy)`.

After excluding the backtracking root `z=x`, the representation gives

`z = cy - x`.

Moreover the parameter inferred from three values is

`c = (z^2-x^2)/(y(z-x)) = (z+x)/y`,

which is algebraically identical to the frozen baseline fit. This equivalence was established before replacement held-out values were inspected.

## Held-out and transfer

The initially proposed D=2 Pell/Catalan test was retired before representation freeze because scratch work had already exposed some values. `PREREGISTRATION_AMENDMENT.md` records this contamination rather than silently reusing it.

The replacement cross-domain held-out was the x-coordinate sequence of solutions to `x^2-7y^2=1`, generated independently by multiplication by `8+3sqrt(7)`. The representation and baseline both inferred `c=16` from the first three x-values and both predicted all seven reserved values exactly.

The replacement adversarial Bell-number control produced the same behavior for both methods: both fit `c=3` from the first three terms, both happen to predict the next term, and both first fail at zero-based index 4. Thus the representation provides no earlier falsification signal.

Exact metrics:

- Pell held-out: baseline `7/7`, seal `7/7`;
- strict predictive gain: **false**;
- strict falsification gain: **false**;
- proof-obligation compression: **false**;
- reusable non-equivalent invariant gain: **false**.

## Training provenance disclosure after freeze

After the representation was frozen, the two training sequences were verified to be

`tr(M_c^n)` for `M_c = [[c,-1],[1,0]]`, with `c=3` and `c=5` respectively. The representation-development phase used only the integer sequences, not this provenance.

This provenance explains why the learned quadratic seal is natural; it is **not** evidence of mathematical novelty.

## Exact reproduction

Standalone verifier:

```bash
python3 -S work/TASK-AIMATH-ND-001/w-5023e0723711/verify_transition_seal.py
```

Local run in the research session:

- Python: `3.13.5`
- exit code: `0`
- stderr: empty under `python3 -S`
- local verifier SHA-256: `976e25817808d006dcff891800466feb94b3c0981a1db79be16200fa8f9a0402`
- local generated-results SHA-256: `b883522a9d33d1071e2da2d360b5ef79bbf86cd10ad0ef361cbc0601925138f5`

Remote read-back at the worker branch found:

- verifier Git blob: `7b4d0bede4c4cb245178e732129b877b0a229731`;
- results Git blob: `ed3c9f48292ece2533dcc95f8540e7c341a6d567`.

The full repository validation suite was not run in the session because no complete local repository checkout was available; repository CI is the whole-tree gate.

## Claim / novelty boundary

Claim level remains **EXPLORATORY**. No theorem promotion, independence claim, publication novelty claim, or external-frontier claim is made.

The reusable information is narrow: within this frozen quadratic transition-seal architecture and baseline, the apparent invariant does not earn AI-native utility because it collapses to the same recurrence. This does not rule out higher-degree, nonlocal, non-polynomial, or otherwise genuinely different AI-native representations.

## Self-assessment (zero allocation authority)

- information_gain: 3/5 — the route is cleanly falsified against its own utility gate;
- mathematical_reusability: 2/5 — the algebraic equivalence is reusable as an anti-duplication note;
- transfer_potential: 1/5 — transfer occurred but added no value beyond baseline;
- external_relevance: 1/5;
- followup_expected_value: 1/5 — do not scale this exact representation family;
- surprise: 2/5;
- uncertainty: 1/5;
- recommendation: `PIVOT` only if a materially non-equivalent representation mechanism is proposed.

This self-assessment has `truth_layer_effect = NONE` and no scheduling authority.
