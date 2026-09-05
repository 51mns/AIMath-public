# TASK-AIMATH-ND-001 preregistration

- Public base: `71547cb5d757afaace54b558f2d0a4a49fad5656`
- Task: `TASK-AIMATH-ND-001`
- Worker: `w-5023e0723711`
- Principal: `gh:51mns`
- Stage: E0, AI-native representation experiment

## Frozen goal

Starting only from the exposed training integer sequences below, construct a compact transition representation and test whether it provides measurable mathematical utility beyond a frozen direct-recurrence baseline. Utility must be demonstrated on held-out data and on an explicit cross-domain transfer. Mere reversible encoding, equivalent restatement, or in-sample fit counts as failure.

## Frozen raw training packet

The representation-development phase sees only these two sequences and the fact that all arithmetic is exact integers:

- `A = [2, 3, 7, 18, 47, 123, 322, 843]`
- `B = [2, 5, 23, 110, 527, 2525, 12098, 57965]`

Their provenance is intentionally not used by the representation search. It may be disclosed only in the final analysis.

## Frozen baseline

The baseline is the smallest direct second-order recurrence of the restricted form

`u[n+1] = c*u[n] - u[n-1]`

when a single exact rational `c` inferred from the first three exposed terms is consistent with all training transitions. On transfer sequences, the baseline receives the first three terms, infers `c = (u[2] + u[0]) / u[1]` when defined, and predicts forward. If a later term disagrees, the transfer is a baseline failure from that point onward.

This baseline is fixed before held-out inspection so a representation does not receive credit for rediscovering an equivalent recurrence.

## Representation budget

After seeing only A and B, the worker may define one representation family using adjacent transitions and exact integer/rational operations. The representation specification must be committed before held-out values are generated or inspected. Search complexity is bounded to primitive homogeneous quadratic transition seals with integer coefficients of absolute value at most 8, plus a parameterized rule justified by both training sequences.

No graph, matrix, vector, spectral, Pell, or continued-fraction primitive is supplied to the representation-development phase.

## Frozen held-out procedure

### Cross-domain held-out

Generate Pell solutions to `x^2 - 2 y^2 = 1` from `(x_0,y_0)=(1,0)` by exact multiplication by `3 + 2*sqrt(2)`:

- `x' = 3x + 4y`
- `y' = 2x + 3y`

Generate ten `x_n` values, expose only the first three to both methods, and reserve indices 3..9 for held-out prediction. The representation specification is frozen before these values are computed.

### Adversarial transfer control

Generate Catalan numbers `C_n = binom(2n,n)/(n+1)` for n=0..9. Expose the first three terms and reserve indices 3..9. A useful method should not silently treat an early accidental fit as universal structure.

## Frozen metrics

1. exact held-out predictions correct / 7 for Pell x-coordinates;
2. first incorrect prediction index on the Catalan control;
3. whether the representation gives strictly more predictive power than the frozen baseline;
4. proof-obligation count: number of independent algebraic obligations required to justify universal forward prediction once the pattern is fixed;
5. whether the representation transfers a reusable invariant that is not merely algebraically equivalent to the baseline recurrence.

## Decision rule

- **Positive utility** requires at least one strict gain over the baseline in prediction, falsification, invariant discovery, proof-obligation compression, or transfer.
- Exact held-out success with no strict gain is **not** success.
- If the representation reduces algebraically to the baseline recurrence, record a bounded negative result rather than promoting it.
- No novelty claim follows from this experiment; literature novelty would require a separate audit.
