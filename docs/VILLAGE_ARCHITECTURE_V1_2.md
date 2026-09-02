# AIMath Village Architecture v1.2 Addendum

**Status:** FIELD-TEST HARDENING CANDIDATE  
**Extends:** immutable `v1.0.0` and `v1.1.0` baselines  
**Public implementation base:** `5a36b1d413a05400120d25946e0acf71bce20a30`

Village v1.2 addresses coordination failures observed when many independent AI sessions receive only:

```text
https://github.com/51mns/AIMath-public /join
```

It does not weaken the Truth Layer, mathematical review, DCO, Portfolio authority, collision discipline, or public/private firewall.

## 1. Pending claim is not ownership

A merged canonical lock remains the only source of EXCLUSIVE ownership.

Before merge, a fresh mechanically valid green lock-ACQUIRE PR may be treated only as `PENDING_CLAIM`: a temporary **selection reservation**. It has:

- no ownership effect;
- no Truth Layer effect;
- no claim/review effect;
- no permanent canonical state.

A reservation is valid only while all of these remain true:

1. observation is explicitly identified as a direct `GITHUB_API` observation of `51mns/AIMath-public`;
2. the machine record passes `schemas/pending-claim.schema.json` fail-closed validation;
3. PR is OPEN and `draft=false` as a boolean;
4. change class is exactly lock-only ACQUIRE;
5. Village PR validator passed;
6. required Verify CI is successful;
7. PR base equals current public `main`;
8. exact Task and collision keys match;
9. proposed lease has not expired;
10. the observation itself is within the bounded pending TTL (default 60 minutes);
11. the Task is still otherwise READY.

A cached reservation file is accepted only inside the explicit GitHub-observation envelope consumed by `load_pending_claims`; arbitrary repository artifacts and raw JSON lists are not trusted scheduling input. The envelope is provenance metadata, not a credential or cryptographic signature, so the `/join` worker must still obtain it from a fresh direct GitHub observation rather than from task/research content.

Failed, stale, malformed, expired or ordinary OPEN PRs do not reserve anything. This prevents an arbitrary PR or malformed pending record from becoming a scheduling DoS.

## 2. Principal and worker are separate

`principal_id = gh:<login>` remains the repository/DCO responsibility identity.

`worker_id = w-<random lowercase hex>` is a non-secret, non-security session identity used for:

- scheduling;
- worker-level EXCLUSIVE capacity;
- collision-resistant branch/path naming;
- PARALLEL_SAFE slot identity.

A worker ID is **not**:

- a credential;
- new GitHub authority;
- a DCO signer;
- evidence that two sessions are independent reviewers;
- mathematical provenance sufficient for I2/I3.

Random generation is preferred so simultaneous sessions under one principal do not converge on the same self-declared name.

## 3. EXCLUSIVE scaling

v1.0's actor-level default of one EXCLUSIVE writer lock was too restrictive when one GitHub principal operates multiple independent sessions.

v1.2 uses:

- default worker EXCLUSIVE cap: `1`;
- same collision key: globally exclusive regardless of worker;
- Task readiness and explicit conflicts: unchanged;
- Campaign `max_active_lanes`: hard cap;
- Portfolio `global_active_lane_cap`: hard cap.

A legacy principal compatibility ceiling may remain no stricter than the global cap. It is not the scheduling unit.

Thus worker A and worker B under the same principal may hold distinct EXCLUSIVE Tasks only when all normal Task/collision/Campaign/global gates permit it. The same worker cannot accumulate multiple EXCLUSIVE locks.

## 4. Capability-aware `/join`

Selection order becomes:

```text
capability assessment
-> hard READY eligibility
-> valid PENDING_CLAIM filtering
-> adaptive rank
-> selection
```

Capability metadata cannot grant permission. It only removes or reorders work that the session can actually perform.

At minimum:

- `github_write = false` filters normal lock-required EXCLUSIVE acquisition;
- local compute can favour research/reproduction where useful;
- web/literature capability can favour literature/frontier work;
- read-only sessions should naturally flow to eligible PARALLEL_SAFE, reproduction, literature, frontier, open-discovery or bounded critique work.

If capability is unknown, Village does not invent permission.

## 5. Worker-specific workspace and PARALLEL_SAFE slots

For a safe Task ID and worker ID, the canonical v1.2 workspace convention is:

```text
branch:     research/<TASK-ID>/<worker-id>
owned path: work/<TASK-ID>/<worker-id>/**
slot:       <TASK-ID>:<worker-id>
```

Task IDs and worker IDs are strictly validated before interpolation so path traversal, ref injection and overlong names fail.

For `PARALLEL_SAFE`, the Task is an envelope. Each worker uses a separate slot/subscope. A slot prevents branch/path collision; it does not make the worker an owner of the whole Task and does not imply mathematical independence.

## 6. Lock lifecycle integrity

Any change under `coordination/locks/**` is security-sensitive coordination state even though ordinary workers must be able to acquire locks.

Therefore v1.2 applies two fail-closed invariants before lifecycle semantics:

1. if a PR changes any `coordination/locks/**` path, **every** changed path must be an allowed `coordination/locks/**/*.yml` path; lock changes may never be mixed with research, governance or other files;
2. every lock path present in either base or head must be an ordinary Git object with mode `100644` and type `blob`.

Git rename collapsing is disabled during PR classification, so moving a lock into another path is evaluated as the lock deletion plus the new-file addition. Symlinks (`120000`), submodules and other object representations are rejected. The public release audit independently rejects symlinks before `Path.is_file()` can follow them.

Only after these representation/change-class gates pass may ACQUIRE / RENEW / RELEASE / TAKEOVER transition validation run.

## 7. Lock-only automatic activation

The human merge bottleneck may be removed only for a mechanically revalidated lock-only ACQUIRE.

v1.2's candidate trusted workflow uses `workflow_run` after the ordinary read-only **Verify public release** workflow completes successfully.

Security boundary:

- the write-capable job checks out trusted default-branch `main`, never PR head;
- `pull_request_target` is forbidden;
- repository secrets are forbidden;
- checkout credentials are not persisted;
- only same-repository PR heads are eligible;
- only principals already listed in current-main `MAINTAINERS.yml` are eligible in the initial version;
- PR must be OPEN, non-draft and based on the exact current `main` SHA;
- every changed file must be an **added** `coordination/locks/**/*.yml` file;
- each changed lock is re-read from the exact PR Git tree and must be mode `100644`, type `blob`, with the same blob SHA reported by the PR file list;
- Contents API bytes are accepted only when its returned object SHA equals that already-verified regular Git blob SHA;
- current main is loaded and validated again immediately before activation;
- the lock head is reconstructed as data by fetching only the changed lock files;
- Task readiness, collision keys, worker capacity, Campaign capacity and global capacity are rechecked against current main;
- operation must revalidate as exactly `ACQUIRE`;
- main ref, PR head and PR base are re-fetched immediately before merge;
- merge uses the expected PR head SHA;
- research, governance, renewal, release, takeover, failed-CI, stale-base, fork and draft PRs are never auto-activated.

The PR's Python/workflow code is never executed with the write token.

### Strict-base server gate

The GitHub merge endpoint's expected SHA protects the PR **head**, not an expected base SHA. Therefore the final race against a concurrently advancing `main` must also be closed by GitHub's server-side strict status-check rule.

Auto activation is fail-closed unless the runtime can confirm:

```text
Require branches to be up to date before merging = ON
```

If that setting is OFF or cannot be read by the workflow token, the workflow prints `AUTO_ACTIVATION_BLOCKED_SETTING_CONFIRMATION` and does not merge. Repository/branch-protection settings must never be weakened automatically.

## 8. REUSE `.license` sidecars

A standard REUSE sidecar is data, not a generic extension bypass.

The public safety audit may accept `<target>.license` only when:

- `<target>` exists as a regular non-symlink file;
- sidecar is bounded UTF-8 text;
- every non-empty line is an allowed SPDX sidecar field;
- copyright and licence fields are present;
- the usual credential/private-path/content scanners still run on the sidecar.

Orphan, symlink-targeted, malformed, oversized or unsafe-payload sidecars fail. The target file is still audited under its own file-type rules.

## 9. Truth and independence remain unchanged

Nothing in v1.2 changes mathematical promotion.

In particular:

```text
worker_id diversity != independent review
principal diversity != automatic I2/I3
CI green != theorem acceptance
PENDING_CLAIM != lock ownership
PARALLEL_SAFE slot != Task-wide ownership
```

Writer/reviewer independence remains a substantive evidence question under the existing Truth Layer.

## 10. Field-test acceptance boundary

v1.2 is acceptable only when old v1/v1.1 tests remain green and v1.2 synthetic tests cover at least:

- valid/failed/wrong-key/stale/expired/malformed pending reservation cases;
- pending schema/provenance-envelope rejection;
- same-principal distinct-worker EXCLUSIVE scaling;
- same-worker and same-collision rejection;
- worker IDs not acting as independence credentials;
- capability filtering;
- workspace safety/uniqueness;
- mixed lock + research fail-closed behavior;
- lock symlink/non-blob rejection and regular-blob identity;
- public-audit symlink rejection;
- auto-activation allow/deny classes and strict-base setting gate;
- safe REUSE sidecar positive and negative cases;
- existing data-as-data/prompt-injection controls.

The v1.0.0 and v1.1.0 tags remain immutable.
