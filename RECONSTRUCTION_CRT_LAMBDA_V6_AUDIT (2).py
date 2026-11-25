#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V6 — audit autonome du PGCD modulaire dans K_p = F_p[beta]/(T).

Lit RESULTANT_SCHUR_T2G_V10_EXACT.txt et le fichier T_BETA_COEFFICIENTS_V2_8_B.txt
(ou son nom encodé GitHub) places dans le même dossier. Les premiers 4057 et 4211 sont des témoins
indépendants et sont explicitement exclus de toute collecte CRT.
Aucune reconstruction rationnelle n'est certifiée par ce script.
"""
from __future__ import annotations
import json, hashlib, re, sys
from pathlib import Path
from datetime import datetime, timezone
import sympy as sp

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "RESULTANT_SCHUR_T2G_V10_EXACT.txt"
TFILE_CANDIDATES = (
    ROOT / "T_BETA_COEFFICIENTS_V2_8_B.txt",
    ROOT / "T_x5f_BETA_x5f_COEFFICIENTS_x5f_V2_x5f_8_x5f_B.txt",
)
TFILE = next((p for p in TFILE_CANDIDATES if p.is_file()), TFILE_CANDIDATES[0])
REPORT = ROOT / "RAPPORT_RECONSTRUCTION_CRT_LAMBDA_V6.json"
HOLDOUTS = (4057, 4211)
BASE_PRIME = 227


def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def read_assignment(path, key):
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith(key+'='):
            return line.split('=',1)[1].strip()
    raise ValueError(f"ligne {key}= absente de {path.name}")

def trim(a):
    while a and a[-1] == 0: a.pop()
    return a

def inv_scalar(a,p):
    a%=p
    if not a: raise ZeroDivisionError('inverse scalaire de zero')
    return pow(a,-1,p)

def poly_add(a,b,p):
    c=[0]*max(len(a),len(b))
    for i in range(len(c)): c[i]=((a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0))%p
    return trim(c)

def poly_sub(a,b,p): return poly_add(a,[(-x)%p for x in b],p)
def poly_mul(a,b,p):
    if not a or not b:return []
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j]=(c[i+j]+x*y)%p
    return trim(c)
def poly_divmod(a,b,p):
    a=trim(a[:]); b=trim(b[:])
    if not b: raise ZeroDivisionError('division polynomiale par zero')
    q=[0]*max(0,len(a)-len(b)+1); ib=inv_scalar(b[-1],p)
    while len(a)>=len(b):
        k=len(a)-len(b); c=a[-1]*ib%p; q[k]=c
        for i,v in enumerate(b): a[i+k]=(a[i+k]-c*v)%p
        trim(a)
    return trim(q),a

def poly_mod(a,m,p): return poly_divmod(a,m,p)[1]
def poly_gcd(a,b,p):
    a=trim(a[:]);b=trim(b[:])
    while b: a,b=b,poly_mod(a,b,p)
    if not a:return []
    z=inv_scalar(a[-1],p);return [(x*z)%p for x in a]
def poly_powmod(a,n,m,p):
    out=[1]
    while n:
        if n&1: out=poly_mod(poly_mul(out,a,p),m,p)
        n >>= 1
        if n: a=poly_mod(poly_mul(a,a,p),m,p)
    return out

def field_inv(a,T,p):
    """Inverse par Euclide etendu polynomial; refuse zero/non-units."""
    a=poly_mod(a,T,p)
    if not a: raise ZeroDivisionError('inverse de zero dans K_p')
    r0,r1=T[:],a[:]; s0,s1=[],[1]
    while r1:
        q,r=poly_divmod(r0,r1,p)
        r0,r1=r1,r
        s0,s1=s1,poly_sub(s0,poly_mul(q,s1,p),p)
    if len(r0)!=1: raise ZeroDivisionError('element non inversible: T reducible ou non-unite')
    return poly_mod([(x*inv_scalar(r0[0],p))%p for x in s0],T,p)

def fadd(a,b,T,p): return poly_mod(poly_add(a,b,p),T,p)
def fsub(a,b,T,p): return poly_mod(poly_sub(a,b,p),T,p)
def fmul(a,b,T,p): return poly_mod(poly_mul(a,b,p),T,p)
def finv(a,T,p): return field_inv(a,T,p)

def rabin_irreducible(T,p):
    if len(T)!=40 or T[-1]%p!=1: return False, 'T non monique de degre 39'
    x=[0,1]
    for q in (3,13):
        z=x[:]
        for _ in range(39//q): z=poly_powmod(z,p,T,p)
        d=poly_gcd(T,poly_sub(z,x,p),p)
        if len(d)!=1: return False, f'PGCD Rabin non trivial pour q={q}'
    z=x[:]
    for _ in range(39): z=poly_powmod(z,p,T,p)
    return (z==x), 'Frobenius X^(p^39)=X' if z==x else 'Frobenius final incorrect'

def parse_expr_poly(text, lam, r):
    return sp.Poly(sp.sympify(text, locals={'lam':lam,'r':r}), lam, domain='EX')

def to_field_coeffs(poly, L, T, p, r):
    result=[]
    invL=inv_scalar(int(L)%p,p)
    for i in range(poly.degree()+1):
        c=poly.nth(i)
        cp=sp.Poly(c,r,domain='QQ')
        v=[0]*max(39,cp.degree()+1)
        for (j,), a in cp.terms():
            num,den=map(int,sp.fraction(a))
            v[j]=(v[j]+num*inv_scalar(den,p)*pow(invL,j,p))%p
        result.append(poly_mod(v,T,p))
    while result and not result[-1]: result.pop()
    return result

def lam_divmod(a,b,T,p):
    a=a[:];b=b[:]
    if not b: raise ZeroDivisionError('division par zero en lambda')
    q=[[] for _ in range(max(0,len(a)-len(b)+1))]
    ib=finv(b[-1],T,p)
    while len(a)>=len(b):
        k=len(a)-len(b); c=fmul(a[-1],ib,T,p);q[k]=c
        for i,v in enumerate(b): a[i+k]=fsub(a[i+k] if i+k<len(a) else [],fmul(c,v,T,p),T,p)
        while a and not a[-1]:a.pop()
    while q and not q[-1]:q.pop()
    return q,a

def lam_gcd(a,b,T,p):
    steps=0
    while b:
        _,r=lam_divmod(a,b,T,p);a,b=b,r;steps+=1
        if steps>30:raise ArithmeticError('trop d etapes Euclide lambda')
    if not a:return [],steps
    iv=finv(a[-1],T,p)
    return [fmul(c,iv,T,p) for c in a],steps

def eval_lambda(poly,x,T,p):
    y=[]
    for c in reversed(poly): y=fadd(fmul(y,x,T,p),c,T,p)
    return y

def modular_audit(p,Fexpr,Gexpr,Tint,L):
    T=[int(x)%p for x in Tint]
    if len(T)!=40 or T[-1]!=1: raise ValueError(f'p={p}: T pas monique degre 39')
    irr,why=rabin_irreducible(T,p)
    if not irr: return {'p':p,'irreducible':False,'reason':why}
    lam,r=sp.symbols('lam r')
    F=to_field_coeffs(parse_expr_poly(Fexpr,lam,r),L,T,p,r)
    G=to_field_coeffs(parse_expr_poly(Gexpr,lam,r),L,T,p,r)
    d,steps=lam_gcd(F,G,T,p)
    item={'p':p,'irreducible':True,'degree_F':len(F)-1,'degree_G':len(G)-1,
          'gcd_degree':len(d)-1,'euclid_steps':steps}
    if len(d)==2:
        root=fsub([],d[0],T,p)
        fv=eval_lambda(F,root,T,p);gv=eval_lambda(G,root,T,p)
        item.update({'F_vanishes':not fv,'G_vanishes':not gv,
                     'root_beta_power_basis':[str(x) for x in root]})
    # Negative control: G+1 should not share the linear factor generically.
    Gbad=G[:]
    if not Gbad:Gbad=[[]]
    Gbad[0]=fadd(Gbad[0],[1],T,p)
    dbad,nbad=lam_gcd(F,Gbad,T,p)
    item.update({'negative_G_plus_1_gcd_degree':len(dbad)-1,
                 'negative_control_pass':len(dbad)==1,'negative_euclid_steps':nbad})
    return item

def main():
    if not SOURCE.is_file() or not TFILE.is_file():
        expected = ', '.join(p.name for p in (SOURCE, *TFILE_CANDIDATES))
        raise FileNotFoundError(f'Fichier(s) requis absent(s). Placer dans le dossier : {expected}')
    source_text=SOURCE.read_text(encoding='utf-8')
    Fexpr=read_assignment(SOURCE,'F_red');Gexpr=read_assignment(SOURCE,'G');Hexpr=read_assignment(SOURCE,'H')
    lam,r=sp.symbols('lam r')
    H=sp.Poly(sp.sympify(Hexpr,locals={'r':r}),r,domain='ZZ')
    if H.degree()!=39:raise ValueError('H doit etre de degre 39')
    L=int(H.nth(39))
    coeffs={int(m.group(1)):int(m.group(2)) for m in re.finditer(r'^c_(\d+)=(-?\d+)$',TFILE.read_text(encoding='utf-8'),re.M)}
    if set(coeffs)!=set(range(40)):raise ValueError('Le fichier T doit contenir exactement c_0..c_39')
    T=[coeffs[i] for i in range(40)]
    transform=[]
    for i in range(39): transform.append(int(H.nth(i))*L**(38-i)==T[i])
    transform.append(T[39]==1)
    if not all(transform):raise ArithmeticError('Echec de la reconstruction exacte T depuis H')
    results=[modular_audit(p,Fexpr,Gexpr,T,L) for p in (BASE_PRIME,*HOLDOUTS)]
    # Les holdouts ne sont pas dans la liste de collecte, par construction.
    holdout_ok=all(x.get('irreducible') and x.get('gcd_degree')==1 and x.get('F_vanishes') and x.get('G_vanishes') and x.get('negative_control_pass') for x in results[1:])
    base_ok=all(x.get('irreducible') and x.get('gcd_degree')==1 and x.get('F_vanishes') and x.get('G_vanishes') and x.get('negative_control_pass') for x in results[:1])
    report={
      'schema':'DODECA_T2G_LAMBDA_V6_AUDIT_1',
      'timestamp_utc':datetime.now(timezone.utc).isoformat(),
      'source_file':SOURCE.name,'source_sha256':sha256(SOURCE),
      'T_file':TFILE.name,'T_file_sha256':sha256(TFILE),
      'degree_H':H.degree(),'degree_T':len(T)-1,'T_monic':T[-1]==1,
      'exact_H_to_T_coefficient_checks':len(transform),'exact_H_to_T_all_pass':all(transform),
      'base_prime':BASE_PRIME,'independent_holdouts':list(HOLDOUTS),
      'crt_collection_status':'NOT_IMPLEMENTED_IN_V6_AUDIT',
      'crt_collection_primes':[],
      'holdouts_excluded_from_crt': 'NOT_APPLICABLE_NO_CRT_COLLECTION',
      'modular_results':results,
      'base_modular_audit_pass':base_ok,'holdout_audits_pass':holdout_ok,
      'exact_rational_lambda_reconstruction':'NOT_DONE',
      'exact_gcd_in_Q_r_mod_H':'NOT_VERIFIED',
      'overall_status':'MODULAR_AUDIT_PASS_EXACT_RECONSTRUCTION_OPEN' if base_ok and holdout_ok else 'AUDIT_FAILED_OR_INCOMPLETE',
      'limitations':['Les calculs sont des reductions modulaires.','Aucun coefficient rationnel exact de lambda_star n est certifie ici.',
                     '4057 et 4211 sont des controles independants, pas des premiers CRT.',
                     'Le resultat modulaire seul ne remplace pas la verification exacte dans Q[r]/(H).',
                     'La collecte CRT et la reconstruction rationnelle ne sont pas implementees dans cette version V6.',
                     'Le champ holdouts_excluded_from_crt est non applicable : aucune collecte CRT n est executee par ce script.']
    }
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    print(f'REPORT={REPORT} SHA256={sha256(REPORT)}')
    if not (base_ok and holdout_ok):sys.exit(2)

if __name__=='__main__':main()
