# Preregistration amendment: held-out contamination correction

This amendment is committed **before the representation specification is frozen and before the replacement held-out values are generated**.

## Why an amendment is necessary

During pre-commit scratch work, the worker had already derived/inspected several values of the originally proposed `D=2` Pell x-coordinate sequence and several Catalan values. Those data therefore do not satisfy a clean held-out interpretation for this session.

The original `PRE_REGISTRATION.md` is retained unchanged as an audit trail. Its `D=2` Pell and Catalan evaluation sets are retired and **will not be counted as held-out evidence**.

## Replacement cross-domain held-out

Use Pell solutions to

`x^2 - 7 y^2 = 1`

starting from `(x_0,y_0)=(1,0)` and repeatedly multiplying by the fundamental solution `8 + 3*sqrt(7)`:

- `x' = 8x + 21y`
- `y' = 3x + 8y`

Generate ten x-coordinates only after the representation specification has been committed. Expose indices 0..2 to both methods and reserve indices 3..9 for evaluation.

No replacement x-coordinate values have been generated or inspected before this amendment.

## Replacement adversarial transfer control

Use Bell numbers `B_0..B_9`, generated only after the representation freeze by the exact Bell-triangle recurrence:

- start row `[1]`;
- each new row starts with the previous row's final entry;
- each subsequent entry is the sum of the entry immediately to its left and the entry above-left in the previous row;
- `B_n` is the first entry of row n.

Expose indices 0..2 and reserve indices 3..9. Values generated before the representation freeze are not admissible evidence.

## Unchanged baseline and decision rule

The baseline, representation budget, metrics, and positive-utility decision rule in `PRE_REGISTRATION.md` remain unchanged. In particular, exact prediction without a strict gain over the frozen direct-recurrence baseline is still a negative outcome.

## Scope boundary

This correction improves held-out hygiene but does not make the experiment perfectly blinded: the worker knows the mathematical definitions of the replacement domains. The evaluation therefore tests unseen exact values and cross-domain transfer, not ignorance of the domain names themselves. Any positive result would need that limitation stated explicitly.
