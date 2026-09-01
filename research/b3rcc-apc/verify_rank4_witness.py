#!/usr/bin/env python3
from itertools import product
from collections import deque

MOVES=[(0,0,0,1),(0,0,1,-1),(0,1,-1,0),(1,0,-1,1)]
VERTS=list(product([0,1],repeat=4))

def determinant4(cols):
    # Bareiss determinant, matrix with given columns.
    a=[[cols[j][i] for j in range(4)] for i in range(4)]
    sign=1; prev=1
    for k in range(3):
        if a[k][k]==0:
            q=next(i for i in range(k+1,4) if a[i][k]!=0)
            a[k],a[q]=a[q],a[k]; sign=-sign
        pivot=a[k][k]
        for i in range(k+1,4):
            for j in range(k+1,4):
                a[i][j]=(a[i][j]*pivot-a[i][k]*a[k][j])//prev
        prev=pivot
    return sign*a[3][3]

def main():
    assert abs(determinant4(MOVES))==1
    dirs=set(MOVES+[tuple(-x for x in u) for u in MOVES])
    edges=[]
    for i,x in enumerate(VERTS):
        for j in range(i+1,len(VERTS)):
            d=tuple(VERTS[j][t]-x[t] for t in range(4))
            if d in dirs: edges.append((i,j))
    assert len(edges)==18
    adj={i:[] for i in range(16)}
    for a,b in edges: adj[a].append(b); adj[b].append(a)
    def dist(s):
        d=[None]*16; d[s]=0; q=deque([s])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if d[v] is None: d[v]=d[u]+1; q.append(v)
        return d
    D=[dist(i) for i in range(16)]
    assert all(v is not None for row in D for v in row)
    def theta(e,f):
        a,b=e; x,y=f
        return D[a][x]+D[b][y] != D[a][y]+D[b][x]
    witness=None
    for e in edges:
        for f in edges:
            if not theta(e,f): continue
            for g in edges:
                if theta(f,g) and not theta(e,g):
                    witness=(e,f,g); break
            if witness: break
        if witness: break
    assert witness is not None
    readable=[[VERTS[u] for u in e] for e in witness]
    print('rank4 witness: det=+/-1, vertices=16, edges=18, connected')
    print('Theta nontransitivity witness:',readable)
    print('rank4 non-partial-cube witness: PASS')
if __name__=='__main__': main()
