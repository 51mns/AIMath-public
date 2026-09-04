# Evidence policy

AIMath Public separates mathematical truth, finite computation, independent reproduction, literature novelty and author confirmation.

## Minimum evidence record

A public research package should record, where applicable:

- claim ID and exact frozen statement;
- canonical private snapshot used for export;
- fixed writer/reviewer commit identifiers as provenance pointers;
- exact inputs and their provenance;
- reproduction commands and exit status;
- runtime/dependency versions when executable evidence depends on them;
- generated artifact hashes when those bytes are load-bearing;
- whether writer and verifier implementations share code;
- known model/harness/context overlap that could create correlated review errors;
- whether evidence is finite/bounded or proves a universal statement;
- mathematical validity, novelty, author confirmation and reproduction status separately.

## Proof versus computation

Finite exact computation may:

- prove a genuinely finite claim;
- certify a concrete witness/counterexample;
- falsify a universal conjecture by finding a counterexample;
- support regression/adversarial controls.

It must not be presented as an infinite theorem merely because no counterexample was found up to a large bound.

A universal claim requires a mathematical argument that covers its full quantifier range.

## Independent review

A writer does not promote its own result to `INDEPENDENTLY_REPRODUCED`.

In AIMath, **independent review means a separately executed review path with its own derivation and evidence record. It does not mean that reviewer errors are statistically independent.** Different sessions, worker IDs, branches, commit hashes or nominally separate agents do not by themselves eliminate correlated failure modes. Related model families or harnesses, shared system/repository context, shared libraries/toolchains, common source material and common upstream assumptions can all cause false agreement.

When known and safe to disclose, a review should record material overlap in model/harness lineage, repository context, implementation libraries and upstream evidence. If the relevant error-mode independence is unknown, it should be treated as **not established**, not silently assumed. Cross-model or human review can reduce some correlated-risk channels, but no review label guarantees correctness.

A strong independent review should disclose:

- what information the reviewer saw before its derivation was fixed;
- whether it imported writer code or generated outputs;
- whether every load-bearing implication was rederived;
- any shared-library, model/harness, repository-context or implementation-independence limitation;
- negative controls or adversarial checks used to detect false agreement.

## Durable evidence identity

A branch name is a workflow locator, not durable mathematical identity. Fixed commits, public claim-package files and immutable tags/releases where needed are stronger evidence identities.

Public packages may cite fixed private evidence SHAs as provenance without exposing private Git history. The public repository deliberately uses a fresh, history-clean Git history.

## Large immutable artifacts

Large accepted binary/certificate bundles should not be pasted into documentation. If they become necessary public evidence, publish the exact accepted bytes through an appropriate immutable release mechanism and record:

- asset name and size;
- SHA-256;
- producing fixed commit;
- independent acceptance/review;
- clean reproduction command and dependency lock.

A release asset complements source/proof history; it does not replace it.

## Novelty and literature

Search failure is not proof of novelty. A literature audit should record:

- primary sources actually inspected;
- exact theorem/equation/page correspondence where possible;
- inaccessible or unresolved sources;
- whether the search was exact-match, bounded neighbourhood, or publication-level.

Use `NEW`, `FIRST`, `NOVEL` or priority language only when the evidence genuinely supports it.

## Author confirmation

Author confirmation is a separate provenance dimension. Public mathematical validity should not depend on raw private correspondence. If the project record reports confirmation but raw correspondence is intentionally not public, say exactly that and limit the confirmation claim to the recorded scope.

## Privacy firewall

Never publish merely for evidentiary completeness:

- raw private conversations or ChatGPT exports;
- raw email/DM/correspondence;
- personal identifiers not required by the mathematics;
- credentials, tokens or secrets;
- private `.git` history;
- opaque private attachments;
- internal coordination logs with no mathematical value.

When useful mathematics exists only inside such material, reconstruct a clean public statement/proof/certificate from the accepted fixed evidence instead.
