# Independent review — Dittert n=5 two-zero matching exclusion

**Writer target:** `f6202668acbd93c36a8acbfda7b71477026c4683`  
**Independent reviewer:** `dfde41ea2d6d1d84624ff7acd3ccfb435ee88df4`  
**Verdict:** `ACCEPT_WITH_QUALIFICATIONS`  
**Mathematical verdict:** `PASS`

The reviewer independently rederived the exact support-class exclusion rather than treating the writer's symbolic checker as a proof oracle.

## Passed gates

- **Fixed-pattern symmetrisation:** the exact two-matching-zero pattern reduces to the seven-positive-parameter canonical matrix without leaving the support class.
- **KKT chamber:** fresh permanent expansion gives `3(d-b)(f-e)>=(a+c)g>0`; the support automorphism permits `d>b`, `f>e`.
- **Stationarity:** direct expansion independently recovers the two identities used in `PROOF.md`.
- **Strict positivity:** `A_w,A_v>0` and `B_w>12Gz^2`, `B_v>12Gy^2` under the support positivity assumptions.
- **Contradiction:** the KKT chamber plus the first identity forces `x<0`, while the second forces `x>0`.
- **Negative controls:** the review confirmed that removing the KKT condition or a required support-positivity sign destroys the contradiction, so the proof is not a symbolic tautology.

## Source boundary

The review used bibliographic/source-backed KKT and symmetrisation statements without redistributing source PDFs. Documentation qualifications in the frozen review did not create a mathematical gap.

## Scope firewall

The full Dittert `n=5` conjecture, other zero-pattern classes, publication novelty/priority and author confirmation are outside this result.
