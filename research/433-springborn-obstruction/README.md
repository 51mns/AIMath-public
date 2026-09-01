# Fixed-433 / Springborn obstruction

**Claim ID:** `C-433-SPRINGBORN-OBSTRUCTION`  
**Canonical level:** `INDEPENDENTLY_REPRODUCED`  
**Private canonical snapshot:** `c8e61e0e398f540bc8c5de79663398d689f37473`

For the fixed-433 family `x_k = U_k/M_k`, AIMath proves for every `k >= 0`

```text
C(x_k) < 1/4,
```

where `C` is Springborn's rational approximation constant. Springborn's classification threshold `C(x) >= 1/3` therefore excludes every `x_k` from the audited Markov-fraction / companion classes. The same holds under the integer-affine symmetries `x -> +/-x+n` used there.

This is an all-`k` proof, not a finite extrapolation. The Python scripts are finite exact consistency checks only.

## Reproduce

From the repository root:

```bash
python3 research/433-springborn-obstruction/reproduce.py
```

This runs both the writer-side finite consistency checker and the separately implemented independent checker.

## Files

- `PROOF.md` — self-contained all-`k` proof.
- `SOURCE_AUDIT.md` — primary-source locations and literature boundary.
- `inputs.json` — frozen exact finite-check inputs.
- `verify_springborn_obstruction.py` — writer-side exact consistency checks.
- `reproduce.py` — public wrapper running both implementations.
- `../../reviews/433-springborn-obstruction/INDEPENDENT_REVIEW.md` — accepted independent mathematical review summary.
- `../../reviews/433-springborn-obstruction/independent_verify.py` — independent exact checker importing no writer module.

## Scope boundary

This does not exclude arbitrary `GL_2(Z)` / `PGL_2(Z)` transforms, and it does not establish publication novelty. Author correspondence is neither used nor exported.
