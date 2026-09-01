# Publishing the history-clean repository

## Recommended repository name

`AIMath-public`

Keep the private canonical workspace private. Do not change its visibility and
do not reuse its Git history.

## GitHub setup

Create a **new empty public repository**.

Important:

- do not import the private repository;
- do not use a GitHub "mirror" or migration operation;
- start with no README, licence, or generated files if you plan to upload this
  bootstrap tree directly;
- enable GitHub's commit-email privacy option before the first public commit.

## Before the first commit

From the extracted public directory:

```bash
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
python3 research/fixed-433/reproduce.py
```

All three commands must pass.

Then initialise **new** history:

```bash
git init
git add .
git commit -m "Initial AIMath public release"
git branch -M main
```

Add the new public repository as `origin` and push `main`.

## Recommended GitHub settings

- Issues: on
- Pull requests: on
- Discussions: optional; useful after there are external users
- Wiki: off initially; keep canonical explanations versioned in the repository
- Default branch: `main`
- Require pull request before merging: recommended after the first release
- Require CI checks: recommended once public CI is added
- Secret scanning / push protection: enable when available

## First public announcement checklist

Do not announce the repository until:

- public safety audit passes;
- fixed-433 replay passes;
- an explicit licence decision has been made;
- the landing README clearly says that `INDEPENDENTLY_REPRODUCED` is not the
  same as publication novelty;
- at least one issue template works;
- the repository contains no inherited private Git history.

## After launch

Export additional accepted claims one at a time. Each export should receive a
fresh privacy/provenance pass and a self-contained replay where computation is
part of the evidence.
