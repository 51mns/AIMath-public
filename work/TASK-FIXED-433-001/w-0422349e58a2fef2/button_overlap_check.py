# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
"""Finite exact diagnostic for TASK-FIXED-433-001.

This script compares J. O. Button's 2001 root-representative formula
x = 3c - 2 b alpha (alpha = a^{-1} mod c, x defined modulo 2c)
with the public AIMath fixed-433 identity 5p + 5U = 4M.

The calculation is only a finite fingerprint for k=0,1,2.  It does not prove
that the two constructions are distinct for every k and it does not establish
publication novelty.  The conceptual literature boundary is recorded in
LITERATURE_AUDIT.md.
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


def button_representative(a: int, b: int, c: int) -> int:
    """Choose the representative of Button's x class in c < x <= 3c.

    Button defines x modulo 2c by x = 3c - 2 b alpha, where alpha is the
    inverse of a modulo c.  Adding 2c selects the same residue class in the
    displayed interval when necessary.
    """
    alpha = pow(a, -1, c)
    x = (3 * c - 2 * b * alpha) % (2 * c)
    if x <= c:
        x += 2 * c
    assert c < x <= 3 * c
    return x


def build():
    values = ray(8)
    rows = []
    for k in range(3):
        n = 2 + 3 * k
        m = values[n]
        y = values[n - 1]
        word = CONTINUANT_BASE + CONTINUANT_STEP * k
        m_from_continuant, u = continuant(word)[0]
        p, m_from_cohn = cohn(n)[0]

        assert m == m_from_continuant == m_from_cohn
        assert 433**2 + y**2 + m**2 == 3 * 433 * y * m
        assert 5 * p + 5 * u == 4 * m

        # Button's construction for (a,b,c) and the swapped (b,a,c).
        bx = button_representative(433, y, m)
        bx_swap = button_representative(y, 433, m)
        assert bx + bx_swap == 4 * m

        same_pair = {bx, bx_swap} == {5 * p, 5 * u}
        assert not same_pair
        rows.append(
            {
                "k": k,
                "M": m,
                "Y": y,
                "U": u,
                "p": p,
                "button_pair": [bx, bx_swap],
                "aimath_scaled_pair": [5 * p, 5 * u],
                "button_pair_sum": bx + bx_swap,
                "aimath_scaled_pair_sum": 5 * p + 5 * u,
                "common_sum": 4 * m,
                "pairs_equal": same_pair,
            }
        )
    return {
        "task_id": "TASK-FIXED-433-001",
        "scope": "finite exact diagnostic only; k=0,1,2",
        "result": "BUTTON_ROOT_PAIR_DIFFERS_FROM_AIMATH_SCALED_PAIR_IN_TESTED_CASES",
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
