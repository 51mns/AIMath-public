# AIMath Public licensing

AIMath-public uses a **path-based multi-licence model** so software, mathematical exposition, and machine-readable research state can be reused under terms appropriate to each kind of artifact.

This is an open-source/open-science project licence policy, not legal advice.

## Root licence index

The root [`LICENSE`](LICENSE) file is a human-readable **licensing index**, not a single repository-wide licence grant. The authoritative per-path assignment is `REUSE.toml`, and exact licence texts are stored in `LICENSES/`.

Because the repository intentionally uses multiple licences, GitHub or other hosting UIs may fail to display a single detected licence. That must not be interpreted as an absence of licensing; use `REUSE.toml` and the applicable SPDX assignment for the path you are reusing.

## Default licences

| Material | SPDX identifier | Intent |
|---|---|---|
| software, validators, CI, schemas and executable tooling | `Apache-2.0` | permissive software reuse with explicit patent terms |
| original proof prose, independent-review prose, diagrams, explanatory documentation and research notes | `CC-BY-4.0` | broad reuse with attribution |
| frozen mathematical statements created by AIMath, certificates, manifests, claim/task/campaign state and other machine-readable scientific data | `CC0-1.0` | friction-minimised machine reuse and dependency chaining |

The authoritative per-path assignment is `REUSE.toml`. Exact licence texts are in `LICENSES/`.

## Important boundaries

- These licences apply only to copyright and related rights that AIMath contributors actually hold.
- AIMath makes no copyright claim over non-copyrightable mathematical facts, ideas, methods, or other material for which it does not hold the relevant rights.
- Third-party material keeps its original terms. If redistribution rights are unclear, use a citation/reference rather than copying the artifact.
- A statement transcribed or quoted from a third-party source is **not** made CC0 merely because it appears near an AIMath statement. Mark it as upstream/reference-only.
- CC0 does not waive patent or trademark rights. Software-like validators and executable logic belong on the Apache-2.0 side.
- There is no project `NOTICE` file. Add one only if a future distribution actually requires retained attribution notices or the project deliberately adopts one.

## Frozen statement boundary

AIMath-authored `STATEMENT.md` files and canonical machine-readable `CLAIM.yml` metadata are assigned `CC0-1.0` by the more specific rules in `REUSE.toml`. Proofs and explanatory prose remain `CC-BY-4.0`.

This avoids attribution stacking when theorem statements are copied through long dependency chains while preserving scientific provenance in claim metadata.

## Contributions: DCO + path-specific inbound licensing

AIMath uses the **Developer Certificate of Origin 1.1 (DCO 1.1)**. The canonical text is maintained at:

`https://developercertificate.org/`

Every contribution commit must contain a `Signed-off-by:` trailer. The sign-off certifies that the submitter has the right to make the contribution under the licence applicable to the target path.

Unless a contribution is explicitly and validly marked otherwise before submission, an intentionally submitted contribution is offered under the licence assigned to its target file/path by SPDX/REUSE metadata.

No copyright assignment to AIMath is required. Contributors retain the rights they hold while licensing the contribution under the applicable outbound licence.

### Privacy

DCO sign-offs are public Git history. Contributors should understand that the sign-off is retained indefinitely. GitHub noreply addresses are allowed and recommended for contributors who do not want to expose a personal email address.

The responsible submitter is the GitHub actor that submits the contribution. AI systems may assist with research or drafting, but the AI itself does not sign the DCO. AI assistance should be recorded as provenance when material.

## Licence, truth, credit and portfolio are separate

- **Licence** decides what may be reused.
- **Truth** decides what mathematical knowledge is accepted.
- **Credit** records who or what contributed to discovery, proof, computation or review.
- **Portfolio** decides where AIMath itself invests research effort.

A campaign being `HOLD` or `CLOSED` never restricts an outside researcher from using the openly licensed material or studying that mathematics.

## REUSE/SPDX

AIMath follows REUSE Specification 3.3 metadata conventions.

Existing files are assigned primarily through root `REUSE.toml`; new files should prefer explicit SPDX headers where practical. The CI `reuse lint` gate must remain green before merge.

## AI-generated material

Licences apply only to rights actually held. AIMath does not make a blanket assertion that pure machine-generated output is copyrightable or owned by a human contributor. The responsible submitter remains accountable for provenance and for having the right to submit any incorporated material.
