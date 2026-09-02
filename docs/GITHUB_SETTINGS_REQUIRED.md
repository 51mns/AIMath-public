# Required GitHub repository settings for Village v1

In-repository policy cannot protect itself if repository settings allow an unreviewed workflow/governance change to merge. The following settings are part of the operational launch gate and must be configured on GitHub:

- protect `main`;
- require pull requests before merge;
- require the `verify` status check (the workflow display name is `Verify public release`, but the required check context is the job/check name `verify`);
- require the branch to be up to date before merge;
- block force pushes;
- block branch deletion;
- keep Actions token permissions read-only by default;
- require approval before workflows from forks or first-time/external contributors run, using the strictest setting available for the repository plan;
- do not allow GitHub Actions to create or approve pull requests unless a later audited lock-bot design explicitly requires and scopes that permission;
- keep secret scanning/push protection enabled when available;
- keep commit-email privacy enabled.

`CODEOWNERS` is committed, but its enforcement depends on GitHub branch/ruleset settings.

These settings are external repository configuration, not mathematical canonical state.

## Maintainer modes

GitHub pull-request approval is repository-governance review. It is **not** AIMath mathematical independence (`I2`/`I3`), which is recorded and enforced separately in the Truth Layer.

### Solo-maintainer mode

Use this mode while only one human maintainer can honestly approve protected-path changes.

- required approving reviews: **0**;
- keep pull requests mandatory;
- keep required status check `verify` mandatory;
- keep strict up-to-date-before-merge enabled;
- keep force pushes and branch deletion blocked;
- keep `CODEOWNERS` committed for ownership/documentation and future multi-maintainer use;
- do not create or use a second account controlled by the same person merely to manufacture an approval.

A zero GitHub-approval requirement does not waive independent mathematical review required for claim promotion.

### Bot-submitter / multi-maintainer mode

When a genuinely distinct human reviewer is available, or a dedicated bot/GitHub App submits work that it actually generated, the repository may require one or more approving reviews and Code Owner review.

For an AI/bot submitter:

- the bot must not be a CODEOWNER;
- the bot must not have approval authority;
- grant the minimum repository permissions needed for submission;
- do not grant secrets access to untrusted research code;
- prefer fork or otherwise isolated submission paths where practical;
- dismiss stale approvals when new commits materially change the reviewed PR;
- do not route a human maintainer's own authored change through a bot merely so that the same maintainer can appear to approve an independent contribution.

Switching modes is a governance/settings change and should reflect the real people and automation involved, not a desired appearance of independence.

## Lease/merge boundary

`main` must require branches to be up to date before merge. Renewal and trusted lifecycle CI evaluate current canonical state. The merge endpoint's expected head SHA does not pin the base SHA, so strict server-side status checking is part of lock correctness, not a performance option.

## Village v1.2.1 trusted lifecycle strict gate

The trusted write workflow uses `GITHUB_TOKEN` only for GitHub Actions/PR reads and the narrowly revalidated contents merge path. It does not change branch protection or Rulesets.

The original v1.2.1 implementation attempted to read classic branch protection at:

```text
GET /repos/51mns/AIMath-public/branches/main/protection/required_status_checks
```

and required the returned `strict` field to be exactly `true`. The live field test confirmed that the normal workflow token cannot read that Administration-scoped endpoint and therefore correctly failed closed with `AUTO_ACTIVATION_BLOCKED_SETTING_CONFIRMATION`.

The replacement attestation source is GitHub's effective branch-rules endpoint:

```text
GET /repos/51mns/AIMath-public/rules/branches/main
```

Automatic mutation may proceed only when the effective rules positively prove both:

```text
required_status_checks.parameters.strict_required_status_checks_policy = true
required_status_checks.parameters.required_status_checks[*].context = "verify"
```

The required context is the Actions job/check name `verify`; the workflow display name remains `Verify public release` and is still used when validating workflow-run provenance. OFF, missing, malformed, wrong-context or unreadable effective rule responses fail closed with `AUTO_ACTIVATION_BLOCKED_SETTING_CONFIRMATION`.

This effective-rules read needs only repository Metadata read access, which the built-in `GITHUB_TOKEN` already has. No PAT, GitHub App, repository secret or environment secret is required for strict-setting attestation.

At setup/read-back on 2026-09-02 the repository Ruleset was observed as:

```text
name: Village main strict lifecycle safety
ruleset id: 22089746
enforcement: active
target: ~DEFAULT_BRANCH
required context: verify
strict_required_status_checks_policy: true
bypass_actors: []
```

The production gate must **not** trust or hard-code Ruleset ID `22089746`. It trusts only the rules GitHub reports as effective for `main`, so replacement/layered Rulesets cannot silently inherit authority from this recorded setup identifier.

Classic branch protection remains in place during this transition. The Ruleset path is an additional positive attestation source and must not be used as a reason to weaken classic protection. Changes to bypass actors, required checks, strictness, force-push/deletion policy or protection mode remain human governance/security-setting changes.