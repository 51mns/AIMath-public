<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# AFRD discovery / evaluator information firewall

## Roles

### Discovery lane
May inspect only:
- the public task statement;
- the visible training tuples explicitly released for discovery;
- public experiment constants and interface/resource limits;
- its own scratch work and frozen candidate package.

Must not inspect before its own candidate freeze:
- H0-H5 instances, factors, randomness or scores;
- evaluator-only baseline implementation details beyond the names required by the public comparison contract;
- candidate-specific prior-work matches or novelty hints;
- another discovery lane's unpublished/frozen representation or derivation;
- accepted proof text that directly contains the hidden target mechanism;
- post-signal reduction/audit output.

If any of those are exposed before freeze, that lane records `LEAKAGE_ABORT` and cannot be reported as a blind AFRD trial.

### Evaluator lane
May know hidden factors and baseline implementations. It must not modify a frozen candidate, training data, hidden split membership, resource budget, or success gate after seeing hidden performance.

### Falsifier lane
Receives the frozen candidate and frozen evaluator contract after initial hidden scoring. It tries generator, temporal, arithmetic, re-encoding, and resource-accounting controls. It does not promote claims.

### Novelty/reduction auditor
Starts only after a candidate passes the predeclared utility gate. It may inspect prior literature and known algorithms, try to algebraically reduce the candidate to known mathematics, and report `KNOWN_REDUCTION`, `CLOSE_PRIOR_ART`, or `NOVELTY_NOT_ESTABLISHED`. Search absence is never novelty proof.

## Freeze sequence

1. Contract and visible-data generator are frozen.
2. Discovery lane works without evaluator baseline detail or hidden data.
3. Candidate package is committed with hashes and a freeze timestamp.
4. H5 is generated only after step 3.
5. Evaluator runs H0-H5 without candidate edits.
6. Results and replay material are frozen.
7. Only candidates that pass the signal gate enter candidate-specific prior-work/reduction audit.
8. Falsification and mathematical extraction are separate from novelty judgement.

## Hidden-state persistence rule

Actual hidden seeds, hidden factors, unreleased H0-H5 instances, and H5 generation material are **not** stored in this public worker path before candidate freeze. This E0 task freezes their generation and commitment protocol, not their values. A future experiment must record a pre-evaluation SHA-256 commitment to each hidden manifest and later publish the replay material after evaluation is frozen.
