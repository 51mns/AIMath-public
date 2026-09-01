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

`main` must require branches to be up to date before merge. Renewal CI evaluates the current canonical lock: if the lease has expired by re-evaluation time, renewal is invalid and takeover is the permitted path. This requirement is part of the v1 lock correctness model, not an optional performance setting.
