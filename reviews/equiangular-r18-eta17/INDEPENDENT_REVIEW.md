# Independent review — R18 eta=17 singleton spectrum

**Writer fixed SHA:** `2b61a27c37d87934c765688140cbd15cc8050440`  
**Phase-1 independent derivation:** `1d5100b713e36f58bbee917da9d255d6b0c72a7b`  
**Final reviewer:** `1f5d19f617ee9187216c51cc69a6bf5f2e750520`  
**Mathematical verdict:** `PASS`

Phase 1 fixed its derivation and exact checker before inspecting the writer proof/artifacts.

## Independently reproduced gates

1. The predecessor eta17/simple-11 assumptions reduce to the unique necessary spectrum
   `-5^41, 9^6, 10, 11, 13^10`.
2. Cauchy interlacing and order-58 Seidel moments force each principal deletion to have
   `F Q_i`, with
   `F=(x+5)^40(x-9)^5(x-13)^9` and
   `Q_i=x^4-38x^3+532x^2+A_ix+B_i`.
3. Endpoint signs produce exactly 64 integer quartic candidates.
4. The complete type-2 coefficient condition leaves exactly
   `Q_0=x^4-38x^3+532x^2-3242x+7227`.
5. The universal principal-deletion identity `p'=sum_i chi_{S_i}` would require `p'/F=59Q_0`, but exact arithmetic gives
   `p'/F-59Q_0=16(19x-213) != 0`.
6. Therefore no Seidel matrix has the frozen spectrum.

Two negative controls were independently rejected: a nearby endpoint-feasible quartic fails type 2, and a trace-preserving perturbed spectrum fails the Seidel second moment.

## Scope firewall

The review does not establish `N(18)<=58`, does not exclude eta `2..16`, does not solve the full maximum equiangular-line problem, and does not establish publication novelty or priority.

The original review recorded two documentation/environment qualifications; neither affects the mathematical proof.
