# Fixed-433 bounded-energy family

**Claim ID:** `C-ROOT-433`  
**Status:** `INDEPENDENTLY_REPRODUCED`  
**Publication novelty:** `NOT ESTABLISHED`

This public package contains:

- the frozen theorem statement;
- the all-k proof;
- the candidate exact-arithmetic construction;
- a separately written independent verifier;
- a self-contained public replay command.

## Reproduce

From the public repository root:

```bash
python3 research/fixed-433/reproduce.py
```

Expected final line:

```text
fixed-433 public reproduction: PASS
```

The replay checks three exact cases through both implementations, cross-compares
their common outputs, reruns the fixed all-k identity bases, and exercises four
negative controls.

The finite cases are **not** used as the proof of the infinite statement; read
`PROOF.md` for the universal argument.

## Public-export boundary

The private workspace also contains historical input provenance and whole-repo
validation artifacts. Those private-workspace artifacts are deliberately not
required by this public self-contained replay.

See `SOURCE_PROVENANCE.md` for source blob hashes.
