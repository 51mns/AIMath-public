# Public export policy

The public repository is built from a private canonical workspace, but it is **not a Git mirror**.

Current source snapshot SHA:

```text
c8e61e0e398f540bc8c5de79663398d689f37473
```

## Never export automatically

- `.git/` history from the private workspace;
- `archive/chatgpt/**`;
- raw ChatGPT exports or rendered private conversations;
- raw email or private correspondence;
- personal identifiers or personal email addresses;
- credentials, API keys, cookies, tokens, SSH/private keys;
- private attachments or opaque binary archives;
- internal coordination logs whose only purpose is private workflow;
- reconstructed private artifacts presented as original bytes.

## Export only after claim-level review

- mathematical proof notes;
- exact scripts and tests;
- certificate JSON/CSV;
- literature maps;
- independent reviews;
- provenance and hashes.

## History rule

The public repository must start with **new Git history**. Do not push, filter, or rewrite the private repository into the public repository unless a separate full-history privacy audit has passed.

## Provenance rule

A public file may record the private canonical source commit SHA and content hashes. It does not need to expose private branch topology, private conversation URLs, or private correspondence.

## Claim rule

Only the current canonical claim level may be exported as status. Unmerged writer branches remain non-canonical even when they contain promising results.
