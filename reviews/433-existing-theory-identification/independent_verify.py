#!/usr/bin/env python3
"""Independent exact verifier; imports no writer module or expected output."""
from fractions import Fraction
import json, math
A=1299
C0=(2,1,1,2,2,1,1,2,4,1,1,3,3,1,1,4,2,1,1,2,2,1,1,2)
B=(2,1,1,1,1,2,2,1,1,2,2,1,1,2,4,1,1,3,3,1,1,4,2,1,1,2,2,1,1,2)
def mm(X,Y): return ((X[0][0]*Y[0][0]+X[0][1]*Y[1][0],X[0][0]*Y[0][1]+X[0][1]*Y[1][1]),(X[1][0]*Y[0][0]+X[1][1]*Y[1][0],X[1][0]*Y[0][1]+X[1][1]*Y[1][1]))
def det(X): return X[0][0]*X[1][1]-X[0][1]*X[1][0]
def K(w):
    R=((1,0),(0,1))
    for a in w: R=mm(R,((a,1),(1,0)))
    return R
def initial():
    A0=((0,1),(-1,3)); B0=((1,2),(2,5)); C12=mm(A0,B0); C23=mm(C12,B0); C35=mm(C12,C23)
    return C12,C23,C35
def source(n):
    _,C,S=initial()
    for _ in range(n): C=mm(S,C)
    return C
def xs(nmax):
    x=[29,37666]
    while len(x)<=nmax: x.append(A*x[-1]-x[-2])
    return x
def audit(cases=11):
    C12,C23,S=initial(); assert C12==((2,5),(5,13)) and C23==((12,29),(31,75)) and S==((179,433),(463,1120))
    assert det(S)==1 and S[0][0]+S[1][1]==1299
    seq=xs(2+3*(cases-1)); rows=[]
    for k in range(cases):
        n=2+3*k; M=seq[n]; Y=seq[n-1]; U=K(C0+B*k)[0][1]
        p,q=source(n)[0]; pp,qp=source(n-1)[0]
        assert q==M and pp*M-p*qp==433
        N=M//5; r=(433*pow(Y,-1,M))%M
        assert M%25==5 and N%5==1 and math.gcd(5,N)==1
        assert Y%5==1 and U%5==2 and (Y*U-433)%N==0
        assert r==M-p and U==r-N
        assert 5*p==4*M-5*U and Fraction(U,M)==Fraction(4,5)-Fraction(p,M)
        rows.append({"k":k,"M":M,"U":U,"p":p,"cross":433,"identity":True})
    # Negative controls from the fixed review.
    reverse=mm(C23,S); correct=mm(S,C23)
    assert correct[0][1]==37666 and reverse[0][1]!=37666
    r0=rows[0]; assert 5*r0["p"] != 4*r0["M"]-5*(r0["U"]+1)
    return {"cases":rows,"negative_controls_pass":True}
if __name__=="__main__": print(json.dumps(audit(),indent=2,sort_keys=True))
