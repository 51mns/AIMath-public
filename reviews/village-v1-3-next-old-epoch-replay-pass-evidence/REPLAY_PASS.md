# Village v1.3 old-source-epoch replay live PASS evidence

Base/current production main at evidence freeze:
`dd13fd15496bab9325e2520e3d1bfad3390eba2d`

Preserved canonical M4 acquisition consumed source epoch:
`c861bf0aef4d98c52f0792e5761ece27d0524264`

Historical source epoch:
`730fe029ad2479bcb83f2d5ce9744f6f18578c783c2c8fa84f0d491e4d691065`

Production replay result after accepted R2 remediation:

```text
FAIL: OLD_ACQUISITION_REPLAY: source epoch already consumed by canonical v1.3 ACQUIRE c861bf0aef4d98c52f0792e5761ece27d0524264
EXIT_CODE=2
```

Post-run fresh-read evidence:

- current `main` remained `dd13fd15496bab9325e2520e3d1bfad3390eba2d`;
- canonical Dittert lock remained unchanged at `coordination/locks/dittert-n5/broader-zero-pattern.yml`, blob `042775d7a876b807dda6ed3e67102336ff5e5f8a`;
- no new pull request was created after PR #54;
- no new unintended `next-acquire/**` ref was created;
- the only remaining `next-acquire/**` ref was the previously canonical Dittert acquisition ref;
- unintended replay PR #52 remained CLOSED / UNMERGED and its replay ref had already been deleted;
- therefore the replay negative control was fail-closed and produced zero GitHub authority writes.

This evidence is frozen before final idempotency and truth-neutral cleanup.
