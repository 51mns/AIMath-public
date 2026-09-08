# Formal proof-assistant evidence policy

Status: additive governance foundation. This policy does not make formalisation mandatory for ordinary Village research and does not alter Task readiness, ranking, locks, claim levels, or continuation decisions.

## Purpose

A proof assistant may provide a stronger machine-checkable evidence layer for important mathematical claims. It is an orthogonal evidence dimension, not a replacement for mathematical review, source fidelity, novelty work, reproduction, or external expert judgement.

The initial supported design target is Lean 4, but the policy is proof-assistant-neutral where practical.

## Core separation

Keep these questions separate:

1. **Mathematical claim:** what statement does AIMath intend to establish?
2. **Statement fidelity:** does the formal statement faithfully encode that intended statement?
3. **Kernel validity:** does the proof assistant kernel accept the encoded theorem from its declared dependencies and axioms?
4. **Independent review:** can a separate reviewer understand or rederive the load-bearing argument?
5. **Computation/certificate validity:** were any finite or external certificates checked under their own evidence rules?
6. **Novelty/frontier impact:** is the result new, and does it improve an external frontier?

A kernel PASS answers item 3 only. It must never silently answer the other items.

## When to formalise

Do not block fast E0/E1-style exploration on formalisation.

Formalisation is appropriate when at least one of the following holds:

- a Task explicitly targets formal proof;
- an important result will be used as a load-bearing premise;
- a promotion candidate would benefit materially from machine checking;
- a long or fragile proof has many reusable sublemmas;
- a statement-translation error would be especially costly;
- independent formal reproduction is itself the research objective.

The existence of a formal proof does not force Campaign continuation.

## Statement freeze and fidelity gate

Before treating a formal proof as evidence for an external mathematical statement:

- freeze the intended human-readable statement;
- freeze the proof-assistant statement separately;
- record the exact statement path and, where load-bearing, its SHA-256;
- audit that quantifiers, domains, side conditions, equality cases, conventions, and imported definitions match the intended claim;
- record `statement_fidelity = AUDITED` only after that comparison.

A proof assistant can perfectly prove the wrong formalisation. Statement fidelity therefore remains a distinct gate.

## Theorem-obligation DAG

Large proofs may be decomposed into theorem obligations rather than extending one Task indefinitely.

Each formal theorem node may be recorded as JSON under the relevant public claim package, for example:

`research/<claim-package>/formal/theorems/THM-...json`

and should validate against `schemas/formal-theorem.schema.json`.

The DAG is a proof-decomposition and navigation layer. It is not a second Task ownership system:

- Task/lock/collision rules remain authoritative for who may work;
- theorem nodes do not create READY work by themselves;
- an OPEN or BLOCKED leaf must not be hidden behind a parent labelled proved;
- decomposition must not move the original hard statement into an unproved helper and call the parent solved;
- theorem IDs are durable proof-obligation identifiers, not new Claim IDs.

## Statement/proof separation

Where practical, keep the frozen theorem statement separate from candidate proofs. A worker solving a formal Task should not be able to weaken the target statement merely to obtain a kernel PASS.

For high-value formal work, prefer a challenge-style boundary in which the target statement is frozen before proof search and candidate workers modify only proof-owned paths.

## Formal verification metadata on claims

`schemas/claim.schema.json` permits an optional `formal_verification` object.

Its `status` is deliberately orthogonal to `mathematical_level`:

- `NONE`
- `STATEMENT_FORMALIZED`
- `STATEMENT_AUDITED`
- `KERNEL_PASS`
- `DUAL_KERNEL_PASS`

No status here automatically promotes `mathematical_level`, establishes novelty, or substitutes for independent reproduction.

Existing Claim records remain valid without this field.

## Kernel-PASS evidence record

A public `KERNEL_PASS` record should preserve, where applicable:

- proof assistant and exact version;
- package/library commit or lockfile;
- frozen theorem statement path/hash;
- proof commit;
- exact build command and exit status;
- axioms or trust assumptions used;
- presence/absence of placeholders or escape hatches relevant to that system;
- generated artifacts or exports if load-bearing.

For Lean, a high-value proof should explicitly account for mechanisms such as `sorry`, added axioms, `unsafe`, `native_decide`, external implementations, or other trust-expanding features when they could affect the claimed evidence strength. These mechanisms are not globally forbidden: the evidence record must state what is trusted and why.

## Stronger checks

For especially important E2/E3-style claims, consider stronger checks proportionally to risk:

- a comparator/challenge that confirms the proved statement is the intended frozen target;
- replay from a clean environment;
- an independent proof implementation;
- a second proof-assistant kernel or independently implemented checker;
- human or cross-model review of statement fidelity and proof architecture.

These are escalation options, not universal requirements.

## Relationship to finite computation

Do not force large finite certificates into a proof assistant merely for appearance.

A hybrid proof may be stronger and cheaper:

`mathematical reduction -> exact external certificate/verifier -> small formally checked bridge`

provided the trust boundary is explicit.

Finite computation remains finite evidence unless the surrounding proof covers the universal quantifiers.

## Rollout rule

This foundation is intentionally non-disruptive:

- no existing Claim must be rewritten;
- no existing Task becomes blocked;
- no rank or READY rule changes;
- no Lean installation is added to mandatory CI in this phase;
- no theorem-DAG file is required unless a formalisation lane chooses to create one.

A later change may add schema validation or formal CI only after at least one real AIMath claim has been piloted and the cost, failure modes, and repository impact are understood.
