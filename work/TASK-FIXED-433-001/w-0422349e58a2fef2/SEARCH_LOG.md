<!--
SPDX-FileCopyrightText: 2026 AIMath contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# TASK-FIXED-433-001 — search log

- Worker: `w-0422349e58a2fef2`
- Search date: 2026-09-02
- Public base held fixed during search: `71547cb5d757afaace54b558f2d0a4a49fad5656`
- Current PR: `#27`
- Parallel comparison deliberately excluded as a work source: Button-centered PR `#26`
- Novelty policy: `NOT_ESTABLISHED`; search absence has no novelty effect

## Frozen objective

Broaden prior-art placement for

`R_5(x)=4/5-x`

and the equivalent fixed-433 identity

`U_k/M_k = 4/5 - mu((9k+8)/(15k+13))`

away from a Button-centered audit.

## Priority order used

1. pre-Button Markoff / Cassels / Cohn lineage;
2. Bombieri;
3. Springborn;
4. post-Button research explicitly using/citing Button in the Markoff uniqueness/ideal-class lineage;
5. Veselov / Cohn-index framework.

## Search interfaces

- general scholarly web index available to this research session;
- direct publisher/journal/archive pages when a result resolved to a primary source;
- primary PDF text extraction when available;
- PDF screenshot/render was attempted for relevant PDFs as a visual check, but several hosts returned cache/render failures; those failures are recorded as access limits rather than mathematical evidence.

No secondary source is used to establish an exact mathematical match or novelty. Secondary/index pages are navigation aids only.

## Query strings executed

The following exact or exact-title query strings were used during the continuation. Minor open/find operations within already located primary sources are listed separately below rather than counted as new discovery queries.

### Pre-Button / classical lineage

- `"Markoff forms" Cohn matrix continued fractions Markoff numbers pdf`
- `"Markoff numbers" Cohn matrices pdf`
- `Cassels Markoff numbers continued fractions congruence pdf`
- `"An Introduction to Diophantine Approximation" Markoff Cassels pdf`
- `"Harvey Cohn" Markoff site:ams.org`
- `"Harvey Cohn" "Markoff" "Math. Ann."`
- `"Harvey Cohn" "Markoff" "continued fractions"`
- `"Cohn" "Markoff" "free group" words`
- `"Markoff's forms" Cohn 1955`
- `"Approach to Markoff's minimal forms through modular functions" Cohn`
- `"Approach to Markoff's Minimal Forms Through Modular Functions" pdf`
- `"Representation of Markoff's binary quadratic forms by geodesics on a perforated torus" pdf`
- `"Markoff forms and primitive words" pdf`
- `"Growth types of Fibonacci and Markoff" pdf`
- `"The Markoff Chain" Cassels 676 685 Markoff equation 1949`
- `"The Markoff Chain" Cassels x^2+y^2+z^2`
- `"The Markoff Chain" Cassels pdf 676`
- `"Sur les formes binaires indéfinies" Markoff 1880 pdf`

### Bombieri

- `"Continued fractions and the Markoff tree" Bombieri pdf`
- `"Continued fractions and the Markoff tree" Bombieri "pdf" "187" "213"`
- `"Continued fractions and the Markoff tree" Bombieri filetype:pdf`
- `"Continued fractions and the Markoff tree" Bombieri "Theorem 3" Markoff`
- `"Continued fractions and the Markoff tree" Bombieri Cohn A =`
- `"Continued fractions and the Markoff tree" Bombieri "Markoff irrational" equation`
- `"Continued fractions and the Markoff tree" Bombieri "free group" X Y`

### Springborn

- `"The worst approximable rational numbers" Springborn pdf`

After locating the primary PDF, direct page/text inspection was used for equations (4)–(7), the reflection passage on p.157, and the Markov-fraction tree.

### Button-citing downstream work

- `"Markoff Numbers, Principal Ideals and Continued Fraction Expansions" citations`
- `"Markoff numbers and ambiguous classes" Srinivasan pdf`
- `"Markoff numbers and ambiguous classes" Button "Theorem 4.3" Baragar`

After locating Srinivasan's primary PDF, direct searches inside that PDF used `Button`, `Cohn`, `ambiguous`, and `3c - 2`.

### Veselov / Cohn-index framework

- `"Markov fractions and Cohn matrices" Veselov 2604.17401 pdf`

After locating the primary arXiv PDF, direct page/text inspection used `Theorem 3.1`, `Aff1`, equations (3)–(5), Proposition 2.1 equations (6)–(8), and equations (12)–(15).

### Semantic false-friend control

- `"On the Markov numbers: Fixed numerator, denominator, and sum conjectures" PDF`

This control was used to prevent the phrase “fixed numerator” in later Markov-number literature from being confused with AIMath's Markov-fraction numerator `p_k`. The paper's fixed-numerator conjecture concerns the rational index of a Markov number `m_{p/q}`, not the fixed-433 representative identity.

## Primary sources actually adjudicated

The final `SOURCE_MAP.md` records the adjudication for:

- Markoff 1879;
- Cassels 1957 (access-limited body, exact chapter/page locations available from primary preview);
- Cohn 1955 (access-limited);
- Cohn 1971 (PDF located, rendering/text path failed);
- Cohn 1972 (primary record located, content endpoint timed out);
- Baragar 1996;
- Bombieri 2007 (publisher metadata/abstract available, body access insufficient);
- Springborn 2024;
- Srinivasan 2009;
- Veselov 2026;
- Button 2001 only as a prior-lane context row, not a fresh principal audit.

## Access/render failures preserved

- Springborn 2024 PDF text was available, but the screenshot endpoint returned a cache miss for the inspected page.
- Srinivasan 2009 PDF text was available, but the screenshot endpoint returned a cache miss for the attempted page.
- Cohn 1971 primary PDF was located through the journal/archive, but the available PDF text/render route did not return inspectable page content.
- Cohn 1972 primary content endpoint timed out.
- Bombieri 2007 publisher page exposed the article metadata and abstract, while full body/equation retrieval was not available through the runtime.

These are **access gaps**, not negative prior-art results.

## Stop rule and why the bounded search closes

The continuation stops when each requested priority class has one of:

1. an equation/page-level primary-source comparison to the AIMath object; or
2. an explicit primary-source access limitation recorded as unresolved;

and when the same-object normalization question has been resolved far enough to distinguish the standard source action from the AIMath map.

That condition is met:

- the pre-Button lineage is mapped with exact Baragar/Markoff content plus explicit Cassels/Cohn access gaps;
- Bombieri is source-identified with an honest body-access boundary;
- Springborn gives the same Markov-fraction object and integer-affine action explicitly;
- a Button-citing downstream primary source (Srinivasan) is mapped and remains on a different object;
- Veselov gives the exact Markov-fraction/Cohn-index bridge and the same integer-affine fundamental-domain action.

A larger search would now be a broader historical-priority campaign rather than completion of this bounded continuation. No such expansion is inferred to be justified by search absence.
