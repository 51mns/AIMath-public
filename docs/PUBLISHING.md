# Publishing and release hardening

`AIMath-public` is the history-clean public distribution. Keep the private canonical workspace private; do not mirror or import its Git history.

## Current release gate

Before announcing or tagging a reusable public release, all of the following must hold:

```bash
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
python3 scripts/build_public_manifest.py . --output /tmp/AIMath-public-manifest.json
python3 scripts/reproduce_public_claims.py .
```

The GitHub Actions workflow on `main` and pull requests should run the same safety/layout/full-replay gate. Pure mathematical proof steps are not replaced by finite computation; executable checks reproduce only the computational evidence in each package.

## Privacy and provenance gate

Before every public merge or tagged release:

- inspect the complete pull-request diff;
- confirm commit metadata uses a GitHub noreply identity rather than a personal email address;
- do not export private Git history or private branch topology;
- do not export raw ChatGPT conversations/exports, raw email/DM correspondence, personal identifiers, credentials, cookies, API keys, private attachments, opaque archives, or runtime file paths;
- export useful mathematics as a clean public claim package from fixed accepted evidence;
- keep unaccepted writer branches and exploratory artifacts out of the accepted public result index;
- keep proof, finite computation, independent reproduction, novelty and external-frontier movement separate.

## Recommended GitHub settings

- Issues: on
- Pull requests: on
- Wiki: off unless deliberately used; canonical research explanations should stay versioned in the repository
- Discussions: optional after there are external users
- Default branch: `main`
- Require pull requests before merging into `main`
- Require the `Verify public release` status check before merging
- Block force-pushes and branch deletion on `main`
- Secret scanning / push protection: enable when available
- Keep commit-email privacy enabled

These repository-level controls complement the in-repository audit scripts; neither one replaces the other.

## Licence gate

Do not describe the repository as broadly reusable until the owner has explicitly chosen and added licence terms. The current recommendation is documented in [`../LICENSING.md`](../LICENSING.md):

- code: Apache License 2.0;
- original project-authored mathematical prose, diagrams and documentation: CC BY 4.0;
- third-party material: original terms/citation, or exclusion when redistribution rights are unclear.

Licence selection is an owner/legal decision and is not inferred from mathematical acceptance or public visibility.

## Tag/release checklist

For a release such as `v0.1.0`:

1. freeze the exact `main` commit SHA;
2. ensure the privacy, layout, live-manifest and full public replay commands above all pass on that exact checkout;
3. verify the GitHub Actions run for the exact release commit succeeds;
4. generate and preserve a SHA-256 manifest from the exact release checkout;
5. confirm `docs/RESULTS.md`, `docs/FAILED_ROUTES.md`, `docs/EXPORT_GAPS.md`, `docs/CONTRIBUTION_TARGETS.md` and `docs/EVIDENCE_POLICY.md` match the released state;
6. confirm the licence decision has been committed;
7. only then create the immutable tag/release.

## After launch

Export additional accepted private-canon claims one package at a time. Every export should receive a fresh privacy/provenance audit, exact scope boundary, failed-route update when relevant, and a self-contained replay when computation is part of the evidence.
