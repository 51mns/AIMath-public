# Security policy

For public issues, do not post secrets or private personal information.

If a credential is exposed, rotate it first. If personal/private data is committed, treat Git history as affected even after a later deletion.

The public export gate is:

```bash
python3 scripts/public_release_audit.py .
```

This repository intentionally contains no private canonical Git history.
