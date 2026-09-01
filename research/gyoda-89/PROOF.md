# Exact counterexample and infinite families

This is the privacy-safe public mathematical surface for canonical claim `C-GYODA-89`.

## 1. The 89 collision

For the fixed audited instance

```text
(k1,k2,k3) = (0,0,6)
sigma = (3,1,2)
```

the independently reconstructed generalized Cohn matrices are

\[
C_{1/5}=\begin{pmatrix}767&293\\89&34\end{pmatrix},\qquad
C_{2/3}=\begin{pmatrix}759&307\\89&36\end{pmatrix}.
\]

Both determinants equal `1`, and both lower-left entries equal `89`. The associated generalized Markov equation witnesses also vanish exactly. Thus two distinct labels have the same generalized Markov **number**:

\[
\boxed{n_{1/5}=n_{2/3}=89}.
\]

This refutes the number-only equality statement of Conjecture 7.6 as written in the audited v4 source.

## 2. Infinite family recurrence

For the audited family `(k1,k2,k3)=(0,0,k)` with the fixed orientation, let

\[
a_m=n_{1/m}.
\]

The independent structural audit checks that along the relevant left spine the correction term always uses positions whose parameters are `k_1=k_2=0`. Hence the Cohn mutation reduces to a fixed determinant-one trace-three recurrence,

\[
\boxed{a_{m+1}=3a_m-a_{m-1}},\qquad a_1=2,\quad a_2=5.
\]

Equivalently,

\[
a_m=F_{2m+1},
\]

with `F_n` the Fibonacci numbers under `F_1=F_2=1`.

The other audited branch is the exact affine expression

\[
\boxed{n_{2/3}=10k+29}.
\]

Therefore a collision occurs exactly when

\[
a_m\equiv9\pmod{10},\qquad k=\frac{a_m-29}{10}\ge0.
\]

## 3. Exact modulo-10 state cycle

Consider the recurrence state `(a_{m-1},a_m) mod 10`. Because the update

\[
(x,y)\mapsto(y,3y-x)
\]

is deterministic and invertible modulo `10`, its orbit is periodic. Direct exact state iteration returns to the starting recurrence state after 30 steps. Within one period,

\[
a_m\equiv9\pmod{10}
\]

exactly for

\[
\boxed{m\equiv5,14,15,24\pmod{30}}.
\]

Consequently each residue class supplies infinitely many nonnegative integer parameters

\[
k=\frac{a_m-29}{10}
\]

and hence infinitely many number-only collisions between the distinct labels `1/m` and `2/3`.

The first representative in each class is:

| residue class | first `m` | `a_m` | `k=(a_m-29)/10` |
|---|---:|---:|---:|
| `5 mod 30` | 5 | 89 | 6 |
| `14 mod 30` | 14 | 514229 | 51420 |
| `15 mod 30` | 15 | 1346269 | 134624 |
| `24 mod 30` | 24 | 7778742049 | 777874202 |

The recurrence is strictly increasing from these positive initial data, so the resulting `k` values are distinct. Also all listed `m>=5`, so `1/m != 2/3`.

## 4. What is proved

- The fixed `89` collision is exact.
- The four residue classes are mathematically established by an independent exact recurrence/state-cycle audit.
- The universal family conclusion comes from the recurrence plus its exact modulo-10 cycle, not from sampling finitely many large instances.

## 5. Scope and provenance

The written conjecture uses equality of generalized Markov numbers. Elsewhere the source also tracks position information. A stronger conjecture requiring equality of number/position pairs is a different statement and is not refuted here.

Raw author correspondence is not part of the public proof. The project record scopes author confirmation to the collision and the `5 mod 30` family only; the other three classes are independent AIMath extensions.

**Accepted private evidence:** source/replay commit `ffedc04af3a0dd951fa1b700dcbcd47c9901407a`; canonical claim level `INDEPENDENTLY_REPRODUCED` on private main `c8e61e0e398f540bc8c5de79663398d689f37473`.
