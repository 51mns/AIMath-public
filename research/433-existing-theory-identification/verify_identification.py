#!/usr/bin/env python3
"""Exact finite consistency checker for the fixed-433 identification.

Finite rows are regression fingerprints; the all-k proof is in PROOF.md.
"""
from __future__ import annotations
from fractions import Fraction
import json
A=1299
C0=(2,1,1,2,2,1,1,2,4,1,1,3,3,1,1,4,2,1,1,2,2,1,1,2)
B=(2,1,1,1,1,2,2,1,1,2,2,1,1,2,4,1,1,3,3,1,1,4,2,1,1,2,2,1,1,2)
S=((179,433),(463,1120)); T0=((12,29),(31,75))
def mm(X,Y): return ((X[0][0]*Y[0][0]+X[0][1]*Y[1][0],X[0][0]*Y[0][1]+X[0][1]*Y[1][1]),(X[1][0]*Y[0][0]+X[1][1]*Y[1][0],X[1][0]*Y[0][1]+X[1][1]*Y[1][1]))
def det(X): return X[0][0]*X[1][1]-X[0][1]*X[1][0]
def K(w):
    R=((1,0),(0,1))
    for d in w: R=mm(R,((d,1),(1,0)))
    return R
def mpow(X,n):
    R=((1,0),(0,1))
    while n:
        if n&1: R=mm(R,X)
        X=mm(X,X); n//=2
    return R
def ray(nmax):
    x=[29,37666]
    while len(x)<=nmax: x.append(A*x[-1]-x[-2])
    return x
def C(n): return mm(mpow(S,n),T0)
def build(cases=11):
    xs=ray(2+3*(cases-1)); rows=[]
    assert det(S)==1 and S[0][0]+S[1][1]==1299
    for k in range(cases):
        n=2+3*k; W=K(C0+B*k); M,U=W[0]; Y=xs[n-1]; assert M==xs[n]
        p,q=C(n)[0]; pp,qp=C(n-1)[0]; assert q==M and pp*M-p*qp==433
        N=M//5; r=(433*pow(Y,-1,M))%M
        assert M%25==5 and N%5==1 and Y%5==1 and U%5==2
        assert (Y*U-433)%N==0 and r==M-p
        assert U==r-N and 5*p==4*M-5*U
        assert Fraction(U,M)==Fraction(4,5)-Fraction(p,M)
        rows.append({"k":k,"farey_label":f"{9*k+8}/{15*k+13}","M":M,"U":U,"p":p,"r":r,"identity":True})
    return {"claim_id":"C-433-EXISTING-THEORY-IDENTIFICATION","scope":"finite exact consistency only","cases":rows}
if __name__=="__main__": print(json.dumps(build(),indent=2,sort_keys=True))
