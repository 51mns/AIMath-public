# Two-pivot residual-capacity theorem

Let `U` be a finite uncovered set, `C` a finite family of distinct available sets, `r>=2` the number of remaining set slots, and `x in U` a fixed first pivot.

For each eligible `A in C` with `x in A`, set `U_A=U\A`. If `U_A` is empty, put `Q_A=0`. Otherwise, for a second pivot `y in U_A` and each distinct `B in C\{A}` with `y in B`, let

```text
U_(A,B) = U\(A union B),
```

and let `S_(r-2)(A,B)` be the sum of the largest `r-2` distinct values

```text
|D intersect U_(A,B)|,  D in C\{A,B},
```

padding with zeros if needed. Define

```text
Q_A = min_(y in U_A) max_(B != A, y in B)
      ( |B intersect U_A| + S_(r-2)(A,B) ).
```

If for a chosen `y` no distinct eligible `B` exists, that `A` branch cannot occur in a valid completion and is excluded from the outer maximum (equivalently its value is `-infinity`). Finally

```text
R2(U,r,x) = max_(A in C, x in A) ( |A intersect U| + Q_A ).
```

## Theorem

If `U` is coverable by at most `r` distinct available sets, then

\[
\boxed{|U|\le R_2(U,r,x)}.
\]

Therefore `R2(U,r,x)<|U|` is a safe pruning certificate.

## Proof

Take any valid completion using at most `r` distinct sets, and choose from it a first set `A` that covers `x`.

If `U_A` is empty, this branch already covers all of `U`. Otherwise choose any second pivot `y` used in the minimum defining `Q_A`. Since the completion covers all residual points, some other completion set `B` covers `y`.

After `A` and `B`, at most `r-2` distinct completion sets remain. On the exact residual `U_(A,B)`, the size of their union is at most the sum of their individual residual marginals. That sum is at most `S_(r-2)(A,B)`, which takes the largest available distinct marginals. Hence the completion covers at most

```text
|A intersect U| + |B intersect U_A| + S_(r-2)(A,B)
```

points of `U`.

The maximum over eligible `B` bounds the actual second completion set, the minimum over second pivots remains valid because the completion covers every residual pivot, and the outer maximum bounds the actual first completion set. Thus `|U|<=R2`.

## Dominance over R1

For any fixed `A,B`, every later residual marginal satisfies

```text
|D intersect U_(A,B)| <= |D intersect U_A|.
```

The set `B` plus the remaining `r-2` sets provide `r-1` distinct candidates after `A`, so their optimistic capacity is at most the one-step top-`r-1` marginal sum. Taking max/min/max preserves this inequality:

\[
\boxed{R_2\le R_1}.
\]

## Bounded strict certificate

The independent LRC replay records a reachable `p=71` state with

```text
U={10,13,15,19,29,30},  r=3,  pivot x=10,
author baseline upper=7, R1=6, R2=5.
```

Thus the branch is kept by the published baseline and by R1 but pruned by R2. This is finite supporting evidence only; it is not the generic proof and did not translate into a successful scaling benchmark.
