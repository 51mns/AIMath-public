# Independent review — fixed-433 existing-theory identification

**Writer fixed commit:** `423a4a1cae9efa52d97240f5bae21ecad1bae19c`  
**Independent review fixed commit:** `cd098e8ad4f6c69bbe6bfa6a134dfda3e8aa41e6`  
**Decision:** `ACCEPT WITH QUALIFICATIONS`  
**Mathematical validity:** `PASS`

The reviewer independently reconstructed the Farey/Cohn ray, source normalization, recurrence identification, cross-determinant sign, factor-5 CRT step and representative inequalities.

## Accepted all-k chain

1. The Farey ray satisfies `t_n=(3n+2)/(5n+3)`.
2. With the reviewed `a=0` Cohn normalization,
   `C_{t_n}(0)=C_{3/5}(0)^n C_{2/3}(0)`.
3. `C_{3/5}(0)` has determinant `1` and trace `1299`; Cayley–Hamilton therefore forces the same recurrence as the canonical AIMath sequence, with matching initial values `29,37666`. Hence every source denominator is identified exactly, not by finite fitting.
4. The oriented source cross-determinant yields
   `p_{n-1}q_n-p_nq_{n-1}=433`.
5. At `n=2+3k`, this fixes the canonical root representative as
   `r_k=M_k-p_k`.
6. Accepted fixed-433 congruences modulo `N_k=M_k/5` and modulo `5`, followed by CRT and representative-range bounds, give
   `U_k=r_k-M_k/5`.
7. Therefore
   `5p_k=4M_k-5U_k` and
   `U_k/M_k=4/5-mu((9k+8)/(15k+13))` for all `k>=0`.

## Independent computation

`independent_verify.py` imports no writer implementation or generated expected output. It reconstructs source matrices and checks exact finite fingerprints plus negative controls. Finite computation supports the fixed definitions but is not used as the universal proof.

## Boundaries

- `R_5(x)=4/5-x` is not an integer-affine symmetry and not in `PGL_2(Z)`.
- The result does not conflict with the separate Springborn obstruction.
- Publication novelty: **NOT ESTABLISHED**.
- Author confirmation: **NONE / NOT CLAIMED**.
- The original review recorded a transport limitation in its runtime; later canonical coordination resolved repository reproduction by hosted checkout. That environment history does not alter the mathematics.

No private correspondence or personal information is part of the exported evidence.
