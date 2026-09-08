<!--
SPDX-FileCopyrightText: 2026 AIMath contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# TASK-FIXED-433-001 outcome

- Worker: `w-5b0eefedca755036`
- Exact base: `279ba9fa98befe3aee37bfd1a98e4f688d333bd4`
- Status: `WAITING_REVIEW`
- Verdict: `SOURCE_BACKED_PARTIAL_EXACT_MATCH`
- Novelty: `NOT_ESTABLISHED`
- Claim promotion/demotion: `NONE`

## Coordinator summary

Button 2001 p.85 and p.87 give an exact all-`k` placement for the fixed-ray complementary representatives. With Button's normalised Hermite representative `x`,

\[
(x-M_k)/2=r_k,
\]

and for the representative obtained by swapping the Markoff-triple entries,

\[
(x'-M_k)/2=p_k.
\]

Button's explicit `x+x'=4M_k` is therefore exactly the complement identity `r_k+p_k=M_k` in these coordinates.

The distinct AIMath factor-5 step

\[
U_k=r_k-M_k/5
\]

was not located explicitly in the bounded Button source audit. This remaining non-detection is not a novelty result.

Review `LITERATURE_AUDIT.md` for the algebraic derivation and source boundary, and run `button_fixed433_exact_overlap.py` for finite exact regression fingerprints.
