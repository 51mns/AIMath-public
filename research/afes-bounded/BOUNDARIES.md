# AFES-0.1 accepted boundaries

## Equality

AFES does not claim a total equality decider. Valid objects may compare as `TRUE`, `FALSE`, or `UNKNOWN`.

Reviewed exact equality mechanisms cover:

- rational expressions;
- structural identity;
- polynomial expressions in one fixed algebraic generator modulo its defining relation.

General independent-series equality, mixed analytic/algebraic identity, cross-generator algebraic canonicalisation and total semantic normalisation remain outside scope.

## Closure

`add`, `sub`, `mul` and `neg` preserve valid-number syntax for valid operands.

Division is partial and certificate-relative: a division expression is accepted as a valid AFES Number only when the denominator has a supported exact nonzero certificate. Current reviewed nonzero mechanisms cover rational expressions and suitable alternating-series interval separation; general algebraic denominator certification is not provided.

Thus a missing certificate for a denominator such as `sqrt(2)` means **unsupported**, not “the denominator is zero”.

## Encoding and certificate binding

The repaired private implementation enforces exact node/certificate key sets and binds certificates to canonical subject hashes. The repair review accepted the previously identified subject-binding and ignored-extra-field defects as closed.

However, a separate scalar canonicality issue remains: in Python, `bool` is a subclass of `int`, and one rational normalisation path can accept boolean payloads where strict JSON integer typing would reject them. Therefore the broad claim “every malformed scalar has one strict canonical encoding” remains only `PROOF_CANDIDATE`.

This scalar qualification does not invalidate the narrower accepted bounded semantic claim.

## Representation scope

The algebraic atom represents indexed roots of suitable squarefree integer polynomials. The analytic atom represents a restricted infinite family of certified alternating recurrence series. AFES does not claim to represent every transcendental number, provide total field operations, or supply cryptographic security.

Publication novelty is not established.
