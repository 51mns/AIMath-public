# Local TP2 statement freeze

Status: **REVIEWED / FROZEN AS A STATEMENT**.  
Claim level: `PROOF_CANDIDATE`.

The definitions and quantifier range below are independently reviewed and accepted as the canonical statement. The strict inequality itself is **not proved**.

## Canonical branch and child orientation

Let `v=t` be any valid vertex of the canonical Farey tree in `Q ∩ (0,1)`, including the root `1/2`. For its ordered Farey boundary neighbours `r<t<s` with `t=r⊕s`, put

```text
C_v = G_t
L_v = G_(r⊕t)
R_v = G_(t⊕s)
```

under the canonical deformed-squared Markov recurrence.

Let

```text
U_v = the unique lower-degree child among {L_v,R_v}
V_v = the unique higher-degree child among {L_v,R_v}.
```

The degree ordering is unique. Define

```text
S_v = U_v - C_v
D_v = V_v - U_v.
```

At the root, `C=G_(1/2)`, `U=G_(1/3)`, and `V=G_(2/3)`. No root exception is needed.

## Coefficient profile

For every polynomial `P(x)`, define `H(P)[n]` by the unique symmetric Laurent expansion

```text
P(q+q^(-1))
=
H(P)[0] + sum_(n>=1) H(P)[n](q^n+q^(-n)).
```

Indices start at `n=0`, with zero extension

```text
H(P)[n] = 0 for n > deg_x(P).
```

## Adjacent determinant

For every integer `n>=0`, define

```text
F_v(n)
=
H(D_v)[n+1] H(S_v)[n]
-
H(D_v)[n] H(S_v)[n+1].
```

## Frozen candidate theorem

Exactly the following strict inequality is the proof candidate:

```text
0 <= n <= deg_x(S_v)  =>  F_v(n) > 0.
```

The terminal index `n=deg_x(S_v)` is included. There,

```text
H(S_v)[deg_x(S_v)+1] = 0,
```

so the terminal claim is a division-free determinant assertion; it must not be replaced by a literal ratio comparison.

For `n>deg_x(S_v)`, zero extension gives `F_v(n)=0` definitionally.

## Orientation relative to the older raw left/right determinant

If `E_v` is the older raw left/right adjacent determinant, then

```text
root or last-L: F_v = E_v
last-R:         F_v = -E_v.
```

The short/long degree ordering already absorbs this sign normalization.

## Scope boundary

This freeze concerns adjacent minors only. It does not assert arbitrary all-column TP2, PF2/log-concavity equivalence, global single-crossing, closure of historical Candidate A/B, or publication novelty.

**Provenance:** statement writer `9507c4be2a859a284683d62672b14e35f5681549`; independent statement/source review `5380e3f898eb0a91d7f47b48a50368637af218e0`; canonical intake `c5e31090d29d57fc1ba4fa2c7670f5b527ce3c1e`.
