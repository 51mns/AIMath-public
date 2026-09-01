#!/usr/bin/env python3
"""Exact stdlib verifier for C-EQUIANGULAR-R18-ETA17-SINGLETON-EXCLUSION."""
from math import comb

def mul(a,b):
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j]+=x*y
    return c

def ppow(a,n):
    r=[1]
    while n:
        if n&1: r=mul(r,a)
        a=mul(a,a); n//=2
    return r

def shift_minus_one(p):
    q=[0]*len(p)
    for k,pk in enumerate(p):
        for j in range(k+1): q[j]+=pk*comb(k,j)*((-1)**(k-j))
    return q

def deriv(p): return [(i+1)*p[i+1] for i in range(len(p)-1)]
def div_exact(a,b):
    a=a[:]; q=[0]*(len(a)-len(b)+1); db=len(b)-1
    while len(a)>=len(b):
        d=len(a)-len(b); lead=a[-1]//b[-1]; q[d]=lead
        for i,v in enumerate(b): a[i+d]-=lead*v
        while a and a[-1]==0: a.pop()
    assert not a
    return q

def endpoint_candidates():
    out=[]
    for A in range(-3249,-3234):
        lo=max(5*A-18675,-10*A-25200,-13*A-34983)
        hi=min(-9*A-21951,-11*A-28435)
        for B in range(lo,hi+1): out.append((A,B))
    return out

def type2(A,B,F):
    Q=[B,A,532,-38,1]
    shifted=shift_minus_one(mul(F,Q)); n=len(shifted)-1
    return all(shifted[n-j]%(1<<j)==0 for j in range(n+1))

def desc(p): return list(reversed(p))
def main():
    F=mul(mul(ppow([5,1],40),ppow([-9,1],5)),ppow([-13,1],9))
    cands=endpoint_candidates(); assert len(cands)==64
    survivors=[c for c in cands if type2(c[0],c[1],F)]
    assert survivors==[(-3242,7227)]
    Q0=[7227,-3242,532,-38,1]
    # Factorisation (x-9)(x-11)(x^2-18x+73).
    assert Q0==mul(mul([-9,1],[-11,1]),[73,-18,1])
    p=mul(mul(mul(mul(ppow([5,1],41),ppow([-9,1],6)),[-10,1]),[-11,1]),ppow([-13,1],10))
    ratio=div_exact(deriv(p),F); fiftynine=[59*x for x in Q0]
    diff=[ratio[i]-fiftynine[i] for i in range(5)]
    assert desc(ratio)==[59,-2242,31388,-190974,422985]
    assert desc(fiftynine)==[59,-2242,31388,-191278,426393]
    assert diff==[-3408,304,0,0,0]
    # Negative controls.
    assert (-3242,7226) in cands and not type2(-3242,7226,F)
    spectrum=[-5]*41+[9]*6+[10,11]+[13]*10
    assert sum(spectrum)==0 and sum(x*x for x in spectrum)==59*58
    bad=spectrum[:]; bad[41]=10; bad[-1]=12
    assert sum(bad)==0 and sum(x*x for x in bad)!=59*58
    print('R18 eta17: endpoint candidates=64; unique type2 quartic=(-3242,7227)')
    print('deck mismatch = 304*x - 3408 = 16*(19*x-213)')
    print('R18 eta17 public reproduction: PASS')
if __name__=='__main__': main()
