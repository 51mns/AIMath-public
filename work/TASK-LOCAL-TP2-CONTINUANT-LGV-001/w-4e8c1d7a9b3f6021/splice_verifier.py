#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
"""Exact finite verifier for the Local TP2 continuant-splice gate.

This executable checks algebraic identities and finite Farey fixtures used by
the proof note.  It is not an all-depth proof of Local TP2.  The all-depth
claims in RESULT.md require the written induction; this script is a negative
control / reproduction aid.
"""

from fractions import Fraction
from math import comb

# Polynomials in x, ascending integer coefficients.
ZERO = (0,)
ONE = (1,)
X = (0, 1)
X_PLUS_1 = (1, 1)
X_PLUS_2 = (2, 1)
TWO_X_PLUS_2 = (2, 2)
THREE_X_PLUS_2 = (2, 3)
M = (3, 3)  # 3(x+1)
ONE_MINUS_X = (1, -1)


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return tuple(p)


def add(a, b):
    n = max(len(a), len(b))
    return trim([
        (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
        for i in range(n)
    ])


def neg(a):
    return tuple(-v for v in a)


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, av in enumerate(a):
        for j, bv in enumerate(b):
            out[i + j] += av * bv
    return trim(out)


def scale(a, c):
    return trim([c * v for v in a])


def degree(a):
    return len(trim(a)) - 1


def nonnegative(a):
    return all(v >= 0 for v in a)


def matmul(a, b):
    return tuple(
        tuple(
            add(mul(a[i][0], b[0][j]), mul(a[i][1], b[1][j]))
            for j in range(2)
        )
        for i in range(2)
    )


def matsub(a, b):
    return tuple(tuple(sub(a[i][j], b[i][j]) for j in range(2)) for i in range(2))


def transpose(a):
    return ((a[0][0], a[1][0]), (a[0][1], a[1][1]))


def mat_nonnegative(a):
    return all(nonnegative(a[i][j]) for i in range(2) for j in range(2))


def det2(a):
    return sub(mul(a[0][0], a[1][1]), mul(a[0][1], a[1][0]))


def identity():
    return ((ONE, ZERO), (ZERO, ONE))


def amat(z):
    return ((z, ONE), (ONE, ZERO))


def word_matrix(word):
    out = identity()
    for z in word:
        out = matmul(out, amat(z))
    return out


J = ((ONE, ZERO), (ONE, (-1,)))
Q = matmul(amat(THREE_X_PLUS_2), J)
# Q = [[3(x+1), -1], [1, 0]].


def minus_one(p):
    return sub(p, ONE)


def farey_sum(a, b):
    return Fraction(a.numerator + b.numerator, a.denominator + b.denominator)


WORDS = {Fraction(1, 2): [TWO_X_PLUS_2, X_PLUS_2]}
PARENTS = {Fraction(1, 2): (Fraction(0), Fraction(1))}


def make_word(r, s, t):
    if t == Fraction(1, 2):
        return WORDS[t]
    if r == 0 and s != 1:
        b = WORDS[s]
        return [TWO_X_PLUS_2, ONE, minus_one(b[-1])] + list(reversed(b[:-1]))
    if r != 0 and s == 1:
        a = WORDS[r]
        return list(reversed(a)) + [THREE_X_PLUS_2, X_PLUS_2]
    a = WORDS[r]
    b = WORDS[s]
    return (
        list(reversed(a))
        + [THREE_X_PLUS_2, ONE, minus_one(b[-1])]
        + list(reversed(b[:-1]))
    )


def ensure(r, s):
    t = farey_sum(r, s)
    if t not in WORDS:
        WORDS[t] = make_word(r, s, t)
        PARENTS[t] = (r, s)
    return t


def generate(depth):
    intervals = [(Fraction(0), Fraction(1))]
    for _ in range(depth):
        new_intervals = []
        for r, s in intervals:
            t = ensure(r, s)
            new_intervals.extend(((r, t), (t, s)))
        intervals = new_intervals


def children(t):
    r, s = PARENTS[t]
    return ensure(r, t), ensure(t, s)


def h_profile(p):
    """H coefficients after x=q+q^-1, indices n>=0."""
    out = []
    for n in range(degree(p) + 1):
        total = 0
        for k, pk in enumerate(p):
            if k >= n and (k - n) % 2 == 0:
                total += pk * comb(k, (k - n) // 2)
        out.append(total)
    return out


def frozen_f(d_poly, s_poly):
    hd = h_profile(d_poly)
    hs = h_profile(s_poly)
    out = []
    for n in range(len(hs)):
        d0 = hd[n] if n < len(hd) else 0
        d1 = hd[n + 1] if n + 1 < len(hd) else 0
        s0 = hs[n]
        s1 = hs[n + 1] if n + 1 < len(hs) else 0
        out.append(d1 * s0 - d0 * s1)
    return out


def p_c(c):
    # 3(x+1)C + 1 - x.
    return add(mul(M, c), ONE_MINUS_X)


def main():
    # Gate-0 exact splice algebra.
    z = (7, 5, 2)  # arbitrary positive test polynomial; identity is coefficientwise.
    lhs = matmul(amat(ONE), amat(sub(z, ONE)))
    rhs = matmul(J, amat(z))
    assert lhs == rhs
    assert Q == (((3, 3), (-1,)), ((1,), (0,)))

    generate(depth=7)
    matrices = {t: word_matrix(w) for t, w in WORDS.items()}
    g = {t: a[0][0] for t, a in matrices.items()}
    g[Fraction(0)] = ONE
    g[Fraction(1)] = X_PLUS_2

    # Virtual boundary matrices make M_t=M_r^T Q M_s^T uniform.
    m0 = ((ONE, ZERO), (neg(X), ONE))
    m1 = ((X_PLUS_2, X_PLUS_1), (ONE, ONE))
    all_m = dict(matrices)
    all_m[Fraction(0)] = m0
    all_m[Fraction(1)] = m1

    root = Fraction(1, 2)
    assert matrices[root] == matmul(matmul(transpose(m0), Q), transpose(m1))

    # Root polynomial and the published 1/3 Laurent fixture.
    assert g[root] == (5, 6, 2)
    one_third = Fraction(1, 3)
    assert g[one_third] == (13, 26, 18, 4)
    assert h_profile(g[one_third]) == [49, 38, 18, 4]

    # Fixed-skew and positive Q M_t^T checks.
    for t, a in matrices.items():
        assert sub(a[0][1], a[1][0]) == X
        assert mat_nonnegative(a)
        assert mat_nonnegative(matmul(Q, transpose(a)))

    # Boundary-gap cone: Delta>=0 and Q Delta>=0.
    for t, a in matrices.items():
        r, s = PARENTS[t]
        for boundary in (r, s):
            delta = matsub(a, all_m[boundary])
            assert mat_nonnegative(delta), (t, boundary, delta)
            assert mat_nonnegative(matmul(Q, delta)), (t, boundary, delta)

    # Ensure children one more generation for S/D checks.
    for t in list(PARENTS):
        children(t)
    for t, w in WORDS.items():
        if t not in matrices:
            matrices[t] = word_matrix(w)
            g[t] = matrices[t][0][0]

    checked = 0
    finite_tp2_checked = 0
    for t in list(PARENTS):
        if t not in matrices:
            continue
        lch, rch = children(t)
        if lch not in matrices or rch not in matrices:
            continue
        r, s = PARENTS[t]
        a = g[r]
        b = g[s]
        c = g[t]
        gl = g[lch]
        gr = g[rch]

        if degree(gl) < degree(gr):
            u, v = gl, gr
        else:
            u, v = gr, gl

        # Higher-degree Farey boundary determines the oriented D factor.
        if degree(a) < degree(b):
            low_boundary, high_boundary = a, b
        else:
            low_boundary, high_boundary = b, a

        s_poly = sub(u, c)
        d_poly = sub(v, u)
        e = sub(high_boundary, low_boundary)
        d_formula = mul(e, p_c(c))

        assert d_poly == d_formula, t
        assert nonnegative(s_poly), t
        assert nonnegative(d_poly), t
        assert sub(high_boundary, low_boundary)[0] >= 0
        checked += 1

        # Finite sanity only: this does not establish the universal theorem.
        f = frozen_f(d_poly, s_poly)
        assert all(value > 0 for value in f), (t, f)
        finite_tp2_checked += 1

    # Exact obstruction to the most direct "gap matrix is the LGV path matrix" idea.
    delta_root_left = matsub(matrices[Fraction(1, 3)], matrices[root])
    assert det2(delta_root_left) == (-1, -2, -1)  # -(x+1)^2

    # Frozen root orientation.
    lch, rch = children(root)
    u, v = (
        (g[lch], g[rch])
        if degree(g[lch]) < degree(g[rch])
        else (g[rch], g[lch])
    )
    s_root = sub(u, g[root])
    d_root = sub(v, u)
    assert h_profile(s_root) == [40, 32, 16, 4]
    assert h_profile(d_root) == [164, 138, 80, 30, 6]
    assert frozen_f(d_root, s_root) == [272, 352, 160, 24]

    print("PASS")
    print(f"farey_words={len(WORDS)}")
    print(f"subtraction_free_sibling_checks={checked}")
    print(f"finite_local_tp2_sanity_checks={finite_tp2_checked}")
    print("direct_gap_network_obstruction=det(M_1/3-M_1/2)=-(x+1)^2")


if __name__ == "__main__":
    main()
