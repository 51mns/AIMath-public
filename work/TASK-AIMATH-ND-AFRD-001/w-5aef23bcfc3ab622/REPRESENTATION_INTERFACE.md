<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# AFRD representation and evaluation interface

## Candidate object

A candidate is not prose alone. Before hidden evaluation it freezes:

```text
encode(N, public_constants) -> X
```

plus deterministic serialization of `X`, source/hash of every readout, all learned parameters and hashes, the exact training manifest, public constants, environment, and resource budget.

`X(N)` must be computable without `p`, `q`, a factor-derived label, hidden answers, or hidden split membership. Serialized `X` is capped at 65,536 bytes per instance in this E0 pilot so a candidate cannot smuggle a large lookup table through the representation object.

## Readout A — factor localisation

The frozen readout may return at most eight disjoint closed integer intervals inside

`[3, floor(sqrt(N))]`.

Only odd integers count toward interval width. With smaller factor `p`, localisation succeeds when `p` lies in the interval union.

Let `M` be the number of odd integers in the full search interval and `W` the number in the returned union. Report:

`bits_saved = log2(M / max(1,W))`.

Returning the full interval has zero bits saved. Coverage and bits saved are reported together; a tiny interval that misses the factor is not a win.

Localisation is evaluated at predeclared total-width budgets `M/2`, `M/4`, `M/16`, and `M/256` (integer width rounded down, minimum 1 odd candidate). At a given budget the union may not exceed that width. Binary coverage at equal width is used for the paired success gate; the full coverage-versus-width curve and median bits saved are secondary descriptive metrics.

This channel is representation-agnostic: a graph, symbolic object, automaton, sequence, tensor, program, or another invented primitive can be used internally as long as the frozen readout produces the standard interval output.

## Readout B — actual factor recovery

The frozen readout may return `d` or failure. Success is exact:

`1 < d < N` and `N % d == 0`.

Timeout, exception, invalid divisor, or no answer is failure. Primary wall-clock caps are 0.01 s, 0.1 s, and 1.0 s per instance, with a 512 MiB memory cap in a frozen evaluator environment. Encoder time is included.

Wall time is an engineering metric, not mathematical complexity. Any later asymptotic claim requires a separate proof.

## Required matched controls

Every candidate is compared against:

1. the same frozen downstream model/readout family using raw `N` rather than `X(N)` where technically meaningful;
2. a trivial reversible re-encoding with matched size;
3. predeclared classical factorisation baselines at the same resource cap;
4. the closest predeclared representation/ML baselines where reproducible.

A representation that wins only because its decoder receives more compute, labels, parameters, or hidden metadata fails the utility attribution test.

## Exact paired signal gate

For each instance against the best predeclared eligible baseline at the same resource cap:

- `w`: candidate succeeds, baseline fails;
- `l`: baseline succeeds, candidate fails.

On H0 require both:

- `(w-l)/n >= 0.05`;
- exact two-sided binomial p-value on `w+l` discordant pairs under `p=1/2` is at most 0.01.

The direction must replicate on H4 and H5 with `w>l` and p-value at most 0.05. The gate is intentionally conservative and applies to binary success channels. Localisation additionally reports coverage-versus-width curves and cannot claim a win from bits-saved alone.

Passing this gate means **held-out signal**, not a new algorithmic complexity result and not novel mathematics.
