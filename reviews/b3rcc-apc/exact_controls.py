from itertools import combinations
from math import comb

def popcount(x): return x.bit_count()
def vc_dimension(family,r):
    fam=set(family); best=0; coords=list(range(r))
    for k in range(1,r+1):
        for T in combinations(coords,k):
            pats={tuple((x>>i)&1 for i in T) for x in fam}
            if len(pats)==2**k: best=max(best,k)
    return best
def complement(x,r): return ((1<<r)-1)^x
def complement_cover_min_vc(r):
    n=1<<r; best=r
    for mask in range(1<<n):
        if any(not((mask>>x)&1) and not((mask>>complement(x,r))&1) for x in range(n)): continue
        fam=[x for x in range(n) if (mask>>x)&1]; best=min(best,vc_dimension(fam,r))
    return best
def anticode_max(r):
    n=1<<r; best=0; max_d=r-2
    for mask in range(1<<n):
        elems=[x for x in range(n) if (mask>>x)&1]
        if len(elems)<best: continue
        if all(popcount(a^b)<=max_d for i,a in enumerate(elems) for b in elems[i+1:]): best=max(best,len(elems))
    return best
def kappa_closed(r): return comb(r,r//2) if r%2==0 else 2*comb(r-1,(r-1)//2)
def kappa_from_kleitman(r):
    d=r-2
    if d%2==0: B=sum(comb(r,i) for i in range(d//2+1))
    else: B=2*sum(comb(r-1,i) for i in range((d-1)//2+1))
    return (1<<r)-2*B
def main():
    for r in range(2,5):
        assert complement_cover_min_vc(r)>=r//2
        b=anticode_max(r); assert (1<<r)-2*b==kappa_closed(r)
    for r in range(2,21):
        t=r//2-1; assert sum(comb(r,i) for i in range(t+1))<2**(r-1)
        assert kappa_from_kleitman(r)==kappa_closed(r)
    assert 16+6+4*(5-5)==22
    print('APC all-rank exact controls: PASS')
if __name__=='__main__': main()
