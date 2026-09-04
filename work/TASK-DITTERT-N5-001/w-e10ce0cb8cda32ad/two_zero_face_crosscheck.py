#!/usr/bin/env python3
"""Writer-side exact cross-check for the external Dittert n=5 two-zero-face reduction.

This does NOT verify the external SOS/Gram certificate.  It independently
reconstructs only the combinatorial polynomial identity used before the
certificate.
"""
from fractions import Fraction
import itertools
import json
import math

N = 5
FORBIDDEN = {(0, 0), (1, 1)}
ALLOWED = [(i, j) for i in range(N) for j in range(N) if (i, j) not in FORBIDDEN]


def permanent(matrix):
    return sum(
        math.prod(matrix[i][perm[i]] for i in range(N))
        for perm in itertools.permutations(range(N))
    )


def build_edges():
    edges = set()
    row_edges = set()
    col_edges = set()
    for support in itertools.combinations(range(len(ALLOWED)), N):
        cells = [ALLOWED[v] for v in support]
        if len({i for i, _ in cells}) == N:
            row_edges.add(support)
        if len({j for _, j in cells}) == N:
            col_edges.add(support)
        if support in row_edges or support in col_edges:
            edges.add(support)
    return row_edges, col_edges, edges


def evaluate_identity(point, edges):
    matrix = [[0] * N for _ in range(N)]
    for value, (i, j) in zip(point, ALLOWED):
        matrix[i][j] = value
    lhs = math.prod(map(sum, matrix))
    lhs += math.prod(sum(matrix[i][j] for i in range(N)) for j in range(N))
    lhs -= permanent(matrix)
    rhs = sum(math.prod(point[v] for v in edge) for edge in edges)
    return lhs, rhs


def main():
    row_edges, col_edges, edges = build_edges()
    assert len(ALLOWED) == 23
    assert len(row_edges) == 2000
    assert len(col_edges) == 2000
    assert len(row_edges & col_edges) == 78
    assert len(edges) == 3922
    assert math.comb(len(ALLOWED) + 4, 5) == 80730

    # The external note's normalization:
    # Phi(A)=5^5 F(A/5), and Phi(J_5)=6130/3125.
    assert Fraction(6130, 3125) / (5**5) == Fraction(1226, 5**9)

    points = [
        tuple([1] * len(ALLOWED)),
        tuple((3 * i + 1) % 5 for i in range(len(ALLOWED))),
        tuple((i * i + 2 * i + 3) % 7 for i in range(len(ALLOWED))),
        tuple((5 * i + 2) % 11 for i in range(len(ALLOWED))),
        tuple((7 * i * i + i + 4) % 13 for i in range(len(ALLOWED))),
    ]
    evaluations = []
    for idx, point in enumerate(points):
        lhs, rhs = evaluate_identity(point, edges)
        assert lhs == rhs
        evaluations.append({"case": idx, "value": lhs})

    print(json.dumps({
        "status": "WRITER_CROSSCHECK_PASS",
        "scope": "combinatorial two-zero-face identity only; SOS certificate not checked",
        "allowed_variables": len(ALLOWED),
        "row_transversals": len(row_edges),
        "column_transversals": len(col_edges),
        "allowed_permutation_transversals": len(row_edges & col_edges),
        "quintic_hyperedges": len(edges),
        "degree5_monomials_23vars": math.comb(len(ALLOWED) + 4, 5),
        "exact_evaluation_cases": evaluations,
    }, indent=2))


if __name__ == "__main__":
    main()
