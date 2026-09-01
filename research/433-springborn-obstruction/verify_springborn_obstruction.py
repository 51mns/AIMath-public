#!/usr/bin/env python3
"""Exact finite consistency checks for the all-k Springborn obstruction.

The universal proof is in PROOF.md. This script checks only fixed definitions
and sample cases; it does not infer universality from them.
"""
from __future__ import annotations
import argparse, json
from fractions import Fraction
from pathlib import Path
from typing import Iterable
HERE = Path(__file__).resolve().parent

def matmul(a,b):
    return [[a[0][0]*b[0][0]+a[0][1]*b[1][0],a[0][0]*b[0][1]+a[0][1]*b[1][1]],
            [a[1][0]*b[0][0]+a[1][1]*b[1][0],a[1][0]*b[0][1]+a[1][1]*b[1][1]]]

def continuant(word: Iterable[int]):
    out=[[1,0],[0,1]]
    for digit in word: out=matmul(out,[[digit,1],[1,0]])
    return out

def markov_ray(last_index,x0,x1,coefficient):
    values=[x0,x1]
    while len(values)<=last_index: values.append(coefficient*values[-1]-values[-2])
    return values

def cf_zero(word):
    tail=Fraction(word[-1],1)
    for digit in reversed(word[:-1]): tail=digit+Fraction(1,tail)
    return Fraction(1,tail)

def build_output(inputs):
    c0=list(inputs["C0"]); block=list(inputs["B"]); prefix=list(inputs["fixed_prefix_before_4"]); cases=int(inputs["verification_cases"])
    assert c0[:len(prefix)]==prefix and c0[len(prefix)]==4
    approx=cf_zero(prefix); assert approx==Fraction(75,194)
    cfg=inputs["markov_ray"]; ray=markov_ray(2+3*(cases-1),int(cfg["x0"]),int(cfg["x1"]),int(cfg["coefficient"]))
    rows=[]
    for k in range(cases):
        matrix=continuant(c0+block*k); M=ray[2+3*k]; U=matrix[0][1]
        assert matrix[0][0]==M and 0<U<M
        cross=abs(approx.denominator*U-approx.numerator*M)
        scaled=Fraction(approx.denominator*cross,M)
        assert scaled<Fraction(1,4) and 4*approx.denominator*cross<M
        rows.append({"k":k,"M":M,"U":U,"cross_difference_abs_194U_minus_75M":cross,
                     "scaled_witness_numerator":scaled.numerator,"scaled_witness_denominator":scaled.denominator})
    return {"claim_id":inputs["claim_id"],"proof_scope":"finite exact consistency only; universal proof is PROOF.md",
            "fixed_convergent":{"numerator":75,"denominator":194},"proved_uniform_upper_bound":"C(U_k/M_k) < 1/4","cases":rows}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--inputs",type=Path,default=HERE/"inputs.json"); args=p.parse_args()
    out=build_output(json.loads(args.inputs.read_text(encoding="utf-8")))
    print(json.dumps(out,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
