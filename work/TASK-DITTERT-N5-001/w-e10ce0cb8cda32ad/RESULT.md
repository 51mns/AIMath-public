# TASK-DITTERT-N5-001 — E0 result

Worker: `w-e10ce0cb8cda32ad`  
Worker branch: `research/TASK-DITTERT-N5-001/w-e10ce0cb8cda32ad`  
Public activation base: `279ba9fa98befe3aee37bfd1a98e4f688d333bd4`  
Private source snapshot referenced by the public campaign: `c8e61e0e398f540bc8c5de79663398d689f37473`

## Decision

**Outcome candidate: `LITERATURE_MATCH` / `PIVOT_RECOMMENDED`.**

Do not continue spending this Task on narrower exact-zero-pattern exclusions until the external working proof below has been independently reproduced or falsified. The located external result, if correct, strictly dominates the Task objective: it excludes the entire two-prescribed-independent-zero face, not merely one exact support orbit.

This is an E0 strategic result. It is **not** an AIMath proof of Dittert `n=5`, not an independent reproduction of the external certificate, and not a novelty claim.

## External working proof fixed for inspection

Repository: `pedromnasc/dittert-conjecture-proof`  
Fixed commit inspected: `894066bbaa715138c98bf3cb7c6fdb4f39a37701`  
Relevant directory: `n5/`

The fixed proof note is titled *An Exact Computer-Assisted Proof of the Dittert Conjecture for n=5* (Pedro Paulo Marques do Nascimento, 23 July 2026). It explicitly labels itself as a working proof that has not undergone independent peer review.

Its proof architecture is materially stronger than `C-DITTERT-N5-Z2-MATCHING-EXCLUSION`:

1. Hwang's positive-support theorem handles a positive maximizer.
2. Cheon--Wanless exclude partly decomposable maximizers and maximizers whose complete zero set is one proper rectangular block.
3. A simple combinatorial lemma then shows that any remaining boundary maximizer must contain two zero positions in distinct rows and distinct columns.
4. Row/column permutation therefore reduces the whole remaining boundary problem to the face `a_11=a_22=0`.
5. On that **entire face**, regardless of additional zeros, the external note gives an integer multiplier--SOS certificate for a strict quintic inequality.

Thus, if the certificate and reduction withstand independent audit, every exact zero-pattern containing an independent pair is already covered at once, and the full `n=5` conjecture follows together with the published structural results.

### Frozen external integrity metadata

The external `n5/SHA256SUMS` at the fixed commit records:

- certificate `dittert_n5_exact_certificate.npz` SHA-256: `373041bda29e1164059a2adbad1aaacd2911784a273629f419972e7ec7b5fdca`;
- verifier `verify_primary.py` SHA-256: `c51b3490f84fa6411a19e822885ec71addb225d0ee6a77343fbbacd3dda56aab`;
- proof TeX SHA-256: `5ac554b8b4583dcaed73306796cbee20b6df84b26a97c3807495eaa49cb79613`.

The note/verifier specify a 23-variable two-zero face, a symmetry group of order 144, 3922 quintic hyperedges, 80,730 degree-five monomials, and a strictly positive minimum residual numerator `7,628,882,599,067,611,080` over the common exact denominator.

## AIMath writer-side exact cross-check completed

`two_zero_face_crosscheck.py` was written independently of the external verifier. It does **not** load or use the external certificate.

Local execution:

```text
exit code: 0
status: WRITER_CROSSCHECK_PASS
allowed variables: 23
row transversals: 2000
column transversals: 2000
allowed permutation transversals: 78
quintic hyperedges: 3922
degree-5 monomials in 23 variables: 80730
exact evaluation cases: 5/5 PASS
```

The five deterministic integer evaluation points independently verify

`F = product(row sums) + product(column sums) - permanent`

for the two-zero face, and the exact normalization

`(6130/3125) / 5^5 = 1226/5^9`.

Local script SHA-256 at execution: `bf8adb91dd6bbf4ae28675937b2c0f078cef9a626112a22db48057c04647f0df`.  
Git blob after remote read-back: `a645de3fbc9a3742fe34cc6c22d9dd7d9619a14d`.

This independently confirms the **combinatorial/polynomial front end only**. It is useful because the 3922/80730 counts and hypergraph identity are load-bearing inputs to the external certificate verifier.

## What has NOT been verified here

The external binary `.npz` certificate could not be transferred into this session's execution runtime through the available connector path. The interface can read repository metadata/text but the binary blob transport failed, and the container has no direct DNS access to GitHub.

Therefore this worker has **not**:

- recomputed the certificate's SHA-256 from downloaded raw bytes;
- run `verify_primary.py` against the certificate;
- independently reconstructed the three Gram/SOS matrices;
- independently checked all 80,730 residual coefficients;
- independently audited the published Hwang / Cheon--Wanless dependencies at theorem-proof level;
- established peer-reviewed or publication-level acceptance.

No `INDEPENDENTLY_REPRODUCED`, `SOLVED`, `NEW`, `FIRST`, or publication-novelty claim is licensed by this worker result.

## Strategic consequence for AIMath

The current public Task asks for a genuinely broader zero-pattern exclusion rather than another exact Z2 case. A source now exists whose claimed theorem covers the **entire** two-independent-zero face and hence dominates any proposed 3-zero/4-zero support-by-support campaign.

Accordingly the highest-information next action is not another structural writer on narrower zero patterns. It is a bounded independent reproduction/audit of the fixed external `n5` proof bundle, with exact binary read-back and a separately implemented verifier or coefficient audit.

Recommended routing:

- **PIVOT** this research Task away from incremental zero-pattern theorem production;
- create/route a separate quality/reproduction Task for fixed external commit `894066bbaa715138c98bf3cb7c6fdb4f39a37701` if the portfolio wants to rely on the working proof;
- if that audit passes, reassess whether `CAM-DITTERT-N5` should close as externally dominated/solved-working-proof rather than continue internal boundary classification;
- if the external proof fails, reopen the structural route with the failure boundary recorded.

## Sources

- Gi-Sang Cheon and Ian M. Wanless, *Some results towards the Dittert conjecture on permanents*, Linear Algebra and its Applications 436 (2012), 791--801, DOI `10.1016/j.laa.2010.08.041`.
- `pedromnasc/dittert-conjecture-proof`, fixed commit `894066bbaa715138c98bf3cb7c6fdb4f39a37701`, especially `n5/dittert_n5_exact_proof.tex`, `n5/verify_primary.py`, `n5/SHA256SUMS`, and `n5/README.md`.
