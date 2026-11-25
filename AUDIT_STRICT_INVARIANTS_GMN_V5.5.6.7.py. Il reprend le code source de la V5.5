```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDIT STRICT INVARIANTS GMN V5.5.6.7.
Nouveau fichier autonome. V5.5.5 a V5.5.6.6 conservees, inchangees.
Depot : hydraglide21/DODECA-T2G-Archives.
V5.5.6.6 -> V5.5.6.7 :
Correction des deux déballages de calculer_enveloppe_inf : récupération des 4 valeurs.
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
        return ("PASS PARTIEL","Verrou V5.5.6.7 : PASS GLOBAL impossible, preuves non etablies.")
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
        sh,hull,raison_enveloppe,detecteur_enveloppe=calculer_enveloppe_inf(pts)
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
