#!/usr/bin/env python3
"""Independent exact audit of the fixed-433 Springborn obstruction.

No writer module or generated expected output is imported.
"""
from fractions import Fraction
from math import gcd
import json
C0=(2,1,1,2,2,1,1,2,4,1,1,3,3,1,1,4,2,1,1,2,2,1,1,2)
B=(2,1,1,1,1,2,2,1,1,2,2,1,1,2,4,1,1,3,3,1,1,4,2,1,1,2,2,1,1,2)
PREFIX=C0[:8]
def convs(word):
    a=(0,)+tuple(word); p2,p1=0,1; q2,q1=1,0; out=[]
    for d in a:
        p=d*p1+p2; q=d*q1+q2; out.append((p,q)); p2,p1=p1,p; q2,q1=q1,q
    return out
def cf0(word):
    t=Fraction(word[-1],1)
    for d in reversed(word[:-1]): t=d+Fraction(1,t)
    return 1/t
def cq(word):
    t=Fraction(word[-1],1)
    for d in reversed(word[:-1]): t=d+Fraction(1,t)
    return t
def cont(word):
    p2,p1=0,1; q2,q1=1,0
    for d in word:
        p=d*p1+p2; q=d*q1+q2; p2,p1=p1,p; q2,q1=q1,q
    return p1,q1
def ray(last):
    x=[29,37666]
    while len(x)<=last: x.append(1299*x[-1]-x[-2])
    return x
def audit(cases=7):
    assert PREFIX==(2,1,1,2,2,1,1,2) and C0[8]==4
    cs=convs(PREFIX); (p,q),(pp,qq)=cs[-1],cs[-2]
    assert (p,q)==(75,194) and (pp,qq)==(29,75) and p*qq-pp*q==-1 and gcd(p,q)==1
    r=ray(2+3*(cases-1)); rows=[]
    for k in range(cases):
        word=C0+B*k; M_cf,U=cont(word); M=r[2+3*k]; assert M_cf==M
        x=Fraction(U,M); assert x==cf0(word) and x!=Fraction(75,194)
        t=cq(word[8:]); assert t>4
        assert Fraction(75*t+29,194*t+75)==x
        scaled=194*194*abs(x-Fraction(75,194)); assert scaled==Fraction(194,1)/(194*t+75) and scaled<Fraction(1,4)
        rows.append({"k":k,"M":M,"U":U,"scaled_lt_1_4":True})
    return {"prefix_convergent":[75,194],"previous_convergent":[29,75],"cases":rows}
if __name__=="__main__": print(json.dumps(audit(),indent=2,sort_keys=True))
