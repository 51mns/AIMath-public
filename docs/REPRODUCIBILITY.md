# Reproducibility contract

Every exported mathematical claim package should be independently usable without private AIMath context.

## Required package structure

```text
research/<claim>/
  README.md
  STATEMENT.md
  PROOF.md                  # when a proof exists
  inputs/ or inputs.json
  reproduce.py or reproduce.sh
  expected_output.json
  SHA256SUMS.txt
reviews/<claim>/
  INDEPENDENT_REVIEW.md
  independent_verify.py     # when computation is involved
```

A package may use a different layout if the README explains it clearly.

## Minimum reproduction record

A public reproduction should state:

1. exact claim ID and statement;
2. runtime / dependency versions;
3. exact input files;
4. exact command;
5. exit code;
6. expected output or certificate;
7. SHA-256 hashes of durable artifacts;
8. negative or mutation controls when meaningful;
9. the boundary between finite computation and mathematical proof.

## Recommended command

From the repository root:

```bash
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
```

Each claim package should then expose one simple command of its own.

## Independence rule

An independent verifier should not simply import the writer's implementation. If the proof depends on computation, the reviewer should reimplement the decisive invariant/check whenever feasible.

## Failure is useful

If a public replay fails:

- record operating system and Python version;
- paste the exact command;
- include the first meaningful error;
- say whether hashes still match;
- open a **Reproduction failure** issue.

Do not silently change expected outputs to make a test pass.
