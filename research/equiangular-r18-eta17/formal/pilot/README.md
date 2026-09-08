# R18 eta17 formal-proof pilot

This is the first AIMath public pilot of the formal-proof evidence policy on an already `INDEPENDENTLY_REPRODUCED` Claim.

It intentionally formalises only the **final exact deck-mismatch bridge**. It does not change the Claim's mathematical level and it does not claim that the full Seidel-matrix theorem is formalised.

## Formalised statement

The accepted exact Python verifier reconstructs two integer polynomials at the final characteristic-polynomial deck gate:

- `p'/F`, with descending coefficients `[59, -2242, 31388, -190974, 422985]`;
- `59 Q0`, with descending coefficients `[59, -2242, 31388, -191278, 426393]`.

`R18Eta17FormalPilot/Statement.lean` freezes these as integer-valued expressions and freezes the proposition that they are not identical as functions on `Int`.

Statement SHA-256:

```text
9241e1e958bcc05207e72b8d0acd7ed1ca1484ba69c4231062095708147c24e9
```

`R18Eta17FormalPilot/Proof.lean` proves the frozen proposition by observing that the two expressions already disagree at `x = 0`.

`R18Eta17FormalPilot/FinalCheck.lean` uses `#guard_msgs` around `#print axioms`, so the build fails if the recorded zero-axiom result changes.

## Verified environment

The exact Lean source in this directory was checked at pilot commit:

```text
a8b3044543b54ff42be15c29754890cba8a85394
```

GitHub Actions run `34196114477` passed with:

- Lean `4.33.1` (`819816b2e0a3bf405af45ae5c7af2491d8f5bee6`);
- Lake `5.0.0-src+819816b`;
- Lean core only, no Mathlib dependency;
- `lake build`: PASS;
- `#guard_msgs` / `#print axioms`: theorem depends on no axioms;
- bundled `leanchecker`: PASS;
- `axiom-audit` v0.1.2 (`46024e005996495c65ef609368e11ab39c4222e3`): PASS, 5 declarations audited.

The exact evidence metadata is in `theorems/THM-EQUIANGULAR-R18-ETA17-DECK-MISMATCH.json`.

## Secondary-kernel qualification

A nanoda check was attempted separately. `leanprover/lean-action` v1 currently clones the `debug` branch of `ammkrn/nanoda_lib`, whose package version is `0.3.2`. The Lean 4.33.1 environment exported successfully, but that nanoda build terminated with:

```text
invalid digit found in string
```

Therefore AIMath records `secondary_kernel = NOT_RUN` / tool incompatibility, **not** a proof failure and not a dual-kernel PASS.

## Explicit trust boundary

Lean does **not** yet prove:

- completeness of the 64 endpoint candidates;
- the type-2 divisibility filter;
- uniqueness of `Q0`;
- derivation of the quotient coefficients from `p'/F`;
- the Seidel spectral/deletion lemmas that make polynomial identity necessary;
- the full Claim that no `59 x 59` Seidel matrix has the frozen spectrum.

Those remain supported by the existing exact Python verifier and independent mathematical review. This package is therefore a kernel-checked **subtheorem**, not `KERNEL_PASS` for the whole Claim.

## Reproduce the kernel build

From the repository root:

```bash
cd research/equiangular-r18-eta17/formal/pilot
lake build
```

The pinned `lean-toolchain` selects Lean 4.33.1. The `lake-manifest.json` has no external package dependencies.
