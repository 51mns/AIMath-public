# Required GitHub repository settings for Village v1

In-repository policy cannot protect itself if repository settings allow an unreviewed workflow/governance change to merge. The following settings are part of the operational launch gate and must be configured on GitHub:

- protect `main`;
- require pull requests before merge;
- require the `Verify public release` status check;
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
- keep required status check `Verify public release` mandatory;
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

## Village v1.2.1 Phase A trusted RELEASE gate

The Phase A write workflow uses `GITHUB_TOKEN` only for GitHub Actions/PR reads and the narrowly revalidated contents merge path. It does not change branch protection.

Before any automatic RELEASE or existing automatic ACQUIRE merge, trusted-main code calls:

```text
GET /repos/51mns/AIMath-public/branches/main/protection/required_status_checks
```

and requires the returned `strict` field to be exactly `true`. OFF, malformed or unreadable responses fail closed with `AUTO_ACTIVATION_BLOCKED_SETTING_CONFIRMATION`.

Reading this branch-protection endpoint requires repository **Administration: read** permission under GitHub's fine-grained permission model. Normal workflow `GITHUB_TOKEN` permissions do not expose an `administration` scope. If the runtime token cannot read the endpoint, do not weaken protection and do not add a PAT/App/secret automatically. A human must explicitly approve a minimal read-only Administration credential or another audited GitHub-supported way to attest the same effective strict setting before live auto-merge can be enabled. Existing `GITHUB_TOKEN` remains the merge credential; the setting-reader credential should not receive write Administration permission.
