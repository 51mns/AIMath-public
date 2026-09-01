# Privacy and security

AIMath Public intentionally excludes private research-history material.

## Do not submit

- passwords, API keys, access tokens or cookies;
- personal email addresses, phone numbers or home addresses;
- private chat exports;
- private correspondence without permission;
- proprietary or confidential datasets;
- files whose provenance/licence is unclear.

## If sensitive information is accidentally committed

Do not merely delete the file in a later commit. Treat it as a history incident: rotate exposed credentials if applicable, remove the material from history, and verify all refs before release.

## Automated checks

`scripts/public_release_audit.py` blocks a conservative set of high-risk patterns and forbidden paths. It is a guardrail, not a substitute for human review.
