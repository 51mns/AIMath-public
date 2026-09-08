<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# AFRD data and hidden-split contract

All factors are distinct odd primes and labels use `p<q`. Prime bit length means `2^(b-1) <= p < 2^b`. The evaluator rejects duplicate `N` across every visible/hidden split.

## Visible discovery training

- generator: `GEN-A`
- factor bit pairs: `(16,16)`, `(20,20)`, `(24,24)`
- 4096 instances per pair
- total: **12,288**
- visible seed convention: `AFRD-E0-v1-visible-training` for the eventual frozen public manifest

The discovery packet may expose `(N,p,q)` labels if that choice is frozen before the run, but deployed hidden-evaluation code may use only `N` and public constants.

## Hidden splits

| Split | Construction | Count | Purpose |
|---|---|---:|---|
| H0 | GEN-A; same three factor-bit pairs; 512 each | 1,536 | interpolation |
| H1 | GEN-A; `(28,28),(32,32),(36,36)`; 384 each | 1,152 | scale extrapolation |
| H2 | GEN-A; `(16,24),(20,28),(24,32)`; 384 each | 1,152 | balance shift |
| H3 | GEN-A; `(24,24)`; four arithmetic families; 256 each | 1,024 | arithmetic shift |
| H4 | independent GEN-B; training bit pairs; 512 each | 1,536 | generator shift |
| H5 | independent GEN-B; generated only after candidate freeze | 1,024 | temporal holdout |

Hidden total: **7,424**.

## H3 arithmetic families

The smaller factor `p` is constrained as follows; the evaluator rejects/resamples until `p<q` and both are 24-bit primes.

1. `SAFE_PRIME_FACTOR`: `p=2r+1` with both `r` and `p` prime.
2. `P_MINUS_1_4096_SMOOTH_FACTOR`: the largest prime divisor of `p-1` is at most 4096.
3. `P_MINUS_1_HAS_FACTOR_AT_LEAST_2_POW_20`: the largest prime divisor of `p-1` is at least `2^20`.
4. `SELECTED_MOD16_CLASSES`: 128 instances satisfy `(p mod 16,q mod 16)=(1,15)` and 128 satisfy `(3,13)`.

H3 generation may use factors internally because it is evaluator-side instance construction; the candidate still receives only `N`.

## H5 temporal strata

H5 is generated after the complete candidate package is frozen:

- 512 balanced `(24,24)` instances;
- 256 unbalanced `(20,28)` instances;
- 256 arithmetic-shift instances: 64 from each H3 family, using GEN-B rather than GEN-A.

This prevents H5 from being only another sample of the easiest training regime.

## GEN-A

`gen_a_reference.py` is the public reference implementation. It uses a seed string hashed by SHA-256 into a Python 3.13 `random.Random` stream and deterministic Miller-Rabin bases `[2,3,5,7,11,13,17]`. All factor candidates are below `2^36`, within the deterministic range used by this reference. Visible data use a public seed; each hidden split uses evaluator-side seed material withheld until reveal.

## GEN-B

GEN-B must not import/reuse GEN-A code, candidate ordering, or RNG state. The frozen E0 choice is an evaluator wrapper around **OpenSSL 3.x** `openssl prime -generate -bits <b>`, using OpenSSL's independently seeded DRBG. The evaluator records exact OpenSSL version and the exact generated `(N,p,q)` manifest.

GEN-B randomness is not treated as reproducible from a disclosed seed. Post-evaluation publication of the exact sorted manifest is the replay authority. The purpose of H4/H5 is generator independence, not bit-for-bit re-generation of OpenSSL randomness.

## Commitment and reveal

Before any hidden split is evaluated, the evaluator records:

- split identifier;
- generator/version;
- count;
- SHA-256 of canonical sorted `(N,p,q)` manifest;
- environment/toolchain;
- generation timestamp.

The manifest contents, factors, and hidden GEN-A seed material stay unreleased until the candidate and evaluation results are frozen. H5 cannot be generated before candidate freeze. After evaluation freeze, enough replay material is published to independently recompute every score.
