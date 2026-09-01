# Public export validation — 2026-09-01

This record covers the public-export completion branch before pull-request review.

## Fixed repository state

- private canonical source snapshot: `c8e61e0e398f540bc8c5de79663398d689f37473`
- public base `main`: `20589c79a34383b3a7699cd824eeaa930da9f231`
- public export branch checkpoint used for the fixed-blob replay: `7600813cabd7151b4e642ab9a557b5e1094ad76c`

The validation environment could not open a network Git clone because DNS/network access to GitHub was unavailable. Therefore the executable public files were fetched from GitHub through the connected repository API at the public branch, reconstructed in an isolated directory, and checked with `git hash-object` before execution. A replay was counted only when the reconstructed Git blob SHA exactly matched the SHA returned by GitHub.

Environment: Python `3.13.5`.

## Exact Git-blob read-back

| Public file | Git blob SHA | Result |
|---|---|---|
| `research/433-springborn-obstruction/verify_springborn_obstruction.py` | `d4628cadf1f146171f9be0e749f8ba7280515c0b` | byte-identical replay PASS |
| `research/433-springborn-obstruction/inputs.json` | `919876047a695c14e3cd0689e9af6c84baec9409` | byte-identical input |
| `reviews/433-springborn-obstruction/independent_verify.py` | `b40af6fa78918db1c4a8da2d022c07c8ceb913cc` | byte-identical replay PASS |
| `research/433-existing-theory-identification/verify_identification.py` | `434d4a678a278617aa06c1281f18dcb7e5c28a12` | byte-identical replay PASS |
| `reviews/433-existing-theory-identification/independent_verify.py` | `9e54cf38b286555b30013d02b01eda18310a57c1` | byte-identical replay PASS |
| `research/gyoda-89/verify.py` | `ae86a8eda5c7a6814d51e94dcb7ad059587cd548` | byte-identical replay PASS |
| `research/equiangular-r18-eta17/verify.py` | `4445ee000e3215220696bbddc2191df6010548f7` | byte-identical replay PASS |
| `research/b3rcc-apc/verify_rank4_witness.py` | `a249e2154976ed85e7a36072839630b1219fed40` | byte-identical replay PASS |
| `reviews/b3rcc-apc/exact_controls.py` | `7ef2e805216d28a42f6f7202e3e2cb6e47870456` | byte-identical replay PASS |
| `research/afes-bounded/verify.py` | `4d25dec33ef7dd8272b603511d48a496ad0f1933` | byte-identical replay PASS |
| `research/thue-morse-rediscovery/verify.py` | `cd80289d18fd356b6584095d2986d34002472f62` | byte-identical replay PASS |

The pre-existing `research/fixed-433/reproduce.py` package is not duplicated in this table; the repository's existing GitHub Actions workflow already runs that replay on pull requests.

## Deterministic output SHA-256

The byte-identical fixed-blob executions above returned exit code `0`. Captured stdout hashes:

```text
36f106abcd89121ea9df5342049420a22da0bbc40305932e738d9661b5d2d7e2  springborn-writer
 e07eb8f3be37c3701b8f680cf9cae2bcf48d7ec74ae4b010709e2880817c9871  springborn-independent
86b51ff073ceca65d4ed1d1c3b17c7d4ac67130cc3b959a412ee1d7a40fc3e58  identification-writer
4563e6a413da970f3fda7d8d7f67f2ebf42c53cda3279241923e5b2bc2fe08d0  identification-independent
24cabe8ecce90a165013403bb666a6dd6162dde8b62c1fc054157481ca27a0e5  gyoda-89
b01fbc735a273b00b70f5892a317006215f45f5ba7572c21823df2888cd4a272  equiangular-r18-eta17
e69ee4116a8b392ec8f3dd5f6d9bac23940c541fa28d0b64217f9f2255cd8aea  b3rcc-rank4-witness
0d2cb05e6fbea89cdfbeb5b0e7d93ae6a45604f0890298119fbce3e86ef91099  apc-all-rank-controls
bac3d08fdd85a07cd780c656f471a2ec4cc1c0ee06d2991a8eb3f0d64881d514  afes-bounded
ef2ae56c7403047206d6c0efe8b53ce5e960bc78b7f5ed60f661c7f9c82d24d9  thue-morse
```

The leading space before the second line is formatting only; the hash is the 64-hex string beginning `e07e...`.

## Mathematical/reproduction boundary

These executable checks are supporting reproduction evidence. They do not replace the all-`k` proofs, the APC all-rank proof, or independent mathematical reviews. In particular:

- finite fixed-433 rows do not prove the universal identities;
- the R18 script verifies the exact finite deck certificate used by the proof;
- APC exact controls are sanity/falsification controls, not a finite proof of the all-rank theorem;
- AFES strict canonical encoding remains outside the accepted bounded semantic claim;
- Local TP2 remains `PROOF_CANDIDATE` and no finite scan is promoted to a theorem.

## Privacy boundary

No private Git history, raw conversations, raw correspondence, private attachments, credentials, or personal identifiers were needed for these replays. The branch must still pass `scripts/public_release_audit.py`, public-layout validation, pull-request diff review, and commit-metadata review before merge.
