#!/usr/bin/env python3
# Extraction exacte de S1 et reduction de ses coefficients modulo H39.
import sympy as sp, time, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'RESULTANT_SCHUR_T2G_V10_EXACT.txt'
d={}
for line in SRC.read_text(encoding='utf-8').splitlines():
    if '=' in line:
        k,v=line.split('=',1)
        if k in {'F_red','G','H'}: d[k]=v
assert set(d)=={'F_red','G','H'}
lam,r=sp.symbols('lam r')
F=sp.Poly(sp.sympify(d['F_red'],locals={'lam':lam,'r':r}),lam,domain=sp.QQ.frac_field(r))
G=sp.Poly(sp.sympify(d['G'],locals={'lam':lam,'r':r}),lam,domain=sp.QQ.frac_field(r))
H=sp.Poly(sp.sympify(d['H'],locals={'r':r}),r,domain=sp.QQ)
t0=time.time()
srs=sp.subresultants(F,G)
trace=[q.degree() for q in srs]
assert trace==[13,9,8,7,6,5,4,3,2,1,0]
lin=[q for q in srs if q.degree()==1]
assert len(lin)==1
S1=lin[0]
red=[]
for c in S1.all_coeffs():
    num,den=sp.fraction(sp.cancel(c))
    pn=sp.Poly(num,r,domain=sp.QQ).rem(H)
    pd=sp.Poly(den,r,domain=sp.QQ).rem(H)
    assert not pd.is_zero
    red.append((pn,pd))
(s11n,s11d),(s10n,s10d)=red
s11=s11n.as_expr()/s11d.as_expr()
s10=s10n.as_expr()/s10d.as_expr()
# Check s11 nonzero and coprime to H using exact numerator/denominator.
assert not s11n.is_zero and sp.gcd(s11n,H).degree()==0
assert sp.gcd(s11d,H).degree()==0 and sp.gcd(s10d,H).degree()==0
(ROOT/'S1_exact_over_Qr.txt').write_text('S1 = ('+str(S1.as_expr())+')\n')
(ROOT/'S11_reduit_num.txt').write_text(str(s11n.as_expr())+'\n')
(ROOT/'S11_reduit_den.txt').write_text(str(s11d.as_expr())+'\n')
(ROOT/'S10_reduit_num.txt').write_text(str(s10n.as_expr())+'\n')
(ROOT/'S10_reduit_den.txt').write_text(str(s10d.as_expr())+'\n')
report={
 'status':'PASS_EXTRACTION_S1_AND_REDUCTION_MOD_H; EXACT_INVERSION_PENDING',
 'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
 'F_degree_lambda':F.degree(),'G_degree_lambda':G.degree(),
 'subresultant_degree_trace':trace,'degree_one_subresultant_count':len(lin),
 'S1_coefficients_reduced_mod_H':True,
 's11_reduced_numerator_degree':s11n.degree(),
 's11_reduced_denominator_degree':s11d.degree(),
 's10_reduced_numerator_degree':s10n.degree(),
 's10_reduced_denominator_degree':s10d.degree(),
 's11_nonzero_mod_H':True,'gcd_s11_numerator_H_degree':sp.gcd(s11n,H).degree(),
 'gcd_s11_denominator_H_degree':sp.gcd(s11d,H).degree(),
 'gcd_s10_denominator_H_degree':sp.gcd(s10d,H).degree(),
 'lambda_star_rational_coefficients_reconstructed':False,
 'exact_inverse_attempt_previous_run':'exceeded 120-second execution limit',
 'elapsed_seconds':round(time.time()-t0,3)
}
(ROOT/'V15C3_EXTRACTION_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
