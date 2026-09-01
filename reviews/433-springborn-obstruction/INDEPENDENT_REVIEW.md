# Independent review — fixed-433 Springborn obstruction

**Writer fixed commit:** `5130ada104d4c71e68b2b56811210d510d83d831`  
**Independent review fixed commit:** `24569ada8f0cb233e0edd2af2b61b48cec32863a`  
**Decision:** `ACCEPT WITH QUALIFICATIONS`

The independent review rederived every load-bearing step rather than treating the writer checker as the proof.

## Mathematical checks

The review independently confirmed:

1. `w_k=C0 B^k` represents `M_k/U_k`, hence `[0;w_k]=U_k/M_k`.
2. The common all-`k` prefix is `2,1,1,2,2,1,1,2,4,...`.
3. The convergent before `4` is `75/194`; the previous convergent is `29/75`.
4. With complete quotient `t_k`,
   `x_k=(75 t_k+29)/(194 t_k+75)`.
5. `75^2-29*194=-1`, so
   `194^2 |x_k-75/194| = 194/(194 t_k+75)`.
6. `t_k>4`, and therefore the exact quantity above is `<1/4`.
7. `75/194` is a distinct admissible rational competitor in the definition of `C(x_k)`.
8. Springborn Theorem 2.2 therefore excludes each target from the stated Markov-fraction / companion classes.
9. The integer-affine extension `x -> +/-x+n` is valid.
10. No general `GL_2(Z)` / `PGL_2(Z)` orbit exclusion is inferred.

The reviewer also noted that `t_k>4` is stronger than needed: `t_k>=4` already yields `194/(194t_k+75) <= 194/851 < 1/4`.

## Independent computation

`independent_verify.py` imports none of the writer module or generated expected output and reproduces the fixed definitions and first seven exact cases. These cases support consistency only; the universal conclusion comes from the proof above.

## Qualifications

- Publication novelty: **NOT ESTABLISHED**.
- One adjacent article body was not available in the frozen source audit, so no formula-level novelty conclusion is drawn from it.
- Author confirmation: **NONE / NOT CLAIMED**.

No private correspondence or personal information is part of the public evidence.
