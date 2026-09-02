# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0

"""Exact symbolic checker for TASK-DITTERT-N5-002.

This checker independently reconstructs the seven-parameter Dittert functional
as a sparse multivariate polynomial, differentiates it exactly, and verifies
the polynomial identities used in the fresh stationarity contradiction.

It does not decide positivity by sampling: the order argument remains in the
human proof, while all algebraic identities used there are checked exactly.
"""

from fractions import Fraction
from itertools import permutations


class Poly:
    N = 7

    def __init__(self, terms=None):
        self.terms = {}
        if terms:
            for mon, coeff in terms.items():
                coeff = Fraction(coeff)
                if coeff:
                    self.terms[tuple(mon)] = coeff

    @classmethod
    def const(cls, value):
        return cls({(0,) * cls.N: Fraction(value)})

    @classmethod
    def var(cls, index):
        mon = [0] * cls.N
        mon[index] = 1
        return cls({tuple(mon): Fraction(1)})

    def __add__(self, other):
        other = as_poly(other)
        out = dict(self.terms)
        for mon, coeff in other.terms.items():
            out[mon] = out.get(mon, Fraction(0)) + coeff
            if out[mon] == 0:
                del out[mon]
        return Poly(out)

    __radd__ = __add__

    def __neg__(self):
        return Poly({m: -c for m, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-as_poly(other))

    def __rsub__(self, other):
        return as_poly(other) - self

    def __mul__(self, other):
        other = as_poly(other)
        out = {}
        for m1, c1 in self.terms.items():
            for m2, c2 in other.terms.items():
                mon = tuple(x + y for x, y in zip(m1, m2))
                out[mon] = out.get(mon, Fraction(0)) + c1 * c2
        return Poly({m: c for m, c in out.items() if c})

    __rmul__ = __mul__

    def __pow__(self, power):
        if power < 0:
            raise ValueError("negative powers are not supported")
        result = Poly.const(1)
        base = self
        p = power
        while p:
            if p & 1:
                result = result * base
            base = base * base
            p >>= 1
        return result

    def derivative(self, index):
        out = {}
        for mon, coeff in self.terms.items():
            if mon[index]:
                new_mon = list(mon)
                factor = new_mon[index]
                new_mon[index] -= 1
                out[tuple(new_mon)] = coeff * factor
        return Poly(out)

    def __eq__(self, other):
        return self.terms == as_poly(other).terms

    def assert_equal(self, other, label):
        other = as_poly(other)
        diff = self - other
        if diff.terms:
            raise AssertionError(f"{label}: {diff.terms}")


def as_poly(value):
    return value if isinstance(value, Poly) else Poly.const(value)


def product(items):
    ans = Poly.const(1)
    for item in items:
        ans *= item
    return ans


def permanent(matrix):
    n = len(matrix)
    ans = Poly.const(0)
    for perm in permutations(range(n)):
        ans += product(matrix[i][perm[i]] for i in range(n))
    return ans


def minor(matrix, i, j):
    return [
        [entry for jj, entry in enumerate(row) if jj != j]
        for ii, row in enumerate(matrix)
        if ii != i
    ]


def phi_ij(matrix, rows, cols, i, j):
    return (
        product(rows[k] for k in range(5) if k != i)
        + product(cols[k] for k in range(5) if k != j)
        - permanent(minor(matrix, i, j))
    )


def main():
    # Variable order: u, v, w, alpha, beta, gamma, g.
    u, v, w, alpha, beta, gamma, g = [Poly.var(i) for i in range(7)]

    a = u + alpha
    c = u - alpha
    b = v - beta
    d = v + beta
    e = w + gamma
    f = w - gamma

    matrix = [
        [0, a, b, b, b],
        [c, 0, d, d, d],
        [e, f, g, g, g],
        [e, f, g, g, g],
        [e, f, g, g, g],
    ]
    rows = [sum(row, Poly.const(0)) for row in matrix]
    cols = [sum((matrix[i][j] for i in range(5)), Poly.const(0)) for j in range(5)]
    Phi = product(rows) + product(cols) - permanent(matrix)

    P_w = 27*g**3 + 48*g**2*w + 36*g*w**2 + 8*w**3
    P_v = 27*g**3 + 48*g**2*v + 36*g*v**2 + 8*v**3
    C_w = 27*g**3 + 54*g**2*w + 32*g*w**2 + 8*w**3
    C_v = 27*g**3 + 54*g**2*v + 32*g*v**2 + 8*v**3

    dbeta_expected = (
        6*P_w*alpha
        - 18*C_w*beta
        - 36*g**2*u*gamma
        - 72*g*beta*gamma**2
    )
    dgamma_expected = (
        6*P_v*alpha
        - 36*g**2*u*beta
        - 18*C_v*gamma
        - 72*g*beta**2*gamma
    )

    Phi.derivative(4).assert_equal(dbeta_expected, "dPhi/dbeta")
    Phi.derivative(5).assert_equal(dgamma_expected, "dPhi/dgamma")

    phib = phi_ij(matrix, rows, cols, 0, 2)
    phid = phi_ij(matrix, rows, cols, 1, 2)
    phie = phi_ij(matrix, rows, cols, 2, 0)
    phif = phi_ij(matrix, rows, cols, 2, 1)
    Phi.derivative(4).assert_equal(3*(phid-phib), "beta derivative / positive stationarity")
    Phi.derivative(5).assert_equal(3*(phie-phif), "gamma derivative / positive stationarity")

    phi11 = phi_ij(matrix, rows, cols, 0, 0)
    phi12 = phi_ij(matrix, rows, cols, 0, 1)
    phi22 = phi_ij(matrix, rows, cols, 1, 1)
    phi21 = phi_ij(matrix, rows, cols, 1, 0)
    chamber_lhs = phi11 - phi12 + phi22 - phi21
    chamber_lhs.assert_equal(12*g**2*(u*g + 6*beta*gamma), "zero-entry chamber identity")

    # A second exact ring for the sign certificates, using variable order
    # u, v, w, x, y, dummy, g. The unused sixth variable keeps Poly.N fixed.
    U, V, W, X, Y, _, G = [Poly.var(i) for i in range(7)]
    H = 6*X*Y - U*G
    CW = 27*G**3 + 54*G**2*W + 32*G*W**2 + 8*W**3
    CV = 27*G**3 + 54*G**2*V + 32*G*V**2 + 8*V**3

    B_plus = CW*X - 2*G**2*U*Y + 4*G*X*Y**2
    B_plus_cert = X*(CW - 8*G*Y**2) + 2*G*Y*H
    B_plus.assert_equal(B_plus_cert, "alpha-positive certificate")

    minus_B_minus = CV*Y + 4*G*X**2*Y - 2*G**2*U*X
    minus_B_minus_cert = Y*(CV - 8*G*X**2) + 2*G*X*H
    minus_B_minus.assert_equal(minus_B_minus_cert, "alpha-negative certificate")

    CW_minus = CW - 8*G*Y**2
    CW_positive_decomp = (
        27*G**3 + 54*G**2*W + 24*G*W**2 + 8*W**3
        + 8*G*(W-Y)*(W+Y)
    )
    CW_minus.assert_equal(CW_positive_decomp, "Cw positivity decomposition")

    CV_minus = CV - 8*G*X**2
    CV_positive_decomp = (
        27*G**3 + 54*G**2*V + 24*G*V**2 + 8*V**3
        + 8*G*(V-X)*(V+X)
    )
    CV_minus.assert_equal(CV_positive_decomp, "Cv positivity decomposition")

    print("PASS: exact universal stationarity-contradiction identities")


if __name__ == "__main__":
    main()
