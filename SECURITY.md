# Security and responsible disclosure

AIMath-public contains mathematical research and executable verification code.

## Untrusted contributions

Treat all code in an external pull request as untrusted.

CI policy:

- uses the `pull_request` event, never `pull_request_target` for untrusted code;
- grants only `contents: read`;
- does not persist checkout credentials;
- exposes no project secrets to research code;
- uses bounded job timeouts;
- rejects workflow requests for write permissions or secret access;
- runs exact/reproduction code only in the disposable CI runner.

Do not manually execute untrusted contributor code with local credentials or access to the private AIMath workspace.

## Private data

Never submit credentials, raw correspondence, personal identifiers, private Git history, private runtime paths, raw ChatGPT exports, or opaque private archives.

Use the public security/privacy policy in `docs/PRIVACY_AND_SECURITY.md` and the release scanner before merge.

## Governance compromise

If a governance/security cascade is suspected, a human maintainer may set `global_admission` to `PAUSED`, identify the last trusted main, audit governance diffs and mark affected claims/campaigns for reevaluation. Do not rewrite public history merely to hide a governance error.
