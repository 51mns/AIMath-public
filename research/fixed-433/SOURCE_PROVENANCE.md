# Source provenance

Public snapshot source commit:

`c8e61e0e398f540bc8c5de79663398d689f37473`

The following source blobs were read from the private canonical repository before
building this history-clean public package:

| Public role | Canonical path | Git blob SHA |
|---|---|---|
| Candidate verifier | `research/433-family/candidate/generate_certificate.py` | `5c7b32d07e61d92e24cfdb44fd0d812f94dda28f` |
| Independent verifier | `research/433-family/independent/verify_fixed_433.py` | `045b2b469a44141fc3180448888d85cae2c3f0f7` |
| Frozen statement | `research/433-family/STATEMENT.md` | `6cc951f4bdc87c826ec5a7b03b36a6d253cf30c6` |
| Proof | `research/433-family/PROOF.md` | `a26d3a89fd07b6618027c0acba840fc173028a22` |
| Independent review | `research/433-family/INDEPENDENT_REVIEW.md` | `e3e343ab2405563ee516c5200c9c0b3905a77075` |

The public replay wrapper is new public-distribution glue. It does not replace
the independent verifier and does not make the independent verifier import the
candidate implementation.
