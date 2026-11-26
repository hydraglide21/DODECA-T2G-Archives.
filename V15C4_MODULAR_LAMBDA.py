import sympy as sp,json,time,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
# load integer polynomial serializations written by V15C3
r=sp.symbols('r')
d={}
for line in (R/'RESULTANT_SCHUR_T2G_V10_EXACT.txt').read_text().splitlines():
 if '=' in line:
  k,v=line.split('=',1)
  if k in {'H'}: d[k]=v
H=sp.Poly(sp.sympify(d['H'],locals={'r':r}),r,domain=sp.QQ)
s11=sp.Poly(sp.sympify((R/'S11_reduit_num.txt').read_text(),locals={'r':r}),r,domain=sp.QQ)
s10=sp.Poly(sp.sympify((R/'S10_reduit_num.txt').read_text(),locals={'r':r}),r,domain=sp.QQ)
results=[]; t=time.time()
for p in list(sp.primerange(227,5000)):
 Hp=sp.Poly(H,r,modulus=p)
 def modpoly(P):
  expr=0
  for (i,),c in P.terms():
   c=sp.Rational(c); den=int(c.q)%p
   if den==0: raise ZeroDivisionError('bad denominator')
   expr += ((int(c.p)%p)*pow(den,-1,p)%p)*r**i
  return sp.Poly(expr,r,modulus=p)
 try:
  a=modpoly(s11); b=modpoly(s10)
 except ZeroDivisionError:
  continue
 if Hp.degree()!=39 or not Hp.is_irreducible: continue
 if a.degree()!=38 or sp.gcd(a,Hp).degree()!=0: continue
 inv=sp.invert(a,Hp)
 lam=(-b*inv).rem(Hp)
 assert lam.degree()<39 and (a*lam+b).rem(Hp).is_zero
 results.append({'p':p,'lambda_coefficients_r0_to_r38':[int(lam.nth(i))%p for i in range(39)],'s11_nonzero':True,'identity_mod_H':True})
 print('prime',p,'done',flush=True)
 if len(results)>=4: break
out={'status':'PASS_MODULAR_LAMBDA_VECTORS','basis':'1,r,...,r^38','modulus_polynomial':'H39','results':results,'elapsed_seconds':round(time.time()-t,3)}
(R/'V15C4_MODULAR_LAMBDA.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
