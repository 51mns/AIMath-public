# Village v1.3 /next live-field recovery — R2 merge evidence

Status: `R2_REMEDIATION_MERGED_POSTVERIFY_PASS`

This branch is evidence-only and is not merged to `main`.

## Preserved canonical state before remediation merge

- Preserved M4: `c861bf0aef4d98c52f0792e5761ece27d0524264`
- Canonical Dittert lock path: `coordination/locks/dittert-n5/broader-zero-pattern.yml`
- Canonical Dittert lock blob: `042775d7a876b807dda6ed3e67102336ff5e5f8a`
- Historical source epoch: `730fe029ad2479bcb83f2d5ce9744f6f18578c783c2c8fa84f0d491e4d691065`

## Live replay failure evidence retained before cleanup

Unexpected replay transport:

- PR #52: OPEN / DRAFT / UNMERGED immediately before R2 merge
- head: `a178b69e9c6229e5cc1da7d7bcbb3646fa6138e2`
- ref: `next-acquire/e41095302836fbc77ccf0a6b2e08278d3fd54f5c9e579dbf3849d07bf815ec1c/TASK-FIXED-433-001/w-0bebfd2fd11cb67f`
- selected Task: `TASK-FIXED-433-001`
- source epoch binding: historical source epoch above
- this transport never became canonical ownership.

Failed R1 remediation evidence:

- PR #53: OPEN / NON-DRAFT / UNMERGED immediately before R2 merge
- R1 head: `ba307883dd74afced832ac8673c78c78b90e86f4`
- R1 residual independent-review finding: retained ACQUIRE transport handoff could bypass the source-epoch consumption guard after canonical confirmation failed.

## Accepted R2 remediation

- PR #54
- final head: `8c5c7b6b7272d2cd22d8fda26f73dc905635d187`
- target core blob: `9aa52123cfd95f06189bfd56c55c07a5a70da827`
- target test blob: `861451d1b44b53487eb6bc45fdbf792c8464d3d4`
- exact-head Verify #132 / run `33848696838`: completed / success
- independent R2 review commit: `f70f546da5ce9d77949860be1c0b32120f85ffa0`
- independent R2 review blob: `5215f442088ba73ca9ae3955dc95b37f68cb0e61`
- verdict: `PASS — REMEDIATION_ACCEPTED`
- unresolved CRITICAL/HIGH/MEDIUM/LOW: `0/0/0/0`

## Merge and post-merge proof

PR #54 was merged with exact expected head.

- post-remediation main: `dd13fd15496bab9325e2520e3d1bfad3390eba2d`
- merge parents:
  - preserved M4 `c861bf0aef4d98c52f0792e5761ece27d0524264`
  - accepted R2 head `8c5c7b6b7272d2cd22d8fda26f73dc905635d187`
- merge tree: `d7a740535cbd149b6098f075c562790a5a114c08`
- GitHub commit signature: valid
- post-merge Verify #133 / run `33850436937`: `completed / success`

The merge changes only the cumulative accepted R1+R2 production/test scope. The preserved Dittert lock remains canonical history evidence and was not manually renewed, taken over, deleted, or rewritten during remediation.

## Recovery policy after this freeze

1. Close PR #52 without merge.
2. Delete only its unintended replay ref.
3. Do not use PR #52 as canonical authority.
4. Reconstruct the stale historical source-epoch replay state from preserved evidence and execute exactly one production `/next` replay against fresh post-remediation `main`.
5. Expected result: `OLD_ACQUISITION_REPLAY`, exit 2, zero GitHub transport writes, no new RELEASE/ACQUIRE ref or PR, and no canonical lock mutation.
6. Then run final idempotency using the original successful ACTIVE_NEXT retained state.
7. Only after replay/idempotency evidence passes, perform truth-neutral Dittert cleanup under the preregistered cleanup policy.
