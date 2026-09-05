<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# AFRD evaluator-side baseline packet

**Do not give this file to a blind discovery lane before its representation freeze.** This packet exists to prevent a post-hoc baseline from being chosen only after seeing a candidate. It is not a candidate-specific novelty audit.

## Predeclared baseline classes

- raw-`N` matched readout;
- trivial reversible re-encoding matched for representation size;
- trial division;
- Fermat-style difference-of-squares search;
- Pollard rho;
- Pollard p-1;
- ECM when the frozen runtime makes it feasible;
- a distributed/vector-symbolic representation reference;
- an ML-assisted Fermat reference.

NFS is retained as a scale/context baseline rather than an E0 per-instance runtime baseline because these pilot sizes and sub-second caps are not intended to benchmark state-of-the-art large-integer NFS implementations.

## Frozen literature anchors

These establish that several important factorisation mechanisms and representation/ML directions predate AFRD. They do **not** establish that any future AFRD candidate is equivalent to them.

1. J. M. Pollard, *Theorems on factorization and primality testing*, Proc. Cambridge Philos. Soc. 76 (1974), 521–528. DOI: `10.1017/S0305004100049252`.
2. H. W. Lenstra Jr., *Factoring integers with elliptic curves*, Annals of Mathematics 126 (1987), 649–673. DOI: `10.2307/1971363`.
3. A. K. Lenstra and H. W. Lenstra Jr. (eds.), *The Development of the Number Field Sieve*, Lecture Notes in Mathematics 1554 (1993). DOI: `10.1007/BFb0091534`.
4. D. Kleyko et al., *Integer Factorization with Compositional Distributed Representations* (2022), arXiv:`2203.00920`.
5. S. Blake, *Integer Factorisation, Fermat & Machine Learning on a Classical Computer* (2023), arXiv:`2308.12290`.

## Non-claims

- This is not an exhaustive factorisation bibliography.
- These anchors do not prove novelty or non-novelty of a future `X(N)`.
- Search absence is not novelty evidence.
- A candidate can be useful even if later reduced to known mathematics; in that case it is not promoted as new mathematics.
- Candidate-specific nearest-prior-work searching is intentionally delayed until after candidate freeze and held-out gating.
