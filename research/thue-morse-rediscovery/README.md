# Thue–Morse constant rediscovery

**Claim ID:** `C-THUE-MORSE-REDISCOVERY`  
**Canonical level:** `INDEPENDENTLY_REPRODUCED`

The frozen pilot candidate

\[
C=\sum_{n\ge0}\frac{\operatorname{popcount}(n)\bmod2}{2^{n+1}}
\]

is exactly the already-known **Thue–Morse constant**. This is a validated rediscovery/certification example, not a new constant.

It has the exact product characterization

\[
C=\frac12-\frac14\prod_{k\ge0}\left(1-2^{-2^k}\right).
\]

## Reproduce

```bash
python3 research/thue-morse-rediscovery/verify.py
```

The verifier uses exact integers/Fractions, checks the finite product identity, supplies a rigorous dyadic tail enclosure, and prints a certified decimal prefix.

## Boundary

`NEW_CONSTANT_DISCOVERED` is false. Bounded relation-search failure does not imply transcendence, algebraic independence, or any global nonrelation statement.

Writer `6085146de4f50c9959d72f0d5e5fddcbdea2e3fa`; independent reviewer `789776523fb9f67a76761abdae8916b97fd9dc34`.
