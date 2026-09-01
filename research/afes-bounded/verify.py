#!/usr/bin/env python3
"""Small independent public witness checker for the accepted AFES bounded surface.

This is not the full private AFES implementation and does not claim strict JSON
scalar canonicality. It verifies the fixed exact semantic witnesses only.
"""
from fractions import Fraction
from math import factorial

def poly_reduce(poly, relation):
    # ascending coefficients; relation is monic ascending.
    p=[Fraction(x) for x in poly]; r=[Fraction(x) for x in relation]
    while len(p)>=len(r):
        c=p[-1]
        if c:
            shift=len(p)-len(r)
            for i,x in enumerate(r): p[i+shift]-=c*x
        while len(p)>1 and p[-1]==0: p.pop()
    return p

def leibniz_partial(m):
    return sum((Fraction((-1)**n,2*n+1) for n in range(m+1)),Fraction(0))

def exp_minus_one_partial(m):
    return sum((Fraction((-1)**n,factorial(n)) for n in range(m+1)),Fraction(0))

def alternating_interval(partial_m,next_term_signed):
    other=partial_m+next_term_signed
    return min(partial_m,other),max(partial_m,other)

def main():
    # Rational witness.
    assert Fraction(1,3)*3==1

    # Algebraic relation reductions in one generator.
    # sqrt2: x^2-2=0 => x^2-2 reduces to zero.
    assert poly_reduce([-2,0,1],[-2,0,1])==[Fraction(0)]
    # i: x^2+1=0.
    assert poly_reduce([1,0,1],[1,0,1])==[Fraction(0)]
    # phi: x^2-x-1=0 => phi^2-(phi+1)=0.
    assert poly_reduce([-1,-1,1],[-1,-1,1])==[Fraction(0)]

    # pi = 4 * Leibniz alternating series. Consecutive partial sums enclose it.
    m=6
    s=leibniz_partial(m)
    nxt=Fraction((-1)**(m+1),2*(m+1)+1)
    lo,hi=alternating_interval(s,s*0+nxt)
    pi_lo,pi_hi=4*lo,4*hi
    assert Fraction(3)<pi_lo<pi_hi<Fraction(4)

    # e is represented as reciprocal of sum (-1)^n/n! = e^-1.
    m=4
    s=exp_minus_one_partial(m)
    nxt=Fraction((-1)**(m+1),factorial(m+1))
    lo,hi=alternating_interval(s,nxt)
    assert lo>0

    # A mixed composite such as pi+e is a finite expression tree even though
    # AFES does not claim total cross-family equality reduction.
    pi_spec={"kind":"mul","args":[{"kind":"rat","value":[4,1]},{"kind":"alt_series","name":"Leibniz"}]}
    e_spec={"kind":"div","args":[{"kind":"rat","value":[1,1]},{"kind":"alt_series","name":"exp(-1)"}],"nonzero_cert":"positive_interval"}
    composite={"kind":"add","args":[pi_spec,e_spec]}
    assert composite["kind"]=="add" and len(composite["args"])==2

    print('AFES fixed semantic witnesses: PASS')
    print('pi exact enclosure:',pi_lo,pi_hi)
    print('exp(-1) denominator exact positive enclosure:',lo,hi)
    print('strict scalar canonical encoding: NOT CLAIMED')
if __name__=='__main__': main()
