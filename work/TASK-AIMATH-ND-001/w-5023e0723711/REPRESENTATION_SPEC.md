# Frozen representation specification

This specification was derived from the two exposed training sequences only. The replacement D=7 Pell and Bell held-out values in `PREREGISTRATION_AMENDMENT.md` had not been generated when this file was frozen.

## Invented primitive: transition seal

For two adjacent exposed integers `(x,y)`, define a **transition seal**

`S_(a,b,d)(x,y) = a*x^2 + b*x*y + d*y^2`

where `(a,b,d)` is a primitive integer coefficient triple with canonical first-nonzero-positive sign.

The bounded discovery rule enumerates `|a|,|b|,|d| <= 8` and retains a seal only when its exact integer value is constant on every adjacent transition in one training sequence.

This is an invented representation for this experiment; it is not claimed to be new mathematics.

## Training discovery

Exact exhaustive search gives one canonical primitive seal for each training sequence:

- A: `(1,-3,1)`, constant value `-5`;
- B: `(1,-5,1)`, constant value `-21`.

The shared representation grammar is therefore

`Q_c(x,y) = x^2 - c*x*y + y^2`.

The representation stores a sequence transition as its parameter `c`, its constant seal value `K`, and a direction bit selecting the non-backtracking continuation.

## Frozen continuation rule

If consecutive values are `x,y,z` and `Q_c(x,y)=Q_c(y,z)`, exact subtraction gives

`(z-x) * (z + x - c*y) = 0`.

For a non-backtracking transition (`z != x`), the next value must satisfy

`z = c*y - x`.

From the first three non-backtracking terms, seal equality determines

`c = (z^2 - x^2) / (y*(z-x)) = (z+x)/y`

when denominators are nonzero.

## Pre-held-out falsification of the utility hypothesis

The last formula is **algebraically identical** to the preregistered baseline parameter fit

`c = (u[2] + u[0]) / u[1]`,

and the frozen continuation is exactly the baseline recurrence.

Therefore, before looking at replacement held-out values, this representation already fails to establish a strict predictive gain over the baseline. The held-out run is still required to test transfer correctness and false-transfer behavior, but exact prediction by itself cannot rescue the representation as a positive AIMath-ND result.

## Proof-obligation comparison frozen before held-out

- Baseline: one recurrence identity `z = c*y - x` once `c` is fixed.
- Seal representation: seal preservation plus exclusion of the backtracking root are required to recover the same recurrence.

Thus the representation does not pre-register a proof-obligation compression advantage. A positive result would have to arise from a different metric (for example, superior falsification on the adversarial control), not from relabeling the recurrence.
