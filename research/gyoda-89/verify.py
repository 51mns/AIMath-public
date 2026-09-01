#!/usr/bin/env python3
"""Exact privacy-safe verifier for C-GYODA-89.

Checks the fixed 89 collision and the modulo-10 recurrence classes. No floating
point and no private archive import is used.
"""
from __future__ import annotations
import json

def mm(A,B):
    return ((A[0][0]*B[0][0]+A[0][1]*B[1][0],A[0][0]*B[0][1]+A[0][1]*B[1][1]),
            (A[1][0]*B[0][0]+A[1][1]*B[1][0],A[1][0]*B[0][1]+A[1][1]*B[1][1]))
def sub(A,B): return tuple(tuple(A[i][j]-B[i][j] for j in range(2)) for i in range(2))
def det(A): return A[0][0]*A[1][1]-A[0][1]*A[1][0]
def delta(x,y,z): return x*x+y*y+z*z+6*y*z-9*x*y*z

def fixed_collision():
    k3=6; K=9
    def D3(): return ((k3,k3*K),(0,k3))
    C0=((9,-55),(1,-6)); C1=((17,8),(2,1))
    C12=mm(C0,C1); C13=mm(C0,C12); C14=mm(C0,C13); C15=mm(C0,C14)
    C23=sub(mm(C12,C1),D3())
    assert C12==((43,17),(5,2)); assert C13==((112,43),(13,5)); assert C14==((293,112),(34,13))
    assert C15==((767,293),(89,34)); assert C23==((759,307),(89,36))
    assert det(C15)==det(C23)==1 and C15[1][0]==C23[1][0]==89
    assert delta(1,89,34)==0 and delta(89,2,5)==0
    return {"C_1_5":C15,"C_2_3":C23,"common_number":89}

def recurrence_values(nmax):
    a=[None,2,5]
    for m in range(2,nmax): a.append(3*a[-1]-a[-2])
    return a

def residue_classes():
    a=recurrence_values(61)
    classes=[m for m in range(1,31) if a[m]%10==9]
    assert classes==[5,14,15,24]
    # State returns after 30 steps.
    assert (a[31]%10,a[32]%10)==(a[1]%10,a[2]%10)
    first={m:(a[m],(a[m]-29)//10) for m in classes}
    assert first[5]==(89,6); assert first[14]==(514229,51420); assert first[15]==(1346269,134624); assert first[24]==(7778742049,777874202)
    for m,(am,k) in first.items(): assert am==10*k+29 and k>=0
    # Two representatives per class, using recurrence only.
    a2=recurrence_values(85)
    for c in classes:
        for m in (c,c+30): assert a2[m]%10==9 and (a2[m]-29)%10==0
    return {"classes_mod_30":classes,"first":{str(m):{"a_m":v[0],"k":v[1]} for m,v in first.items()}}

def main():
    out={"claim_id":"C-GYODA-89","fixed_collision":fixed_collision(),"families":residue_classes(),
         "scope":"exact collision plus recurrence/mod-10 family mechanism; no author correspondence"}
    print(json.dumps(out,indent=2,sort_keys=True,default=list)); return 0
if __name__=="__main__": raise SystemExit(main())
