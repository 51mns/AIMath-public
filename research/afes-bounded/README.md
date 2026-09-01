# AFES-0.1 bounded exact semantics

**Claim ID:** `C-AFES-BOUNDED-SEMANTICS`  
**Canonical level:** `INDEPENDENTLY_REPRODUCED`

AFES (AIMath Finite Exact Specification) is a bounded proof-carrying number formalism with three atom families:

```text
rat
alg_root
alt_series
```

and a recursive expression layer

```text
add, sub, mul, neg, certificate-relative div.
```

The accepted claim is deliberately narrow: the reviewed constructors/operations and fixed exact examples have coherent bounded syntax/semantics, with partial equality and certificate-relative division.

## Fixed benchmark

The reviewed examples include exact specifications of

```text
0, 1, -1, 2, 1/3, sqrt(2), i, golden ratio, pi, e.
```

The algebraic identities `sqrt(2)^2=2`, `i^2=-1`, `phi^2=phi+1`, exact rational arithmetic, and an exact alternating-series enclosure `3<pi<4` are certificate-level checks.

## Important separate open claim

`C-AFES-STRICT-CANONICAL-ENCODING` remains `PROOF_CANDIDATE`. The independent repair review found a Python bool/int scalar-type edge in the private implementation. Therefore this public package does **not** claim that every malformed JSON scalar has a unique/rejected encoding.

See `BOUNDARIES.md`.

Writer repair `27a68a1acef3ee30c613ba6e262759bcb424aee5`; repair-limited independent review `337c697532b95c018f2ccaea7204bd7ae0fae0bc`; canonical intake `2e6ba0312ac201aaf8914d310fc40a0898b7d3f2`.
