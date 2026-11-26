import json,re,hashlib,sys
from pathlib import Path
import sympy as sp
ROOT=Path(__file__).resolve().parent
N=39
V=json.loads((ROOT/'RAPPORT_V14E_KERNEL_MULTI_PRIME_12P.json').read_text())
vt=(ROOT/'RESULTANT_SCHUR_T2G_V10_EXACT.txt').read_text()
red=(ROOT/'ENTRELACEURS_ET_MATRICES_REDUITES_COMPLETS.txt').read_text()
r,lam,beta=sp.symbols('r lam beta')
def lineval(key):
 m=re.search(r'^'+re.escape(key)+r'=(.*)$',vt,re.M)
 if not m: raise RuntimeError('missing '+key)
 return m.group(1)
H=sp.Poly(sp.sympify(lineval('H'),locals={'r':r}),r,domain=sp.QQ)
D=int(H.LC())
T=sp.Poly(sp.expand(D**39*H.monic().as_expr().subs(r,beta/D)),beta,domain=sp.QQ)
assert T.degree()==N and T.LC()==1 and all(c.q==1 for c in T.all_coeffs())

def getmat(name):
 header=name+'_multiplicite =\nMatrix('
 pos=red.find(header)
 if pos<0: raise RuntimeError('matrix header not found '+name)
 start=pos+len(header); depth=1
 for k in range(start,len(red)):
  if red[k]=='(': depth+=1
  elif red[k]==')':
   depth-=1
   if depth==0:
    return sp.Matrix(sp.sympify(red[start:k],rational=True))
 raise RuntimeError('unterminated matrix '+name)
M,K0,Kd=[getmat(x) for x in ('M_T','K0_T','Kd_T')]
assert M.shape==K0.shape==Kd.shape==(13,13)

def field(p):
 tc=[int(T.nth(i))%p for i in range(N)]
 Z=(0,)*N; ONE=(1,)+(0,)*(N-1)
 def add(a,b): return tuple((a[i]+b[i])%p for i in range(N))
 def neg(a): return tuple((-x)%p for x in a)
 def sub(a,b): return add(a,neg(b))
 def mul(a,b):
  c=[0]*(2*N-1)
  for i,x in enumerate(a):
   if x:
    for j,y in enumerate(b):
     if y:c[i+j]=(c[i+j]+x*y)%p
  for k in range(2*N-2,N-1,-1):
   x=c[k]
   if x:
    q=k-N
    for j in range(N):c[q+j]=(c[q+j]-x*tc[j])%p
  return tuple(c[:N])
 def pw(a,e):
  out=ONE
  while e:
   if e&1:out=mul(out,a)
   a=mul(a,a);e>>=1
  return out
 def inv(a):
  if not any(a):raise ZeroDivisionError
  return pw(a,p**N-2)
 def rat(x):
  x=sp.Rational(x); den=int(x.q)%p
  if den==0:raise ZeroDivisionError('matrix denominator divisible by prime')
  return (int(x.p)%p)*pow(den,-1,p)%p
 def scale(a,c):return tuple((c*x)%p for x in a)
 return Z,ONE,add,sub,mul,inv,rat,scale

results=[]
for entry in V['results']:
 p=entry['p']; Z,ONE,add,sub,mul,inv,rat,scale=field(p)
 if len(entry['kernel_u1_to_u12_beta_basis_mod_p'])!=12:raise RuntimeError('bad vector size')
 u=[tuple(int(x)%p for x in a) for a in entry['kernel_u1_to_u12_beta_basis_mod_p']]+[ONE]
 beta_el=(0,1)+(0,)*(N-2); Dinv=pow(D%p,-1,p)
 r_el=scale(beta_el,Dinv)
 # Build numerator n=(K0+r Kd)u and denominator d=M u
 nums=[]; dens=[]
 for i in range(13):
  n=Z; d=Z
  for j in range(13):
   k0=scale(ONE,rat(K0[i,j])); kd=scale(r_el,rat(Kd[i,j])); mij=scale(ONE,rat(M[i,j]))
   kij=add(k0,kd)
   n=add(n,mul(kij,u[j])); d=add(d,mul(mij,u[j]))
  nums.append(n);dens.append(d)
 idx=next((i for i,x in enumerate(dens) if any(x)),None)
 if idx is None: raise RuntimeError(f'{p}: Mu=0 for all rows')
 lam_p=mul(nums[idx],inv(dens[idx]))
 residual=[sub(nums[i],mul(lam_p,dens[i])) for i in range(13)]
 if any(any(x) for x in residual):
  bad=[i for i,x in enumerate(residual) if any(x)]
  raise RuntimeError(f'{p}: extracted lambda fails rows {bad}')
 results.append({'p':p,'lambda_beta_coeffs':list(lam_p),'row_used_1based':idx+1,'all_13_rows_verified':True,'Mu_nonzero_rows':[i+1 for i,x in enumerate(dens) if any(x)]})
 print('PASS',p,'lambda extracted from archived u; all 13 rows zero; row',idx+1,flush=True)
out={'status':'PASS_LAMBDA_REEXTRACTED_FROM_ARCHIVED_KERNEL_VECTORS','source_kernel_report_sha256':hashlib.sha256((ROOT/'RAPPORT_V14E_KERNEL_MULTI_PRIME_12P.json').read_bytes()).hexdigest(),'source_reduced_matrices_sha256':hashlib.sha256((ROOT/'ENTRELACEURS_ET_MATRICES_REDUITES_COMPLETS.txt').read_bytes()).hexdigest(),'source_v10_sha256':hashlib.sha256((ROOT/'RESULTANT_SCHUR_T2G_V10_EXACT.txt').read_bytes()).hexdigest(),'basis':'F_p[beta]/(T(beta)); beta=D*r; normalized u13=1','method':'Recover lambda_p from (K0+r Kd)u=lambda M u using first nonzero coordinate of M u; verify all 13 equations.','results':results,'scope':'Re-extraction from archived V14 modular kernel vectors; does not validate characteristic-zero rational reconstruction.'}
(ROOT/'RAPPORT_LAMBDA_REEXTRAIT_12P.json').write_text(json.dumps(out,indent=2)+'\n')
print('REPORT_SHA256',hashlib.sha256((ROOT/'RAPPORT_LAMBDA_REEXTRAIT_12P.json').read_bytes()).hexdigest())
