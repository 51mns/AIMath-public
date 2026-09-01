# Lonely Runner set-cover pruning — two-pivot residual capacity

**Claim ID:** `C-LRC-R2-RESIDUAL-CAPACITY`  
**Canonical level:** `INDEPENDENTLY_REPRODUCED`

This is a generic safe set-cover pruning theorem that arose from the LRC(13) translate-cover search. It does not solve `LRC(13)`.

For an uncovered set `U`, distinct available sets, remaining budget `r>=2`, and a fixed first pivot `x`, the two-pivot bound `R2` conditions on a first set `A`, then on a worst residual pivot `y`, then on an optimistic second set `B`, followed by the top `r-2` exact residual marginals. If a second-pivot branch has no eligible distinct `B`, that first-set branch is impossible and is excluded (equivalently assigned `-infinity`).

Every valid completion obeys

```text
|U| <= R2,
```

so `R2<|U|` is a safe prune. Also `R2<=R1` for the corresponding one-step top-marginal bound.

## Important outcome boundary

The theorem has strict examples, including an independently reproduced `p=71` LRC branch where author baseline keeps, `R1` keeps, and `R2` prunes. However later bounded benchmarking concluded `NO_GO_FOR_SCALING`: the literal R2 evaluation did not justify escalation to a large LRC search. Mathematical validity and performance are separate.

Writer `39a9efc6b2273da00d0a5da0aa166d3c03fdc227`; independent final review `092f9110a50c775040f5d3482f0a8e1b2c6bc580`.
