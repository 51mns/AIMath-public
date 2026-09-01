#!/usr/bin/env python3
from fractions import Fraction

def tm(n): return n.bit_count() & 1
def eps(n): return -1 if tm(n) else 1

def finite_product(K):
    # coefficients of product_(k<K)(1-x^(2^k))
    c=[1]
    for k in range(K):
        m=1<<k; d=[0]*(m+1); d[0]=1; d[m]=-1
        out=[0]*(len(c)+len(d)-1)
        for i,a in enumerate(c):
            for j,b in enumerate(d): out[i+j]+=a*b
        c=out
    return c

def prefix(N):
    return sum((Fraction(tm(n),1<<(n+1)) for n in range(N)), Fraction(0))

def decimal_floor(frac,digits):
    scale=10**digits
    return (frac.numerator*scale)//frac.denominator

def main():
    for K in range(1,11):
        c=finite_product(K)
        assert c==[eps(n) for n in range(1<<K)]
        N=1<<K
        Pk=sum((Fraction(eps(n),1<<n) for n in range(N)), Fraction(0))
        Ck=prefix(N)
        assert Ck==Fraction(1,2)*(1-Fraction(1,1<<N))-Fraction(1,4)*Pk
    N=900
    C=prefix(N); tail=Fraction(1,1<<N)
    assert tail < Fraction(1,10**250)
    lo=decimal_floor(C,250); hi=decimal_floor(C+tail,250)
    assert lo==hi
    s=str(lo).rjust(251,'0')
    print('certified_250_digits=0.'+s[-250:])
    print('tail_bound=2^(-900)')
    print('Thue-Morse rediscovery public reproduction: PASS')
if __name__=='__main__': main()
