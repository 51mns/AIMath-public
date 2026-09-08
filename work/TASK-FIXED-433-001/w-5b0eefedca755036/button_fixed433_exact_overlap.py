# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
"""Exact finite regression for the Button-2001 / fixed-433 placement audit.

The universal correspondence is proved algebraically in LITERATURE_AUDIT.md.
This script checks k=0..10 only as exact integer fingerprints; it is not the
universal proof and it is not a novelty test.
"""
from __future__ import annotations

import json

TRACE = 1299
S = ((179, 433), (463, 1120))
T0 = ((12, 29), (31, 75))
CONTINUANT_BASE = (
    2, 1, 1, 2, 2, 1, 1, 2, 4, 1, 1, 3,
    3, 1, 1, 4, 2, 1, 1, 2, 2, 1, 1, 2,
)
CONTINUANT_STEP = (
    2, 1, 1, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 4,
    1, 1, 3, 3, 1, 1, 4, 2, 1, 1, 2, 2, 1, 1, 2,
)


def mm(x, y):
    return (
        (
            x[0][0] * y[0][0] + x[0][1] * y[1][0],
            x[0][0] * y[0][1] + x[0][1] * y[1][1],
        ),
        (
            x[1][0] * y[0][0] + x[1][1] * y[1][0],
            x[1][0] * y[0][1] + x[1][1] * y[1][1],
        ),
    )


def mpow(x, n):
    out = ((1, 0), (0, 1))
    while n:
        if n & 1:
            out = mm(out, x)
        x = mm(x, x)
        n //= 2
    return out


def cohn(n):
    return mm(mpow(S, n), T0)


def continuant(word):
    out = ((1, 0), (0, 1))
    for digit in word:
        out = mm(out, ((digit, 1), (1, 0)))
    return out


def ray(nmax):
    values = [29, 37666]
    while len(values) <= nmax:
        values.append(TRACE * values[-1] - values[-2])
    return values


def button_x(a: int, b: int, c: int) -> int:
    """Button p.85 representative, normalised by c < x <= 3c.

    The source defines x modulo 2c by x = 3c - 2*b*alpha, where alpha is
    the inverse of a modulo c.  This routine selects the p.87 purely-periodic
    representative interval.
    """
    alpha = pow(a, -1, c)
    x = (3 * c - 2 * b * alpha) % (2 * c)
    if x <= c:
        x += 2 * c
    assert c < x <= 3 * c
    return x


def build(cases: int = 11):
    values = ray(2 + 3 * (cases - 1))
    rows = []
    for k in range(cases):
        n = 2 + 3 * k
        m = values[n]
        y = values[n - 1]
        m_cont, u = continuant(CONTINUANT_BASE + CONTINUANT_STEP * k)[0]
        p, m_cohn = cohn(n)[0]

        assert m == m_cont == m_cohn
        assert 433**2 + y**2 + m**2 == 3 * 433 * y * m
        assert m % 25 == 5

        r = (433 * pow(y, -1, m)) % m
        x = button_x(433, y, m)
        x_swap = button_x(y, 433, m)
        assert (x - m) % 2 == 0
        assert (x_swap - m) % 2 == 0
        t = (x - m) // 2
        t_swap = (x_swap - m) // 2

        # Exact finite fingerprints of the all-k algebra in LITERATURE_AUDIT.md.
        assert x + x_swap == 4 * m
        assert t == r
        assert t_swap == p
        assert t + t_swap == m

        # This is the separate AIMath factor-5 step; no Button source match is
        # asserted by this checker.
        assert u == r - m // 5
        assert 5 * p + 5 * u == 4 * m

        rows.append(
            {
                "k": k,
                "M": m,
                "Y": y,
                "U": u,
                "p": p,
                "r": r,
                "button_x": x,
                "button_x_swapped": x_swap,
                "button_t": t,
                "button_t_swapped": t_swap,
                "button_pair_exactly_r_p": True,
                "aimath_factor5_shift": True,
            }
        )

    return {
        "task_id": "TASK-FIXED-433-001",
        "worker_id": "w-5b0eefedca755036",
        "scope": "finite exact regression only; universal argument is in LITERATURE_AUDIT.md",
        "cases": rows,
    }


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
