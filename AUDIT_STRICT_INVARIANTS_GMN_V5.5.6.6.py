#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDIT STRICT INVARIANTS GMN V5.5.6.6.
Nouveau fichier autonome. V5.5.5 a V5.5.6.5 conservees, inchangees.
Depot : hydraglide21/DODECA-T2G-Archives.
V5.5.6.5 -> V5.5.6.6 :
C11 test 18 : tolerance supprimee, exige exactement NON_DET + certifier_phi2 calcul_local_manquant.
Fixture valide : phi1=[1,1], lambda1=Fraction(4,1), psi1=0b11, phi2=[17,1] (diff=16, v2=4, pente=-4, residuel=0b11).
C11 : type exigee verifie en etape A avant verrou, type bool exact exige.
C09 : canonique conserve, cas branche liste/chaine/None/entier/booleen, incomplet, champ absent, ajoutes.
C13 : None strict conserve, injections supplementaires.
Python 3.9.25, stdlib uniquement. int, Fraction exacts. Aucun flottant dans les calculs mathematiques.
EXECUTION DANS CETTE SESSION : NON EFFECTUEE.
"""
import hashlib, math, os, py_compile, re, sys, datetime
from fractions import Fraction
OK="OK"; ECHEC="ECHEC"; NON_DET="NON DETERMINE"
CALCULE="CALCULÉ"; CONDITIONNEL="CONDITIONNEL"; OUVERT="OUVERT"; TEST_LOGICIEL="TEST_LOGICIEL"
CALCUL_FORMEL_OK="CALCUL_FORMEL_OK"; CANDIDAT_GMN="CANDIDAT_GMN"; CERTIFICATION_GMN="CERTIFICATION_GMN"
CALCUL_LOCAL_EFFECTIF_IMPLEMENTE=False; ENUMERATION_BRANCHES_EFFECTIVE=False; CERTIFICATION_LOCALE_ETABLIE=False
_SENTINELLE=object()
def _flag(nom):
    if nom not in globals(): return (NON_DET,None,"variable %s absente : absence != preuve"%nom,"_flag absence")
    v=globals()[nom]
    if type(v) is bool: return (OK,v,"variable %s bool exact %s"%(nom,v),"_flag bool")
    return (ECHEC,None,"variable %s type invalide %s"%(nom,type(v).__name__),"_flag type")
def to_frac_strict(x,nom="valeur"):
    if type(x) is int: return Fraction(x)
    if type(x) is Fraction: return x
    raise TypeError("%s: conversion interdite %s (%r)"%(nom,type(x).__name__,x))
class Resultat:
    def __init__(self,nom,statut,detail="",obligatoire=True,raison="",detecteur="",categorie=NON_DET):
        if statut not in (OK,ECHEC,NON_DET): raise ValueError("Statut non autorise")
        self.nom=nom; self.statut=statut; self.detail=detail; self.obligatoire=obligatoire; self.raison=raison; self.detecteur=detecteur; self.categorie=categorie
def statut_global(resultats):
    try:
        if not isinstance(resultats,(list,tuple)): return ("ECHEC GLOBAL","Collection invalide")
        if len([r for r in resultats if getattr(r,"obligatoire",False)])==0: return ("ECHEC GLOBAL","Liste obligatoire vide")
        for r in resultats:
            if getattr(r,"statut",None) not in (OK,ECHEC,NON_DET): return ("ECHEC GLOBAL","Statut non autorise")
            if type(getattr(r,"obligatoire",None)) is not bool: return ("ECHEC GLOBAL","Drapeau obligatoire invalide")
        if any(getattr(r,"statut",None)==ECHEC and getattr(r,"obligatoire",False) for r in resultats): return ("ECHEC GLOBAL","Obligatoire refute")
        return ("PASS PARTIEL","Verrou V5.5.6.6 : PASS GLOBAL impossible, preuves non etablies.")
    except Exception as e: return ("ECHEC GLOBAL","Erreur statut_global : %s"%e)
def _check_gf2(x,nom):
    if type(x) is bool: return (ECHEC,None,"GF2 %s : bool refuse"%nom)
    if not type(x) is int: return (ECHEC,None,"GF2 %s : type %s"%(nom,type(x).__name__))
    if x<0: return (ECHEC,None,"GF2 %s : negatif refuse"%nom)
    return (OK,x,"GF2 %s : int >=0"%nom)
def degF(p):
    st,_,raison=_check_gf2(p,"degF")
    if st!=OK: return (st,None,raison,"_check_gf2 degF")
    if p==0: return (OK,-1,"degF(0)=-1 convention","degF nul")
    return (OK,p.bit_length()-1,"degF","degF")
def mulF(a,b):
    s1,_,r1=_check_gf2(a,"mulF a")
    if s1!=OK: return (s1,None,r1,"_check_gf2 mulF a")
    s2,_,r2=_check_gf2(b,"mulF b")
    if s2!=OK: return (s2,None,r2,"_check_gf2 mulF b")
    if a==0 or b==0: return (OK,0,"mulF nul","mulF nul")
    r=0; aa,bb=a,b
    while bb:
        if bb&1: r^=aa
        aa<<=1; bb>>=1
    return (OK,r,"mulF","mulF")
def divmodF(a,b):
    s1,_,r1=_check_gf2(a,"divmodF a")
    if s1!=OK: return (s1,None,None,r1,"_check_gf2 divmodF a")
    s2,_,r2=_check_gf2(b,"divmodF b")
    if s2!=OK: return (s2,None,None,r2,"_check_gf2 divmodF b")
    if b==0: return (ECHEC,None,None,"diviseur nul","divmodF diviseur nul")
    if a==0: return (OK,0,0,"divmodF(0,b)=(0,0)","divmodF nul")
    _,db,_,_=degF(b); q,r=0,a
    while r:
        _,dr,_,_=degF(r)
        if dr<db: break
        s=dr-db; q^=(1<<s); r^=(b<<s)
    return (OK,q,r,"divmodF","divmodF")
def modF(a,b):
    st,q,r,raison,det=divmodF(a,b)
    if st!=OK: return (st,None,raison,det)
    return (OK,r,"modF",det)
def gcdF(a,b):
    s1,_,r1=_check_gf2(a,"gcdF a")
    if s1!=OK: return (s1,None,r1,"_check_gf2 gcdF a")
    s2,_,r2=_check_gf2(b,"gcdF b")
    if s2!=OK: return (s2,None,r2,"_check_gf2 gcdF b")
    if a==0 and b==0: return (ECHEC,None,"gcdF(0,0) indefini","gcdF nuls")
    if a==0: return (OK,b,"gcdF(0,b)=b","gcdF nul")
    if b==0: return (OK,a,"gcdF(a,0)=a","gcdF nul")
    x,y=a,b
    for _ in range(10000):
        if y==0: break
        st,_,r,_,_=divmodF(x,y)
        if st!=OK: return (st,None,"gcdF divmod","gcdF divmod")
        x,y=y,r
    else: return (ECHEC,None,"gcdF limite","gcdF limite")
    return (OK,x,"gcdF","gcdF")
def derivF(p):
    st,_,raison=_check_gf2(p,"derivF")
    if st!=OK: return (st,None,raison,"_check_gf2 derivF")
    if p==0: return (OK,0,"derivF(0)=0","derivF nul")
    _,d,_,_=degF(p); r=0
    for i in range(d+1):
        if ((p>>i)&1) and (i%2==1): r^=(1<<(i-1))
    return (OK,r,"derivF","derivF")
def is_irred_rabin_strict(p):
    st,_,raison,_=_check_gf2(p,"irred")
    if st!=OK: return (st,False,raison,"_check_gf2 irred")
    if p==0: return (ECHEC,False,"irred nul","irred nul")
    _,n,_,_=degF(p)
    if n<=0: return (OK,False,"deg <=0","irred deg")
    if ((p>>n)&1)!=1: return (ECHEC,False,"irred non monique","irred monicite")
    if n==1: return (OK,True,"deg 1","irred deg1")
    if (p&1)==0: return (OK,False,"constant nul","irred constant")
    def pow_x_2n(n_):
        r=0b10
        for _ in range(n_):
            _,rr,_,_=mulF(r,r); _,_,rr2,_,_=divmodF(rr,p); r=rr2
        return r
    exp=0b10
    if pow_x_2n(n)!=exp: return (OK,False,"x^{2^n} != x","irred Rabin")
    def prime_divisors(m):
        res=[]; d=2
        while d*d<=m:
            if m%d==0:
                res.append(d)
                while m%d==0: m//=d
            d+=1 if d==2 else 2
        if m>1: res.append(m)
        return res
    for ell in prime_divisors(n):
        pw=pow_x_2n(n//ell); _,g,_,_=gcdF(pw^exp,p)
        if g!=1: return (OK,False,"pgcd !=1","irred Rabin")
    return (OK,True,"Rabin OK","irred Rabin")
def v2_int_strict(n):
    if type(n) is bool or isinstance(n,float): return (ECHEC,None,"v2_int: bool/float refuse","v2_int type")
    if not type(n) is int: return (ECHEC,None,"v2_int: non int","v2_int type")
    if n==0: return (ECHEC,None,"v2_int(0) indefini","v2_int nul")
    v,m=0,abs(n)
    while m%2==0: m//=2; v+=1
    return (OK,v,"v2","v2_int")
def valider_coeffs_int(coeffs,nom="coeffs"):
    if coeffs is None: return (NON_DET,"{} manquants".format(nom),"valider_coeffs_int absence")
    if not isinstance(coeffs,list): return (ECHEC,"{} non liste".format(nom),"valider_coeffs_int type")
    for idx,c in enumerate(coeffs):
        if isinstance(c,float) or type(c) is bool: return (ECHEC,"{}[{}] float/bool".format(nom,idx),"valider_coeffs_int type")
        if not type(c) is int: return (ECHEC,"{}[{}] non int".format(nom,idx),"valider_coeffs_int type")
    return (OK,"{} int stricts".format(nom),"valider_coeffs_int")
def poly_deg_strict(c):
    if c is None: return (NON_DET,None,"poly manquant","poly_deg_strict absence")
    if not isinstance(c,list): return (ECHEC,None,"poly non liste","poly_deg_strict type")
    if len(c)==0: return (ECHEC,None,"poly vide","poly_deg_strict vide")
    st,raison,_=valider_coeffs_int(c,"poly")
    if st!=OK: return (st,None,raison,"poly_deg_strict coeffs")
    if not any(c): return (OK,-1,"poly nul, degre -1","poly_deg_strict nul")
    d=len(c)-1
    while d>0 and c[d]==0: d-=1
    return (OK,d,"degre","poly_deg_strict")
def poly_deg_value(c):
    st,d,raison,det=poly_deg_strict(c)
    if st!=OK: raise ValueError("%s (%s)"%(raison,det))
    return d
def poly_add(a,b):
    try:
        s1,r1,d1=valider_coeffs_int(a,"poly_add a")
        if s1!=OK: return (s1,None,r1,d1)
        s2,r2,d2=valider_coeffs_int(b,"poly_add b")
        if s2!=OK: return (s2,None,r2,d2)
        if len(a)==0 or len(b)==0: return (ECHEC,None,"poly_add vide","poly_add vide")
        n=max(len(a),len(b)); r=[(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(n)]
        while len(r)>1 and r[-1]==0: r.pop()
        return (OK,r or [0],"poly_add","poly_add")
    except Exception as e: return (ECHEC,None,"Exception poly_add : %s"%e,"poly_add exception")
def poly_mul(a,b):
    try:
        s1,r1,d1=valider_coeffs_int(a,"poly_mul a")
        if s1!=OK: return (s1,None,r1,d1)
        s2,r2,d2=valider_coeffs_int(b,"poly_mul b")
        if s2!=OK: return (s2,None,r2,d2)
        if len(a)==0 or len(b)==0: return (ECHEC,None,"poly_mul vide","poly_mul vide")
        r=[0]*(len(a)+len(b)-1)
        for i,ca in enumerate(a):
            for j,cb in enumerate(b): r[i+j]+=ca*cb
        while len(r)>1 and r[-1]==0: r.pop()
        return (OK,r or [0],"poly_mul","poly_mul")
    except Exception as e: return (ECHEC,None,"Exception poly_mul : %s"%e,"poly_mul exception")
def poly_divmod_strict(a,b):
    try:
        s1,_,_=valider_coeffs_int(a,"a"); s2,_,_=valider_coeffs_int(b,"b")
        if s1!=OK: return (s1,None,None,"a invalide","poly_divmod_strict a")
        if s2!=OK: return (s2,None,None,"b invalide","poly_divmod_strict b")
        if len(a)==0 or len(b)==0: return (ECHEC,None,None,"vide","poly_divmod_strict vide")
        if not any(b): return (ECHEC,None,None,"diviseur nul","poly_divmod_strict diviseur nul")
        db=poly_deg_value(b)
        if b[db]!=1: return (ECHEC,None,None,"diviseur non monique","poly_divmod_strict monicite")
        r=list(a)
        while len(r)<len(b): r.append(0)
        q=[0]*(max(0,len(a)-db)+1)
        for k in range(len(a)-1,db-1,-1):
            if k<len(r) and r[k]!=0:
                cc=r[k]; q[k-db]=cc
                for j in range(db+1): r[k-db+j]-=cc*b[j]
        while len(r)>1 and r[-1]==0: r.pop()
        while len(q)>1 and q[-1]==0: q.pop()
        return (OK,q,r,"poly_divmod","poly_divmod_strict")
    except Exception as e: return (ECHEC,None,None,"Exception poly_divmod: %s"%e,"poly_divmod_strict exception")
def expansion_phi_adique_strict(T,phi):
    try:
        s1,_,_=valider_coeffs_int(T,"T"); s2,_,_=valider_coeffs_int(phi,"phi")
        if s1!=OK: return (s1,None,"T invalide","expansion T")
        if s2!=OK: return (s2,None,"phi invalide","expansion phi")
        if len(T)==0 or len(phi)==0: return (ECHEC,None,"vide","expansion vide")
        if not any(phi): return (ECHEC,None,"phi nul","expansion phi nul")
        sd,deg_phi,rd,dd=poly_deg_strict(phi)
        if sd!=OK: return (sd,None,rd,dd)
        if deg_phi<1: return (ECHEC,None,"phi constant","expansion phi constant")
        if phi[deg_phi]!=1: return (ECHEC,None,"phi non monique","expansion monicite")
        coeffs,reste=[],list(T)
        for _ in range(101):
            st,q,r,raison,det=poly_divmod_strict(reste,phi)
            if st!=OK: return (st,None,raison,det)
            coeffs.append(r)
            if len(q)==1 and q[0]==0: break
            reste=q
        else: return (NON_DET,None,"Limite 101 atteinte","expansion limite")
        recon,puis=[0],[1]
        for a in coeffs:
            sm,prod,rm,dm=poly_mul(a,puis)
            if sm!=OK: return (sm,None,rm,dm)
            sa,recon,ra,da=poly_add(recon,prod)
            if sa!=OK: return (sa,None,ra,da)
            sp,puis,rp,dp=poly_mul(puis,phi)
            if sp!=OK: return (sp,None,rp,dp)
        while len(recon)<len(T): recon.append(0)
        while len(recon)>1 and recon[-1]==0: recon.pop()
        t=list(T)
        while len(t)>1 and t[-1]==0: t.pop()
        if recon!=t: return (ECHEC,None,"expansion ne reconstruit pas T","expansion reconstruction")
        return (OK,coeffs,"expansion","expansion")
    except Exception as e: return (ECHEC,None,"Exception expansion: %s"%e,"expansion exception")
def v0_poly_strict(a):
    try:
        st,_,_=valider_coeffs_int(a,"a")
        if st!=OK: return (st,None,"coeffs invalides","v0 coeffs")
        if len(a)==0: return (ECHEC,None,"v0 vide","v0 vide")
        nz=[x for x in a if x!=0]
        if not nz: return (ECHEC,None,"v0(0) indefinie","v0 nul")
        vals=[]
        for x in nz:
            s2,v,_,_=v2_int_strict(x)
            if s2!=OK: return (s2,None,"v2_int","v0 v2")
            vals.append(v)
        return (OK,min(vals),"v0","v0")
    except Exception as e: return (ECHEC,None,"Exception v0: %s"%e,"v0 exception")
def normaliser_residuel(coeffs):
    try:
        st,raison,det=valider_coeffs_int(coeffs,"residuel")
        if st!=OK: return (st,None,None,raison,det)
        if len(coeffs)==0: return (ECHEC,None,None,"residuel vide","normaliser vide")
        if not any(coeffs): return (ECHEC,None,None,"residuel nul : v0 indefinie","normaliser nul")
        sv,v0,_,_=v0_poly_strict(coeffs)
        if sv!=OK: return (sv,None,None,"v0","normaliser v0")
        div=2**v0; norm=[]
        for c in coeffs:
            if c%div!=0: return (ECHEC,None,None,"coefficient non divisible par 2^v0","normaliser divisibilite")
            norm.append(c//div)
        if not any(x%2==1 for x in norm): return (ECHEC,None,None,"aucun impair apres normalisation","normaliser impair")
        if [x*div for x in norm]!=list(coeffs): return (ECHEC,None,None,"reconstruction echec","normaliser reconstruction")
        return (OK,norm,v0,"normalisation OK : v0=%d"%v0,"normaliser_residuel")
    except Exception as e: return (ECHEC,None,None,"Exception normaliser: %s"%e,"normaliser exception")
def v1_poly_strict(a,phi1,lambda1):
    try:
        if type(lambda1) is bool or isinstance(lambda1,float) or not (type(lambda1) is int or type(lambda1) is Fraction): return (ECHEC,None,ECHEC,"lambda1 bool/float/type","certification ECHEC","v1 lambda1")
        lam=to_frac_strict(lambda1,"lambda1"); s1,_,_=valider_coeffs_int(a,"a"); s2,_,_=valider_coeffs_int(phi1,"phi1")
        if s1!=OK or s2!=OK or not any(a): return (ECHEC,None,ECHEC,"a/phi1 invalide ou nul","certification ECHEC","v1 entrees")
        sv,v0phi1,_,_=v0_poly_strict(phi1)
        if sv!=OK: return (sv,None,ECHEC,"v0(phi1)","certification ECHEC","v1 v0")
        v1_phi=Fraction(v0phi1)+lam; se,coeffs,_,_=expansion_phi_adique_strict(a,phi1)
        if se!=OK: return (se,None,NON_DET,"expansion","certification NON_DET","v1 expansion")
        vals=[]
        for j,cj in enumerate(coeffs):
            if any(cj):
                sv2,v0cj,_,_=v0_poly_strict(cj)
                if sv2!=OK: return (sv2,None,ECHEC,"v0(coeff)","certification ECHEC","v1 v0")
                vals.append(Fraction(v0cj)+Fraction(j)*v1_phi)
        if not vals: return (ECHEC,None,ECHEC,"v1 aucun terme","certification ECHEC","v1 vide")
        return (OK,min(vals),NON_DET,"CALCUL_FORMEL_OK : min formel = %s"%min(vals),"CERTIFICATION_GMN NON_DET","v1")
    except Exception as e: return (ECHEC,None,ECHEC,"Exception v1: %s"%e,"certification ECHEC","v1 exception")
def red1_poly_strict(a,phi1,lambda1):
    try:
        if type(lambda1) is bool or isinstance(lambda1,float) or not (type(lambda1) is int or type(lambda1) is Fraction): return (ECHEC,None,None,None,None,ECHEC,"lambda1 bool/float/type","certification ECHEC","red1 lambda1")
        lam=to_frac_strict(lambda1,"lambda1"); e1=lam.denominator; s1,_,_=valider_coeffs_int(a,"a"); s2,_,_=valider_coeffs_int(phi1,"phi1")
        if s1!=OK or s2!=OK or not any(a): return (ECHEC,None,None,None,None,ECHEC,"a/phi1 invalide ou nul","certification ECHEC","red1 entrees")
        sv,v0phi1,_,_=v0_poly_strict(phi1)
        if sv!=OK: return (sv,None,None,None,None,ECHEC,"v0(phi1)","certification ECHEC","red1 v0")
        v1_phi=Fraction(v0phi1)+lam; se,coeffs,_,_=expansion_phi_adique_strict(a,phi1)
        if se!=OK: return (se,None,None,None,None,NON_DET,"expansion","certification NON_DET","red1 expansion")
        det=[]
        for t,ct in enumerate(coeffs):
            if any(ct):
                sv2,v0ct,_,_=v0_poly_strict(ct)
                if sv2!=OK: return (sv2,None,None,None,None,ECHEC,"v0","certification ECHEC","red1 v0")
                det.append((t,ct,Fraction(v0ct)+Fraction(t)*v1_phi))
        if not det: return (ECHEC,None,None,None,None,ECHEC,"red1 aucun terme","certification ECHEC","red1 vide")
        v1=min(d[2] for d in det); tmin=[d[0] for d in det if d[2]==v1]; t0=min(tmin)
        for t in tmin:
            if (t-t0)%e1!=0: return (ECHEC,None,None,None,None,ECHEC,"normalisation","certification ECHEC","red1 normalisation")
        if poly_deg_value(phi1)==1:
            P=0
            for (t,ct,_) in det:
                if t in tmin:
                    if len(ct)!=1 or ct[0]==0: return (ECHEC,None,None,None,None,ECHEC,"coeff","certification ECHEC","red1 coeff")
                    sv3,vv,_,_=v2_int_strict(ct[0])
                    if sv3!=OK or (ct[0]//(2**vv))%2!=1: return (ECHEC,None,None,None,None,ECHEC,"coeff normalise","certification ECHEC","red1 coeff")
                    P^=(1<<((t-t0)//e1))
            return (OK,P,t0,e1,v1,NON_DET,"CALCUL_FORMEL_OK","CERTIFICATION_GMN NON_DET","red1")
        phi_mod2=0
        for i,cc in enumerate(phi1):
            if cc%2==1: phi_mod2^=(1<<i)
        Pd={}
        for (t,ct,_) in det:
            if t in tmin:
                sn,ad,_,_,_=normaliser_residuel(ct)
                if sn!=OK: return (sn,None,None,None,None,ECHEC,"normalisation residuel","certification ECHEC","red1 normaliser")
                am=0
                for j,cc in enumerate(ad):
                    if cc%2==1: am^=(1<<j)
                sm,coeff,_,_=modF(am,phi_mod2) if phi_mod2!=0 else (OK,am,"","")
                if sm!=OK: return (sm,None,None,None,None,ECHEC,"mod","certification ECHEC","red1 mod")
                e=(t-t0)//e1; Pd[e]=Pd.get(e,0)^coeff
        return (OK,Pd,t0,e1,v1,NON_DET,"CALCUL_FORMEL_OK","CERTIFICATION_GMN NON_DET","red1")
    except Exception as e: return (ECHEC,None,None,None,None,ECHEC,"Exception red1: %s"%e,"certification ECHEC","red1 exception")
def valider_points_polygone(points):
    try:
        if points is None: return (NON_DET,"points manquants","valider_points absence")
        if not isinstance(points,list) or len(points)==0: return (ECHEC,"points non liste ou vide","valider_points type")
        prev=None
        for idx,pt in enumerate(points):
            if not isinstance(pt,tuple) or len(pt)!=2: return (ECHEC,"point %d incomplet"%idx,"valider_points structure")
            x,y=pt
            if isinstance(x,float) or type(x) is bool or not type(x) is int: return (ECHEC,"abscisse %d invalide"%idx,"valider_points abscisse")
            if isinstance(y,float) or type(y) is bool or not (type(y) is int or type(y) is Fraction): return (ECHEC,"ordonnee %d invalide"%idx,"valider_points ordonnee")
            if prev is not None and (x==prev or x<prev): return (ECHEC,"abscisses non strictement croissantes","valider_points ordre")
            prev=x
        return (OK,"points valides","valider_points")
    except Exception as e: return (ECHEC,"Exception valider_points: %s"%e,"valider_points exception")
def calculer_enveloppe_inf(points):
    try:
        st,_,_=valider_points_polygone(points)
        if st!=OK: return (st,None,"points invalides","enveloppe points")
        hull=[]
        for p in points:
            while len(hull)>=2:
                x1,y1=hull[-2]; x2,y2=hull[-1]; x3,y3=p
                if Fraction(y2-y1,x2-x1)>=Fraction(y3-y2,x3-x2): hull.pop()
                else: break
            hull.append(p)
        s2,r2,d2=valider_points_polygone(hull)
        if s2!=OK: return (s2,None,r2,d2)
        return (OK,hull,"enveloppe","enveloppe")
    except Exception as e: return (ECHEC,None,"Exception enveloppe: %s"%e,"enveloppe exception")
def residuel_ordre1_strict(phi,T):
    try:
        s1,_,_=valider_coeffs_int(phi,"phi"); s2,_,_=valider_coeffs_int(T,"T")
        if s1!=OK or s2!=OK or not any(phi): return (ECHEC,None,ECHEC,"phi/T invalide","certification ECHEC","residuel entrees")
        se,coeffs,_,_=expansion_phi_adique_strict(T,phi)
        if se!=OK: return (se,None,NON_DET,"expansion","certification NON_DET","residuel expansion")
        d=poly_deg_value(phi); pts=[]
        for i,a in enumerate(coeffs):
            if any(a):
                sv,v0a,_,_=v0_poly_strict(a)
                if sv!=OK: return (sv,None,ECHEC,"v0","certification ECHEC","residuel v0")
                pts.append((i,Fraction(v0a)))
        sh,hull,_=calculer_enveloppe_inf(pts)
        if sh!=OK: return (sh,None,ECHEC,"enveloppe","certification ECHEC","residuel enveloppe")
        segs=[]
        for k in range(len(hull)-1):
            x0,y0=hull[k]; x1,y1=hull[k+1]; L=x1-x0; Hh=y0-y1; dd=math.gcd(L,Hh) if Hh!=0 else L; e=L//dd if dd else L; pente=Fraction(-Hh,L)
            if d==1:
                res=0
                for i in range(x0,x1+1):
                    y_exp=Fraction(y0)-Fraction(Hh*(i-x0),L)
                    if y_exp.denominator==1 and (i,int(y_exp)) in pts and (i-x0)%e==0: res^=(1<<((i-x0)//e))
                segs.append((x0,x1,pente,res))
            else:
                phi_mod2=0
                for i,cc in enumerate(phi):
                    if cc%2==1: phi_mod2^=(1<<i)
                rl=[]
                for i in range(x0,x1+1):
                    y_exp=Fraction(y0)-Fraction(Hh*(i-x0),L)
                    if y_exp.denominator==1 and (i,int(y_exp)) in pts and (i-x0)%e==0:
                        sn,ad,_,_,_=normaliser_residuel(coeffs[i])
                        if sn!=OK: return (sn,None,ECHEC,"normalisation","certification ECHEC","residuel normaliser")
                        am=0
                        for j,cc in enumerate(ad):
                            if cc%2==1: am^=(1<<j)
                        sm,coeff,_,_=modF(am,phi_mod2) if phi_mod2!=0 else (OK,am,"","")
                        rl.append(((i-x0)//e,coeff))
                segs.append((x0,x1,pente,rl))
        return (OK,segs,NON_DET,"CALCUL_FORMEL_OK : polygone formel, CANDIDAT_GMN","CERTIFICATION_GMN NON_DET","residuel")
    except Exception as e: return (ECHEC,None,ECHEC,"Exception residuel: %s"%e,"certification ECHEC","residuel exception")
def valider_v2_gmn(coeffs,preuve_locale,representation):
    try:
        if coeffs is None: return (NON_DET,None,"b_j manquant","valider_v2_gmn absence")
        if representation is None: return (NON_DET,None,"representation manquante","valider_v2_gmn representation")
        sc,_,_=valider_coeffs_int(coeffs,"b_j")
        if sc!=OK or len(coeffs)==0 or not any(coeffs): return (sc if sc!=OK else ECHEC,None,"b_j invalide/vide/nul","valider_v2_gmn coeffs")
        sf,val_f,rf,df=_flag("CALCUL_LOCAL_EFFECTIF_IMPLEMENTE")
        if sf!=OK: return (sf,None,rf,df)
        if not val_f: return (NON_DET,None,"calcul local non implemente","valider_v2_gmn calcul_local_manquant")
        return (NON_DET,None,"calcul local non justifie","valider_v2_gmn")
    except Exception as e: return (ECHEC,None,"Exception valider_v2_gmn: %s"%e,"valider_v2_gmn exception")
def calculer_u_j_arithmetique(v2_bj,j,v2_phi2,prov_bj,prov_phi2):
    try:
        if v2_bj is None or v2_phi2 is None or j is None: return (NON_DET,None,NON_DET,"donnee manquante","interpretation GMN NON_DET","calculer_u_j absence")
        for nom,val in [("v2_bj",v2_bj),("j",j),("v2_phi2",v2_phi2)]:
            if isinstance(val,float) or type(val) is bool or not (type(val) is int or type(val) is Fraction): return (ECHEC,None,ECHEC,"%s float/bool/type"%nom,"interpretation GMN ECHEC","calculer_u_j type")
        if type(j) is not int or j<0: return (ECHEC,None,ECHEC,"j entier >=0 exige","interpretation GMN ECHEC","calculer_u_j j")
        u=to_frac_strict(v2_bj,"v2_bj")+Fraction(j)*to_frac_strict(v2_phi2,"v2_phi2")
        return (OK,u,NON_DET,"arithmetique OK : %s"%u,"interpretation GMN NON_DET : provenance non demontree","calculer_u_j")
    except Exception as e: return (ECHEC,None,ECHEC,"Exception calculer_u_j: %s"%e,"interpretation GMN ECHEC","calculer_u_j exception")
def valider_structure_bj_list(lst):
    try:
        if lst is None: return (NON_DET,"coeffs b_j manquants","structure_bj absence")
        if not isinstance(lst,list): return (ECHEC,"coeffs b_j non liste","structure_bj type")
        for j,bj in enumerate(lst):
            if bj is None: return (NON_DET,"b_j manquant j=%d"%j,"structure_bj absence")
            st,_,_=valider_coeffs_int(bj,"b_j j=%d"%j)
            if st!=OK: return (st,"b_j j=%d invalide"%j,"structure_bj")
        return (OK,"structure b_j valide","structure_bj")
    except Exception as e: return (ECHEC,"Exception structure_bj: %s"%e,"structure_bj exception")
def valider_types_uj_list(lst):
    try:
        if lst is None: return (NON_DET,"u_j manquants","types_uj absence")
        if not isinstance(lst,list): return (ECHEC,"u_j non liste","types_uj type")
        for j,uj in enumerate(lst):
            if uj is None: continue
            if type(uj) is bool or isinstance(uj,float) or not (type(uj) is int or type(uj) is Fraction): return (ECHEC,"u_j j=%d bool/float/type"%j,"types_uj type")
        return (OK,"types u_j valides","types_uj")
    except Exception as e: return (ECHEC,"Exception types_uj: %s"%e,"types_uj exception")
def valider_ordonnees_gmn(coeffs_bj_list,phi2,u_j_list,preuve_bj,representation,preuve_phi2):
    try:
        ss,rs,ds=valider_structure_bj_list(coeffs_bj_list)
        if ss!=OK: return (ss,"STRUCTURE : "+rs,ds)
        st,rt,dt=valider_types_uj_list(u_j_list)
        if st!=OK: return (st,"TYPES : "+rt,dt)
        if len(coeffs_bj_list)!=len(u_j_list): return (ECHEC,"STRUCTURE : longueurs incoherentes","ordonnees longueurs")
        for j,(bj,uj) in enumerate(zip(coeffs_bj_list,u_j_list)):
            if all(c==0 for c in bj) and uj is not None: return (ECHEC,"b_j=0 mais u_j non None j=%d"%j,"ordonnees b_j nul")
        for j,(bj,uj) in enumerate(zip(coeffs_bj_list,u_j_list)):
            if all(c==0 for c in bj): continue
            sv,_,rv,dv=valider_v2_gmn(bj,preuve_bj,representation)
            if sv!=OK: return (sv,"VERROU AMONT CERTIFICATION : v2(b_j) j=%d : %s ; couple NON VERIFIE"%(j,rv),"ordonnees verrou amont v2")
            if uj is None: return (NON_DET,"u_j manquant j=%d"%j,"ordonnees u_j absence")
        return (OK,"ordonnees GMN verifiees","ordonnees")
    except Exception as e: return (ECHEC,"Exception ordonnees: %s"%e,"ordonnees exception")
def valider_t1(s1,ell1,u_j,e1,t1_propose,hypotheses,exige_integrite,exige_positivite,provenance):
    try:
        if type(exige_integrite) is not bool or type(exige_positivite) is not bool: return (ECHEC,None,ECHEC,"exige_* type non bool","certification ECHEC","t1 exige type")
        if e1 is None: return (NON_DET,None,NON_DET,"e1 manquant","certification NON_DET","t1 e1 absence")
        if isinstance(e1,float) or type(e1) is bool or not type(e1) is int or e1<=0: return (ECHEC,None,ECHEC,"e1 float/bool/non int/<=0","certification ECHEC","t1 e1")
        for nom,val in [("s1",s1),("ell1",ell1),("u_j",u_j)]:
            if val is None: return (NON_DET,None,NON_DET,"%s manquant"%nom,"certification NON_DET","t1 %s absence"%nom)
            if isinstance(val,float) or type(val) is bool or not (type(val) is int or type(val) is Fraction): return (ECHEC,None,ECHEC,"%s float/bool/type"%nom,"certification ECHEC","t1 %s type"%nom)
        if t1_propose is None: return (NON_DET,None,NON_DET,"t1 propose manquant","certification NON_DET","t1 propose absence")
        if isinstance(t1_propose,float) or type(t1_propose) is bool or not (type(t1_propose) is int or type(t1_propose) is Fraction): return (ECHEC,None,ECHEC,"t1 propose float/bool/type","certification ECHEC","t1 propose type")
        resF=(to_frac_strict(s1,"s1")-to_frac_strict(ell1,"ell1")*to_frac_strict(u_j,"u_j"))/Fraction(e1)
        if exige_integrite and resF.denominator!=1: return (ECHEC,None,ECHEC,"t1 non entier %s"%resF,"certification ECHEC","t1 integrite")
        if exige_positivite and resF<0: return (ECHEC,None,ECHEC,"t1 negatif %s"%resF,"certification ECHEC","t1 positivite")
        if to_frac_strict(t1_propose,"t1")!=resF: return (ECHEC,None,ECHEC,"t1 propose != exact %s"%resF,"certification ECHEC","t1 recalcul")
        if hypotheses is not True: return (OK,resF,NON_DET,"calcul exact OK : t1 = %s"%resF,"certification NON_DET : hypotheses non etablies","t1 hypotheses")
        if provenance is None: return (OK,resF,NON_DET,"calcul exact OK","certification NON_DET : provenance manquante","t1 provenance")
        return (OK,resF,NON_DET,"calcul exact OK","certification NON_DET : True != preuve","t1 certification")
    except Exception as e: return (ECHEC,None,ECHEC,"Exception t1: %s"%e,"certification ECHEC","t1 exception")
def verifier_convention_historique(): return (NON_DET,"Convention historique NON DETERMINE : documentation independante manquante.")
def parser_strict_fichier_T(texte):
    try:
        if texte is None: return (NON_DET,None,"Fichier absent : NON_DET","parser absence")
        if not isinstance(texte,str): return (ECHEC,None,"texte non str","parser type")
        lignes=[l.strip() for l in texte.splitlines()]; has_c=any(l.startswith("c_") for l in lignes); has_H=any(l.startswith("H=") for l in lignes)
        if has_H and not has_c: return (NON_DET,None,"Forme H= : reconstruction non etablie","parser H=")
        coeffs={}
        for line in lignes:
            if line=="" or line.startswith("#") or line.startswith("HEADER:"): continue
            if line.startswith("c_"):
                m=re.match(r"^c_(\d+)=(-?\d+)$",line)
                if not m: return (ECHEC,None,"Ligne mal formee : %r"%line,"parser malforme")
                idx=int(m.group(1))
                if idx<0 or idx>39: return (ECHEC,None,"Indice hors plage c_%d"%idx,"parser hors plage")
                if idx in coeffs: return (ECHEC,None,"Indice duplique c_%d"%idx,"parser duplique")
                coeffs[idx]=int(m.group(2))
            else: return (ECHEC,None,"Ligne inconnue : %r"%line,"parser inconnue")
        if len(coeffs)!=40: return (ECHEC,None,"Coefficients manquants : %d/40"%len(coeffs),"parser manquant")
        if sorted(coeffs.keys())!=list(range(40)): return (ECHEC,None,"Indices c_0..c_39 non exacts","parser indices")
        c=[coeffs[i] for i in range(40)]; st,_,_=valider_coeffs_int(c,"T")
        if st!=OK: return (st,None,"coeffs T invalides","parser coeffs")
        return (OK,c,"parseur strict OK","parser")
    except Exception as e: return (ECHEC,None,"Exception parser: %s"%e,"parser exception")
def verifier_resultat_parseur(attendu,obtenu):
    if attendu is None: return obtenu is None
    return obtenu==attendu
def valider_authenticite_T(coeffs,sha_attendu):
    try:
        sc,dc=verifier_convention_historique()
        if sc!=OK: return (NON_DET,"authenticite = NON DETERMINE : %s"%dc,"authenticite convention")
        if coeffs is None or not isinstance(coeffs,list) or len(coeffs)!=40: return (ECHEC,"coeffs manquants/longueur !=40","authenticite longueur")
        st,_,_=valider_coeffs_int(coeffs,"T")
        if st!=OK or poly_deg_value(coeffs)!=39 or coeffs[39]!=1: return (ECHEC,"coeffs/degre/monicite","authenticite structure")
        ser="\n".join(str(coeffs[i]) for i in range(39,-1,-1))+"\n"
        if hashlib.sha256(ser.encode("utf-8")).hexdigest()!=sha_attendu: return (ECHEC,"SHA != attendu","authenticite SHA")
        return (OK,"authentification OK","authenticite")
    except Exception as e: return (ECHEC,"Exception authentification: %s"%e,"authenticite exception")
def valider_sha_avec_convention_test(coeffs,sha_attendu,convention_nom):
    try:
        if coeffs is None or not isinstance(coeffs,list) or len(coeffs)!=40: return (ECHEC,"longueur !=40","SHA test longueur")
        st,_,_=valider_coeffs_int(coeffs,"T")
        if st!=OK or poly_deg_value(coeffs)!=39 or coeffs[39]!=1: return (ECHEC,"structure","SHA test structure")
        ser="\n".join(str(coeffs[i]) for i in range(39,-1,-1))+"\n"
        if hashlib.sha256(ser.encode("utf-8")).hexdigest()!=sha_attendu: return (ECHEC,"SHA != attendu (convention test %s)"%convention_nom,"SHA test SHA")
        return (OK,"SHA OK avec convention test %s (non historique)"%convention_nom,"SHA test")
    except Exception as e: return (ECHEC,"Exception SHA test: %s"%e,"SHA test exception")
def valider_structure_polynome(poly,nom):
    try:
        if poly is None: return (NON_DET,"%s manquant"%nom,"structure absence")
        if not isinstance(poly,list) or len(poly)==0: return (ECHEC,"%s non liste/vide"%nom,"structure type")
        st,_,_=valider_coeffs_int(poly,nom)
        if st!=OK or not any(poly): return (st if st!=OK else ECHEC,"%s coeffs/nul"%nom,"structure coeffs")
        deg=poly_deg_value(poly)
        if poly[deg]!=1: return (ECHEC,"%s non monique"%nom,"structure monicite")
        return (OK,"%s valide deg %d monique"%(nom,deg),"structure")
    except Exception as e: return (ECHEC,"Exception structure %s: %s"%(nom,e),"structure exception")
def certifier_phi2_strict(phi1,lambda1,psi1,phi2,exigee,documentee,preuve_locale,pente_fournie=_SENTINELLE,residuel_fourni=_SENTINELLE,invariant_fourni=True):
    try:
        # ETAPE A : entrees, types exacts, absences, denominateurs, structures listes, exigee bool exact
        if phi1 is None or lambda1 is None or psi1 is None or phi2 is None: return (ECHEC,{"raison":"ETAPE A entree absente : phi1/lambda1/psi1/phi2 None","detecteur":"certifier_phi2 absence","resultat":None})
        if type(exigee) is not bool: return (ECHEC,{"raison":"ETAPE A exigee type non bool : %r"%(exigee,),"detecteur":"certifier_phi2 exigee","resultat":None})
        if type(lambda1) is bool or isinstance(lambda1,float) or isinstance(lambda1,str): return (ECHEC,{"raison":"ETAPE A lambda1 bool/float/chaine","detecteur":"certifier_phi2 lambda1","resultat":None})
        if isinstance(lambda1,tuple):
            if len(lambda1)!=2: return (ECHEC,{"raison":"ETAPE A lambda1 tuple mal forme","detecteur":"certifier_phi2 lambda1 denominateur","resultat":None})
            num,den=lambda1
            if type(den) is bool or isinstance(den,float) or isinstance(den,str) or not type(den) is int: return (ECHEC,{"raison":"ETAPE A denominateur mal type","detecteur":"certifier_phi2 lambda1 denominateur","resultat":None})
            if den==0: return (ECHEC,{"raison":"ETAPE A denominateur nul","detecteur":"certifier_phi2 lambda1 denominateur","resultat":None})
            if type(num) is bool or isinstance(num,float) or isinstance(num,str) or not type(num) is int: return (ECHEC,{"raison":"ETAPE A numerateur mal type","detecteur":"certifier_phi2 lambda1 numerateur","resultat":None})
            lam=Fraction(num,den)
        elif type(lambda1) is int or type(lambda1) is Fraction: lam=to_frac_strict(lambda1,"lambda1")
        else: return (ECHEC,{"raison":"ETAPE A lambda1 type inattendu","detecteur":"certifier_phi2 lambda1","resultat":None})
        if pente_fournie is not _SENTINELLE:
            if type(pente_fournie) is bool or isinstance(pente_fournie,float) or isinstance(pente_fournie,str) or not type(pente_fournie) is Fraction: return (ECHEC,{"raison":"ETAPE A pente mal typee : Fraction exacte exigee","detecteur":"certifier_phi2 pente","resultat":None})
        if residuel_fourni is not _SENTINELLE:
            if type(residuel_fourni) is bool: return (ECHEC,{"raison":"ETAPE A residuel bool","detecteur":"certifier_phi2 residuel","resultat":None})
            if isinstance(residuel_fourni,float): return (ECHEC,{"raison":"ETAPE A residuel float","detecteur":"certifier_phi2 residuel","resultat":None})
            if not type(residuel_fourni) is int: return (ECHEC,{"raison":"ETAPE A residuel type inattendu","detecteur":"certifier_phi2 residuel","resultat":None})
        if type(psi1) is bool or isinstance(psi1,float) or isinstance(psi1,str) or not type(psi1) is int: return (ECHEC,{"raison":"ETAPE A psi1 mal forme : int exact exige","detecteur":"certifier_phi2 psi1","resultat":None})
        if psi1==0: return (ECHEC,{"raison":"ETAPE A psi1 nul","detecteur":"certifier_phi2 psi1","resultat":None})
        if not isinstance(phi1,list) or not isinstance(phi2,list): return (ECHEC,{"raison":"ETAPE A phi1/phi2 non listes","detecteur":"certifier_phi2 structure","resultat":None})
        if len(phi1)==0 or len(phi2)==0: return (ECHEC,{"raison":"ETAPE A phi1/phi2 vides","detecteur":"certifier_phi2 structure","resultat":None})
        s1,_,_=valider_coeffs_int(phi1,"phi1")
        if s1!=OK: return (ECHEC,{"raison":"ETAPE A phi1 coeffs invalides","detecteur":"certifier_phi2 phi1","resultat":None})
        s2,_,_=valider_coeffs_int(phi2,"phi2")
        if s2!=OK: return (ECHEC,{"raison":"ETAPE A phi2 coeffs invalides","detecteur":"certifier_phi2 phi2","resultat":None})
        if not any(phi1) or not any(phi2): return (ECHEC,{"raison":"ETAPE A phi1/phi2 nuls","detecteur":"certifier_phi2 structure","resultat":None})
        # ETAPE B : algebrique structurel, avant tout verrou
        deg1=poly_deg_value(phi1); deg2=poly_deg_value(phi2)
        if phi1[deg1]!=1: return (ECHEC,{"raison":"ETAPE B phi1 non monique","detecteur":"certifier_phi2 phi1 monicite","resultat":None})
        if phi2[deg2]!=1: return (ECHEC,{"raison":"ETAPE B phi2 non monique","detecteur":"certifier_phi2 phi2 monicite","resultat":None})
        if deg1!=1: return (ECHEC,{"raison":"ETAPE B degre phi1 incorrect : %d != 1"%deg1,"detecteur":"certifier_phi2 phi1 degre","resultat":None})
        if deg2!=1: return (ECHEC,{"raison":"ETAPE B degre phi2 incorrect : %d != 1"%deg2,"detecteur":"certifier_phi2 phi2 degre","resultat":None})
        _,f1,_,_=degF(psi1)
        if f1<=0: return (ECHEC,{"raison":"ETAPE B psi1 degre invalide","detecteur":"certifier_phi2 psi1","resultat":None})
        if deg2!=deg1*f1: return (ECHEC,{"raison":"ETAPE B relation degres incorrecte : deg2 %d != deg1*f1 %d"%(deg2,deg1*f1),"detecteur":"certifier_phi2 degres relation","resultat":None})
        if ((psi1>>f1)&1)!=1: return (ECHEC,{"raison":"ETAPE B psi1 non monique","detecteur":"certifier_phi2 psi1 monicite","resultat":None})
        diff=[phi2[i]-(phi1[i] if i<len(phi1) else 0) for i in range(max(len(phi2),len(phi1)))]
        while len(diff)>1 and diff[-1]==0: diff.pop()
        if poly_deg_value(diff)!=0 or diff[0]==0: return (ECHEC,{"raison":"ETAPE B difference phi2-phi1 incorrecte : non constante ou nulle","detecteur":"certifier_phi2 difference","resultat":None})
        sv2,v2d,_,_=v2_int_strict(diff[0])
        if sv2!=OK or v2d!=lam.numerator or abs(diff[0])//(2**lam.numerator)%2!=1: return (ECHEC,{"raison":"ETAPE B v2(difference) != h1 ou d pair","detecteur":"certifier_phi2 difference v2","resultat":None})
        se,exp,de,dede=expansion_phi_adique_strict(phi2,phi1)
        if se!=OK: return (se,{"raison":"ETAPE B expansion : "+de,"detecteur":dede,"resultat":None})
        pts=[]
        for i,a in enumerate(exp):
            if any(a):
                sv,v0a,_,_=v0_poly_strict(a)
                if sv!=OK: return (sv,{"raison":"ETAPE B v0","detecteur":"certifier_phi2 v0","resultat":None})
                pts.append((i,Fraction(v0a)))
        sh,hull,_=calculer_enveloppe_inf(pts)
        if sh!=OK or len(hull)!=2: return (ECHEC,{"raison":"ETAPE B polygone != 2 sommets","detecteur":"certifier_phi2 polygone","resultat":None})
        (x0,y0),(x1,y1)=hull[0],hull[1]
        if x1==x0: return (ECHEC,{"raison":"ETAPE B pente division par zero","detecteur":"certifier_phi2 pente","resultat":None})
        pente_calculee=Fraction(-(y0-y1),x1-x0)
        if pente_calculee!=Fraction(-lam): return (ECHEC,{"raison":"ETAPE B pente %s != -lambda1 %s"%(pente_calculee,-lam),"detecteur":"certifier_phi2 pente","resultat":None})
        if pente_fournie is not _SENTINELLE and pente_fournie!=pente_calculee: return (ECHEC,{"raison":"ETAPE B pente fournie != pente calculee","detecteur":"certifier_phi2 pente","resultat":None})
        sr,segs,scr,rr,rcr,dr=residuel_ordre1_strict(phi1,phi2)
        if sr!=OK: return (sr,{"raison":"ETAPE B residuel : "+rr,"detecteur":dr,"resultat":None})
        if len(segs)!=1: return (ECHEC,{"raison":"ETAPE B segments residuel != 1","detecteur":"certifier_phi2 residuel","resultat":None})
        _,_,_,res_phi2=segs[0]
        if type(res_phi2) is bool or not type(res_phi2) is int: return (ECHEC,{"raison":"ETAPE B residuel bool/non int","detecteur":"certifier_phi2 residuel","resultat":None})
        if res_phi2!=psi1: return (ECHEC,{"raison":"ETAPE B residuel %s != psi1 %s"%(res_phi2,psi1),"detecteur":"certifier_phi2 residuel","resultat":None})
        if residuel_fourni is not _SENTINELLE and residuel_fourni!=res_phi2: return (ECHEC,{"raison":"ETAPE B residuel fourni != residuel calcule","detecteur":"certifier_phi2 residuel","resultat":None})
        if invariant_fourni is not True: return (ECHEC,{"raison":"ETAPE B invariant incorrect : invariant_fourni != True","detecteur":"certifier_phi2 invariant","resultat":None})
        if documentee is not True: return (ECHEC,{"raison":"ETAPE B construction psi1 non documentee","detecteur":"certifier_phi2 invariant","resultat":None})
        if exigee:
            si,est_irr,ri,_=is_irred_rabin_strict(psi1)
            if si!=OK or not est_irr: return (ECHEC,{"raison":"ETAPE B psi1 irreductibilite : "+ri,"detecteur":"certifier_phi2 invariant","resultat":None})
        if lam.denominator!=1: return (ECHEC,{"raison":"ETAPE B e1 != 1 : cas general non demontre dans ce chemin","detecteur":"certifier_phi2 e1","resultat":None})
        # ETAPE C : verrou seulement apres B
        sf,val_f,rf,df=_flag("CALCUL_LOCAL_EFFECTIF_IMPLEMENTE")
        if sf!=OK: return (sf,{"raison":rf,"detecteur":df,"resultat":None})
        if not val_f: return (NON_DET,{"raison":"ETAPE C VERROU calcul local non implemente : structure valide, certification impossible","detecteur":"certifier_phi2 calcul_local_manquant","resultat":None})
        return (NON_DET,{"raison":"CERTIFICATION GMN NON_DET : hypotheses non etablies","detecteur":"certifier_phi2 certification","resultat":None})
    except Exception as e: return (ECHEC,{"raison":"Exception certifier_phi2: %s"%e,"detecteur":"certifier_phi2 exception","resultat":None})
def valider_collection_identifiants(collection):
    try:
        if collection is None: return (ECHEC,None,"collection None refusee","identites collection None")
        if type(collection) is bool: return (ECHEC,None,"collection bool refusee","identites collection bool")
        if isinstance(collection,str): return (ECHEC,None,"collection chaine refusee : liste exigee","identites collection chaine")
        if not isinstance(collection,list): return (ECHEC,None,"collection type non autorise","identites collection type")
        if len(collection)==0: return (ECHEC,None,"collection vide : au moins une branche exigee","identites collection vide")
        if len(set([str(x) for x in collection]))!=len(collection): return (ECHEC,None,"identifiant duplique","identites duplique")
        for x in collection:
            if type(x) is not str: return (ECHEC,None,"identifiant non-string : %r"%(x,),"identites type")
            if len(x)==0: return (ECHEC,None,"identifiant vide","identites vide")
            if len(x.strip())==0: return (ECHEC,None,"identifiant espaces seuls","identites espaces")
            if " " in x or "\t" in x or "\n" in x: return (ECHEC,None,"identifiant contient un espace : politique espaces interdits","identites espaces")
            if x!=x.strip(): return (ECHEC,None,"identifiant espaces en bord","identites espaces")
        return (OK,list(collection),"collection valide","identites")
    except Exception as e: return (ECHEC,None,"Exception collection: %s"%e,"identites exception")
def valider_identites_branches(perimetre,branches):
    try:
        if perimetre is None: return (NON_DET,"perimetre manquant","identites perimetre absence")
        if not isinstance(perimetre,dict): return (ECHEC,"perimetre non dict","identites perimetre type")
        if "identifiants_branches_attendus" not in perimetre: return (ECHEC,"identifiants_branches_attendus absents : source canonique manquante","identites absence")
        attendus=perimetre["identifiants_branches_attendus"]; sc,canon,rc,dc=valider_collection_identifiants(attendus)
        if sc!=OK: return (sc,rc,dc)
        derive=len(canon)
        if "branches_attendues" in perimetre:
            hist=perimetre["branches_attendues"]
            if type(hist) is bool or not type(hist) is int: return (ECHEC,"branches_attendues historique type non int","identites historique type")
            if hist!=derive: return (ECHEC,"incoherence historique : branches_attendues %d != derive %d"%(hist,derive),"identites historique incoherence")
        if branches is None: return (NON_DET,"branches manquantes","identites branches absence")
        if not isinstance(branches,dict): return (ECHEC,"branches non dict","identites branches type")
        sc2,fournis_list,rc2,dc2=valider_collection_identifiants(list(branches.keys()))
        if sc2!=OK: return (sc2,rc2,dc2)
        fournis=set(fournis_list); voulu=set(canon); manquantes=sorted(voulu-fournis); supplementaires=sorted(fournis-voulu)
        if manquantes: return (ECHEC,"branches manquantes : %s"%manquantes,"identites manquantes")
        if supplementaires: return (ECHEC,"branches supplementaires : %s"%supplementaires,"identites supplementaires")
        return (OK,"identites exactes : structure coherente, exhaustivite NON demontree","identites")
    except Exception as e: return (ECHEC,"Exception identites branches: %s"%e,"identites exception")
def valider_perimetre_strict(perimetre,branches):
    try:
        if perimetre is None: return (NON_DET,"perimetre manquant","perimetre absence")
        if not isinstance(perimetre,dict): return (ECHEC,"perimetre non dict","perimetre type")
        if "couverture_demonteree" not in perimetre: return (ECHEC,"perimetre cle manquante couverture_demonteree","perimetre structure")
        if type(perimetre["couverture_demonteree"]) is not bool: return (ECHEC,"couverture_demonteree type non bool","perimetre couverture type")
        si,ri,di=valider_identites_branches(perimetre,branches)
        if si!=OK: return (si,ri,di)
        return (OK,"perimetre canonique valide ; couverture NON demontree","perimetre")
    except Exception as e: return (ECHEC,"Exception perimetre: %s"%e,"perimetre exception")
def verifier_branches_completes(branches,perimetre,hypotheses_gmn):
    try:
        if type(hypotheses_gmn) is not bool: return (ECHEC,None,"hypotheses_gmn type non bool","branches hypotheses_gmn type")
        if branches is None: return (NON_DET,None,"branches manquantes","branches absence")
        if perimetre is None: return (NON_DET,None,"perimetre non defini","branches perimetre")
        if not isinstance(branches,dict) or len(branches)==0: return (ECHEC,None,"branches non dict/vide","branches type")
        for nom,b in branches.items():
            if isinstance(b,str): return (ECHEC,None,"branche %s remplacee par une chaine"%nom,"branches chaine")
            if isinstance(b,list): return (ECHEC,None,"branche %s remplacee par une liste"%nom,"branches liste")
            if b is None: return (ECHEC,None,"branche %s None"%nom,"branches None")
            if type(b) is bool: return (ECHEC,None,"branche %s booleen"%nom,"branches booleen")
            if type(b) is int: return (ECHEC,None,"branche %s entier"%nom,"branches entier")
            if not isinstance(b,dict): return (ECHEC,None,"branche %s non dict"%nom,"branches structure")
            for cle in ["degre","pente","multiplicite","residuel","hypotheses"]:
                if cle not in b: return (ECHEC,None,"branche %s cle manquante %s"%(nom,cle),"branches champ absent")
            if type(b["degre"]) is bool: return (ECHEC,None,"branche %s degre bool"%nom,"branches degre bool")
            if isinstance(b["degre"],float) or not type(b["degre"]) is int or b["degre"]<=0: return (ECHEC,None,"branche %s degre invalide"%nom,"branches degre")
            if isinstance(b["pente"],float) or not type(b["pente"]) is Fraction: return (ECHEC,None,"branche %s pente float/non Fraction"%nom,"branches pente")
            if type(b["multiplicite"]) is bool or isinstance(b["multiplicite"],float) or not type(b["multiplicite"]) is int or b["multiplicite"]<=0: return (ECHEC,None,"branche %s multiplicite invalide"%nom,"branches multiplicite")
            if type(b["residuel"]) is bool or isinstance(b["residuel"],float) or not type(b["residuel"]) is int: return (ECHEC,None,"branche %s residuel invalide"%nom,"branches residuel")
            if type(b["hypotheses"]) is not bool: return (ECHEC,None,"branche %s hypotheses mal typees"%nom,"branches hypotheses type")
        sp,rp,dp=valider_perimetre_strict(perimetre,branches)
        if sp!=OK: return (sp,None,rp,dp)
        sf,val_f,rf,df=_flag("ENUMERATION_BRANCHES_EFFECTIVE")
        if sf!=OK: return (sf,None,rf,df)
        if not val_f: return (NON_DET,None,"verrou branches : identites exactes, calcul formel non certifie, couverture NON demontree, certification NON etablie. Bool True != preuve.","branches verrou")
        return (NON_DET,None,"exhaustivite non demontree","branches verrou")
    except Exception as e: return (ECHEC,None,"Exception branches: %s"%e,"branches exception")
def audit_ordre2(phi2,coeffs_bj,u_j_list,residuel_ordre2,hypotheses_gmn):
    try:
        if phi2 is None or coeffs_bj is None or u_j_list is None or residuel_ordre2 is None: return (NON_DET,"donnees ordre 2 manquantes","ordre2 absence")
        if hypotheses_gmn is not True: return (NON_DET,"hypotheses GMN ordre 2 non etablies","ordre2 hypotheses")
        return (NON_DET,"ordre 2 non acheve","ordre2")
    except Exception as e: return (ECHEC,"Exception ordre2: %s"%e,"ordre2 exception")
def detecte_fragment_markdown(texte):
    try:
        if texte is None or not isinstance(texte,str): return False
        marqueur=chr(96)+chr(96)+chr(96); return marqueur in texte
    except Exception: return False
def verifier_integrite_source():
    try:
        chemin=os.path.abspath(__file__)
        with open(chemin,"r",encoding="utf-8") as fh: contenu=fh.read()
        lignes=contenu.splitlines(); marqueur=chr(96)+chr(96)+chr(96); marqueurs=[(i+1,l) for i,l in enumerate(lignes) if marqueur in l]
        if marqueurs: return (ECHEC,"fragments Markdown : %s"%marqueurs,"integrite markdown")
        try: py_compile.compile(chemin,doraise=True)
        except Exception as e: return (ECHEC,"py_compile echec : %s"%e,"integrite py_compile")
        if detecte_fragment_markdown("a "+marqueur+"python b") is not True: return (ECHEC,"fragment injecte NON detecte","integrite test negatif")
        if detecte_fragment_markdown("texte propre") is not False: return (ECHEC,"detecteur fragment incoherent","integrite detecteur")
        return (OK,"integrite : lecture OK, aucun fragment, py_compile OK, fragment injecte detecte","integrite")
    except Exception as e: return (ECHEC,"Exception integrite: %s"%e,"integrite exception")
def main():
    debut=datetime.datetime.now(); fonctions=[]; exceptions=[]; resultats=[]
    def ajouter(nom,statut,detail="",obligatoire=True,raison="",detecteur="",categorie=NON_DET):
        try: r=Resultat(nom,statut,detail,obligatoire,raison,detecteur,categorie)
        except Exception as e: r=Resultat(nom,ECHEC,"statut non autorise: %s"%e,obligatoire,str(e),"ajouter",NON_DET); exceptions.append(str(e))
        resultats.append(r); fonctions.append(nom); print("[V5.5.6.6] %s : %s (%s) obligatoire=%s raison=%s detecteur=%s categorie=%s"%(nom,r.statut,detail,obligatoire,raison,detecteur,categorie)); return r
    def test_valeur(nom,statut_attendu,statut_obtenu,valeur_attendue,valeur_obtenue,detecteur_attendu=None,detecteur_obtenu=None,categorie=CALCULE):
        ok_test=(statut_obtenu==statut_attendu and valeur_obtenue==valeur_attendue and (detecteur_attendu is None or detecteur_obtenu==detecteur_attendu)); print("[V5.5.6.6] TEST VALEUR %s | %s"%(nom,"PASS" if ok_test else "FAIL")); ajouter(nom,OK if ok_test else ECHEC,"statut=%s valeur=%r"%(statut_obtenu,valeur_obtenue),obligatoire=True,raison="statut+valeur+detecteur",detecteur=detecteur_obtenu if detecteur_obtenu is not None else "",categorie=categorie); return ok_test
    _SENTINELLE_ABSENT=object(); _EXIGE_OMIS=object()
    def _evaluer_test_negatif(attendu_statut,obtenu_statut,raison,obtenu_detecteur,detecteur_attendu,resultat_obtenu=_SENTINELLE_ABSENT,exige_resultat_none=_EXIGE_OMIS):
        if exige_resultat_none is _EXIGE_OMIS: return False
        if exige_resultat_none is not None and type(exige_resultat_none) is not bool: return False
        if obtenu_statut!=attendu_statut or obtenu_detecteur!=detecteur_attendu: return False
        if raison is None or len(str(raison))==0: return False
        if exige_resultat_none is True:
            if resultat_obtenu is _SENTINELLE_ABSENT or resultat_obtenu is not None: return False
        elif exige_resultat_none is False:
            if resultat_obtenu is _SENTINELLE_ABSENT or resultat_obtenu is None: return False
        elif exige_resultat_none is None: pass
        else: return False
        return True
    def test_negatif(nom,entree,fonction,attendu_statut,obtenu_statut,raison,obtenu_detecteur,detecteur_attendu,categorie=TEST_LOGICIEL,resultat_obtenu=_SENTINELLE_ABSENT,exige_resultat_none=_EXIGE_OMIS):
        ok_test=_evaluer_test_negatif(attendu_statut,obtenu_statut,raison,obtenu_detecteur,detecteur_attendu,resultat_obtenu,exige_resultat_none); print("[V5.5.6.6] TEST NEGATIF %s | %s"%(nom,"PASS" if ok_test else "FAIL")); ajouter(nom,OK if ok_test else ECHEC,"attendu=%s obtenu=%s exige=%s"%(attendu_statut,obtenu_statut,"OMIS" if exige_resultat_none is _EXIGE_OMIS else repr(exige_resultat_none)),obligatoire=True,raison=raison,detecteur=obtenu_detecteur,categorie=categorie); return ok_test
    def verifier_c11(nom,kwargs,att_statut,att_detecteur):
        st,det=certifier_phi2_strict(**kwargs); raison=det.get("raison","") if isinstance(det,dict) else str(det); detecteur=det.get("detecteur","") if isinstance(det,dict) else ""; resultat=det.get("resultat",None) if isinstance(det,dict) else None; ok_test=(st==att_statut and detecteur==att_detecteur and len(raison)>0 and resultat is None); print("[V5.5.6.6] TEST C11 %s | %s"%(nom,"PASS" if ok_test else "FAIL")); ajouter(nom,OK if ok_test else ECHEC,"statut=%s detecteur=%s raison=%s resultat=%r"%(st,detecteur,raison,resultat),obligatoire=True,raison=raison,detecteur=detecteur,categorie=TEST_LOGICIEL); return ok_test
    print("[V5.5.6.6] AUDIT STRICT INVARIANTS GMN V5.5.6.6. V5.5.5 a V5.5.6.5 preservees."); print("[V5.5.6.6] Python %s"%sys.version.split()[0]); print("[V5.5.6.6] Debut %s"%debut.isoformat())
    st_int,raison_int,det_int=verifier_integrite_source(); ajouter("C13 integrite source lecture + Markdown + py_compile + fragment injecte",st_int,raison_int,obligatoire=True,raison=raison_int,detecteur=det_int,categorie=TEST_LOGICIEL)
    ajouter("C13 fragment injecte detecte",OK if detecte_fragment_markdown("x "+chr(96)*3+"python y") else ECHEC,"detecteur negatif",obligatoire=True,raison="fragment injecte",detecteur="detecte_fragment_markdown",categorie=TEST_LOGICIEL)
    ajouter("C13 texte propre non signale",OK if not detecte_fragment_markdown("texte propre sans marqueur") else ECHEC,"pas de faux positif",obligatoire=True,raison="texte propre",detecteur="detecte_fragment_markdown",categorie=TEST_LOGICIEL)
    cas_moteur=[("Moteur True + absent -> False",ECHEC,ECHEC,"r","d","d",_SENTINELLE_ABSENT,True,False),("Moteur True + None -> True",ECHEC,ECHEC,"r","d","d",None,True,True),("Moteur True + non-None -> False",ECHEC,ECHEC,"r","d","d",1,True,False),("Moteur False + absent -> False",ECHEC,ECHEC,"r","d","d",_SENTINELLE_ABSENT,False,False),("Moteur False + None -> False",ECHEC,ECHEC,"r","d","d",None,False,False),("Moteur False + non-None -> True",ECHEC,ECHEC,"r","d","d",1,False,True),("Moteur None + absent -> True",ECHEC,ECHEC,"r","d","d",_SENTINELLE_ABSENT,None,True),("Moteur None + None -> True",ECHEC,ECHEC,"r","d","d",None,None,True),("Moteur None + non-None -> True",ECHEC,ECHEC,"r","d","d",1,None,True),("Moteur omis -> False",ECHEC,ECHEC,"r","d","d",None,_EXIGE_OMIS,False),("Moteur 0 -> False",ECHEC,ECHEC,"r","d","d",None,0,False),("Moteur 1 -> False",ECHEC,ECHEC,"r","d","d",None,1,False),("Moteur 'True' -> False",ECHEC,ECHEC,"r","d","d",None,"True",False),("Moteur 'False' -> False",ECHEC,ECHEC,"r","d","d",None,"False",False)]
    for (nom,att,obt,raison,det_obt,det_att,res,exige,attendu_bool) in cas_moteur:
        obtenu_bool=_evaluer_test_negatif(att,obt,raison,det_obt,det_att,res,exige); ajouter(nom,OK if obtenu_bool==attendu_bool else ECHEC,"obtenu=%s attendu=%s"%(obtenu_bool,attendu_bool),obligatoire=True,raison="coeur moteur",detecteur="_evaluer_test_negatif",categorie=TEST_LOGICIEL)
    sg,det_sg=statut_global([Resultat("a",OK,"",True),Resultat("b",OK,"",True)]); ajouter("Verrou : tous OK -> PASS PARTIEL max",OK if sg=="PASS PARTIEL" else ECHEC,"sg=%s"%sg,obligatoire=True,raison=det_sg,detecteur="statut_global",categorie=TEST_LOGICIEL)
    sg,det_sg=statut_global([]); ajouter("Verrou : liste vide -> ECHEC GLOBAL",OK if sg=="ECHEC GLOBAL" else ECHEC,"sg=%s"%sg,obligatoire=True,raison=det_sg,detecteur="statut_global",categorie=TEST_LOGICIEL)
    st,val,raison,det=mulF(0b101,0b11); test_valeur("GF2 mulF",OK,st,0b1111,val,"mulF",det,categorie=CALCULE)
    st,val,raison,det=degF(0b101); test_valeur("GF2 degF",OK,st,2,val,"degF",det,categorie=CALCULE)
    st,q,r,raison,det=divmodF(0b1111,0b11); test_valeur("GF2 divmodF quotient",OK,st,0b101,q,"divmodF",det,categorie=CALCULE); test_valeur("GF2 divmodF reste",OK,st,0,r,"divmodF",det,categorie=CALCULE)
    st,val,raison,det=gcdF(0b101,0b11); test_valeur("GF2 gcdF",OK,st,0b11,val,"gcdF",det,categorie=CALCULE)
    st,val,raison,det=derivF(0b101); test_valeur("GF2 derivF",OK,st,0,val,"derivF",det,categorie=CALCULE)
    st,val,raison,det=degF(True); test_negatif("GF2 degF bool","True","degF",ECHEC,st,raison,det,"_check_gf2 degF",categorie=TEST_LOGICIEL,resultat_obtenu=val,exige_resultat_none=True)
    st,res,raison,det=poly_add([1,2],[3,4]); test_valeur("poly_add",OK,st,[4,6],res,"poly_add",det,categorie=CALCULE)
    st,res,raison,det=poly_add([1],[True]); test_negatif("poly_add bool","[True]","poly_add",ECHEC,st,raison,det,"valider_coeffs_int type",categorie=TEST_LOGICIEL,resultat_obtenu=res,exige_resultat_none=True)
    st,res,raison,det=poly_mul([1,1],[1,1]); test_valeur("poly_mul",OK,st,[1,2,1],res,"poly_mul",det,categorie=CALCULE)
    st,coeffs,raison,det=expansion_phi_adique_strict([1,1],[1,1]); test_valeur("Expansion",OK,st,[[0],[1]],coeffs,"expansion",det,categorie=CALCULE)
    st,coeffs,raison,det=expansion_phi_adique_strict([1,1],[5]); test_negatif("Expansion phi constant","phi=[5]","expansion",ECHEC,st,raison,det,"expansion phi constant",categorie=TEST_LOGICIEL,resultat_obtenu=coeffs,exige_resultat_none=True)
    st,hull,raison,det=calculer_enveloppe_inf([(0,Fraction(4)),(1,Fraction(2)),(2,Fraction(0))]); test_valeur("Polygone colineaires",OK,st,[(0,Fraction(4)),(2,Fraction(0))],hull,"enveloppe",det,categorie=CALCULE)
    for entree,attendu_norm,attendu_v0 in [([12,20],[3,5],2),([-12,20],[-3,5],2),([6,10],[3,5],1),([-8,-12],[-1,-3],3)]:
        sn,norm,v0n,rn,dn=normaliser_residuel(entree); test_valeur("C08 normaliser %s"%(entree,),OK,sn,attendu_norm,norm,"normaliser_residuel",dn,categorie=CALCULE); ajouter("C08 reconstruction + impair %s"%(entree,),OK if (sn==OK and v0n==attendu_v0 and any(x%2==1 for x in norm) and [x*(2**v0n) for x in norm]==list(entree)) else ECHEC,"v0=%s"%v0n,obligatoire=True,raison=rn,detecteur=dn,categorie=TEST_LOGICIEL)
    for entree,att_st,att_det in [([0,0],ECHEC,"normaliser nul"),([True,2],ECHEC,"valider_coeffs_int type"),([1.5,2],ECHEC,"valider_coeffs_int type"),([],ECHEC,"normaliser vide"),(None,NON_DET,"valider_coeffs_int absence"),("abc",ECHEC,"valider_coeffs_int type"),(123,ECHEC,"valider_coeffs_int type")]:
        sn,norm,v0n,rn,dn=normaliser_residuel(entree); test_negatif("C08 normaliser %r"%(entree,),repr(entree),"normaliser_residuel",att_st,sn,rn,dn,att_det,categorie=TEST_LOGICIEL,resultat_obtenu=norm,exige_resultat_none=True)
    preuve_complete={"type":"preuve_locale_verifiee","verifiee":True}
    st_v,_,raison_v,det_v=valider_v2_gmn([4,8],preuve_complete,"anneau local"); ajouter("Certification locale v2 dict fabrique -> NON_DET",OK if st_v==NON_DET else ECHEC,raison_v,obligatoire=True,raison=raison_v,detecteur=det_v,categorie=NON_DET)
    st_s,rs,ds=valider_structure_bj_list([[1],[1]]); ajouter("C10 structure b_j valide",OK if st_s==OK else ECHEC,rs,obligatoire=True,raison=rs,detecteur=ds,categorie=TEST_LOGICIEL)
    st_s,rs,ds=valider_structure_bj_list([[1],[True]]); test_negatif("C10 structure b_j bool","[True]","structure_bj",ECHEC,st_s,rs,ds,"structure_bj",categorie=TEST_LOGICIEL,resultat_obtenu=None,exige_resultat_none=None)
    st_t,rt,dt=valider_types_uj_list([Fraction(4),Fraction(4)]); ajouter("C10 types u_j valides",OK if st_t==OK else ECHEC,rt,obligatoire=True,raison=rt,detecteur=dt,categorie=TEST_LOGICIEL)
    for val_uj,nom_uj in [(True,"True"),(False,"False"),(4.0,"4.0"),("4","'4'"),([4],"[4]")]:
        st_t,rt,dt=valider_types_uj_list([val_uj,Fraction(4)]); test_negatif("C10 types u_j %s"%nom_uj,nom_uj,"types_uj",ECHEC,st_t,rt,dt,"types_uj type",categorie=TEST_LOGICIEL,resultat_obtenu=None,exige_resultat_none=None)
    st_ord,ro,do=valider_ordonnees_gmn([[1],[1]],[-15,1],[Fraction(4),Fraction(4)],preuve_complete,"anneau local",preuve_complete); ajouter("C10 ordonnees dict fabrique -> NON_DET",OK if st_ord==NON_DET else ECHEC,ro,obligatoire=True,raison=ro,detecteur=do,categorie=NON_DET)
    st_ord,ro,do=valider_ordonnees_gmn([[1],[1]],[-15,1],[True,Fraction(4)],preuve_complete,"anneau local",preuve_complete); ajouter("C10 ordonnees u_j True -> ECHEC avant verrou",OK if (st_ord==ECHEC and "TYPES" in ro) else ECHEC,ro,obligatoire=True,raison=ro,detecteur=do,categorie=TEST_LOGICIEL)
    # C11 : fixture valide B : phi1=[1,1], phi2=[17,1], lambda1=Fraction(4,1), psi1=0b11
    base_c11={"phi1":[1,1],"lambda1":Fraction(4,1),"psi1":0b11,"phi2":[17,1],"exigee":True,"documentee":True,"preuve_locale":preuve_complete}
    # Verification explicite pre-verrou de la fixture : diff, pente, residuel recalcules independamment
    diff_f=[base_c11["phi2"][i]-(base_c11["phi1"][i] if i<len(base_c11["phi1"]) else 0) for i in range(2)]; sv_f,v2_f,_,_=v2_int_strict(diff_f[0]); se_f,exp_f,_,_=expansion_phi_adique_strict(base_c11["phi2"],base_c11["phi1"]); sr_f,segs_f,_,_,_,_=residuel_ordre1_strict(base_c11["phi1"],base_c11["phi2"])
    fixture_ok=(diff_f==[16,0] and sv_f==OK and v2_f==4 and se_f==OK and exp_f==[[16],[1]] and sr_f==OK and len(segs_f)==1 and segs_f[0][2]==Fraction(-4) and segs_f[0][3]==0b11)
    ajouter("C11 fixture valide verifiee avant verrou (diff=16,v2=4,exp=[[16],[1]],pente=-4,residuel=0b11)",OK if fixture_ok else ECHEC,"diff=%s v2=%s exp=%s segs=%s"%(diff_f,v2_f,exp_f,segs_f),obligatoire=True,raison="fixture B",detecteur="C11 fixture",categorie=TEST_LOGICIEL)
    verifier_c11("C11 1 lambda1 bool",dict(base_c11,lambda1=True),ECHEC,"certifier_phi2 lambda1")
    verifier_c11("C11 2 lambda1 float",dict(base_c11,lambda1=4.0),ECHEC,"certifier_phi2 lambda1")
    verifier_c11("C11 3 lambda1 chaine",dict(base_c11,lambda1="4"),ECHEC,"certifier_phi2 lambda1")
    verifier_c11("C11 4 denominateur nul",dict(base_c11,lambda1=(4,0)),ECHEC,"certifier_phi2 lambda1 denominateur")
    verifier_c11("C11 5 denominateur mal type",dict(base_c11,lambda1=(4,"2")),ECHEC,"certifier_phi2 lambda1 denominateur")
    verifier_c11("C11 6 phi1 non monique",dict(base_c11,phi1=[2,1]),ECHEC,"certifier_phi2 phi1 monicite")
    verifier_c11("C11 7 phi2 non monique",dict(base_c11,phi2=[2,1]),ECHEC,"certifier_phi2 phi2 monicite")
    verifier_c11("C11 8 degre phi1 incorrect",dict(base_c11,phi1=[1,1,1]),ECHEC,"certifier_phi2 phi1 degre")
    verifier_c11("C11 9 degre phi2 incorrect",dict(base_c11,phi2=[1,1,1]),ECHEC,"certifier_phi2 phi2 degre")
    verifier_c11("C11 10 relation degres incorrecte",dict(base_c11,psi1=0b111,phi2=[17,1]),ECHEC,"certifier_phi2 degres relation")
    verifier_c11("C11 11 psi1 mal type",dict(base_c11,psi1=True),ECHEC,"certifier_phi2 psi1")
    verifier_c11("C11 12 difference phi2-phi1 incorrecte",dict(base_c11,phi2=[1,1]),ECHEC,"certifier_phi2 difference")
    verifier_c11("C11 13 pente float",dict(base_c11,pente_fournie=4.0),ECHEC,"certifier_phi2 pente")
    verifier_c11("C11 14 residuel bool",dict(base_c11,residuel_fourni=True),ECHEC,"certifier_phi2 residuel")
    verifier_c11("C11 15 residuel float",dict(base_c11,residuel_fourni=1.5),ECHEC,"certifier_phi2 residuel")
    verifier_c11("C11 16 invariant incorrect",dict(base_c11,invariant_fourni=False),ECHEC,"certifier_phi2 invariant")
    verifier_c11("C11 17 entree absente",dict(base_c11,phi1=None),ECHEC,"certifier_phi2 absence")
    # C11 test 18 STRICT : exactement NON_DET + detecteur verrou, aucun ECHEC accepte, fixture deja verifiee
    verifier_c11("C11 18 structure valide + verrou ferme -> NON_DET exact",dict(base_c11),NON_DET,"certifier_phi2 calcul_local_manquant")
    # C11 exigee : True accepte structurellement -> NON_DET verrou ; False defini -> NON_DET verrou ; autres -> ECHEC exigee
    verifier_c11("C11 exigee=True accepte -> NON_DET verrou",dict(base_c11,exigee=True),NON_DET,"certifier_phi2 calcul_local_manquant")
    verifier_c11("C11 exigee=False defini -> NON_DET verrou",dict(base_c11,exigee=False),NON_DET,"certifier_phi2 calcul_local_manquant")
    verifier_c11("C11 exigee=1 -> ECHEC",dict(base_c11,exigee=1),ECHEC,"certifier_phi2 exigee")
    verifier_c11("C11 exigee=0 -> ECHEC",dict(base_c11,exigee=0),ECHEC,"certifier_phi2 exigee")
    verifier_c11("C11 exigee=None -> ECHEC",dict(base_c11,exigee=None),ECHEC,"certifier_phi2 exigee")
    verifier_c11("C11 exigee='True' -> ECHEC",dict(base_c11,exigee="True"),ECHEC,"certifier_phi2 exigee")
    verifier_c11("C11 exigee=[] -> ECHEC",dict(base_c11,exigee=[]),ECHEC,"certifier_phi2 exigee")
    # C09 canonique + nouveaux cas
    branche_b1={"degre":1,"pente":Fraction(-4,1),"multiplicite":1,"residuel":0b11,"hypotheses":True}; branches_valides={"b1":branche_b1}; perimetre_ok={"couverture_demonteree":True,"identifiants_branches_attendus":["b1"]}; perimetre_ok_hist={"couverture_demonteree":True,"branches_attendues":1,"identifiants_branches_attendus":["b1"]}
    si,ri,di=valider_identites_branches(perimetre_ok,branches_valides); ajouter("C09 1 perimetre canonique valide",OK if si==OK else ECHEC,ri,obligatoire=True,raison=ri,detecteur=di,categorie=TEST_LOGICIEL)
    si,ri,di=valider_identites_branches(perimetre_ok_hist,branches_valides); ajouter("C09 1b historique coherent avec derive",OK if si==OK else ECHEC,ri,obligatoire=True,raison=ri,detecteur=di,categorie=TEST_LOGICIEL)
    for nom,per,br,att_det in [("C09 2 identifiant vide",{"identifiants_branches_attendus":[""]},branches_valides,"identites vide"),("C09 3 identifiant espaces",{"identifiants_branches_attendus":["   "]},branches_valides,"identites espaces"),("C09 4 identifiant bool",{"identifiants_branches_attendus":[True]},branches_valides,"identites type"),("C09 5 identifiant entier",{"identifiants_branches_attendus":[1]},branches_valides,"identites type"),("C09 6 identifiant duplique",{"identifiants_branches_attendus":["b1","b1"]},branches_valides,"identites duplique"),("C09 7 collection None",{"identifiants_branches_attendus":None},branches_valides,"identites collection None"),("C09 8 collection chaine",{"identifiants_branches_attendus":"b1"},branches_valides,"identites collection chaine"),("C09 9 collection vide",{"identifiants_branches_attendus":[]},branches_valides,"identites collection vide"),("C09 10 branche manquante",{"identifiants_branches_attendus":["b1","b2"]},branches_valides,"identites manquantes"),("C09 11 branche supplementaire",perimetre_ok,{"b1":branche_b1,"b2":branche_b1},"identites supplementaires"),("C09 12 remplacement meme cardinalite",{"identifiants_branches_attendus":["bX"]},branches_valides,"identites manquantes"),("C09 20 incoherence historique",{"branches_attendues":2,"identifiants_branches_attendus":["b1"]},branches_valides,"identites historique incoherence"),("C09 identifiant non textuel",{"identifiants_branches_attendus":[1.5]},branches_valides,"identites type")]:
        si2,ri2,di2=valider_identites_branches(per,br); ajouter(nom,OK if (si2==ECHEC and di2==att_det) else ECHEC,"statut=%s detecteur=%s"%(si2,di2),obligatoire=True,raison=ri2,detecteur=di2,categorie=TEST_LOGICIEL)
    for nom,br,att_det in [("C09 branche liste",{"b1":[1,2]},"branches liste"),("C09 branche chaine",{"b1":"chaine"},"branches chaine"),("C09 branche None",{"b1":None},"branches None"),("C09 branche entier",{"b1":1},"branches entier"),("C09 branche booleen",{"b1":True},"branches booleen"),("C09 dictionnaire incomplet",{"b1":{"degre":1}},"branches champ absent"),("C09 champ obligatoire absent",{"b1":{"degre":1,"pente":Fraction(-4,1),"multiplicite":1,"residuel":0b11}},"branches champ absent"),("C09 multiplicite bool",{"b1":dict(branche_b1,multiplicite=True)},"branches multiplicite"),("C09 residuel bool",{"b1":dict(branche_b1,residuel=True)},"branches residuel"),("C09 degre bool",{"b1":dict(branche_b1,degre=True)},"branches degre bool"),("C09 degre float",{"b1":dict(branche_b1,degre=1.5)},"branches degre"),("C09 pente float",{"b1":dict(branche_b1,pente=4.0)},"branches pente"),("C09 hypotheses mauvais type",{"b1":dict(branche_b1,hypotheses=1)},"branches hypotheses type")]:
        st_b,_,rb,db=verifier_branches_completes(br,perimetre_ok,True); ajouter(nom,OK if (st_b==ECHEC and db==att_det) else ECHEC,rb,obligatoire=True,raison=rb,detecteur=db,categorie=TEST_LOGICIEL)
    st_b,_,rb,db=verifier_branches_completes(branches_valides,perimetre_ok,True); ajouter("C09 couverture True sans demonstration -> NON_DET",OK if (st_b==NON_DET and db=="branches verrou") else ECHEC,rb,obligatoire=True,raison=rb,detecteur=db,categorie=NON_DET)
    st_c,t1_val,st_cert,rc,rcert,dt_t=valider_t1(4,0,Fraction(4),1,4,True,True,True,"branche fixture"); ajouter("t1 calcul exact OK, certification NON_DET",OK if (st_c==OK and t1_val==Fraction(4) and st_cert==NON_DET) else ECHEC,"t1=%s"%t1_val,obligatoire=True,raison=rcert,detecteur=dt_t,categorie=CONDITIONNEL)
    st_f,v1_val,st_cert,rf,rc,dv1=v1_poly_strict([1,1],[1,1],Fraction(4,1)); ajouter("v1 CALCUL_FORMEL_OK, CERTIFICATION_GMN NON_DET",OK if (st_f==OK and st_cert==NON_DET) else ECHEC,"v1=%s"%v1_val,obligatoire=True,raison=rc,detecteur=dv1,categorie=CONDITIONNEL)
    st_f,P,t0,e1_v,v1_v,st_cert,rf,rc,dr=red1_poly_strict([1,1],[1,1],Fraction(4,1)); ajouter("red1 CALCUL_FORMEL_OK, CERTIFICATION_GMN NON_DET",OK if (st_f==OK and st_cert==NON_DET) else ECHEC,"P=%s"%P,obligatoire=True,raison=rc,detecteur=dr,categorie=CONDITIONNEL)
    st_f,segs,st_cert,rf,rc,dres=residuel_ordre1_strict([1,1],[1,1]); ajouter("residuel CALCUL_FORMEL_OK (CANDIDAT_GMN), CERTIFICATION_GMN NON_DET",OK if (st_f==OK and st_cert==NON_DET) else ECHEC,"segs=%s"%segs,obligatoire=True,raison=rc,detecteur=dres,categorie=CONDITIONNEL)
    st_a,u,st_g,ra,rg,du=calculer_u_j_arithmetique(4,1,4,"entree arithmetique","entree arithmetique"); test_valeur("u_j arithmetique 4+1*4=8",OK,st_a,Fraction(8),u,"calculer_u_j",du,categorie=CALCULE); ajouter("u_j interpretation GMN NON_DET",OK if st_g==NON_DET else ECHEC,rg,obligatoire=True,raison=rg,detecteur=du,categorie=CONDITIONNEL)
    st_o,ro,do=audit_ordre2(None,None,None,None,False); ajouter("Ordre 2 donnees manquantes -> NON_DET",st_o,ro,obligatoire=True,raison=ro,detecteur=do,categorie=NON_DET)
    cas_parseur=[]
    cas_parseur.append(("Parser fichier absent",None,NON_DET,None,"parser absence")); cas_parseur.append(("Parser entree vide","",ECHEC,None,"parser manquant")); cas_parseur.append(("Parser commentaire historique","# commentaire\n"+"\n".join(["c_%d=0"%i for i in range(40)]),OK,[0]*40,"parser")); cas_parseur.append(("Parser en-tete valide","HEADER: test\n"+"\n".join(["c_%d=0"%i for i in range(40)]),OK,[0]*40,"parser")); cas_parseur.append(("Parser ligne H=","H=1\n",NON_DET,None,"parser H=")); cas_parseur.append(("Parser 40 coefficients valides","\n".join(["c_%d=%d"%(i,i) for i in range(40)]),OK,list(range(40)),"parser")); cas_parseur.append(("Parser coefficient duplique","\n".join(["c_0=1","c_0=2"]+["c_%d=0"%i for i in range(1,40)]),ECHEC,None,"parser duplique")); cas_parseur.append(("Parser coefficient hors plage","\n".join(["c_%d=0"%i for i in range(40)]+["c_40=1"]),ECHEC,None,"parser hors plage")); cas_parseur.append(("Parser coefficient mal forme","\n".join(["c_0=abc"]+["c_%d=0"%i for i in range(1,40)]),ECHEC,None,"parser malforme")); cas_parseur.append(("Parser cle inconnue","\n".join(["c_%d=0"%i for i in range(40)]+["FOO=1"]),ECHEC,None,"parser inconnue")); cas_parseur.append(("Parser coefficient manquant","\n".join(["c_%d=0"%i for i in range(39)]),ECHEC,None,"parser manquant")); cas_parseur.append(("Parser fichier valide complet","\n".join(["c_%d=%d"%(i,-i) for i in range(40)]),OK,[-i for i in range(40)],"parser")); cas_parseur.append(("Parser resultat None attendu","H=1\n",NON_DET,None,"parser H=")); cas_parseur.append(("Parser resultat non-None attendu","\n".join(["c_%d=0"%i for i in range(40)]),OK,[0]*40,"parser"))
    for (nom,entree,att_st,att_res,att_det) in cas_parseur:
        st_p,coeffs_p,raison_p,det_p=parser_strict_fichier_T(entree)
        if att_res is None: ok_res=(coeffs_p is None)
        else: ok_res=(coeffs_p==att_res)
        ok_test=(st_p==att_st and det_p==att_det and ok_res and len(str(raison_p))>0); print("[V5.5.6.6] TEST PARSEUR %s | %s"%(nom,"PASS" if ok_test else "FAIL")); ajouter(nom,OK if ok_test else ECHEC,"statut=%s det=%s resultat_is_None=%s"%(st_p,det_p,coeffs_p is None),obligatoire=True,raison=raison_p,detecteur=det_p,categorie=TEST_LOGICIEL)
    for nom,att,obt,att_bool in [("C13 injection None attendu + [0]",None,[0],False),("C13 injection None attendu + liste",None,[1,2],False),("C13 injection None attendu + entier",None,5,False),("C13 injection None attendu + chaine",None,"x",False),("C13 injection liste attendue + None",[0],None,False),("C13 injection liste attendue + liste differente",[0],[1],False),("C13 controle None attendu + None",None,None,True),("C13 controle liste attendue + egale",[1],[1],True)]:
        ok_inj=(verifier_resultat_parseur(att,obt) is att_bool); ajouter(nom,OK if ok_inj else ECHEC,"verifier_resultat_parseur=%s attendu=%s"%(verifier_resultat_parseur(att,obt),att_bool),obligatoire=True,raison="None strict",detecteur="verifier_resultat_parseur",categorie=TEST_LOGICIEL)
    st_conv,det_conv=verifier_convention_historique(); ajouter("C12 convention historique SHA -> NON_DET",st_conv,det_conv,obligatoire=True,raison=det_conv,detecteur="verifier_convention_historique",categorie=NON_DET)
    coeffs_test=[0]*39+[1]; ser_test="\n".join(str(coeffs_test[i]) for i in range(39,-1,-1))+"\n"; sha_test=hashlib.sha256(ser_test.encode("utf-8")).hexdigest()
    st_auth,raison_auth,det_auth=valider_authenticite_T(coeffs_test,sha_test); ajouter("C12 authenticite historique -> NON_DET meme avec bon SHA",OK if st_auth==NON_DET else ECHEC,raison_auth,obligatoire=True,raison=raison_auth,detecteur=det_auth,categorie=NON_DET)
    st_sha,raison_sha,det_sha=valider_sha_avec_convention_test(coeffs_test,sha_test,"test-canonique"); ajouter("C12 SHA convention de test -> OK, distinct de l'historique",OK if st_sha==OK else ECHEC,raison_sha,obligatoire=True,raison=raison_sha,detecteur=det_sha,categorie=TEST_LOGICIEL)
    ajouter("authenticite_historique",NON_DET,"authenticite_historique = NON DETERMINE",obligatoire=True,raison="convention non demontree",detecteur="verifier_convention_historique",categorie=NON_DET)
    ajouter("Certification locale GMN",NON_DET,"CERTIFICATION LOCALE = NON_DET",obligatoire=True,raison="calcul local manquant",detecteur="valider_v2_gmn",categorie=NON_DET)
    ajouter("Exhaustivite des branches",NON_DET,"EXHAUSTIVITE = NON_DET",obligatoire=True,raison="enumeration manquante",detecteur="verifier_branches_completes",categorie=NON_DET)
    ajouter("Indice local en 2",NON_DET,"INDICE LOCAL EN 2 : NON CALCULE",obligatoire=True,raison="calcul non effectue",detecteur="indice local",categorie=OUVERT)
    ajouter("Maximalite de Z[beta]",NON_DET,"MAXIMALITE : NON DEMONTREE",obligatoire=True,raison="demonstration manquante",detecteur="maximalite",categorie=OUVERT)
    ajouter("Egalite Z[beta]=O_K",NON_DET,"EGALITE : NON DEMONTREE",obligatoire=True,raison="demonstration manquante",detecteur="egalite ordre",categorie=OUVERT)
    st_e,hull_e,raison_e,det_e=calculer_enveloppe_inf([(0,Fraction(4)),(1,Fraction(2)),(2,Fraction(0))]); ajouter("Regression enveloppe colineaires",OK if (st_e==OK and hull_e==[(0,Fraction(4)),(2,Fraction(0))]) else ECHEC,"hull=%s"%(hull_e,),obligatoire=True,raison=raison_e,detecteur=det_e,categorie=TEST_LOGICIEL)
    st_pa,res_pa,raison_pa,det_pa=poly_add([1,0,0],[2]); ajouter("Regression poly_add [1,0,0]+[2]=[3]",OK if (st_pa==OK and res_pa==[3] and det_pa=="poly_add") else ECHEC,"res=%s"%(res_pa,),obligatoire=True,raison=raison_pa,detecteur=det_pa,categorie=TEST_LOGICIEL)
    fin=datetime.datetime.now(); n_tests=len(resultats); n_pass=len([r for r in resultats if r.statut==OK]); n_fail=len([r for r in resultats if r.statut==ECHEC]); n_non_det=len([r for r in resultats if r.statut==NON_DET]); echecs=[r.nom for r in resultats if r.statut==ECHEC]; ok_compteurs=(n_tests==n_pass+n_fail+n_non_det) and (len(echecs)==n_fail)
    print("[V5.5.6.6] CONTROLE COMPTEURS : n_tests=%d n_pass=%d n_fail=%d n_non_det=%d len(echecs)=%d coherent=%s"%(n_tests,n_pass,n_fail,n_non_det,len(echecs),ok_compteurs)); print("[V5.5.6.6] ===== RAPPORT FINAL =====")
    print("[V5.5.6.6] 3. Resultats formels : CALCUL_FORMEL_OK pour GF(2), expansion, v1, red1, residuel, u_j arithmetique, t1 calcul, poly_add, poly_mul.")
    print("[V5.5.6.6] 4. Candidats GMN : CANDIDAT_GMN pour v1, red1, residuel, u_j, t1. Aucun candidat ne devient une certification.")
    print("[V5.5.6.6] 5. Hypotheses etablies : aucune hypothese GMN locale etablie.")
    print("[V5.5.6.6] 6. Hypotheses non etablies : calcul local, valuations locales, invariants ordre 2, branches, ordre 2, convention historique, certification phi2.")
    print("[V5.5.6.6] 7. Certifications locales : NON_DET."); print("[V5.5.6.6] 8. Exhaustivite des branches : NON_DET."); print("[V5.5.6.6] 9. Indice local en 2 : NON CALCULE."); print("[V5.5.6.6] 10. Maximalite : NON DEMONTREE. Z[beta] = O_K : NON DEMONTRE.")
    print("[V5.5.6.6] DEMONTRE : aucune proposition GMN demontree (categorie reservee, jamais attribuee a un test logiciel).")
    print("[V5.5.6.6] CONDITIONNEL :")
    for r in resultats:
        if r.categorie==CONDITIONNEL: print("[V5.5.6.6]   %s : %s (%s)"%(r.nom,r.statut,r.detail))
    print("[V5.5.6.6] OUVERT :")
    for r in resultats:
        if r.categorie==OUVERT: print("[V5.5.6.6]   %s : %s (%s)"%(r.nom,r.statut,r.detail))
    print("[V5.5.6.6] POINTS NON DETERMINES :")
    for r in resultats:
        if r.categorie==NON_DET: print("[V5.5.6.6]   %s : %s (%s)"%(r.nom,r.statut,r.detail))
    print("[V5.5.6.6] Version Python : %s"%sys.version.split()[0]); print("[V5.5.6.6] Nombre de tests : %d"%n_tests); print("[V5.5.6.6] Nombre de PASS : %d"%n_pass); print("[V5.5.6.6] Nombre de FAIL : %d"%n_fail); print("[V5.5.6.6] Nombre de NON_DET : %d"%n_non_det); print("[V5.5.6.6] Controle compteurs coherent : %s"%ok_compteurs); print("[V5.5.6.6] Liste des echecs : %s"%echecs)
    sg,det_sg=statut_global(resultats); print("[V5.5.6.6] Conclusion globale : %s (%s)"%(sg,det_sg)); print("[V5.5.6.6] Aucun PASS GLOBAL."); print("[V5.5.6.6] Debut : %s ; Fin : %s"%(debut.isoformat(),fin.isoformat())); print("[V5.5.6.6] Fonctions : %s"%", ".join(sorted(set(fonctions)))); print("[V5.5.6.6] Exceptions : %s"%exceptions); print("[V5.5.6.6] INDICE LOCAL EN 2 : NON CALCULE"); print("[V5.5.6.6] Maximalite de Z[beta] : NON DEMONTREE"); print("[V5.5.6.6] Z[beta] = O_K : NON DEMONTRE")
if __name__=="__main__": main()
# Verification (a executer, non pretendue executee ici) :
#   python3 --version
#   python3 -m py_compile AUDIT_STRICT_INVARIANTS_GMN_V5.5.6.6.py
#   sha256sum AUDIT_STRICT_INVARIANTS_GMN_V5.5.6.6.py
#   python3 AUDIT_STRICT_INVARIANTS_GMN_V5.5.6.6.py
