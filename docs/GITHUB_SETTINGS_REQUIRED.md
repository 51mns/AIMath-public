# Required GitHub repository settings for Village v1

In-repository policy cannot protect itself if repository settings allow an unreviewed workflow/governance change to merge. The following settings are part of the operational launch gate and must be configured on GitHub:

- protect `main`;
- require pull requests before merge;
- require the `Verify public release` status check;
- require the branch to be up to date before merge;
- block force pushes;
- block branch deletion;
- require Code Owner review for protected Village paths where the plan supports it;
- keep Actions token permissions read-only by default;
- require approval before workflows from forks or first-time/external contributors run, using the strictest setting available for the repository plan;
- do not allow GitHub Actions to create or approve pull requests unless a later audited lock-bot design explicitly requires and scopes that permission;
- keep secret scanning/push protection enabled when available;
- keep commit-email privacy enabled.

`CODEOWNERS` is committed, but its enforcement depends on GitHub branch/ruleset settings.

These settings are external repository configuration, not mathematical canonical state.

## Lease/merge boundary

`main` must require branches to be up to date before merge. Renewal CI evaluates the current canonical lock: if the lease has expired by re-evaluation time, renewal is invalid and takeover is the permitted path. This requirement is part of the v1 lock correctness model, not an optional performance setting.
