# Independent review — two-pivot residual capacity

**Writer:** `39a9efc6b2273da00d0a5da0aa166d3c03fdc227`  
**Method freeze:** `5e78d3ea3cd2993f6b4b2accbca711ea925b9723`  
**Independent proof/control freeze:** `9d4270adff6b0b3959e7ceec69253ca2bea3d8a9`  
**Independent p=71 certificate:** `fb4101869b6ee66e0050cd2533989f00e6673b6b`  
**Final reviewer:** `092f9110a50c775040f5d3482f0a8e1b2c6bc580`

Decision: `ACCEPT_WITH_QUALIFICATIONS`; the generic theorem is mathematically correct.

## Reproduced results

The reviewer independently reconstructed the proof that every valid completion satisfies `|U|<=R2`, and independently proved `R2<=R1`. The only formal qualification was that impossible second-pivot branches must be explicitly totalized by exclusion or `-infinity`; the public theorem does so.

Independent bounded controls covered 9,303 small abstract states, 8,310 of which were coverable, with zero false R2 prunes and zero `R2>R1` failures. A deliberately malformed min-vs-max rule produced a false prune, confirming the load-bearing max/min order.

The LRC translate identities and the reachable `p=71` strict certificate were separately reconstructed. That certificate is bounded evidence, not the generic theorem.

## Performance and scope

This result does not prove `LRC(13)`, does not establish a practical speedup, and does not license R3/R4/R5 escalation. Later frozen benchmarking closed the measured scaling route as `NO_GO_FOR_SCALING`.

Publication novelty was not assessed.
