# Getting started

## I only want to understand the results

Read `docs/RESULTS.md`. Every important result is named by a stable Claim ID and comes with a boundary statement.

## I want to reproduce a result

1. Open the claim package under `research/`.
2. Read `STATEMENT.md`.
3. Check `requirements.lock` or the package README.
4. Run its `reproduce` command.
5. Compare the result with the committed expected output and hashes.
6. Read the corresponding independent review under `reviews/`.

## I think a proof is wrong

Great — open a **Math review** issue. Give the Claim ID, the exact lemma/step, and either a counterexample or the smallest point where the inference fails.

## I found a stronger theorem

Open an issue before rewriting the existing claim. State:

- the old Claim ID;
- the stronger statement;
- which hypotheses were removed/changed;
- whether your evidence is proof, finite computation, or conjecture;
- what independent check would decide it.

## I want to use AIMath as a research workflow

Use the template under `templates/claim-package/`. The core idea is simple:

```text
freeze statement -> produce proof/certificate -> independent reproduction
-> novelty audit -> public status
```
