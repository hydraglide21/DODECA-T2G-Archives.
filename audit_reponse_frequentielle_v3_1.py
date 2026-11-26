#!/usr/bin/env python3
"""V3.1: six-face orientation scan and refined lambda sweep.
Exact rational face assembly/ranks; double precision modal and damped FRF scan.
"""
from pathlib import Path
import sympy as sp, numpy as np, csv, hashlib, zipfile
from scipy.linalg import eigh, solve
D=Path(__file__).resolve().parent
q=sp.Rational
# Reuse the audited V2.2 exact polynomial matrices.
s22={'__file__':str(D/'audit_faces_cube_v2_2.py'),'__name__':'v22_v31'}
src22=(D/'audit_faces_cube_v2_2.py').read_text()
exec(src22.split('# V2.2 — genuine two-dimensional')[0],s22)
ME_E,ME_T=s22['ME_archE'],s22['ME_archT']
K0_E,K0_T=s22['K0_archE'],s22['K0_archT']
Kd_E,Kd_T=s22['Kd_archE'],s22['Kd_archT']
KEdge_E,KEdge_T=s22['Kedge_E'],s22['Kedge_T']
# Reuse exact integration of a rectangular patch on an internal plane.
s27={'__file__':str(D/'audit_cube_interieur_decentre_v2_7.py'),'__name__':'v27_v31'}
src27=(D/'audit_cube_interieur_decentre_v2_7.py').read_text()
exec(src27.split('a=sp.Rational(1,4); shifts=')[0],s27)
face_patch=s27['face_patch']
a=q(1,4); c=(q(1,8),q(0),q(0)); zero=sp.zeros(20,39)
faces=[]; names=[]
for normal in range(3):
    tang=[j for j in range(3) if j!=normal]
    bounds=tuple((c[j]-a,c[j]+a) for j in tang)
    for sign in (-1,1):
        faces.append(face_patch(normal,c[normal]+sign*a,bounds))
        names.append('xyz'[normal]+('-' if sign<0 else '+'))
Xsum=sum((f[2] for f in faces),zero)
assert Xsum==zero
face_ranks=[int(f[2].rank()) for f in faces]
# Exact rational lambda grid for all orientations.
lambdas=[q(1,4),q(1,2),q(3,4),q(1),q(5,4),q(3,2),q(2),q(3),q(4)]
exact_rows=[]
for i,name in enumerate(names):
    for lam in lambdas:
        X=(lam-1)*faces[i][2]
        exact_rows.append({'face':name,'lambda':str(lam),'individual_face_rank':face_ranks[i],
                           'assembled_cross_rank':int(X.rank()),
                           'frobenius_sq_exact':str(sp.factor(sum(v*v for v in X)))})
with (D/'CERTIFICAT_ORIENTATIONS_LAMBDA_V3_1.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(exact_rows[0]));w.writeheader();w.writerows(exact_rows)
# Dynamic FRF: all six orientations; moderate refined grid around cancellation and amplification.
M=sp.diag(ME_E,ME_T); K0=sp.diag(K0_E,K0_T); Kd=sp.diag(Kd_E,Kd_T); KEdge=sp.diag(KEdge_E,KEdge_T)
CE=sp.zeros(2,20); CE[0,0]=-2; CE[0,1]=-1; CE[1,1]=-3
CT=sp.zeros(3,39); CT[0,1]=1; CT[1,2]=1; CT[2,0]=1
Obs=sp.diag(CE,CT)
Mf=np.array(M.evalf(),float); K0f=np.array(K0.evalf(),float); Kdf=np.array(Kd.evalf(),float); KEf=np.array(KEdge.evalf(),float); Of=np.array(Obs.evalf(),float)
r=g=eta=1.0
dyn_lams=[q(1,2),q(3,4),q(1),q(5,4),q(3,2),q(2),q(3),q(4)]
dyn_rows=[]
for i,name in enumerate(names):
    for lam in dyn_lams:
        KsurfE=sum((f[0] for f in faces),sp.zeros(20))+(lam-1)*faces[i][0]
        KsurfT=sum((f[1] for f in faces),sp.zeros(39))+(lam-1)*faces[i][1]
        KsurfX=(lam-1)*faces[i][2]
        Ksurf=KsurfE.row_join(KsurfX).col_join(KsurfX.T.row_join(KsurfT))
        Kf=K0f+r*Kdf+g*KEf+eta*np.array(Ksurf.evalf(),float)
        vals,_=eigh(Kf,Mf)
        if vals[0] <= 0: raise RuntimeError(f'non-positive stiffness: {name}, {lam}')
        om=np.sqrt(vals); zeta=.02; lo,hi=om[0],om[-1]
        alpha=2*zeta*lo*hi/(lo+hi); beta=2*zeta/(lo+hi); Df=alpha*Mf+beta*Kf
        # Focused grid: modal interval; 260 samples per configuration.
        wg=np.linspace(.85*lo,1.15*hi,260)
        peak=-1.; ptotal=0.; pratio=0.; pw=0.
        for w in wg:
            A=Kf-(w*w)*Mf+1j*w*Df
            H=Of@solve(A,Of.T,assume_a='gen')
            hc=np.linalg.svd(H[2:,:2],compute_uv=False)[0]
            ht=np.linalg.svd(H,compute_uv=False)[0]
            if hc>peak: peak=float(hc); ptotal=float(ht); pratio=float(hc/(ht+1e-30)); pw=float(w)
        X=(lam-1)*faces[i][2]
        dyn_rows.append({'face':name,'lambda':str(lam),'exact_cross_rank':int(X.rank()),
                         'omega_peak_sampled':pw,'cross_gain_peak_sampled':peak,
                         'total_gain_at_cross_peak':ptotal,'cross_to_total_at_cross_peak':pratio,
                         'frequency_samples':len(wg),'positive_definite':True,'zeta_endpoint':zeta})
with (D/'TRANSFERT_FREQUENTIEL_V3_1.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(dyn_rows[0]));w.writeheader();w.writerows(dyn_rows)
# Report orientation and best sampled outcomes.
lines=['V3.1 — BALAYAGE DES SIX ORIENTATIONS ET DE LAMBDA',
'Cube interieur cote 1/2, centre (1/8,0,0), six faces integrees exactement sur Q.',
'Poids lambda applique a une face; les cinq autres gardent le poids 1.',
'Balayage exact: 6 orientations x 9 valeurs rationnelles de lambda = 54 configurations.',
'Balayage dynamique: 6 orientations x 8 valeurs rationnelles = 48 configurations; 260 frequences par configuration.',
'K=K0+Kd+K_aretes+K_surface; amortissement Rayleigh calibre a 2% aux frequences propres extremes.',
'Les pics sont des maxima echantillonnes; aucune optimisation continue ni certification de maximum global.',
'',f'Rangs individuels par face, ordre {names}: {face_ranks}.',
'La somme des six blocs croises a poids egal est exactement nulle.' ,'']
for name in names:
    rr=[r for r in dyn_rows if r['face']==name]
    best=max(rr,key=lambda x:x['cross_gain_peak_sampled'])
    lines.append(f"{name}: rang individuel={face_ranks[names.index(name)]}; meilleur lambda echantillonne={best['lambda']}; gain={best['cross_gain_peak_sampled']:.8g}; omega={best['omega_peak_sampled']:.8g}; ratio={best['cross_to_total_at_cross_peak']:.6%}")
best=max(dyn_rows,key=lambda x:x['cross_gain_peak_sampled'])
lines += ['',f"MEILLEUR POINT ECHANTILLONNE: face={best['face']}, lambda={best['lambda']}, gain={best['cross_gain_peak_sampled']:.10g}, omega={best['omega_peak_sampled']:.10g}, ratio={best['cross_to_total_at_cross_peak']:.8%}.",
'INTERPRETATION: la dependance en orientation et lambda est calculee pour le modele polynomial surfacique. Le gain spectral n est pas une fraction d energie ni une mesure experimentale.',
'LIMITES: modele lineaire, amortissement choisi, sorties centrales existantes, grille frequentielle finie; pas de coque autonome, contact, non-linearite ou calibration physique.']
(D/'RAPPORT_REPONSE_FREQUENTIELLE_V3_1.txt').write_text('\n'.join(lines)+'\n')
files=[D/'audit_reponse_frequentielle_v3_1.py',D/'CERTIFICAT_ORIENTATIONS_LAMBDA_V3_1.csv',D/'TRANSFERT_FREQUENTIEL_V3_1.csv',D/'RAPPORT_REPONSE_FREQUENTIELLE_V3_1.txt',D/'audit_faces_cube_v2_2.py',D/'audit_cube_interieur_decentre_v2_7.py',D/'bases_cubiques_Eg_T2g_exactes.txt',D/'matrices_completes_Eg_T2g_exactes.txt']
(D/'SHA256SUMS_V3_1.txt').write_text('\n'.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}' for p in files)+'\n');files.append(D/'SHA256SUMS_V3_1.txt')
zp=D/'audit_reponse_frequentielle_v3_1.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.name)
with zipfile.ZipFile(zp) as z: bad=z.testzip()
if bad: raise RuntimeError(f'ZIP test failed: {bad}')
print('\n'.join(lines)); print('ZIP_TEST',bad,'FILES',len(files),'EXACT_ROWS',len(exact_rows),'DYNAMIC_ROWS',len(dyn_rows))
