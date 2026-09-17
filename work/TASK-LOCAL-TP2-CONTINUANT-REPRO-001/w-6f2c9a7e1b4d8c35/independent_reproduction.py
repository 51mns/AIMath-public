# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0

from fractions import Fraction
from math import comb


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return tuple(p)


def p_add(a, b):
    n = max(len(a), len(b))
    out = [0] * n
    for i, v in enumerate(a):
        out[i] += v
    for i, v in enumerate(b):
        out[i] += v
    return trim(out)


def p_neg(a):
    return tuple(-v for v in a)


def p_sub(a, b):
    return p_add(a, p_neg(b))


def p_mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return trim(out)


def p_degree(p):
    return len(trim(p)) - 1


def m_transpose(A):
    return ((A[0][0], A[1][0]), (A[0][1], A[1][1]))


def m_mul(A, B):
    return tuple(
        tuple(
            p_add(p_mul(A[i][0], B[0][j]), p_mul(A[i][1], B[1][j]))
            for j in range(2)
        )
        for i in range(2)
    )


def m_sub(A, B):
    return tuple(tuple(p_sub(A[i][j], B[i][j]) for j in range(2)) for i in range(2))


def m_scale(p, A):
    return tuple(tuple(p_mul(p, A[i][j]) for j in range(2)) for i in range(2))


def splice(Mr, Ms, Q):
    return m_mul(m_mul(m_transpose(Mr), Q), m_transpose(Ms))


def h_profile(p):
    d = p_degree(p)
    return tuple(
        sum(
            b * comb(j, (j - n) // 2)
            for j, b in enumerate(p)
            if j >= n and (j - n) % 2 == 0
        )
        for n in range(d + 1)
    )


def adjacent_minor_profile(S, D):
    hs = h_profile(S)
    hd = h_profile(D)
    out = []
    for n in range(p_degree(S) + 1):
        s0 = hs[n] if n < len(hs) else 0
        s1 = hs[n + 1] if n + 1 < len(hs) else 0
        d0 = hd[n] if n < len(hd) else 0
        d1 = hd[n + 1] if n + 1 < len(hd) else 0
        out.append(d1 * s0 - d0 * s1)
    return tuple(out)


ONE = (1,)
ZERO = (0,)
X = (0, 1)

M0 = ((ONE, ZERO), (p_neg(X), ONE))
M1 = ((p_add(X, (2,)), p_add(X, (1,))), (ONE, ONE))
Q = (((3, 3), (-1,)), (ONE, ZERO))

nodes = {}


def build_interval(fr, Mr, fs, Ms, depth, max_depth):
    if depth > max_depth:
        return
    t = Fraction(fr.numerator + fs.numerator, fr.denominator + fs.denominator)
    Mt = splice(Mr, Ms, Q)
    nodes[t] = {"left": fr, "right": fs, "M": Mt, "depth": depth}
    build_interval(fr, Mr, t, Mt, depth + 1, max_depth)
    build_interval(t, Mt, fs, Ms, depth + 1, max_depth)


build_interval(Fraction(0), M0, Fraction(1), M1, 1, 9)

root = nodes[Fraction(1, 2)]["M"]
assert root == (
    ((5, 6, 2), (2, 2)),
    ((2, 1), (1,)),
)

subtraction_free_checks = 0
finite_local_tp2_checks = 0

for t, rec in nodes.items():
    if rec["depth"] > 7:
        continue
    r, s = rec["left"], rec["right"]
    left_child = Fraction(r.numerator + t.numerator, r.denominator + t.denominator)
    right_child = Fraction(t.numerator + s.numerator, t.denominator + s.denominator)
    C = rec["M"][0][0]
    GL = nodes[left_child]["M"][0][0]
    GR = nodes[right_child]["M"][0][0]

    if p_degree(GL) <= p_degree(GR):
        U, V = GL, GR
    else:
        U, V = GR, GL

    S = p_sub(U, C)
    D = p_sub(V, U)

    assert all(c >= 0 for c in S)
    assert all(c >= 0 for c in D)
    subtraction_free_checks += 1

    F = adjacent_minor_profile(S, D)
    assert all(v > 0 for v in F)
    finite_local_tp2_checks += 1

C_root = nodes[Fraction(1, 2)]["M"][0][0]
U_root = nodes[Fraction(1, 3)]["M"][0][0]
V_root = nodes[Fraction(2, 3)]["M"][0][0]
S_root = p_sub(U_root, C_root)
D_root = p_sub(V_root, U_root)

assert h_profile(S_root) == (40, 32, 16, 4)
assert h_profile(D_root) == (164, 138, 80, 30, 6)
assert adjacent_minor_profile(S_root, D_root) == (272, 352, 160, 24)

Delta = m_sub(nodes[Fraction(1, 3)]["M"], nodes[Fraction(1, 2)]["M"])
assert Delta == (
    ((8, 20, 16, 4), (3, 5, 2)),
    ((3, 5, 2), (1, 1)),
)
det_delta = p_sub(
    p_mul(Delta[0][0], Delta[1][1]),
    p_mul(Delta[0][1], Delta[1][0]),
)
assert det_delta == (-1, -2, -1)

R = m_mul(m_transpose(M0), Q)
rho = (3, 2)
P = [ONE, rho]
for _ in range(1, 9):
    P.append(p_sub(p_mul(rho, P[-1]), P[-2]))

boundary_chain_checks = 0
for n in range(3, 10):
    Bn = m_sub(nodes[Fraction(1, n)]["M"], nodes[Fraction(1, n - 1)]["M"])
    expected = m_scale(
        (1, 1),
        (
            (P[n - 1], P[n - 2]),
            (P[n - 2], P[n - 3]),
        ),
    )
    assert Bn == expected
    if n < 9:
        Bnext = m_sub(nodes[Fraction(1, n + 1)]["M"], nodes[Fraction(1, n)]["M"])
        assert Bnext == m_mul(R, Bn)
    boundary_chain_checks += 1

print("PASS")
print(f"farey_words={len(nodes)}")
print(f"subtraction_free_sibling_checks={subtraction_free_checks}")
print(f"finite_local_tp2_sanity_checks={finite_local_tp2_checks}")
print(f"boundary_chain_checks={boundary_chain_checks}")
print("root_HS=[40, 32, 16, 4]")
print("root_HD=[164, 138, 80, 30, 6]")
print("root_F=[272, 352, 160, 24]")
print("direct_gap_network_obstruction=det(M_1/3-M_1/2)=-(x+1)^2")
