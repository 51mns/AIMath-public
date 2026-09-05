# Local TP2 independent strategy critique

Date: 2026-09-05

Reviewer worker: `w-ff42c70dd81f71e6`

Base public main: `79d2da6afb3dd0af7c7b7cd8d343d683bbfb4929`

Campaign: `CAM-LOCAL-TP2`

Source outcome: `TASK-LOCAL-TP2-REFRESH-001` (`STRUCTURAL_REDUCTION`)

Candidate successor: `TASK-LOCAL-TP2-CONTINUANT-LGV-001`

## Scope and independence

This is the independent **strategy critique** required by `docs/CONTINUATION_GATE.md` before a human `HOLD -> ACTIVE` decision. It is not a mathematical proof review and it does not change Campaign state, Task state, claim level, novelty, or truth.

The critique was performed in a separate session from the refresh workers and re-read the public canonical statement, failed-route ledger, campaign/task state, and primary literature. It did not treat the refresh workers' optimism or Portfolio evaluation as evidence that the route works.

Independence limitation: the reviewer is another AI session and should not be treated as statistically independent mathematical verification merely because the session/worker differs. This artifact is a strategy recommendation, not an independent proof of Local TP2 or of the proposed continuant/LGV invariant.

## Recommendation

**RECOMMEND BOUNDED REOPEN: yes, but only for `TASK-LOCAL-TP2-CONTINUANT-LGV-001`.**

I recommend that the human Portfolio authority may change `CAM-LOCAL-TP2` from `HOLD` to `ACTIVE` with `max_active_lanes = 1` solely to execute the already-approved bounded continuant/LGV gate. I do **not** recommend a broad Local TP2 campaign restart.

After that Task reaches a terminal Outcome, continuation should be reconsidered from that fixed artifact. A failure of the common-network representation is not evidence that the frozen Local TP2 theorem is false; absent a new named mechanism, the default should be to return/remain on `HOLD` rather than immediately opening a replacement route.

Confidence in this strategy recommendation: **MEDIUM**.

The reason to spend one lane is information gain, not high estimated proof probability.

## Why this route clears the reopen bar

### 1. It is materially different from the closed Local TP2 routes

The existing ledger blocks QW3 individual-sign propagation, quotient restatements, far-minor bounded ansatz families, and higher finite-depth/degree variants. The continuant route changes the proof object: it uses the Farey-recursive continued-fraction representation of the deformed squared Markov polynomials and asks for a subtraction-free common path model for the two canonical differences `S_v = U_v - C_v` and `D_v = V_v - U_v`.

That is a theorem-native all-depth mechanism rather than a larger scan or a higher-degree version of a failed ansatz, so it satisfies the campaign's stated reopen condition in substance.

### 2. The external theorem matches the recursive object, not merely the surrounding topic

Bittmann--Jouteur--Kantarcı Oğuz--Molander--Yıldırım, *A Mirror deformation of Markov Numbers*, arXiv:2602.14802, proves positivity of the Laurent-polynomial entries on the deformed squared Markov tree and explicitly imports a Farey-recursive continued fraction `F_t^+(q)` whose numerator is the deformed squared Markov polynomial `M_t(q)` (Definition 3.1 / the cited GMS result; see https://arxiv.org/html/2602.14802v1#S3.SS1).

This is unusually well aligned with the frozen Local TP2 objects: the source gives a recursive combinatorial representation at every Farey parameter, rather than only a finite family or an asymptotic statement.

### 3. The proposed endgame is exact if its missing invariant exists

If the four adjacent `H` coefficients can be realized as a compatible planar path matrix, the Lindström--Gessel--Viennot determinant mechanism is a natural exact way to turn a nonintersecting two-path family into the frozen determinant

`F_v(n) = H(D_v)[n+1] H(S_v)[n] - H(D_v)[n] H(S_v)[n+1]`.

This is better targeted than proving a stronger global TP2 property: the Task asks only for the adjacent minor actually needed by the frozen theorem.

### 4. The Task has a real kill condition

The proposed Task can terminate negatively if a generic Farey splice forces unavoidable signed cancellation or if a canonical vertex refutes the proposed common-network invariant. That makes one lane scientifically useful even if the route fails: it can close a genuinely new architecture instead of producing another inconclusive finite scan.

## Main objections / failure risks

### A. Individual continuant positivity does not imply positivity of the differences

This is the largest risk.

The source theorem proves that each `M_t(q)` has positive coefficients and realizes it as a continued-fraction numerator. Local TP2, however, is about

- `S_v = U_v - C_v`,
- `D_v = V_v - U_v`, and
- a cross-family adjacent determinant of their `H` coefficients.

None of those statements follows from coefficient positivity of `C_v`, `U_v`, and `V_v` separately. Subtracting two positive continuants can introduce cancellations. Therefore the first genuinely new theorem obligation is not “build a planar network”; it is to obtain exact **simultaneous subtraction-free identities for both differences**.

The source mutation formula itself can be written with negative terms, so positivity of the tree entries should not be mistaken for a monotone-difference theorem.

### B. A common compatible network is much stronger than two separate path models

Even if `S_v` and `D_v` each receive subtraction-free continuant/path formulas, Local TP2 still needs them placed in one compatible planar geometry with the correct source/sink ordering. Two unrelated nonnegative network representations do not imply the desired determinant sign.

This is the central architectural bottleneck and should remain explicit. The Task should be judged PARTIAL, not successful, if it obtains separate positive formulas but cannot prove common-network compatibility.

### C. Strict positivity is stronger than LGV nonnegativity

LGV would naturally give `F_v(n) >= 0` from nonnegative weights. The frozen theorem requires `F_v(n) > 0` for every required index, including the terminal index.

So the proof must identify at least one positive nonintersecting path pair for **every** `n` in the frozen range. Boundary/support effects can make determinants vanish even when all individual coefficients are positive. This must be a separate final gate, not assumed from the network construction.

### D. The generic interior splice may not automatically cover every frozen convention

The canonical theorem uses degree-oriented children `U_v` and `V_v`, explicit zero extension, indices starting at zero, and the strict terminal determinant. The continued-fraction recursion has interior and boundary cases (`r=0` or `s=1`) and reverses/concatenates words.

A generic word identity therefore needs an explicit check that:

1. it respects the degree-based `U_v/V_v` orientation;
2. the boundary Farey cases are covered or separately proved;
3. coefficient/exponent lifting agrees exactly with the canonical `H` indexing; and
4. determinant row/column orientation produces `+F_v(n)`, not its negative.

These are inexpensive checks compared with inventing the invariant, but they are load-bearing.

### E. Failure of this representation would be a route failure, not a theorem failure

The “one common subtraction-free planar network” is a proof architecture stronger than Local TP2 itself. A decisive obstruction to that representation should be recorded as a failed route with its exact scope. It must not be promoted into a counterexample or into evidence that the universal determinant inequality is false unless an actual canonical negative `F_v(n)` is produced.

## Recommended execution order

The current Task scope is good, but the work should be staged to avoid spending effort on network engineering before the algebraic bottleneck is passed.

### Gate 0 — exact object map

Freeze the dictionary between the public `G_t/C_v/U_v/V_v` objects and the `M_t(q)` continued-fraction numerators used in the primary source. Verify the degree-oriented child convention and one or more canonical exact fixtures. This is a mapping check, not evidence for the theorem.

### Gate 1 — generic subtraction-free splice identities

Work in continuant / 2x2 transfer-matrix language first. For a generic interior Farey triple, derive exact identities for both

`U_v - C_v` and `V_v - U_v`

as nonnegative combinations/continuants/path sums that expose a shared combinatorial overlap.

**Early kill condition:** if generic exact identities necessarily retain sign cancellation that cannot be reorganized into nonnegative weights, stop the route here and record the obstruction. Do not compensate by increasing finite depth.

### Gate 2 — common-network compatibility

Only after Gate 1 passes, construct one planar network (or one controlled pair with a proven common embedding) whose relevant path matrix contains the four adjacent `H` entries in the frozen determinant orientation.

If only separate networks are available, record PARTIAL rather than silently weakening the success criterion.

### Gate 3 — strictness and terminal index

Give a uniform argument producing at least one positive nonintersecting two-path family for every `0 <= n <= deg_x(S_v)`, explicitly including the terminal index and boundary Farey cases.

### Gate 4 — theorem packaging / review

If Gates 0--3 pass, freeze the exact theorem statement and proof artifact before any claim promotion. Because this would be a major all-depth result, send the fixed artifact to independent mathematical review/reproduction. The present strategy critique cannot serve as that proof review.

## Alternatives considered

### More finite computation

Reject as a continuation strategy. The public finite baseline already records no counterexample through denominator 120, and the Campaign explicitly says larger denominator/depth alone is not a reopen reason. Finite computation remains useful only as a falsifier/debugger for a proposed identity.

### Return to QW3 / quotient / far-minor families

Reject absent a named new theorem-level ingredient. Those route families already have canonical blocked/no-go records.

### Broad literature search before trying the splice

Low priority. A fresh check confirms that the 2026 mirror-deformation paper supplies the exact Farey continued-fraction representation and individual coefficient positivity, while the 2025 Banaian--Gyoda work supplies weighted fence-poset/matrix/skein-like structure (https://arxiv.org/abs/2507.06900). Neither source, as currently stated, supplies the required two-difference adjacent `H`-grade determinant theorem. The marginal information gain is therefore higher in testing the exact splice invariant than in another broad search pass.

### Immediate use of mirror-factor positivity

Reject as load-bearing. The route should rely only on proved statements. Any conjectural positivity of mirror factors can be heuristic but cannot close Local TP2.

## Portfolio decision supported by this critique

Supported human decision:

- `CAM-LOCAL-TP2`: `HOLD -> ACTIVE` **only for one bounded lane**;
- execute `TASK-LOCAL-TP2-CONTINUANT-LGV-001` as written, with the Gate 0--3 ordering above;
- retain `max_active_lanes = 1`;
- do not open parallel QW3/quotient/far-minor or bigger finite-scan lanes;
- after the terminal Outcome and required post-outcome Evaluation, require a new continuation decision before any further Local TP2 Task.

Not supported:

- treating the current structural reduction as a proof;
- broad/open-ended Local TP2 restart;
- claim promotion;
- novelty claims;
- interpreting a common-network obstruction as a counterexample to Local TP2.

## Bottom line

The continuant/LGV idea has a serious central weakness: the literature gives positivity of the **individual Farey-recursive polynomials**, while the theorem needs a **joint subtraction-free model for two differences plus a strict mixed minor**. That gap is large enough that success should not be presumed.

Nevertheless, it is precisely the kind of gap worth one bounded lane: it is structurally new, all-depth, tightly matched to the frozen theorem, and falsifiable at an early algebraic splice gate. On strategy grounds, the expected information gain clears the bar for a narrow human-authorized reopen, but not for a general Campaign restart.