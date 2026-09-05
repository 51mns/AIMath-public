#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
"""Independent finite negative-control checker for the #85 gap-cone review.

This program reimplements Definition 3.1 of arXiv:2602.14802 from scratch.
It does not import the writer's splice_verifier.py and it is not an all-depth
proof. The universal argument is in the accompanying mathematical review.
"""

from fractions import Fraction

ZERO = (0,)
ONE = (1,)
X = (0, 1)


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return tuple(p)


def add(a, b):
    n = max(len(a), len(b))
    return trim(
        (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
        for i in range(n)
    )


def neg(a):
    return tuple(-c for c in a)


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] += ai * bj
    return trim(out)


def nonnegative(p):
    return all(c >= 0 for c in p)


def degree(p):
    return len(trim(p)) - 1


def lin(c0, c1):
    return (c0, c1)


def matmul(a, b):
    return tuple(
        tuple(
            add(mul(a[i][0], b[0][j]), mul(a[i][1], b[1][j]))
            for j in range(2)
        )
        for i in range(2)
    )


def matsub(a, b):
    return tuple(
        tuple(sub(a[i][j], b[i][j]) for j in range(2))
        for i in range(2)
    )


def transpose(a):
    return ((a[0][0], a[1][0]), (a[0][1], a[1][1]))


def amat(z):
    return ((z, ONE), (ONE, ZERO))


def word_matrix(word):
    out = ((ONE, ZERO), (ZERO, ONE))
    for z in word:
        out = matmul(out, amat(z))
    return out


def det(a):
    return sub(mul(a[0][0], a[1][1]), mul(a[0][1], a[1][0]))


def mediant(r, s):
    return Fraction(
        r.numerator + s.numerator,
        r.denominator + s.denominator,
    )


Q = ((lin(3, 3), (-1,)), (ONE, ZERO))
M0 = ((ONE, ZERO), (neg(X), ONE))
M1 = ((lin(2, 1), lin(1, 1)), (ONE, ONE))

words = {Fraction(1, 2): [lin(2, 2), lin(2, 1)]}
parents = {Fraction(1, 2): (Fraction(0), Fraction(1))}


def ensure(r, s):
    t = mediant(r, s)
    if t in words:
        return t
    if r == 0:
        b = words[s]
        word = [lin(2, 2), ONE, sub(b[-1], ONE)] + b[-2::-1]
    elif s == 1:
        a = words[r]
        word = a[::-1] + [lin(2, 3), lin(2, 1)]
    else:
        a, b = words[r], words[s]
        word = (
            a[::-1]
            + [lin(2, 3), ONE, sub(b[-1], ONE)]
            + b[-2::-1]
        )
    words[t] = word
    parents[t] = (r, s)
    return t


def generate(depth):
    intervals = [(Fraction(0), Fraction(1))]
    for _ in range(depth):
        nxt = []
        for r, s in intervals:
            t = ensure(r, s)
            nxt.extend(((r, t), (t, s)))
        intervals = nxt


def factor_pc(c):
    # 3(x+1)C + 1 - x
    return add(mul(lin(3, 3), c), (1, -1))


def main():
    generate(7)
    matrices = {t: word_matrix(w) for t, w in words.items()}
    all_m = dict(matrices)
    all_m[Fraction(0)] = M0
    all_m[Fraction(1)] = M1

    # Recompute the transfer splice, fixed skew, degree rank, and cone.
    cone_edges = 0
    for t, mt in matrices.items():
        r, s = parents[t]
        assert mt == matmul(matmul(transpose(all_m[r]), Q), transpose(all_m[s]))
        assert sub(mt[0][1], mt[1][0]) == X
        assert det(mt) == ONE
        assert degree(mt[0][0]) == t.numerator + t.denominator - 1

        for entry in words[t]:
            assert nonnegative(entry)
        assert words[t][-1][0] >= 2
        assert nonnegative(sub(mul(lin(3, 3), words[t][-1]), ONE))

        for boundary in (r, s):
            gap = matsub(mt, all_m[boundary])
            qgap = matmul(Q, gap)
            assert all(nonnegative(e) for row in gap for e in row)
            assert all(nonnegative(e) for row in qgap for e in row)
            cone_edges += 1

    # Build one extra child generation for the D factorisation checks.
    existing = list(parents)
    for t in existing:
        r, s = parents[t]
        ensure(r, t)
        ensure(t, s)
    for t, w in words.items():
        if t not in matrices:
            matrices[t] = word_matrix(w)

    d_checks = 0
    for t in existing:
        r, s = parents[t]
        left = mediant(r, t)
        right = mediant(t, s)
        gl = matrices[left][0][0]
        gr = matrices[right][0][0]
        a = all_m[r][0][0]
        b = all_m[s][0][0]
        c = matrices[t][0][0]

        if degree(b) > degree(a):
            high_boundary, low_boundary = b, a
            high_child, low_child = gr, gl
        else:
            high_boundary, low_boundary = a, b
            high_child, low_child = gl, gr

        assert degree(high_child) > degree(low_child)
        assert sub(high_child, low_child) == mul(
            sub(high_boundary, low_boundary),
            factor_pc(c),
        )
        assert nonnegative(sub(high_boundary, low_boundary))
        assert nonnegative(sub(high_child, low_child))
        d_checks += 1

    # Extreme 1/n chain: independent recurrence/formula control.
    rho = lin(3, 2)
    p = [ONE, rho]
    for _ in range(2, 9):
        p.append(sub(mul(rho, p[-1]), p[-2]))
    for n in range(3, 9):
        bn = matsub(matrices[Fraction(1, n)], matrices[Fraction(1, n - 1)])
        expected = (
            (mul(lin(1, 1), p[n - 1]), mul(lin(1, 1), p[n - 2])),
            (mul(lin(1, 1), p[n - 2]), mul(lin(1, 1), p[n - 3])),
        )
        assert bn == expected
        assert all(nonnegative(e) for row in matmul(Q, bn) for e in row)

    # Root obstruction to the raw-gap LGV architecture.
    delta = matsub(matrices[Fraction(1, 3)], matrices[Fraction(1, 2)])
    assert det(delta) == (-1, -2, -1)

    print("PASS")
    print(f"farey_vertices={len(existing)}")
    print(f"cone_edge_checks={cone_edges}")
    print(f"d_factor_checks={d_checks}")
    print("extreme_chain_n=3..8")
    print("root_gap_det=-(x+1)^2")


if __name__ == "__main__":
    main()
