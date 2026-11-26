#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M30_FERMETURE_RESERVES_V2.py

Validation indépendante de la chaîne énergie réelle -> Hessienne réelle
-> projection de Fourier -> symbole de Bloch, sur le tore périodique 4^3.

La Hessienne est assemblée directement à partir des formes linéaires
microscopiques NN, NNN et TRI. La matrice compacte M_P n'intervient que
comme cible de comparaison finale.

Aucun calcul algébrique antérieur n'est modifié. Script non exécuté ici.
"""
import itertools
import sympy as sp

I = sp.I
kc, k2, kth = sp.symbols('kc k2 kth', real=True)
L = 4
N = L**3
SITES = list(itertools.product(range(L), repeat=3))
SITE_ID = {n: i for i, n in enumerate(SITES)}
DOF = 3*N


def check(name, condition, detail=''):
    ok = bool(condition)
    print(f"[{'OK' if ok else 'ECHEC'}] {name}" + (f" : {detail}" if detail else ''))
    if not ok:
        raise AssertionError(name)


def wrap(v):
    return tuple(v[i] % L for i in range(3))


def add(n, R):
    return wrap(tuple(n[i] + R[i] for i in range(3)))


def dot(a, b):
    return sum(a[i]*b[i] for i in range(3))


def dof(site, comp):
    return 3*SITE_ID[site] + comp


NN_ORIENTED = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
NN_POS = [(1,0,0),(0,1,0),(0,0,1)]
NNN_ORIENTED = [v for v in itertools.product((-1,0,1), repeat=3)
                if sum(abs(x) for x in v) == 2]
def is_positive(R):
    for x in R:
        if x:
            return x > 0
    return False
NNN_POS = [R for R in NNN_ORIENTED if is_positive(R)]
TRI_PAIRS = [(a,b) for a,b in itertools.combinations(NN_ORIENTED,2)
             if dot(a,b) == 0]

print('='*72)
print('M30 — FERMETURE DES RÉSERVES V2')
print('='*72)
print(f'Réseau périodique : {L}^3 = {N} sites ; {DOF} degrés de liberté')
check('3 directions NN non orientées', len(NN_POS) == 3)
check('6 directions NNN non orientées', len(NNN_POS) == 6)
check('12 paires TRI orthogonales', len(TRI_PAIRS) == 12)

# ----------------------------------------------------------------------
# 1. Comptages non orientés et unicité périodique
# ----------------------------------------------------------------------
def undirected_bond_set(directions):
    out = set()
    for n in SITES:
        for R in directions:
            m = add(n,R)
            key = tuple(sorted((SITE_ID[n], SITE_ID[m])))
            out.add(key)
    return out

NN_BONDS = undirected_bond_set(NN_POS)
NNN_BONDS = undirected_bond_set(NNN_POS)
check('NN : 3N liaisons non orientées distinctes', len(NN_BONDS) == 3*N,
      f'obtenu {len(NN_BONDS)}')
check('NNN : 6N liaisons non orientées distinctes', len(NNN_BONDS) == 6*N,
      f'obtenu {len(NNN_BONDS)}')

TRI_KEYS = set()
for n in SITES:
    for a,b in TRI_PAIRS:
        p, q = add(n,a), add(n,b)
        TRI_KEYS.add((SITE_ID[n], tuple(sorted((SITE_ID[p],SITE_ID[q])))))
check('TRI : 12N triplets centre-paire distincts', len(TRI_KEYS) == 12*N,
      f'obtenu {len(TRI_KEYS)}')

# ----------------------------------------------------------------------
# 2. Hessienne réelle assemblée directement depuis les énergies.
# Chaque terme est E_t = (1/2) k (sum_j c_j u_j)^2,
# donc sa Hessienne vaut k c c^T.
# ----------------------------------------------------------------------
H = sp.MutableSparseMatrix(DOF, DOF, {})

def add_rank_one(coeffs, stiffness):
    # coeffs: dictionnaire indice DDL -> coefficient exact
    items = list(coeffs.items())
    for ia, ca in items:
        for ib, cb in items:
            H[ia,ib] += stiffness*ca*cb

# NN : projection sur Rhat = R (vecteur unité)
for n in SITES:
    for R in NN_POS:
        m = add(n,R)
        coeffs = {}
        for c in range(3):
            coeffs[dof(m,c)] = sp.Integer(R[c])
            coeffs[dof(n,c)] = -sp.Integer(R[c])
        add_rank_one(coeffs,kc)

# NNN : Rhat = R/sqrt(2), donc coefficients R/sqrt(2).
# Le produit extérieur introduit exactement le facteur 1/2.
for n in SITES:
    for R in NNN_POS:
        m = add(n,R)
        coeffs = {}
        for c in range(3):
            coeffs[dof(m,c)] = sp.Rational(R[c],2) * sp.sqrt(2)
            coeffs[dof(n,c)] = -sp.Rational(R[c],2) * sp.sqrt(2)
        add_rank_one(coeffs,k2)

# TRI : dtheta = -[a.(u_{n+b}-u_n)+b.(u_{n+a}-u_n)].
# Le signe global disparaît dans dtheta^2.
for n in SITES:
    for a,b in TRI_PAIRS:
        na, nb = add(n,a), add(n,b)
        coeffs = {}
        for c in range(3):
            coeffs[dof(nb,c)] = coeffs.get(dof(nb,c),0) + sp.Integer(a[c])
            coeffs[dof(na,c)] = coeffs.get(dof(na,c),0) + sp.Integer(b[c])
            coeffs[dof(n,c)] = coeffs.get(dof(n,c),0) - sp.Integer(a[c]+b[c])
        coeffs = {j:sp.simplify(v) for j,v in coeffs.items() if v != 0}
        add_rank_one(coeffs,kth)

check('Hessienne réelle symétrique', H == H.T)
check('Hessienne réelle de taille 192 x 192', H.shape == (DOF,DOF))

# Trois translations uniformes doivent être dans le noyau.
for comp in range(3):
    t = sp.zeros(DOF,1)
    for n in SITES:
        t[dof(n,comp),0] = 1
    residual = H*t
    check(f'Translation uniforme composante {comp}: Ht=0',
          all(sp.simplify(x)==0 for x in residual))

# ----------------------------------------------------------------------
# 3. Projection de Fourier de la Hessienne réelle.
# D_ab(q) = (1/N) sum_{n,m} exp(-iq.n) H_(n,a),(m,b) exp(iq.m).
# Cette projection est extraite de H, sans utiliser M_P.
# ----------------------------------------------------------------------
H_entries = list(H.todok().items())
print(f'Entrées non nulles de H : {len(H_entries)}')


def phase(qidx, site, sign=1):
    exponent = sum(qidx[i]*site[i] for i in range(3))
    return sp.exp(sign*I*sp.pi*exponent/2)


def fourier_project(qidx):
    Dq = sp.zeros(3,3)
    for (row,col), value in H_entries:
        site_n_id, alpha = divmod(row,3)
        site_m_id, beta = divmod(col,3)
        n, m = SITES[site_n_id], SITES[site_m_id]
        Dq[alpha,beta] += phase(qidx,n,-1)*value*phase(qidx,m,1)/N
    return Dq.applyfunc(sp.simplify)


def target_2MP(qidx):
    q = [sp.pi*sp.Integer(j)/2 for j in qidx]
    cs = [sp.cos(x) for x in q]
    ss = [sp.sin(x) for x in q]
    xs = [1-c for c in cs]
    B = k2 + 2*kth
    diag = []
    for i in range(3):
        j,k = (i+1)%3,(i+2)%3
        diag.append((kc+2*k2)*xs[i] + (k2+4*kth)*(xs[j]+xs[k])
                    - k2*xs[i]*(xs[j]+xs[k]))
    MP = sp.zeros(3,3)
    for i in range(3):
        for j in range(3):
            MP[i,j] = diag[i] if i==j else B*ss[i]*ss[j]
    return (2*MP).applyfunc(sp.simplify)

print('\nProjection des 64 modes discrets :')
for qidx in itertools.product(range(L), repeat=3):
    D_fourier = fourier_project(qidx)
    D_target = target_2MP(qidx)
    delta = (D_fourier-D_target).applyfunc(sp.simplify)
    check(f'Fourier(H réelle) = 2 M_P pour q-index={qidx}',
          all(x == 0 for x in delta))
    check(f'Hermiticité pour q-index={qidx}',
          D_fourier.H == D_fourier)

# ----------------------------------------------------------------------
# 4. Contrôle explicite des modes auto-conjugués q = -q modulo 2pi.
# Ils correspondent aux indices 0 ou 2 dans chaque coordonnée.
# Le script ne leur applique aucune formule d'énergie N/4 d'onde réelle.
# ----------------------------------------------------------------------
self_conjugate = [q for q in itertools.product(range(L),repeat=3)
                  if all((2*q[i]) % L == 0 for i in range(3))]
check('8 modes auto-conjugués identifiés', len(self_conjugate)==8,
      f'{self_conjugate}')
check('56 modes non auto-conjugués identifiés', N-len(self_conjugate)==56)

print('\n'+'='*72)
print('RÉSUMÉ V2')
print('='*72)
print('H réelle assemblée directement depuis les formes énergétiques NN/NNN/TRI.')
print('Projection de Fourier calculée depuis H, sans construire H depuis M_P.')
print('Comparaison à 2 M_P effectuée sur les 64 modes discrets.')
print('Les 8 modes auto-conjugués sont identifiés séparément.')
print('Dimensions physiques et origine des constantes : réserves documentaires distinctes.')
print('Fin des contrôles.')
