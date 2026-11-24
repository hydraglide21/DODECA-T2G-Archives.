#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDIT STRICT INVARIANTS GMN V5.5.6.1 - CORRECTIONS C13, C10, C08, C09, C11.
NOUVEAU fichier autonome. Ne pas modifier V5.5.5 ni V5.5.6. Toutes conservees.
Base : V5.5.6 (texte complet, sans l'intrusion Markdown autour de _br_hyp).
C13 : integrite syntaxique, aucune ligne Markdown dans le code, test d'auto-lecture.
C10 : structure b_j / types u_j / certification locale separes, independants du verrou NON_DET.
C08 : normaliser_residuel() fonction de production, appelee par les tests.
C09 : valider_perimetre_strict(), refus des booleens comme preuves d'exhaustivite.
C11 : certifier_phi2_strict() branches etiquetees, verrous mathematiques conserves.
Python 3.9.25, stdlib uniquement. Calculs exacts : int, Fraction. Aucun flottant dans les controles mathematiques.
EXECUTION DANS CETTE SESSION : NON EFFECTUEE. SHA-256, compilation et tests ne sont PAS pretendus executes ici.
"""
import hashlib, math, os, re, sys, datetime
from fractions import Fraction
SHA_T_REF = "dcd2e52240144dfcbba15c0a31b81ced6738cd8b64e01b56c1a577e45f09644c"
NOM_LOGIQUE_T = "T_BETA_COEFFICIENTS_V2_8_B.txt"
NOM_ENCODE_T = "T_x5f_BETA_x5f_COEFFICIENTS_x5f_V2_x5f_8_x5f_B.txt"
OK = "OK"; ECHEC = "ECHEC"; NON_DET = "NON DETERMINE"
DEMONTRE = "DEMONTRÉ"; CALCULE = "CALCULÉ"; CONDITIONNEL = "CONDITIONNEL"; OUVERT = "OUVERT"
TEST_LOGICIEL = "TEST_LOGICIEL"
CALCUL_FORMEL_OK = "CALCUL_FORMEL_OK"; CANDIDAT_GMN = "CANDIDAT_GMN"; CERTIFICATION_GMN = "CERTIFICATION_GMN"
CALCUL_LOCAL_EFFECTIF_IMPLEMENTE = False
ENUMERATION_BRANCHES_EFFECTIVE = False
CERTIFICATION_LOCALE_ETABLIE = False
def _flag(nom):
    try:
        if nom not in globals():
            return (NON_DET, None, "variable %s absente : absence != preuve positive" % nom, "_flag absence")
        v = globals()[nom]
        if type(v) is bool:
            return (OK, v, "variable %s bool exact %s" % (nom, v), "_flag bool")
        return (ECHEC, None, "variable %s type invalide %s : bool exact exige" % (nom, type(v).__name__), "_flag type")
    except Exception as e:
        return (ECHEC, None, "Exception _flag %s : %s" % (nom, e), "_flag exception")
def _sauvegarder_globales(noms):
    sav = {}
    for _n in noms:
        if _n in globals():
            sav[_n] = (True, globals()[_n])
        else:
            sav[_n] = (False, None)
    return sav
def _restaurer_globales(sauvegarde):
    try:
        if not isinstance(sauvegarde, dict):
            return (ECHEC, "sauvegarde non dict", "_restaurer_globales type")
        for _n, (present, val) in sauvegarde.items():
            if type(present) is not bool:
                return (ECHEC, "sauvegarde presence non bool pour %s" % _n, "_restaurer_globales presence")
            if present:
                globals()[_n] = val
            elif _n in globals():
                del globals()[_n]
        return (OK, "restauration exacte", "_restaurer_globales")
    except Exception as e:
        return (ECHEC, "Exception _restaurer_globales: %s" % e, "_restaurer_globales exception")
def to_frac_strict(x, nom="valeur"):
    if type(x) is int:
        return Fraction(x)
    if type(x) is Fraction:
        return x
    raise TypeError("%s: conversion Fraction interdite pour %s (%r)" % (nom, type(x).__name__, x))
class Resultat:
    def __init__(self, nom, statut, detail="", obligatoire=True, raison="", detecteur="", categorie=NON_DET):
        if statut not in (OK, ECHEC, NON_DET):
            raise ValueError("Statut non autorise")
        self.nom = nom; self.statut = statut; self.detail = detail; self.obligatoire = obligatoire
        self.raison = raison; self.detecteur = detecteur; self.categorie = categorie
def statut_global(resultats, certification_locale=None):
    try:
        _ = certification_locale
        if not isinstance(resultats, (list, tuple)):
            return ("ECHEC GLOBAL", "Collection de resultats invalide")
        mand = [r for r in resultats if getattr(r, "obligatoire", False)]
        if len(mand) == 0:
            return ("ECHEC GLOBAL", "Liste obligatoire vide : succes global impossible")
        for r in resultats:
            if getattr(r, "statut", None) not in (OK, ECHEC, NON_DET):
                return ("ECHEC GLOBAL", "Statut non autorise %s" % getattr(r, "nom", "?"))
            if type(getattr(r, "obligatoire", None)) is not bool:
                return ("ECHEC GLOBAL", "Drapeau obligatoire invalide")
        if any(getattr(r, "statut", None) == ECHEC and getattr(r, "obligatoire", False) for r in resultats):
            return ("ECHEC GLOBAL", "Obligatoire refute")
        res = ("PASS PARTIEL", "Verrou V5.5.6.1 : PASS GLOBAL impossible (valuations locales, branches, conditions mathematiques non etablies).")
        if res[0] == "PASS GLOBAL":
            return ("ECHEC GLOBAL", "Erreur de verrouillage : PASS GLOBAL interdit")
        return res
    except Exception as e:
        return ("ECHEC GLOBAL", "Erreur maitrisee dans statut_global : %s (jamais de certification)" % e)
def _check_gf2(x, nom):
    if type(x) is bool:
        return (ECHEC, None, "GF2 %s : bool refuse comme entier" % nom)
    if not type(x) is int:
        return (ECHEC, None, "GF2 %s : type %s, int strict exige" % (nom, type(x).__name__))
    if x < 0:
        return (ECHEC, None, "GF2 %s : entier negatif refuse" % nom)
    return (OK, x, "GF2 %s : int >=0" % nom)
def degF(p):
    st, _, raison = _check_gf2(p, "degF")
    if st != OK:
        return (st, None, raison, "_check_gf2 degF")
    if p == 0:
        return (OK, -1, "degF(0)=-1 par convention explicite documentee", "degF polynome nul")
    return (OK, p.bit_length() - 1, "degF", "degF")
def mulF(a, b):
    st1, _, r1 = _check_gf2(a, "mulF a")
    if st1 != OK:
        return (st1, None, r1, "_check_gf2 mulF a")
    st2, _, r2 = _check_gf2(b, "mulF b")
    if st2 != OK:
        return (st2, None, r2, "_check_gf2 mulF b")
    if a == 0 or b == 0:
        return (OK, 0, "mulF par polynome nul = 0", "mulF nul")
    r = 0; aa, bb = a, b
    while bb:
        if bb & 1:
            r ^= aa
        aa <<= 1; bb >>= 1
    return (OK, r, "mulF", "mulF")
def divmodF(a, b):
    st1, _, r1 = _check_gf2(a, "divmodF a")
    if st1 != OK:
        return (st1, None, None, r1, "_check_gf2 divmodF a")
    st2, _, r2 = _check_gf2(b, "divmodF b")
    if st2 != OK:
        return (st2, None, None, r2, "_check_gf2 divmodF b")
    if b == 0:
        return (ECHEC, None, None, "divmodF : diviseur nul interdit", "divmodF diviseur nul")
    if a == 0:
        return (OK, 0, 0, "divmodF(0,b)=(0,0)", "divmodF nul")
    _, db, _, _ = degF(b); q, r = 0, a
    while r:
        _, dr, _, _ = degF(r)
        if dr < db:
            break
        s = dr - db; q ^= (1 << s); r ^= (b << s)
    return (OK, q, r, "divmodF", "divmodF")
def modF(a, b):
    st, q, r, raison, det = divmodF(a, b)
    if st != OK:
        return (st, None, raison, det)
    return (OK, r, "modF", det)
def gcdF(a, b):
    st1, _, r1 = _check_gf2(a, "gcdF a")
    if st1 != OK:
        return (st1, None, r1, "_check_gf2 gcdF a")
    st2, _, r2 = _check_gf2(b, "gcdF b")
    if st2 != OK:
        return (st2, None, r2, "_check_gf2 gcdF b")
    if a == 0 and b == 0:
        return (ECHEC, None, "gcdF(0,0) indefini", "gcdF nuls")
    if a == 0:
        return (OK, b, "gcdF(0,b)=b", "gcdF nul")
    if b == 0:
        return (OK, a, "gcdF(a,0)=a", "gcdF nul")
    x, y = a, b
    for _ in range(10000):
        if y == 0:
            break
        st, _, r, _, _ = divmodF(x, y)
        if st != OK:
            return (st, None, "gcdF divmod", "gcdF divmod")
        x, y = y, r
    else:
        return (ECHEC, None, "gcdF : limite iterations", "gcdF limite")
    return (OK, x, "gcdF", "gcdF")
def derivF(p):
    st, _, raison = _check_gf2(p, "derivF")
    if st != OK:
        return (st, None, raison, "_check_gf2 derivF")
    if p == 0:
        return (OK, 0, "derivF(0)=0", "derivF nul")
    _, d, _, _ = degF(p); r = 0
    for i in range(d + 1):
        if ((p >> i) & 1) and (i % 2 == 1):
            r ^= (1 << (i - 1))
    return (OK, r, "derivF", "derivF")
def is_irred_rabin_strict(p):
    st, _, raison, _ = _check_gf2(p, "irred")
    if st != OK:
        return (st, False, raison, "_check_gf2 irred")
    if p == 0:
        return (ECHEC, False, "irred : polynome nul", "irred nul")
    _, n, _, _ = degF(p)
    if n <= 0:
        return (OK, False, "deg <=0 non irreductible", "irred deg")
    if ((p >> n) & 1) != 1:
        return (ECHEC, False, "irred : non monique", "irred monicite")
    if n == 1:
        return (OK, True, "deg 1 irreductible", "irred deg1")
    if (p & 1) == 0:
        return (OK, False, "terme constant nul", "irred constant")
    def pow_x_2n(n_):
        r = 0b10
        for _ in range(n_):
            _, rr, _, _ = mulF(r, r); _, _, rr2, _, _ = divmodF(rr, p); r = rr2
        return r
    exp = 0b10
    if pow_x_2n(n) != exp:
        return (OK, False, "x^{2^n} != x mod p", "irred Rabin")
    def prime_divisors(m):
        res = []; d = 2
        while d * d <= m:
            if m % d == 0:
                res.append(d)
                while m % d == 0:
                    m //= d
            d += 1 if d == 2 else 2
        if m > 1:
            res.append(m)
        return res
    for ell in prime_divisors(n):
        e = n // ell; pw = pow_x_2n(e)
        _, g, _, _ = gcdF(pw ^ exp, p)
        if g != 1:
            return (OK, False, "pgcd !=1", "irred Rabin")
    return (OK, True, "Rabin OK", "irred Rabin")
def v2_int_strict(n):
    if type(n) is bool or isinstance(n, float):
        return (ECHEC, None, "v2_int: bool/float refuse", "v2_int type")
    if not type(n) is int:
        return (ECHEC, None, "v2_int: non int", "v2_int type")
    if n == 0:
        return (ECHEC, None, "v2_int(0) indefini", "v2_int nul")
    v, m = 0, abs(n)
    while m % 2 == 0:
        m //= 2; v += 1
    return (OK, v, "v2", "v2_int")
def valider_coeffs_int(coeffs, nom="coeffs"):
    if coeffs is None:
        return (NON_DET, "{} manquants".format(nom), "valider_coeffs_int absence")
    if not isinstance(coeffs, list):
        return (ECHEC, "{} non liste".format(nom), "valider_coeffs_int type")
    for idx, c in enumerate(coeffs):
        if isinstance(c, float) or type(c) is bool:
            return (ECHEC, "{}[{}] float/bool".format(nom, idx), "valider_coeffs_int type")
        if not type(c) is int:
            return (ECHEC, "{}[{}] non int".format(nom, idx), "valider_coeffs_int type")
    return (OK, "{} int stricts".format(nom), "valider_coeffs_int")
def poly_deg_strict(c):
    if c is None:
        return (NON_DET, None, "poly_deg_strict : polynome manquant (None)", "poly_deg_strict absence")
    if not isinstance(c, list):
        return (ECHEC, None, "poly_deg_strict : polynome non liste", "poly_deg_strict type")
    if len(c) == 0:
        return (ECHEC, None, "poly_deg_strict : polynome vide refuse", "poly_deg_strict vide")
    st, raison, _ = valider_coeffs_int(c, "poly")
    if st != OK:
        return (st, None, raison, "poly_deg_strict coeffs")
    if not any(c):
        return (OK, -1, "poly_deg_strict : polynome nul, degre conventionnel -1", "poly_deg_strict nul")
    d = len(c) - 1
    while d > 0 and c[d] == 0:
        d -= 1
    return (OK, d, "poly_deg_strict : degre = plus grand indice non nul", "poly_deg_strict")
def poly_deg_value(c):
    st, d, raison, det = poly_deg_strict(c)
    if st != OK:
        raise ValueError("%s (%s)" % (raison, det))
    return d
def poly_add(a, b):
    try:
        st1, raison1, det1 = valider_coeffs_int(a, "poly_add a")
        if st1 != OK:
            return (st1, None, raison1, det1)
        st2, raison2, det2 = valider_coeffs_int(b, "poly_add b")
        if st2 != OK:
            return (st2, None, raison2, det2)
        if len(a) == 0:
            return (ECHEC, None, "poly_add : polynome vide a refuse", "poly_add vide")
        if len(b) == 0:
            return (ECHEC, None, "poly_add : polynome vide b refuse", "poly_add vide")
        n = max(len(a), len(b))
        r = [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]
        while len(r) > 1 and r[-1] == 0:
            r.pop()
        if len(r) == 0:
            r = [0]
        return (OK, r, "poly_add", "poly_add")
    except Exception as e:
        return (ECHEC, None, "Exception poly_add : %s" % e, "poly_add exception")
def poly_mul(a, b):
    try:
        st1, raison1, det1 = valider_coeffs_int(a, "poly_mul a")
        if st1 != OK:
            return (st1, None, raison1, det1)
        st2, raison2, det2 = valider_coeffs_int(b, "poly_mul b")
        if st2 != OK:
            return (st2, None, raison2, det2)
        if len(a) == 0:
            return (ECHEC, None, "poly_mul : polynome vide a refuse", "poly_mul vide")
        if len(b) == 0:
            return (ECHEC, None, "poly_mul : polynome vide b refuse", "poly_mul vide")
        r = [0] * (len(a) + len(b) - 1)
        for i, ca in enumerate(a):
            if ca:
                for j, cb in enumerate(b):
                    if cb:
                        r[i + j] += ca * cb
        while len(r) > 1 and r[-1] == 0:
            r.pop()
        if len(r) == 0:
            r = [0]
        return (OK, r, "poly_mul", "poly_mul")
    except Exception as e:
        return (ECHEC, None, "Exception poly_mul : %s" % e, "poly_mul exception")
def poly_divmod_strict(a, b):
    try:
        st1, _, _ = valider_coeffs_int(a, "a"); st2, _, _ = valider_coeffs_int(b, "b")
        if st1 != OK:
            return (st1, None, None, "a invalide", "poly_divmod_strict a")
        if st2 != OK:
            return (st2, None, None, "b invalide", "poly_divmod_strict b")
        if len(a) == 0:
            return (ECHEC, None, None, "dividende vide", "poly_divmod_strict vide")
        if len(b) == 0:
            return (ECHEC, None, None, "diviseur vide", "poly_divmod_strict vide")
        if not any(b):
            return (ECHEC, None, None, "diviseur nul", "poly_divmod_strict diviseur nul")
        db = poly_deg_value(b)
        if db < 0:
            return (ECHEC, None, None, "diviseur nul : degre conventionnel -1", "poly_divmod_strict diviseur nul")
        if b[db] != 1:
            return (ECHEC, None, None, "diviseur non monique", "poly_divmod_strict monicite")
        r = list(a)
        while len(r) < len(b):
            r.append(0)
        q = [0] * (max(0, len(a) - db) + 1)
        for k in range(len(a) - 1, db - 1, -1):
            if k < len(r) and r[k] != 0:
                cc = r[k]; q[k - db] = cc
                for j in range(db + 1):
                    r[k - db + j] -= cc * b[j]
        while len(r) > 1 and r[-1] == 0:
            r.pop()
        while len(q) > 1 and q[-1] == 0:
            q.pop()
        return (OK, q, r, "poly_divmod", "poly_divmod_strict")
    except Exception as e:
        return (ECHEC, None, None, "Exception poly_divmod: %s" % e, "poly_divmod_strict exception")
def expansion_phi_adique_strict(T, phi):
    try:
        st1, _, _ = valider_coeffs_int(T, "T"); st2, _, _ = valider_coeffs_int(phi, "phi")
        if st1 != OK:
            return (st1, None, "T invalide", "expansion T")
        if st2 != OK:
            return (st2, None, "phi invalide", "expansion phi")
        if len(T) == 0:
            return (ECHEC, None, "T vide", "expansion vide")
        if len(phi) == 0:
            return (ECHEC, None, "phi vide", "expansion vide")
        if not any(phi):
            return (ECHEC, None, "phi nul : expansion impossible", "expansion phi nul")
        st_d, deg_phi, raison_d, det_d = poly_deg_strict(phi)
        if st_d != OK:
            return (st_d, None, raison_d, det_d)
        if deg_phi < 1:
            return (ECHEC, None, "phi constant (deg<1) : expansion impossible", "expansion phi constant")
        if phi[deg_phi] != 1:
            return (ECHEC, None, "phi non monique", "expansion monicite")
        coeffs, reste = [], list(T)
        for _ in range(101):
            st, q, r, raison, det = poly_divmod_strict(reste, phi)
            if st != OK:
                return (st, None, raison, det)
            coeffs.append(r)
            if len(q) == 1 and q[0] == 0:
                break
            reste = q
        else:
            return (NON_DET, None, "Limite 101 atteinte : expansion non calculee (non impossible)", "expansion limite")
        recon, puis = [0], [1]
        for a in coeffs:
            st_m, prod, raison_m, det_m = poly_mul(a, puis)
            if st_m != OK:
                return (st_m, None, raison_m, det_m)
            st_a, recon_new, raison_a, det_a = poly_add(recon, prod)
            if st_a != OK:
                return (st_a, None, raison_a, det_a)
            recon = recon_new
            st_p, puis_new, raison_p, det_p = poly_mul(puis, phi)
            if st_p != OK:
                return (st_p, None, raison_p, det_p)
            puis = puis_new
        while len(recon) < len(T):
            recon.append(0)
        while len(recon) > 1 and recon[-1] == 0:
            recon.pop()
        t = list(T)
        while len(t) > 1 and t[-1] == 0:
            t.pop()
        if recon != t:
            return (ECHEC, None, "expansion ne reconstruit pas T : impossible", "expansion reconstruction")
        return (OK, coeffs, "expansion", "expansion")
    except Exception as e:
        return (ECHEC, None, "Exception expansion: %s" % e, "expansion exception")
def v0_poly_strict(a):
    try:
        st, _, _ = valider_coeffs_int(a, "a")
        if st != OK:
            return (st, None, "coeffs invalides", "v0 coeffs")
        if len(a) == 0:
            return (ECHEC, None, "v0 : polynome vide", "v0 vide")
        nz = [x for x in a if x != 0]
        if not nz:
            return (ECHEC, None, "v0(0) indefinie (polynome nul)", "v0 nul")
        vals = []
        for x in nz:
            st2, v, _, _ = v2_int_strict(x)
            if st2 != OK:
                return (st2, None, "v2_int", "v0 v2")
            vals.append(v)
        return (OK, min(vals), "v0", "v0")
    except Exception as e:
        return (ECHEC, None, "Exception v0: %s" % e, "v0 exception")
def normaliser_residuel(coeffs):
    try:
        st, raison, det = valider_coeffs_int(coeffs, "residuel")
        if st != OK:
            return (st, None, None, raison, det)
        if len(coeffs) == 0:
            return (ECHEC, None, None, "residuel vide", "normaliser vide")
        if not any(coeffs):
            return (ECHEC, None, None, "residuel nul : v0 indefinie", "normaliser nul")
        st_v, v0, _, _ = v0_poly_strict(coeffs)
        if st_v != OK:
            return (st_v, None, None, "v0", "normaliser v0")
        div = 2 ** v0
        norm = []
        for c in coeffs:
            if c % div != 0:
                return (ECHEC, None, None, "coefficient non divisible par 2^v0", "normaliser divisibilite")
            norm.append(c // div)
        if not all(type(x) is int for x in norm):
            return (ECHEC, None, None, "coefficients normalises non entiers", "normaliser entiers")
        if not any(x % 2 == 1 for x in norm):
            return (ECHEC, None, None, "aucun coefficient impair apres normalisation", "normaliser impair")
        recon = [x * div for x in norm]
        if recon != list(coeffs):
            return (ECHEC, None, None, "reconstruction avant/apres normalisation echec", "normaliser reconstruction")
        return (OK, norm, v0, "normalisation OK : v0=%d, au moins un impair, reconstruction exacte" % v0, "normaliser_residuel")
    except Exception as e:
        return (ECHEC, None, None, "Exception normaliser: %s" % e, "normaliser exception")
def v1_poly_strict(a, phi1, lambda1):
    try:
        if type(lambda1) is bool or isinstance(lambda1, float):
            return (ECHEC, None, ECHEC, "lambda1 bool/float", "certification ECHEC", "v1 lambda1")
        if not (type(lambda1) is int or type(lambda1) is Fraction):
            return (ECHEC, None, ECHEC, "lambda1 type", "certification ECHEC", "v1 lambda1")
        lam = to_frac_strict(lambda1, "lambda1")
        st1, _, _ = valider_coeffs_int(a, "a"); st2, _, _ = valider_coeffs_int(phi1, "phi1")
        if st1 != OK:
            return (st1, None, ECHEC, "a invalide", "certification ECHEC", "v1 a")
        if st2 != OK:
            return (st2, None, ECHEC, "phi1 invalide", "certification ECHEC", "v1 phi1")
        if not any(a):
            return (ECHEC, None, ECHEC, "v1(0) indefinie", "certification ECHEC", "v1 nul")
        st_v0, v0phi1, _, _ = v0_poly_strict(phi1)
        if st_v0 != OK:
            return (st_v0, None, ECHEC, "v0(phi1)", "certification ECHEC", "v1 v0")
        v1_phi = Fraction(v0phi1) + lam
        st_exp, coeffs, _, _ = expansion_phi_adique_strict(a, phi1)
        if st_exp != OK:
            return (st_exp, None, NON_DET, "expansion", "certification NON_DET", "v1 expansion")
        vals = []
        for j, cj in enumerate(coeffs):
            if any(cj):
                st, v0cj, _, _ = v0_poly_strict(cj)
                if st != OK:
                    return (st, None, ECHEC, "v0(coeff)", "certification ECHEC", "v1 v0")
                vals.append(Fraction(v0cj) + Fraction(j) * v1_phi)
        if not vals:
            return (ECHEC, None, ECHEC, "v1 aucun terme", "certification ECHEC", "v1 vide")
        return (OK, min(vals), NON_DET, "CALCUL_FORMEL_OK : min formel = %s" % min(vals), "CERTIFICATION_GMN NON_DET : hypotheses GMN non etablies", "v1")
    except Exception as e:
        return (ECHEC, None, ECHEC, "Exception v1: %s" % e, "certification ECHEC", "v1 exception")
def red1_poly_strict(a, phi1, lambda1):
    try:
        if type(lambda1) is bool or isinstance(lambda1, float):
            return (ECHEC, None, None, None, None, ECHEC, "lambda1 bool/float", "certification ECHEC", "red1 lambda1")
        lam = to_frac_strict(lambda1, "lambda1"); e1 = lam.denominator
        if e1 <= 0:
            return (ECHEC, None, None, None, None, ECHEC, "e1 invalide", "certification ECHEC", "red1 e1")
        st1, _, _ = valider_coeffs_int(a, "a"); st2, _, _ = valider_coeffs_int(phi1, "phi1")
        if st1 != OK:
            return (st1, None, None, None, None, ECHEC, "a invalide", "certification ECHEC", "red1 a")
        if st2 != OK:
            return (st2, None, None, None, None, ECHEC, "phi1 invalide", "certification ECHEC", "red1 phi1")
        if not any(a):
            return (ECHEC, None, None, None, None, ECHEC, "red1(0)", "certification ECHEC", "red1 nul")
        st_v0, v0phi1, _, _ = v0_poly_strict(phi1)
        if st_v0 != OK:
            return (st_v0, None, None, None, None, ECHEC, "v0(phi1)", "certification ECHEC", "red1 v0")
        v1_phi = Fraction(v0phi1) + lam
        st_exp, coeffs, _, _ = expansion_phi_adique_strict(a, phi1)
        if st_exp != OK:
            return (st_exp, None, None, None, None, NON_DET, "expansion", "certification NON_DET", "red1 expansion")
        det = []
        for t, ct in enumerate(coeffs):
            if any(ct):
                st, v0ct, _, _ = v0_poly_strict(ct)
                if st != OK:
                    return (st, None, None, None, None, ECHEC, "v0", "certification ECHEC", "red1 v0")
                det.append((t, ct, v0ct, Fraction(v0ct) + Fraction(t) * v1_phi))
        if not det:
            return (ECHEC, None, None, None, None, ECHEC, "red1 aucun terme", "certification ECHEC", "red1 vide")
        v1 = min(d[3] for d in det); tmin = [d[0] for d in det if d[3] == v1]; t0 = min(tmin)
        for t in tmin:
            if (t - t0) % e1 != 0:
                return (ECHEC, None, None, None, None, ECHEC, "normalisation", "certification ECHEC", "red1 normalisation")
        phi_mod2 = 0
        for i, cc in enumerate(phi1):
            if cc % 2 == 1:
                phi_mod2 ^= (1 << i)
        d = poly_deg_value(phi1); raison_cert = "CERTIFICATION_GMN NON_DET : hypotheses GMN non etablies"
        if d == 1:
            P = 0
            for (t, ct, v0ct, _) in det:
                if t in tmin:
                    if len(ct) != 1:
                        return (ECHEC, None, None, None, None, ECHEC, "coeff non reduit modulo phi1 : len(ct)=%d" % len(ct), "certification ECHEC", "red1 coeff non reduit")
                    if ct[0] == 0:
                        return (ECHEC, None, None, None, None, ECHEC, "coeff nul", "certification ECHEC", "red1 coeff")
                    st2, vv, _, _ = v2_int_strict(ct[0])
                    if st2 != OK:
                        return (st2, None, None, None, None, ECHEC, "v2", "certification ECHEC", "red1 v2")
                    if (ct[0] // (2 ** vv)) % 2 != 1:
                        return (ECHEC, None, None, None, None, ECHEC, "coeff normalise pair", "certification ECHEC", "red1 coeff")
                    P ^= (1 << ((t - t0) // e1))
            return (OK, P, t0, e1, v1, NON_DET, "CALCUL_FORMEL_OK : residuel formel", "%s" % raison_cert, "red1")
        Pd = {}
        for (t, ct, v0ct, _) in det:
            if t in tmin:
                st_n, ad, _, _, _ = normaliser_residuel(ct)
                if st_n != OK:
                    return (st_n, None, None, None, None, ECHEC, "normalisation residuel", "certification ECHEC", "red1 normaliser")
                am = 0
                for j, cc in enumerate(ad):
                    if cc % 2 == 1:
                        am ^= (1 << j)
                st_m, coeff, _, _ = modF(am, phi_mod2) if phi_mod2 != 0 else (OK, am, "", "")
                if st_m != OK:
                    return (st_m, None, None, None, None, ECHEC, "mod", "certification ECHEC", "red1 mod")
                e = (t - t0) // e1; Pd[e] = Pd.get(e, 0) ^ coeff
        return (OK, Pd, t0, e1, v1, NON_DET, "CALCUL_FORMEL_OK : residuel formel", "%s" % raison_cert, "red1")
    except Exception as e:
        return (ECHEC, None, None, None, None, ECHEC, "Exception red1: %s" % e, "certification ECHEC", "red1 exception")
def valider_points_polygone(points):
    try:
        if points is None:
            return (NON_DET, "points manquants", "valider_points absence")
        if not isinstance(points, list):
            return (ECHEC, "points non liste", "valider_points type")
        if len(points) == 0:
            return (ECHEC, "polygone vide", "valider_points vide")
        prev = None
        for idx, pt in enumerate(points):
            if not isinstance(pt, tuple) or len(pt) != 2:
                return (ECHEC, "point %d incomplet" % idx, "valider_points structure")
            x, y = pt
            if isinstance(x, float) or type(x) is bool or not type(x) is int:
                return (ECHEC, "abscisse %d float/bool/non int" % idx, "valider_points abscisse")
            if isinstance(y, float) or type(y) is bool or not (type(y) is int or type(y) is Fraction):
                return (ECHEC, "ordonnee %d float/bool/non exacte" % idx, "valider_points ordonnee")
            if prev is not None:
                if x == prev:
                    return (ECHEC, "abscisse dupliquee %s" % x, "valider_points doublon")
                if x < prev:
                    return (ECHEC, "abscisses non croissantes", "valider_points ordre")
            prev = x
        return (OK, "points valides", "valider_points")
    except Exception as e:
        return (ECHEC, "Exception valider_points: %s" % e, "valider_points exception")
def calculer_enveloppe_inf(points):
    try:
        st, _, _ = valider_points_polygone(points)
        if st != OK:
            return (st, None, "points invalides", "enveloppe points")
        hull = []
        for p in points:
            while len(hull) >= 2:
                x1, y1 = hull[-2]; x2, y2 = hull[-1]; x3, y3 = p
                if x2 == x1 or x3 == x2:
                    return (ECHEC, None, "division par zero enveloppe", "enveloppe division")
                if Fraction(y2 - y1, x2 - x1) >= Fraction(y3 - y2, x3 - x2):
                    hull.pop()
                else:
                    break
            hull.append(p)
        st2, raison2, detecteur2 = valider_points_polygone(hull)
        if st2 != OK:
            return (st2, None, raison2, detecteur2)
        return (OK, hull, "enveloppe", "enveloppe")
    except Exception as e:
        return (ECHEC, None, "Exception enveloppe: %s" % e, "enveloppe exception")
def residuel_ordre1_strict(phi, T):
    try:
        st1, _, _ = valider_coeffs_int(phi, "phi"); st2, _, _ = valider_coeffs_int(T, "T")
        if st1 != OK:
            return (st1, None, ECHEC, "phi invalide", "certification ECHEC", "residuel phi")
        if st2 != OK:
            return (st2, None, ECHEC, "T invalide", "certification ECHEC", "residuel T")
        if not any(phi):
            return (ECHEC, None, ECHEC, "phi nul", "certification ECHEC", "residuel phi nul")
        st_exp, coeffs, _, _ = expansion_phi_adique_strict(T, phi)
        if st_exp != OK:
            return (st_exp, None, NON_DET, "expansion", "certification NON_DET", "residuel expansion")
        d = poly_deg_value(phi); pts = []
        for i, a in enumerate(coeffs):
            if any(a):
                st, v0a, _, _ = v0_poly_strict(a)
                if st != OK:
                    return (st, None, ECHEC, "v0", "certification ECHEC", "residuel v0")
                pts.append((i, Fraction(v0a)))
        st_hull, hull, _ = calculer_enveloppe_inf(pts)
        if st_hull != OK:
            return (st_hull, None, ECHEC, "enveloppe", "certification ECHEC", "residuel enveloppe")
        segs = []
        for k in range(len(hull) - 1):
            x0, y0 = hull[k]; x1, y1 = hull[k + 1]
            if x1 == x0:
                return (ECHEC, None, ECHEC, "division par zero pente", "certification ECHEC", "residuel pente")
            L = x1 - x0; Hh = y0 - y1; dd = math.gcd(L, Hh) if Hh != 0 else L; e = L // dd if dd else L
            pente = Fraction(-Hh, L)
            if d == 1:
                res = 0
                for i in range(x0, x1 + 1):
                    y_exp = Fraction(y0) - Fraction(Hh * (i - x0), L)
                    if y_exp.denominator == 1 and (i, int(y_exp)) in pts and (i - x0) % e == 0:
                        res ^= (1 << ((i - x0) // e))
                segs.append((x0, x1, pente, res))
            else:
                phi_mod2 = 0
                for i, cc in enumerate(phi):
                    if cc % 2 == 1:
                        phi_mod2 ^= (1 << i)
                rl = []
                for i in range(x0, x1 + 1):
                    y_exp = Fraction(y0) - Fraction(Hh * (i - x0), L)
                    if y_exp.denominator == 1 and (i, int(y_exp)) in pts and (i - x0) % e == 0:
                        a = coeffs[i]; st, vv, _, _ = v0_poly_strict(a)
                        if st != OK:
                            return (st, None, ECHEC, "v0", "certification ECHEC", "residuel v0")
                        st_n, ad, _, _, _ = normaliser_residuel(a)
                        if st_n != OK:
                            return (st_n, None, ECHEC, "normalisation", "certification ECHEC", "residuel normaliser")
                        am = 0
                        for j, cc in enumerate(ad):
                            if cc % 2 == 1:
                                am ^= (1 << j)
                        st_m, coeff, _, _ = modF(am, phi_mod2) if phi_mod2 != 0 else (OK, am, "", "")
                        rl.append(((i - x0) // e, coeff))
                segs.append((x0, x1, pente, rl))
        return (OK, segs, NON_DET, "CALCUL_FORMEL_OK : polygone formel calcule, CANDIDAT_GMN", "CERTIFICATION_GMN NON_DET : hypotheses GMN non etablies", "residuel")
    except Exception as e:
        return (ECHEC, None, ECHEC, "Exception residuel: %s" % e, "certification ECHEC", "residuel exception")
def _preuve_locale_valide(preuve):
    return False
def calculer_v2_poly_effectif(coeffs, nom="b_j"):
    try:
        st, raison, _ = valider_coeffs_int(coeffs, nom)
        if st != OK:
            return (st, None, raison, "calculer_v2 coeffs")
        if len(coeffs) == 0:
            return (ECHEC, None, "v2_poly : polynome vide", "calculer_v2 vide")
        nz = [x for x in coeffs if x != 0]
        if not nz:
            return (ECHEC, None, "v2_poly(0) indefini : polynome nul", "calculer_v2 nul")
        vals = []
        for c in nz:
            st2, v, _, _ = v2_int_strict(c)
            if st2 != OK:
                return (st2, None, "v2_int", "calculer_v2 v2_int")
            vals.append(v)
        return (OK, min(vals), "v0 effectif = min v2(coeffs) ; NE prouve PAS la valuation locale GMN", "calculer_v2")
    except Exception as e:
        return (ECHEC, None, "Exception calculer_v2: %s" % e, "calculer_v2 exception")
def valider_v2_gmn(coeffs, preuve_locale, representation_anneau_local):
    try:
        if coeffs is None:
            return (NON_DET, None, "objet b_j manquant", "valider_v2_gmn absence")
        if representation_anneau_local is None:
            return (NON_DET, None, "representation dans l'anneau local manquante", "valider_v2_gmn representation")
        st_c, _, _ = valider_coeffs_int(coeffs, "b_j")
        if st_c != OK:
            return (st_c, None, "b_j invalide", "valider_v2_gmn coeffs")
        if len(coeffs) == 0:
            return (ECHEC, None, "b_j vide", "valider_v2_gmn vide")
        if not any(coeffs):
            return (ECHEC, None, "b_j nul", "valider_v2_gmn nul")
        st_f, val_f, raison_f, det_f = _flag("CALCUL_LOCAL_EFFECTIF_IMPLEMENTE")
        if st_f == ECHEC:
            return (ECHEC, None, raison_f, det_f)
        if st_f == NON_DET:
            return (NON_DET, None, raison_f, det_f)
        if not val_f:
            return (NON_DET, None, "calcul local effectif non implemente et non justifie : aucune declaration ne certifie la valuation locale GMN", "valider_v2_gmn calcul_local_manquant")
        return (NON_DET, None, "calcul local non justifie", "valider_v2_gmn")
    except Exception as e:
        return (ECHEC, None, "Exception valider_v2_gmn: %s" % e, "valider_v2_gmn exception")
def calculer_v2_phi2_effectif(phi2, representation_anneau_local):
    try:
        if phi2 is None:
            return (NON_DET, None, "phi2 manquant", "calculer_v2_phi2 absence")
        if representation_anneau_local is None:
            return (NON_DET, None, "representation anneau local manquante", "calculer_v2_phi2 representation")
        return calculer_v2_poly_effectif(phi2, "phi2")
    except Exception as e:
        return (ECHEC, None, "Exception calculer_v2_phi2: %s" % e, "calculer_v2_phi2 exception")
def valider_v2_phi2_gmn(phi2, preuve_locale, representation_anneau_local):
    try:
        if phi2 is None:
            return (NON_DET, None, "phi2 manquant", "valider_v2_phi2 absence")
        st, _, _ = valider_coeffs_int(phi2, "phi2")
        if st != OK:
            return (st, None, "phi2 invalide", "valider_v2_phi2 coeffs")
        if len(phi2) == 0:
            return (ECHEC, None, "phi2 vide", "valider_v2_phi2 vide")
        if not any(phi2):
            return (ECHEC, None, "phi2 nul", "valider_v2_phi2 nul")
        deg = poly_deg_value(phi2)
        if deg < 0:
            return (ECHEC, None, "phi2 nul : degre conventionnel -1", "valider_v2_phi2 nul")
        if phi2[deg] != 1:
            return (ECHEC, None, "phi2 non monique", "valider_v2_phi2 monicite")
        st_f, val_f, raison_f, det_f = _flag("CALCUL_LOCAL_EFFECTIF_IMPLEMENTE")
        if st_f == ECHEC:
            return (ECHEC, None, raison_f, det_f)
        if st_f == NON_DET:
            return (NON_DET, None, raison_f, det_f)
        if not val_f:
            return (NON_DET, None, "calcul local effectif non implemente : monicite insuffisante", "valider_v2_phi2 calcul_local_manquant")
        return (NON_DET, None, "calcul local non justifie", "valider_v2_phi2")
    except Exception as e:
        return (ECHEC, None, "Exception valider_v2_phi2: %s" % e, "valider_v2_phi2 exception")
def calculer_u_j_arithmetique(v2_bj_valeur, j, v2_phi2_valeur, provenance_v2_bj, provenance_v2_phi2):
    try:
        if v2_bj_valeur is None:
            return (NON_DET, None, NON_DET, "v2(b_j) manquante", "interpretation GMN NON_DET : provenance non demontree", "calculer_u_j absence")
        if v2_phi2_valeur is None:
            return (NON_DET, None, NON_DET, "v2(phi2) manquante", "interpretation GMN NON_DET : provenance non demontree", "calculer_u_j absence")
        if j is None:
            return (NON_DET, None, NON_DET, "j manquant", "interpretation GMN NON_DET", "calculer_u_j absence")
        for nom, val in [("v2_bj", v2_bj_valeur), ("j", j), ("v2_phi2", v2_phi2_valeur)]:
            if isinstance(val, float) or type(val) is bool:
                return (ECHEC, None, ECHEC, "%s float/bool" % nom, "interpretation GMN ECHEC : entree invalide", "calculer_u_j type")
            if not (type(val) is int or type(val) is Fraction):
                return (ECHEC, None, ECHEC, "%s type inattendu" % nom, "interpretation GMN ECHEC", "calculer_u_j type")
        if type(j) is not int or j < 0:
            return (ECHEC, None, ECHEC, "j doit etre un entier >=0", "interpretation GMN ECHEC", "calculer_u_j j")
        u = to_frac_strict(v2_bj_valeur, "v2_bj") + Fraction(j) * to_frac_strict(v2_phi2_valeur, "v2_phi2")
        raison_arith = "arithmetique OK : %s + %s*%s = %s" % (v2_bj_valeur, j, v2_phi2_valeur, u)
        raison_gmn = "interpretation GMN NON_DET : provenance locale non demontree (provenances : %r / %r)" % (provenance_v2_bj, provenance_v2_phi2)
        return (OK, u, NON_DET, raison_arith, raison_gmn, "calculer_u_j")
    except Exception as e:
        return (ECHEC, None, ECHEC, "Exception calculer_u_j: %s" % e, "interpretation GMN ECHEC", "calculer_u_j exception")
def valider_structure_bj_list(coeffs_bj_list):
    try:
        if coeffs_bj_list is None:
            return (NON_DET, "coeffs b_j manquants", "structure_bj absence")
        if not isinstance(coeffs_bj_list, list):
            return (ECHEC, "coeffs b_j non liste", "structure_bj type")
        for j, bj in enumerate(coeffs_bj_list):
            if bj is None:
                return (NON_DET, "b_j manquant j=%d" % j, "structure_bj absence")
            st, _, _ = valider_coeffs_int(bj, "b_j j=%d" % j)
            if st != OK:
                return (st, "b_j j=%d invalide" % j, "structure_bj")
        return (OK, "structure b_j valide", "structure_bj")
    except Exception as e:
        return (ECHEC, "Exception structure_bj: %s" % e, "structure_bj exception")
def valider_types_uj_list(u_j_list):
    try:
        if u_j_list is None:
            return (NON_DET, "u_j manquants", "types_uj absence")
        if not isinstance(u_j_list, list):
            return (ECHEC, "u_j non liste", "types_uj type")
        for j, uj in enumerate(u_j_list):
            if uj is None:
                continue
            if type(uj) is bool or isinstance(uj, float):
                return (ECHEC, "u_j j=%d bool/float" % j, "types_uj type")
            if not (type(uj) is int or type(uj) is Fraction):
                return (ECHEC, "u_j j=%d type inattendu" % j, "types_uj type")
        return (OK, "types u_j valides", "types_uj")
    except Exception as e:
        return (ECHEC, "Exception types_uj: %s" % e, "types_uj exception")
def valider_ordonnees_gmn(coeffs_bj_list, phi2, u_j_list, preuve_v2_bj, representation_anneau_local, preuve_v2_phi2):
    try:
        st_s, raison_s, det_s = valider_structure_bj_list(coeffs_bj_list)
        if st_s != OK:
            return (st_s, "STRUCTURE : " + raison_s, det_s)
        st_t, raison_t, det_t = valider_types_uj_list(u_j_list)
        if st_t != OK:
            return (st_t, "TYPES : " + raison_t, det_t)
        if len(coeffs_bj_list) != len(u_j_list):
            return (ECHEC, "STRUCTURE : longueurs incoherentes", "ordonnees longueurs")
        for j, (bj, uj) in enumerate(zip(coeffs_bj_list, u_j_list)):
            if all(c == 0 for c in bj):
                if uj is not None:
                    return (ECHEC, "b_j=0 mais u_j non None j=%d" % j, "ordonnees b_j nul")
        st_phi, _, raison_phi, det_phi = valider_v2_phi2_gmn(phi2, preuve_v2_phi2, representation_anneau_local)
        if st_phi != OK:
            return (st_phi, "VERROU AMONT CERTIFICATION : B v2(phi2) : " + raison_phi + " ; couples b_j/u_j NON ATTEINTS", "ordonnees verrou amont phi2")
        for j, (bj, uj) in enumerate(zip(coeffs_bj_list, u_j_list)):
            if all(c == 0 for c in bj):
                continue
            st_v, _, raison_v, det_v = valider_v2_gmn(bj, preuve_v2_bj, representation_anneau_local)
            if st_v != OK:
                return (st_v, "VERROU AMONT CERTIFICATION : A/B v2(b_j) j=%d : %s ; couple NON VERIFIE" % (j, raison_v), "ordonnees verrou amont v2")
            if uj is None:
                return (NON_DET, "u_j manquant j=%d" % j, "ordonnees u_j absence")
        return (OK, "ordonnees GMN verifiees", "ordonnees")
    except Exception as e:
        return (ECHEC, "Exception ordonnees: %s" % e, "ordonnees exception")
def valider_t1(s1, ell1, u_j, e1, t1_propose, hypotheses_etablies, exige_integrite, exige_positivite, provenance_branche):
    try:
        if type(exige_integrite) is not bool:
            return (ECHEC, None, ECHEC, "exige_integrite type %s : bool exact exige" % type(exige_integrite).__name__, "certification ECHEC", "t1 exige_integrite type")
        if type(exige_positivite) is not bool:
            return (ECHEC, None, ECHEC, "exige_positivite type %s : bool exact exige" % type(exige_positivite).__name__, "certification ECHEC", "t1 exige_positivite type")
        if e1 is None:
            return (NON_DET, None, NON_DET, "e1 manquant", "certification NON_DET : hypothese e1 manquante", "t1 e1 absence")
        if isinstance(e1, float) or type(e1) is bool:
            return (ECHEC, None, ECHEC, "e1 float/bool", "certification ECHEC : entree invalide", "t1 e1 type")
        if not type(e1) is int:
            return (ECHEC, None, ECHEC, "e1 non int", "certification ECHEC", "t1 e1 type")
        if e1 == 0:
            return (ECHEC, None, ECHEC, "e1=0 impossible", "certification ECHEC", "t1 e1 zero")
        if e1 < 0:
            return (ECHEC, None, ECHEC, "e1<0 impossible", "certification ECHEC", "t1 e1 negatif")
        for nom, val in [("s1", s1), ("ell1", ell1), ("u_j", u_j)]:
            if val is None:
                return (NON_DET, None, NON_DET, "%s manquant" % nom, "certification NON_DET : hypothese manquante", "t1 %s absence" % nom)
            if isinstance(val, float) or type(val) is bool:
                return (ECHEC, None, ECHEC, "%s float/bool" % nom, "certification ECHEC", "t1 %s type" % nom)
            if not (type(val) is int or type(val) is Fraction):
                return (ECHEC, None, ECHEC, "%s type inattendu" % nom, "certification ECHEC", "t1 %s type" % nom)
        if t1_propose is None:
            return (NON_DET, None, NON_DET, "t1 propose manquant", "certification NON_DET", "t1 propose absence")
        if isinstance(t1_propose, float) or type(t1_propose) is bool:
            return (ECHEC, None, ECHEC, "t1 propose float/bool", "certification ECHEC", "t1 propose type")
        if not (type(t1_propose) is int or type(t1_propose) is Fraction):
            return (ECHEC, None, ECHEC, "t1 propose type", "certification ECHEC", "t1 propose type")
        numF = to_frac_strict(s1, "s1") - to_frac_strict(ell1, "ell1") * to_frac_strict(u_j, "u_j")
        resF = numF / Fraction(e1)
        if exige_integrite and resF.denominator != 1:
            return (ECHEC, None, ECHEC, "t1 non entier %s alors qu'integrite exigee" % resF, "certification ECHEC", "t1 integrite")
        if exige_positivite and resF < 0:
            return (ECHEC, None, ECHEC, "t1 negatif %s alors que positivite exigee" % resF, "certification ECHEC", "t1 positivite")
        if to_frac_strict(t1_propose, "t1") != resF:
            return (ECHEC, None, ECHEC, "t1 propose %s != exact %s" % (t1_propose, resF), "certification ECHEC", "t1 recalcul")
        raison_calcul = "calcul exact OK : t1 = %s" % resF
        if hypotheses_etablies is not True:
            return (OK, resF, NON_DET, raison_calcul, "certification NON_DET : hypotheses GMN non etablies (declaration insuffisante)", "t1 hypotheses")
        if provenance_branche is None:
            return (OK, resF, NON_DET, raison_calcul, "certification NON_DET : provenance branche manquante", "t1 provenance")
        return (OK, resF, NON_DET, raison_calcul, "certification NON_DET : hypotheses declarees True, non demontrees (bool != preuve)", "t1 certification")
    except Exception as e:
        return (ECHEC, None, ECHEC, "Exception t1: %s" % e, "certification ECHEC", "t1 exception")
def audit_invariants_type(phi1, lambda1, psi1, hypothese_psi1_irreductible_exigee, psi1_construction_documentee):
    try:
        if phi1 is None:
            return (NON_DET, {"etat": "phi1 manquant"})
        st, _, _ = valider_coeffs_int(phi1, "phi1")
        if st != OK:
            return (st, {"etat": "phi1 invalide"})
        if len(phi1) == 0:
            return (ECHEC, {"etat": "phi1 vide"})
        if not any(phi1):
            return (ECHEC, {"etat": "phi1 nul"})
        st_d, deg1, raison_d, det_d = poly_deg_strict(phi1)
        if st_d != OK:
            return (st_d, {"etat": raison_d})
        if phi1[deg1] != 1:
            return (ECHEC, {"etat": "phi1 non monique"})
        phi_mod2 = 0
        for i, cc in enumerate(phi1):
            if cc % 2 == 1:
                phi_mod2 ^= (1 << i)
        if phi_mod2 == 0:
            return (ECHEC, {"etat": "phi1 mod 2 nul"})
        if psi1 is None:
            return (NON_DET, {"etat": "psi1 manquant"})
        if type(psi1) is bool or not type(psi1) is int:
            return (ECHEC, {"etat": "psi1 bool/non int"})
        if psi1 == 0:
            return (ECHEC, {"etat": "psi1 nul"})
        if psi1_construction_documentee is not True:
            return (NON_DET, {"etat": "construction psi1 non documentee (declaration insuffisante)"})
        if type(lambda1) is bool or isinstance(lambda1, float):
            return (ECHEC, {"etat": "lambda1 bool/float"})
        lam = to_frac_strict(lambda1, "lambda1"); e1 = lam.denominator; h1 = lam.numerator
        st_f, f1, _, _ = degF(psi1)
        if st_f != OK:
            return (st_f, {"etat": "f1 deg psi1"})
        if math.gcd(h1, e1) != 1:
            return (ECHEC, {"etat": "gcd(h1,e1)!=1"})
        inv = {"phi1_deg": {"etat": "ETABLI", "valeur": deg1}, "phi1_monique": {"etat": "ETABLI", "valeur": True}, "phi1_mod2": {"etat": "ETABLI", "valeur": phi_mod2}, "psi1": {"etat": "ETABLI", "valeur": psi1}, "psi1_non_nul": {"etat": "ETABLI", "valeur": True}, "e1": {"etat": "CALCULE", "valeur": e1}, "h1": {"etat": "CALCULE", "valeur": h1}, "f1": {"etat": "CALCULE", "valeur": f1}}
        if hypothese_psi1_irreductible_exigee:
            st_irr, est_irr, raison_irr, det_irr = is_irred_rabin_strict(psi1)
            if st_irr != OK:
                return (st_irr, {"etat": "irreductibilite psi1 : " + raison_irr})
            if not est_irr:
                return (ECHEC, {"etat": "psi1 non irreductible alors qu'exigee"})
            inv["psi1_irreductible"] = {"etat": "ETABLI", "valeur": True}
        else:
            inv["psi1_irreductible"] = {"etat": "NON EXIGEE", "valeur": None}
        for nom in ["ell1", "ell_prime_1", "pi1", "pi2", "Phi1", "gamma1", "z1", "s1", "v2"]:
            inv[nom] = {"etat": "NON ETABLI", "valeur": None}
        return (NON_DET, inv)
    except Exception as e:
        return (ECHEC, {"etat": "Exception audit : %s" % e})
def verifier_convention_historique():
    return (NON_DET, "Convention historique NON DETERMINE : documentation independante manquante. Convention rapportee (non etablie) : c_39..c_0, un entier par ligne, fin de ligne finale. Hash fichier source != hash representation canonique != hash reconstruction H : non interchangeables.")
def trouver_fichier_T():
    cands = [NOM_LOGIQUE_T, os.path.join("/mnt/data", NOM_LOGIQUE_T), NOM_ENCODE_T, os.path.join("/mnt/data", NOM_ENCODE_T)]
    for cand in cands:
        if os.path.isfile(cand):
            note = "Nom LOGIQUE (underscores reels)" if "_x5f_" not in cand else "Nom ENCODE (_x5f_ litteral, variante GitHub)"
            return (OK, cand, note)
    return (NON_DET, None, "Fichier absent")
def parser_strict_fichier_T(texte):
    try:
        if texte is None:
            return (NON_DET, None, "Fichier absent : NON_DET, non ECHEC", "parser absence")
        if not isinstance(texte, str):
            return (ECHEC, None, "texte non str", "parser type")
        _lignes_parser = [_l.strip() for _l in texte.splitlines()]
        _has_c_parser = any(_l.startswith("c_") for _l in _lignes_parser)
        _has_H_parser = any(_l.startswith("H=") for _l in _lignes_parser)
        if _has_H_parser and not _has_c_parser:
            return (NON_DET, None, "Forme H= : reconstruction non etablie", "parser H=")
        coeffs = {}
        for raw in texte.splitlines():
            line = raw.strip()
            if line == "":
                continue
            if line.startswith("#") or line.startswith("HEADER:"):
                continue
            if line.startswith("c_"):
                m = re.match(r"^c_(\d+)=(-?\d+)$", line)
                if not m:
                    return (ECHEC, None, "Ligne mal formee : %r" % line, "parser malforme")
                idx = int(m.group(1))
                if idx < 0 or idx > 39:
                    return (ECHEC, None, "Indice hors plage c_%d" % idx, "parser hors plage")
                if idx in coeffs:
                    return (ECHEC, None, "Indice duplique c_%d (ne pas ecraser)" % idx, "parser duplique")
                coeffs[idx] = int(m.group(2))
            else:
                return (ECHEC, None, "Ligne de donnees inconnue : %r" % line, "parser inconnue")
        if len(coeffs) != 40:
            return (ECHEC, None, "Coefficients manquants : %d/40" % len(coeffs), "parser manquant")
        if sorted(coeffs.keys()) != list(range(40)):
            return (ECHEC, None, "Indices c_0..c_39 non exacts", "parser indices")
        c = [coeffs[i] for i in range(40)]
        st, _, _ = valider_coeffs_int(c, "T")
        if st != OK:
            return (st, None, "coeffs T invalides", "parser coeffs")
        return (OK, c, "parseur strict OK", "parser")
    except Exception as e:
        return (ECHEC, None, "Exception parser: %s" % e, "parser exception")
def valider_authenticite_T(coeffs, sha_attendu):
    try:
        st_conv, det_conv = verifier_convention_historique()
        if st_conv != OK:
            return (NON_DET, "authenticite_historique = NON DETERMINE : %s" % det_conv, "authenticite convention")
        if coeffs is None:
            return (ECHEC, "coeffs manquants", "authenticite absence")
        if not isinstance(coeffs, list) or len(coeffs) != 40:
            return (ECHEC, "longueur !=40", "authenticite longueur")
        st, _, _ = valider_coeffs_int(coeffs, "T")
        if st != OK:
            return (st, "coeffs invalides", "authenticite coeffs")
        if poly_deg_value(coeffs) != 39:
            return (ECHEC, "degre !=39", "authenticite degre")
        if coeffs[39] != 1:
            return (ECHEC, "mauvaise monicite", "authenticite monicite")
        ser = "\n".join(str(coeffs[i]) for i in range(39, -1, -1)) + "\n"
        h = hashlib.sha256(ser.encode("utf-8")).hexdigest()
        if h != sha_attendu:
            return (ECHEC, "SHA != attendu", "authenticite SHA")
        return (OK, "authentification OK", "authenticite")
    except Exception as e:
        return (ECHEC, "Exception authentification: %s" % e, "authenticite exception")
def valider_sha_avec_convention_test(coeffs, sha_attendu, convention_nom):
    try:
        if coeffs is None or not isinstance(coeffs, list) or len(coeffs) != 40:
            return (ECHEC, "longueur !=40", "SHA test longueur")
        st, _, _ = valider_coeffs_int(coeffs, "T")
        if st != OK:
            return (st, "coeffs invalides", "SHA test coeffs")
        if poly_deg_value(coeffs) != 39:
            return (ECHEC, "degre !=39", "SHA test degre")
        if coeffs[39] != 1:
            return (ECHEC, "mauvaise monicite", "SHA test monicite")
        ser = "\n".join(str(coeffs[i]) for i in range(39, -1, -1)) + "\n"
        h = hashlib.sha256(ser.encode("utf-8")).hexdigest()
        if h != sha_attendu:
            return (ECHEC, "SHA != attendu (convention test %s)" % convention_nom, "SHA test SHA")
        return (OK, "SHA OK avec convention test %s (non historique)" % convention_nom, "SHA test")
    except Exception as e:
        return (ECHEC, "Exception SHA test: %s" % e, "SHA test exception")
def valider_structure_polynome(poly, nom):
    try:
        if poly is None:
            return (NON_DET, "%s manquant" % nom, "structure absence")
        if not isinstance(poly, list):
            return (ECHEC, "%s non liste" % nom, "structure type")
        if len(poly) == 0:
            return (ECHEC, "%s vide" % nom, "structure vide")
        st, _, _ = valider_coeffs_int(poly, nom)
        if st != OK:
            return (st, "%s coeffs invalides" % nom, "structure coeffs")
        if not any(poly):
            return (ECHEC, "%s nul : degre conventionnel -1, non monique" % nom, "structure nul")
        deg = poly_deg_value(poly)
        if poly[deg] != 1:
            return (ECHEC, "%s non monique" % nom, "structure monicite")
        return (OK, "%s valide deg %d monique" % (nom, deg), "structure")
    except Exception as e:
        return (ECHEC, "Exception structure %s: %s" % (nom, e), "structure exception")
def certifier_phi2_strict(phi1, lambda1, psi1, phi2, hypothese_psi1_irreductible_exigee, psi1_construction_documentee, preuve_locale_v2):
    try:
        if type(lambda1) is bool or isinstance(lambda1, float):
            return (ECHEC, {"raison": "STRUCTUREL lambda1 bool/float", "detecteur": "certifier_phi2 lambda1"})
        if not (type(lambda1) is int or type(lambda1) is Fraction):
            return (ECHEC, {"raison": "STRUCTUREL lambda1 type", "detecteur": "certifier_phi2 lambda1"})
        lam = to_frac_strict(lambda1, "lambda1")
        if lam.denominator != 1:
            return (NON_DET, {"raison": "STRUCTUREL e1 != 1 : construction generale non demontree", "detecteur": "certifier_phi2 e1"})
        st_f, val_f, raison_f, det_f = _flag("CALCUL_LOCAL_EFFECTIF_IMPLEMENTE")
        if st_f == ECHEC:
            return (ECHEC, {"raison": raison_f, "detecteur": det_f})
        if st_f == NON_DET:
            return (NON_DET, {"raison": raison_f, "detecteur": det_f})
        if not val_f:
            return (NON_DET, {"raison": "CERTIFICATION LOCALE calcul local effectif non implemente : certification phi2 impossible", "detecteur": "certifier_phi2 calcul_local_manquant"})
        st_audit, inv = audit_invariants_type(phi1, lambda1, psi1, hypothese_psi1_irreductible_exigee, psi1_construction_documentee)
        if st_audit == ECHEC:
            return (ECHEC, {"raison": "STRUCTUREL audit premier ordre ECHEC : %s" % inv, "detecteur": "certifier_phi2 audit"})
        if st_audit == NON_DET:
            return (NON_DET, {"raison": "HYPOTHESES audit premier ordre NON DETERMINE : invariants essentiels inconnus (ell1 etc.)", "detecteur": "certifier_phi2 audit"})
        if type(psi1) is bool or not type(psi1) is int:
            return (ECHEC, {"raison": "STRUCTUREL psi1 bool/non int", "detecteur": "certifier_phi2 psi1"})
        st1, det1, _ = valider_structure_polynome(phi1, "phi1")
        if st1 != OK:
            return (st1, {"raison": det1, "detecteur": "certifier_phi2 phi1"})
        st2, det2, _ = valider_structure_polynome(phi2, "phi2")
        if st2 != OK:
            return (st2, {"raison": det2, "detecteur": "certifier_phi2 phi2"})
        deg1 = poly_deg_value(phi1); deg2 = poly_deg_value(phi2)
        if deg1 != 1 or deg2 != 1:
            return (NON_DET, {"raison": "FORMEL cas deg phi1=deg phi2=1 non verifie", "detecteur": "certifier_phi2 degre"})
        st_vphi2, _, raison_vphi2, det_vphi2 = valider_v2_phi2_gmn(phi2, preuve_locale_v2, "anneau local")
        if st_vphi2 != OK:
            return (st_vphi2, {"raison": "CERTIFICATION LOCALE v2(phi2) : " + raison_vphi2, "detecteur": det_vphi2})
        st_exp, exp, det_exp, det_exp_det = expansion_phi_adique_strict(phi2, phi1)
        if st_exp != OK:
            return (st_exp, {"raison": det_exp, "detecteur": det_exp_det})
        pts = []
        for i, a in enumerate(exp):
            if any(a):
                st, v0a, _, _ = v0_poly_strict(a)
                if st != OK:
                    return (st, {"raison": "v0", "detecteur": "certifier_phi2 v0"})
                pts.append((i, Fraction(v0a)))
        st_hull, hull, _ = calculer_enveloppe_inf(pts)
        if st_hull != OK:
            return (st_hull, {"raison": "enveloppe", "detecteur": "certifier_phi2 enveloppe"})
        if len(hull) != 2:
            return (ECHEC, {"raison": "FORMEL polygone %d sommets" % len(hull), "detecteur": "certifier_phi2 polygone"})
        (x0, y0), (x1, y1) = hull[0], hull[1]
        if x1 == x0:
            return (ECHEC, {"raison": "FORMEL division par zero pente", "detecteur": "certifier_phi2 pente"})
        pente = Fraction(-(y0 - y1), x1 - x0)
        if pente != Fraction(-lam):
            return (ECHEC, {"raison": "FORMEL pente %s != -lambda1" % pente, "detecteur": "certifier_phi2 pente"})
        st_res, segs, st_cert_res, raison_res, raison_cert_res, det_res = residuel_ordre1_strict(phi1, phi2)
        if st_res != OK:
            return (st_res, {"raison": raison_res, "detecteur": det_res})
        if st_cert_res != OK:
            return (NON_DET, {"raison": "CERTIFICATION LOCALE residuel : " + raison_cert_res, "detecteur": det_res})
        if len(segs) != 1:
            return (ECHEC, {"raison": "FORMEL segments !=1", "detecteur": "certifier_phi2 residuel"})
        _, _, _, res_phi2 = segs[0]
        if type(res_phi2) is bool or not type(res_phi2) is int:
            return (ECHEC, {"raison": "FORMEL residuel bool/non int", "detecteur": "certifier_phi2 residuel"})
        if res_phi2 != psi1:
            return (ECHEC, {"raison": "FORMEL residuel != psi1 (egalite residuels echec)", "detecteur": "certifier_phi2 egalite residuels"})
        if ((psi1 >> degF(psi1)[1]) & 1) != 1:
            return (ECHEC, {"raison": "STRUCTUREL psi1 non monique", "detecteur": "certifier_phi2 psi1 monicite"})
        diff = [phi2[i] - (phi1[i] if i < len(phi1) else 0) for i in range(max(len(phi2), len(phi1)))]
        while len(diff) > 1 and diff[-1] == 0:
            diff.pop()
        if poly_deg_value(diff) != 0:
            return (ECHEC, {"raison": "FORMEL difference non constante", "detecteur": "certifier_phi2 difference"})
        dval = diff[0]
        if dval == 0:
            return (ECHEC, {"raison": "FORMEL difference nulle (phi2==phi1), statut controle, sans v2_int(0)", "detecteur": "certifier_phi2 difference nulle"})
        st_v2, v2d, _, _ = v2_int_strict(dval)
        if st_v2 != OK:
            return (st_v2, {"raison": "v2(d)", "detecteur": "certifier_phi2 v2"})
        if v2d != lam.numerator:
            return (ECHEC, {"raison": "FORMEL v2(d) != h1", "detecteur": "certifier_phi2 v2"})
        if abs(dval) // (2 ** lam.numerator) % 2 != 1:
            return (ECHEC, {"raison": "FORMEL d/2^h1 pair", "detecteur": "certifier_phi2 d"})
        if deg2 != deg1 * 1 * degF(psi1)[1]:
            return (ECHEC, {"raison": "FORMEL degre != attendu", "detecteur": "certifier_phi2 degre"})
        return (NON_DET, {"raison": "CERTIFICATION GMN NON_DET : hypotheses non etablies", "detecteur": "certifier_phi2 certification"})
    except Exception as e:
        return (ECHEC, {"raison": "Exception certifier_phi2: %s" % e, "detecteur": "certifier_phi2 exception"})
def valider_perimetre_strict(perimetre_etudie, branches):
    try:
        if perimetre_etudie is None:
            return (NON_DET, "perimetre manquant", "perimetre absence")
        if not isinstance(perimetre_etudie, dict):
            return (ECHEC, "perimetre non dict", "perimetre type")
        for cle in ["couverture_demonteree", "branches_attendues"]:
            if cle not in perimetre_etudie:
                return (ECHEC, "perimetre cle manquante %s" % cle, "perimetre structure")
        if type(perimetre_etudie["couverture_demonteree"]) is not bool:
            return (ECHEC, "couverture_demonteree type %s : bool exact exige" % type(perimetre_etudie["couverture_demonteree"]).__name__, "perimetre couverture type")
        if type(perimetre_etudie["branches_attendues"]) is bool or not type(perimetre_etudie["branches_attendues"]) is int:
            return (ECHEC, "branches_attendues type : int exact exige, bool refuse", "perimetre branches_attendues type")
        if perimetre_etudie["branches_attendues"] <= 0:
            return (ECHEC, "branches_attendues <= 0", "perimetre branches_attendues valeur")
        if branches is not None and isinstance(branches, dict):
            if perimetre_etudie["branches_attendues"] != len(branches):
                return (ECHEC, "incoherence : branches_attendues=%d mais len(branches)=%d" % (perimetre_etudie["branches_attendues"], len(branches)), "perimetre coherence")
        return (OK, "perimetre structurellement valide ; couverture NON demontree par ce seul controle", "perimetre")
    except Exception as e:
        return (ECHEC, "Exception perimetre: %s" % e, "perimetre exception")
def verifier_branches_completes(branches, perimetre_etudie, hypotheses_gmn):
    try:
        if type(hypotheses_gmn) is not bool:
            return (ECHEC, None, "hypotheses_gmn type %s : bool exact exige" % type(hypotheses_gmn).__name__, "branches hypotheses_gmn type")
        if branches is None:
            return (NON_DET, None, "branches manquantes", "branches absence")
        if perimetre_etudie is None:
            return (NON_DET, None, "perimetre non defini", "branches perimetre")
        if not isinstance(branches, dict):
            return (ECHEC, None, "branches non dict", "branches type")
        if len(branches) == 0:
            return (NON_DET, None, "aucune branche dans le perimetre", "branches vide")
        for nom, b in branches.items():
            if not isinstance(b, dict):
                return (ECHEC, None, "branche %s non dict" % nom, "branches structure")
            for cle in ["degre", "pente", "multiplicite", "residuel", "hypotheses"]:
                if cle not in b:
                    return (ECHEC, None, "branche %s cle manquante %s" % (nom, cle), "branches structure")
            if type(b["degre"]) is bool or not type(b["degre"]) is int or b["degre"] <= 0:
                return (ECHEC, None, "branche %s degre invalide" % nom, "branches degre")
            if not type(b["pente"]) is Fraction:
                return (ECHEC, None, "branche %s pente non Fraction" % nom, "branches pente")
            if type(b["multiplicite"]) is bool or not type(b["multiplicite"]) is int or b["multiplicite"] <= 0:
                return (ECHEC, None, "branche %s multiplicite invalide" % nom, "branches multiplicite")
            if type(b["residuel"]) is bool or not type(b["residuel"]) is int:
                return (ECHEC, None, "branche %s residuel invalide" % nom, "branches residuel")
            if type(b["hypotheses"]) is not bool:
                return (ECHEC, None, "branche %s hypotheses type %s : bool exact exige" % (nom, type(b["hypotheses"]).__name__), "branches hypotheses type")
        st_p, raison_p, det_p = valider_perimetre_strict(perimetre_etudie, branches)
        if st_p != OK:
            return (st_p, None, raison_p, det_p)
        st_f, val_f, raison_f, det_f = _flag("ENUMERATION_BRANCHES_EFFECTIVE")
        if st_f == ECHEC:
            return (ECHEC, None, raison_f, det_f)
        if st_f == NON_DET:
            return (NON_DET, None, raison_f, det_f)
        if not val_f:
            return (NON_DET, None, "verrou branches V5.5.6.1 : structure valide, donnees arithmetiques non certifiees, hypotheses non etablies, enumeration non demontree. Bool True != preuve.", "branches verrou")
        return (NON_DET, None, "exhaustivite non demontree", "branches verrou")
    except Exception as e:
        return (ECHEC, None, "Exception branches: %s" % e, "branches exception")
def audit_ordre2(phi2, coeffs_bj, u_j_list, residuel_ordre2, hypotheses_gmn):
    try:
        if phi2 is None:
            return (NON_DET, "phi2 manquant", "ordre2 phi2 absence")
        if coeffs_bj is None:
            return (NON_DET, "coeffs b_j manquants", "ordre2 b_j absence")
        if u_j_list is None:
            return (NON_DET, "ordonnees GMN manquantes", "ordre2 u_j absence")
        if residuel_ordre2 is None:
            return (NON_DET, "residuel ordre 2 manquant", "ordre2 residuel absence")
        if hypotheses_gmn is not True:
            return (NON_DET, "hypotheses GMN ordre 2 non etablies", "ordre2 hypotheses")
        return (NON_DET, "ordre 2 non acheve : donnees insuffisantes pour conclure dans cette version", "ordre2")
    except Exception as e:
        return (ECHEC, "Exception ordre2: %s" % e, "ordre2 exception")
def main():
    debut = datetime.datetime.now(); fonctions = []; exceptions = []; resultats = []
    def ajouter(nom, statut, detail="", obligatoire=True, raison="", detecteur="", categorie=NON_DET):
        if categorie == DEMONTRE:
            categorie = TEST_LOGICIEL; detail = detail + " [categorie corrigee : DEMONTRE -> TEST_LOGICIEL]"
        try:
            r = Resultat(nom, statut, detail, obligatoire, raison, detecteur, categorie)
        except Exception as e:
            r = Resultat(nom, ECHEC, "statut non autorise: %s" % e, obligatoire, str(e), "ajouter", NON_DET); exceptions.append(str(e))
        resultats.append(r); fonctions.append(nom)
        print("[V5.5.6.1] %s : %s (%s) obligatoire=%s raison=%s detecteur=%s categorie=%s" % (nom, r.statut, detail, obligatoire, raison, detecteur, categorie)); return r
    def _check_statut_valeur(statut_attendu, statut_obtenu, valeur_attendue, valeur_obtenue, detecteur_attendu=None, detecteur_obtenu=None):
        if statut_obtenu != statut_attendu:
            return False
        if valeur_obtenue != valeur_attendue:
            return False
        if detecteur_attendu is not None and detecteur_obtenu != detecteur_attendu:
            return False
        return True
    def test_valeur(nom, statut_attendu, statut_obtenu, valeur_attendue, valeur_obtenue, detecteur_attendu=None, detecteur_obtenu=None, categorie=CALCULE):
        if categorie == DEMONTRE:
            categorie = TEST_LOGICIEL
        ok_test = _check_statut_valeur(statut_attendu, statut_obtenu, valeur_attendue, valeur_obtenue, detecteur_attendu, detecteur_obtenu)
        print("[V5.5.6.1] TEST VALEUR %s | %s" % (nom, "PASS" if ok_test else "FAIL"))
        ajouter(nom, OK if ok_test else ECHEC, "statut=%s valeur=%r" % (statut_obtenu, valeur_obtenue), obligatoire=True, raison="statut+valeur+detecteur", detecteur=detecteur_obtenu if detecteur_obtenu is not None else "", categorie=categorie); return ok_test
    _SENTINELLE_ABSENT = object(); _EXIGE_OMIS = object()
    def _evaluer_test_negatif(attendu_statut, obtenu_statut, raison, obtenu_detecteur, detecteur_attendu, resultat_obtenu=_SENTINELLE_ABSENT, exige_resultat_none=_EXIGE_OMIS):
        if exige_resultat_none is _EXIGE_OMIS:
            return False
        ok_test = (obtenu_statut == attendu_statut) and (obtenu_detecteur == detecteur_attendu) and (raison is not None and len(str(raison)) > 0)
        if not ok_test:
            return False
        if exige_resultat_none is True:
            if resultat_obtenu is _SENTINELLE_ABSENT:
                return False
            if resultat_obtenu is not None:
                return False
        elif exige_resultat_none is False:
            if resultat_obtenu is _SENTINELLE_ABSENT:
                return False
            if resultat_obtenu is None:
                return False
        elif exige_resultat_none is None:
            if resultat_obtenu is not _SENTINELLE_ABSENT:
                return False
        else:
            return False
        return True
    def test_negatif(nom, entree, fonction, attendu_statut, obtenu_statut, raison, obtenu_detecteur, detecteur_attendu, categorie=TEST_LOGICIEL, resultat_obtenu=_SENTINELLE_ABSENT, exige_resultat_none=_EXIGE_OMIS):
        ok_test = _evaluer_test_negatif(attendu_statut, obtenu_statut, raison, obtenu_detecteur, detecteur_attendu, resultat_obtenu, exige_resultat_none)
        print("[V5.5.6.1] TEST NEGATIF %s | %s" % (nom, "PASS" if ok_test else "FAIL"))
        ajouter(nom, OK if ok_test else ECHEC, "attendu=%s obtenu=%s exige=%s" % (attendu_statut, obtenu_statut, "OMIS" if exige_resultat_none is _EXIGE_OMIS else exige_resultat_none), obligatoire=True, raison=raison, detecteur=obtenu_detecteur, categorie=categorie); return ok_test
    print("[V5.5.6.1] AUDIT STRICT INVARIANTS GMN V5.5.6.1. V5.5.5, V5.5.6 preservees.")
    print("[V5.5.6.1] Python %s" % sys.version.split()[0]); print("[V5.5.6.1] Debut %s" % debut.isoformat())
    try:
        _chemin_self = os.path.abspath(__file__)
        with open(_chemin_self, "r", encoding="utf-8") as _fh:
            _lignes_self = _fh.read().splitlines()
        _marqueurs = [(_i + 1, _l) for _i, _l in enumerate(_lignes_self) if "```" in _l]
        ajouter("C13 : aucune ligne Markdown dans le fichier", OK if len(_marqueurs) == 0 else ECHEC, "marqueurs=%s" % _marqueurs, obligatoire=True, raison="integrite syntaxique", detecteur="auto-lecture", categorie=TEST_LOGICIEL)
    except Exception as e:
        ajouter("C13 : auto-lecture echec", ECHEC, str(e), obligatoire=True, raison=str(e), detecteur="auto-lecture", categorie=TEST_LOGICIEL)
    lst_tous_ok = [Resultat("a", OK, "", True), Resultat("b", OK, "", True)]
    sg, det_sg = statut_global(lst_tous_ok); ajouter("Verrou : tous OK -> PASS PARTIEL max", OK if sg == "PASS PARTIEL" else ECHEC, "sg=%s" % sg, obligatoire=True, raison=det_sg, detecteur="statut_global", categorie=TEST_LOGICIEL)
    sg, det_sg = statut_global([]); ajouter("Verrou : liste vide -> ECHEC GLOBAL", OK if sg == "ECHEC GLOBAL" else ECHEC, "sg=%s" % sg, obligatoire=True, raison=det_sg, detecteur="statut_global", categorie=TEST_LOGICIEL)
    sg, det_sg = statut_global([Resultat("a", OK, "", True), Resultat("b", ECHEC, "", True)]); ajouter("Verrou : obligatoire ECHEC -> ECHEC GLOBAL", OK if sg == "ECHEC GLOBAL" else ECHEC, "sg=%s" % sg, obligatoire=True, raison=det_sg, detecteur="statut_global", categorie=TEST_LOGICIEL)
    st, val, raison, det = mulF(0b101, 0b11); test_valeur("GF2 mulF : (Y^2+1)(Y+1)=Y^3+Y^2+Y+1", OK, st, 0b1111, val, "mulF", det, categorie=CALCULE)
    st, val, raison, det = degF(0b101); test_valeur("GF2 degF : deg(Y^2+1)=2", OK, st, 2, val, "degF", det, categorie=CALCULE)
    st, q, r, raison, det = divmodF(0b1111, 0b11); test_valeur("GF2 divmodF : quotient = Y^2+1", OK, st, 0b101, q, "divmodF", det, categorie=CALCULE); test_valeur("GF2 divmodF : reste = 0", OK, st, 0, r, "divmodF", det, categorie=CALCULE)
    st, val, raison, det = gcdF(0b101, 0b11); test_valeur("GF2 gcdF : pgcd(Y^2+1,Y+1)=Y+1", OK, st, 0b11, val, "gcdF", det, categorie=CALCULE)
    st, val, raison, det = derivF(0b101); test_valeur("GF2 derivF : deriv(Y^2+1)=0", OK, st, 0, val, "derivF", det, categorie=CALCULE)
    st, val, raison, det = degF(True); test_negatif("GF2 degF : bool -> ECHEC, resultat None", "True", "degF", ECHEC, st, raison, det, "_check_gf2 degF", categorie=TEST_LOGICIEL, resultat_obtenu=val, exige_resultat_none=True)
    st, res, raison, det = poly_add([1, 2], [3, 4]); test_valeur("poly_add : [1,2]+[3,4]=[4,6]", OK, st, [4, 6], res, "poly_add", det, categorie=CALCULE)
    st, res, raison, det = poly_add([1], [True]); test_negatif("poly_add 2e : bool -> ECHEC, resultat None", "[1]+[True]", "poly_add", ECHEC, st, raison, det, "valider_coeffs_int type", categorie=TEST_LOGICIEL, resultat_obtenu=res, exige_resultat_none=True)
    st, res, raison, det = poly_mul([1, 1], [1, 1]); test_valeur("poly_mul : (1+X)(1+X)=[1,2,1]", OK, st, [1, 2, 1], res, "poly_mul", det, categorie=CALCULE)
    st, coeffs, raison, det = expansion_phi_adique_strict([1, 1], [1, 1]); test_valeur("Expansion : [1,1]/[1,1] = [[0],[1]]", OK, st, [[0], [1]], coeffs, "expansion", det, categorie=CALCULE)
    st, coeffs, raison, det = expansion_phi_adique_strict([1, 1], [5]); test_negatif("Expansion : phi constant -> ECHEC, resultat None", "phi=[5]", "expansion_phi_adique_strict", ECHEC, st, raison, det, "expansion phi constant", categorie=TEST_LOGICIEL, resultat_obtenu=coeffs, exige_resultat_none=True)
    _T_limite = [1] * 153
    st, coeffs, raison, det = expansion_phi_adique_strict(_T_limite, [1, 1])
    test_negatif("Expansion limite 101 depassee -> NON_DET, resultat None", "deg 152", "expansion_phi_adique_strict", NON_DET, st, raison, det, "expansion limite", categorie=TEST_LOGICIEL, resultat_obtenu=coeffs, exige_resultat_none=True)
    st, hull, raison, det = calculer_enveloppe_inf([(0, Fraction(4)), (1, Fraction(2)), (2, Fraction(0))]); test_valeur("Polygone : colineaires -> extremes seulement", OK, st, [(0, Fraction(4)), (2, Fraction(0))], hull, "enveloppe", det, categorie=CALCULE)
    st, hull, raison, det = calculer_enveloppe_inf([(0, Fraction(4)), (0, Fraction(1))])
    test_negatif("Enveloppe : abscisse dupliquee -> ECHEC, resultat None", "x=0 deux fois", "calculer_enveloppe_inf", ECHEC, st, raison, det, "enveloppe points", categorie=TEST_LOGICIEL, resultat_obtenu=hull, exige_resultat_none=True)
    st_n, norm, v0n, raison_n, det_n = normaliser_residuel([12, 20])
    test_valeur("C08 : normaliser [12,20] -> [3,5]", OK, st_n, [3, 5], norm, "normaliser_residuel", det_n, categorie=CALCULE)
    ajouter("C08 : normaliser [12,20] v0=2, au moins un impair", OK if (st_n == OK and v0n == 2 and any(x % 2 == 1 for x in norm)) else ECHEC, "norm=%s v0=%s" % (norm, v0n), obligatoire=True, raison=raison_n, detecteur=det_n, categorie=TEST_LOGICIEL)
    st_n, norm, v0n, raison_n, det_n = normaliser_residuel([-12, 20])
    test_valeur("C08 : normaliser [-12,20] -> [-3,5]", OK, st_n, [-3, 5], norm, "normaliser_residuel", det_n, categorie=CALCULE)
    st_n, norm, v0n, raison_n, det_n = normaliser_residuel([6, 10])
    test_valeur("C08 : normaliser [6,10] -> [3,5]", OK, st_n, [3, 5], norm, "normaliser_residuel", det_n, categorie=CALCULE)
    st_n, norm, v0n, raison_n, det_n = normaliser_residuel([0, 0])
    test_negatif("C08 : normaliser [0,0] -> ECHEC, resultat None", "[0,0]", "normaliser_residuel", ECHEC, st_n, raison_n, det_n, "normaliser nul", categorie=TEST_LOGICIEL, resultat_obtenu=norm, exige_resultat_none=True)
    st_n, norm, v0n, raison_n, det_n = normaliser_residuel([True, 2])
    test_negatif("C08 : normaliser [True,2] -> ECHEC, resultat None", "[True,2]", "normaliser_residuel", ECHEC, st_n, raison_n, det_n, "valider_coeffs_int type", categorie=TEST_LOGICIEL, resultat_obtenu=norm, exige_resultat_none=True)
    st_n, norm, v0n, raison_n, det_n = normaliser_residuel([1.5, 2])
    test_negatif("C08 : normaliser [1.5,2] -> ECHEC, resultat None", "[1.5,2]", "normaliser_residuel", ECHEC, st_n, raison_n, det_n, "valider_coeffs_int type", categorie=TEST_LOGICIEL, resultat_obtenu=norm, exige_resultat_none=True)
    st_n, norm, v0n, raison_n, det_n = normaliser_residuel([])
    test_negatif("C08 : normaliser [] -> ECHEC, resultat None", "[]", "normaliser_residuel", ECHEC, st_n, raison_n, det_n, "normaliser vide", categorie=TEST_LOGICIEL, resultat_obtenu=norm, exige_resultat_none=True)
    st_n, norm, v0n, raison_n, det_n = normaliser_residuel(None)
    test_negatif("C08 : normaliser None -> NON_DET, resultat None", "None", "normaliser_residuel", NON_DET, st_n, raison_n, det_n, "valider_coeffs_int absence", categorie=TEST_LOGICIEL, resultat_obtenu=norm, exige_resultat_none=True)
    preuve_complete = {"type": "preuve_locale_verifiee", "verifiee": True, "source": "texte", "definition": "texte"}
    st_v, _, raison_v, det_v = valider_v2_gmn([4, 8], preuve_complete, "anneau local")
    ajouter("Certification locale v2 : dict fabrique -> NON_DET, jamais OK", OK if st_v == NON_DET else ECHEC, raison_v, obligatoire=True, raison=raison_v, detecteur=det_v, categorie=NON_DET)
    st_s, raison_s, det_s = valider_structure_bj_list([[1], [1]])
    ajouter("C10 : structure b_j valide, independante du verrou NON_DET", OK if st_s == OK else ECHEC, raison_s, obligatoire=True, raison=raison_s, detecteur=det_s, categorie=TEST_LOGICIEL)
    st_s, raison_s, det_s = valider_structure_bj_list([[1], [True]])
    test_negatif("C10 : structure b_j bool -> ECHEC, independant du verrou", "[True]", "valider_structure_bj_list", ECHEC, st_s, raison_s, det_s, "structure_bj", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_s, raison_s, det_s = valider_structure_bj_list([[1], None])
    test_negatif("C10 : structure b_j None -> NON_DET, independant du verrou", "None", "valider_structure_bj_list", NON_DET, st_s, raison_s, det_s, "structure_bj absence", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_s, raison_s, det_s = valider_structure_bj_list("abc")
    test_negatif("C10 : structure b_j non liste -> ECHEC", "'abc'", "valider_structure_bj_list", ECHEC, st_s, raison_s, det_s, "structure_bj type", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_t, raison_t, det_t = valider_types_uj_list([Fraction(4), Fraction(4)])
    ajouter("C10 : types u_j valides, independants du verrou NON_DET", OK if st_t == OK else ECHEC, raison_t, obligatoire=True, raison=raison_t, detecteur=det_t, categorie=TEST_LOGICIEL)
    for _val_uj, _nom_uj in [(True, "True"), (False, "False"), (4.0, "4.0"), ("4", "'4'"), ([4], "[4]")]:
        st_t, raison_t, det_t = valider_types_uj_list([_val_uj, Fraction(4)])
        test_negatif("C10 : types u_j %s -> ECHEC, sans dependre du deverrouillage" % _nom_uj, _nom_uj, "valider_types_uj_list", ECHEC, st_t, raison_t, det_t, "types_uj type", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_t, raison_t, det_t = valider_types_uj_list(None)
    test_negatif("C10 : types u_j None -> NON_DET", "None", "valider_types_uj_list", NON_DET, st_t, raison_t, det_t, "types_uj absence", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_t, raison_t, det_t = valider_types_uj_list([None, Fraction(4)])
    ajouter("C10 : types u_j None dans la liste -> tolere ici, absence signalee plus tard", OK if st_t == OK else ECHEC, raison_t, obligatoire=True, raison=raison_t, detecteur=det_t, categorie=TEST_LOGICIEL)
    st_ord, raison_ord, det_ord = valider_ordonnees_gmn([[1], [1]], [-15, 1], [Fraction(4), Fraction(4)], preuve_complete, "anneau local", preuve_complete)
    ajouter("C10 : ordonnees dict fabrique -> NON_DET (verrou certification)", OK if st_ord == NON_DET else ECHEC, raison_ord, obligatoire=True, raison=raison_ord, detecteur=det_ord, categorie=NON_DET)
    st_ord, raison_ord, det_ord = valider_ordonnees_gmn([[1], [1]], [-15, 1], [True, Fraction(4)], preuve_complete, "anneau local", preuve_complete)
    ajouter("C10 : ordonnees u_j True -> ECHEC avant le verrou", OK if (st_ord == ECHEC and "TYPES" in raison_ord) else ECHEC, raison_ord, obligatoire=True, raison=raison_ord, detecteur=det_ord, categorie=TEST_LOGICIEL)
    st_ord, raison_ord, det_ord = valider_ordonnees_gmn([[1], [1]], [2, 1], [Fraction(4), Fraction(4)], preuve_complete, "anneau local", preuve_complete)
    ajouter("C10 : ordonnees phi2 non monique -> verrou amont explicite", OK if (st_ord == ECHEC and "VERROU AMONT" in raison_ord) else ECHEC, raison_ord, obligatoire=True, raison=raison_ord, detecteur=det_ord, categorie=TEST_LOGICIEL)
    branches_valides = {"b1": {"degre": 1, "pente": Fraction(-4, 1), "multiplicite": 1, "residuel": 0b11, "hypotheses": True}}
    perimetre_ok = {"couverture_demonteree": True, "branches_attendues": 1}
    st_p, raison_p, det_p = valider_perimetre_strict(perimetre_ok, branches_valides)
    ajouter("C09 : perimetre valide structurellement, couverture NON demontree par ce seul controle", OK if st_p == OK else ECHEC, raison_p, obligatoire=True, raison=raison_p, detecteur=det_p, categorie=TEST_LOGICIEL)
    st_p, raison_p, det_p = valider_perimetre_strict({"branches_attendues": 1}, branches_valides)
    test_negatif("C09 : perimetre cle manquante -> ECHEC", "cle manquante", "valider_perimetre_strict", ECHEC, st_p, raison_p, det_p, "perimetre structure", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_p, raison_p, det_p = valider_perimetre_strict({"couverture_demonteree": 1, "branches_attendues": 1}, branches_valides)
    test_negatif("C09 : perimetre couverture=1 -> ECHEC type", "couverture=1", "valider_perimetre_strict", ECHEC, st_p, raison_p, det_p, "perimetre couverture type", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_p, raison_p, det_p = valider_perimetre_strict({"couverture_demonteree": "True", "branches_attendues": 1}, branches_valides)
    test_negatif("C09 : perimetre couverture='True' -> ECHEC type", "couverture='True'", "valider_perimetre_strict", ECHEC, st_p, raison_p, det_p, "perimetre couverture type", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_p, raison_p, det_p = valider_perimetre_strict({"couverture_demonteree": True, "branches_attendues": True}, branches_valides)
    test_negatif("C09 : perimetre branches_attendues=True -> ECHEC type", "branches_attendues=True", "valider_perimetre_strict", ECHEC, st_p, raison_p, det_p, "perimetre branches_attendues type", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_p, raison_p, det_p = valider_perimetre_strict({"couverture_demonteree": True, "branches_attendues": 2}, branches_valides)
    test_negatif("C09 : perimetre incoherence compte -> ECHEC", "2 != 1", "valider_perimetre_strict", ECHEC, st_p, raison_p, det_p, "perimetre coherence", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_p, raison_p, det_p = valider_perimetre_strict("abc", branches_valides)
    test_negatif("C09 : perimetre non dict -> ECHEC", "'abc'", "valider_perimetre_strict", ECHEC, st_p, raison_p, det_p, "perimetre type", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_b, _, raison_b, det_b = verifier_branches_completes(branches_valides, perimetre_ok, True)
    test_negatif("C09 : branches tout True + couverture True -> NON_DET, pas de preuve", "tout True", "verifier_branches_completes", NON_DET, st_b, raison_b, det_b, "branches verrou", categorie=NON_DET, resultat_obtenu=None, exige_resultat_none=None)
    st_b, _, raison_b, det_b = verifier_branches_completes({"b1": {"degre": 0, "pente": Fraction(-4, 1), "multiplicite": 1, "residuel": 0b11, "hypotheses": True}}, perimetre_ok, True)
    test_negatif("C09 : branches degre invalide -> ECHEC", "degre 0", "verifier_branches_completes", ECHEC, st_b, raison_b, det_b, "branches degre", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_b, _, raison_b, det_b = verifier_branches_completes(branches_valides, perimetre_ok, 1)
    test_negatif("C09 : hypotheses_gmn=1 -> ECHEC type", "1", "verifier_branches_completes", ECHEC, st_b, raison_b, det_b, "branches hypotheses_gmn type", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    _br_hyp = {"b1": {"degre": 1, "pente": Fraction(-4, 1), "multiplicite": 1, "residuel": 0b11, "hypotheses": 1}}
    st_b, _, raison_b, det_b = verifier_branches_completes(_br_hyp, perimetre_ok, True)
    test_negatif("C09 : branche hypotheses=1 -> ECHEC type", "hypotheses=1", "verifier_branches_completes", ECHEC, st_b, raison_b, det_b, "branches hypotheses type", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_c, t1_val, st_cert, raison_c, raison_cert, det_t = valider_t1(4, 0, Fraction(4), 1, 4, True, True, True, "branche fixture")
    ajouter("t1 : calcul exact OK, certification NON_DET meme avec hypotheses=True", OK if (st_c == OK and t1_val == Fraction(4) and st_cert == NON_DET) else ECHEC, "t1=%s" % t1_val, obligatoire=True, raison=raison_cert, detecteur=det_t, categorie=CONDITIONNEL)
    st_c, t1_val, st_cert, raison_c, raison_cert, det_t = valider_t1(4, 0, Fraction(4), 1, 0, True, True, True, "branche")
    test_negatif("t1 : substitution t0 -> calcul ECHEC", "t1=0", "valider_t1", ECHEC, st_c, raison_c, det_t, "t1 recalcul", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    for _val in [1, 0, "True", "False", None]:
        st_c, t1_val, st_cert, raison_c, raison_cert, det_t = valider_t1(4, 0, Fraction(4), 1, 4, True, _val, True, "branche")
        test_negatif("C02 : exige_integrite=%r -> ECHEC type" % (_val,), "exige_integrite=%r" % (_val,), "valider_t1", ECHEC, st_c, raison_c, det_t, "t1 exige_integrite type", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
        st_c, t1_val, st_cert, raison_c, raison_cert, det_t = valider_t1(4, 0, Fraction(4), 1, 4, True, True, _val, "branche")
        test_negatif("C02 : exige_positivite=%r -> ECHEC type" % (_val,), "exige_positivite=%r" % (_val,), "valider_t1", ECHEC, st_c, raison_c, det_t, "t1 exige_positivite type", categorie=TEST_LOGICIEL, resultat_obtenu=None, exige_resultat_none=None)
    st_f, v1_val, st_cert, raison_f, raison_c, det_v1 = v1_poly_strict([1, 1], [1, 1], Fraction(4, 1))
    ajouter("v1 : CALCUL_FORMEL_OK, CERTIFICATION_GMN NON_DET", OK if (st_f == OK and st_cert == NON_DET) else ECHEC, "v1=%s" % v1_val, obligatoire=True, raison=raison_c, detecteur=det_v1, categorie=CONDITIONNEL)
    st_f, P, t0, e1_v, v1_v, st_cert, raison_f, raison_c, det_r = red1_poly_strict([1, 1], [1, 1], Fraction(4, 1))
    ajouter("red1 : CALCUL_FORMEL_OK, CERTIFICATION_GMN NON_DET", OK if (st_f == OK and st_cert == NON_DET) else ECHEC, "P=%s" % P, obligatoire=True, raison=raison_c, detecteur=det_r, categorie=CONDITIONNEL)
    st_f, segs, st_cert, raison_f, raison_c, det_res = residuel_ordre1_strict([1, 1], [1, 1])
    ajouter("residuel : CALCUL_FORMEL_OK (CANDIDAT_GMN), CERTIFICATION_GMN NON_DET", OK if (st_f == OK and st_cert == NON_DET) else ECHEC, "segs=%s" % segs, obligatoire=True, raison=raison_c, detecteur=det_res, categorie=CONDITIONNEL)
    st_arith, u, st_gmn, raison_a, raison_g, det_u = calculer_u_j_arithmetique(4, 1, 4, "entree arithmetique", "entree arithmetique")
    test_valeur("u_j : arithmetique 4+1*4=8, statut arith OK", OK, st_arith, Fraction(8), u, "calculer_u_j", det_u, categorie=CALCULE)
    ajouter("u_j : interpretation GMN NON_DET", OK if st_gmn == NON_DET else ECHEC, raison_g, obligatoire=True, raison=raison_g, detecteur=det_u, categorie=CONDITIONNEL)
    st_inv, inv = audit_invariants_type([1, 1], Fraction(4, 1), 0b11, True, True); ajouter("Audit invariants premier ordre (FIXTURE_SYNTHETIQUE)", st_inv, "FIXTURE : [1,1], Fraction(4,1), 0b11 ne sont PAS des donnees de T", obligatoire=True, raison=str(inv), detecteur="audit_invariants_type", categorie=NON_DET)
    st_cert, det_cert = certifier_phi2_strict([1, 1], Fraction(4, 1), 0b11, [-15, 1], True, True, preuve_complete); ajouter("C11 : certification phi2 dict fabrique -> NON_DET", st_cert, str(det_cert), obligatoire=True, raison=str(det_cert), detecteur="certifier_phi2_strict", categorie=NON_DET)
    st_cert, det_cert = certifier_phi2_strict([1, 1], True, 0b11, [-15, 1], True, True, preuve_complete); ajouter("C11 : STRUCTUREL lambda1 bool -> ECHEC", OK if st_cert == ECHEC else ECHEC, str(det_cert), obligatoire=True, raison=str(det_cert), detecteur="certifier_phi2_strict", categorie=TEST_LOGICIEL)
    st_cert, det_cert = certifier_phi2_strict([1, 1], 4.0, 0b11, [-15, 1], True, True, preuve_complete); ajouter("C11 : STRUCTUREL lambda1 float -> ECHEC", OK if st_cert == ECHEC else ECHEC, str(det_cert), obligatoire=True, raison=str(det_cert), detecteur="certifier_phi2_strict", categorie=TEST_LOGICIEL)
    st_cert, det_cert = certifier_phi2_strict([1, 1], "4", 0b11, [-15, 1], True, True, preuve_complete); ajouter("C11 : STRUCTUREL lambda1 str -> ECHEC", OK if st_cert == ECHEC else ECHEC, str(det_cert), obligatoire=True, raison=str(det_cert), detecteur="certifier_phi2_strict", categorie=TEST_LOGICIEL)
    st_cert, det_cert = certifier_phi2_strict([1, 1], Fraction(1, 2), 0b11, [-15, 1], True, True, preuve_complete); ajouter("C11 : STRUCTUREL e1 != 1 -> NON_DET", OK if st_cert == NON_DET else ECHEC, str(det_cert), obligatoire=True, raison=str(det_cert), detecteur="certifier_phi2_strict", categorie=NON_DET)
    st_cert, det_cert = certifier_phi2_strict([1, 1], Fraction(4, 1), 0b11, [2, 1], True, True, preuve_complete); ajouter("C11 : STRUCTUREL phi2 non monique -> NON_DET / ECHEC, jamais OK", OK if st_cert in (NON_DET, ECHEC) else ECHEC, str(det_cert), obligatoire=True, raison=str(det_cert), detecteur="certifier_phi2_strict", categorie=NON_DET)
    st_cert, det_cert = certifier_phi2_strict([2, 1], Fraction(4, 1), 0b11, [-15, 1], True, True, preuve_complete); ajouter("C11 : STRUCTUREL phi1 non monique -> ECHEC / NON_DET, jamais OK", OK if st_cert in (NON_DET, ECHEC) else ECHEC, str(det_cert), obligatoire=True, raison=str(det_cert), detecteur="certifier_phi2_strict", categorie=NON_DET)
    st_cert, det_cert = certifier_phi2_strict([1, 1], Fraction(4, 1), True, [-15, 1], True, True, preuve_complete); ajouter("C11 : STRUCTUREL psi1 bool -> ECHEC / NON_DET, jamais OK", OK if st_cert in (NON_DET, ECHEC) else ECHEC, str(det_cert), obligatoire=True, raison=str(det_cert), detecteur="certifier_phi2_strict", categorie=NON_DET)
    st_o, raison_o, det_o = audit_ordre2(None, None, None, None, False); ajouter("Ordre 2 : donnees manquantes -> NON_DET", st_o, raison_o, obligatoire=True, raison=raison_o, detecteur=det_o, categorie=NON_DET)
    st, coeffs, raison, det = parser_strict_fichier_T(None); test_negatif("Parser : fichier T absent -> NON_DET, resultat None", "None", "parser_strict_fichier_T", NON_DET, st, raison, det, "parser absence", categorie=NON_DET, resultat_obtenu=coeffs, exige_resultat_none=True)
    txt_hist = "\n".join(["# commentaire autorise", "HEADER: test"] + ["c_%d=0" % i for i in range(40)])
    st, coeffs, raison, det = parser_strict_fichier_T(txt_hist)
    ajouter("Parser historique : # + HEADER: acceptes", OK if st == OK else ECHEC, raison, obligatoire=True, raison=raison, detecteur=det, categorie=TEST_LOGICIEL)
    txt_H_comment = "\n".join(["# H= commentaire, pas une donnee"] + ["c_%d=0" % i for i in range(40)])
    st, coeffs, raison, det = parser_strict_fichier_T(txt_H_comment)
    ajouter("Parser : 'H=' dans # ne declenche pas NON_DET", OK if st == OK else ECHEC, raison, obligatoire=True, raison=raison, detecteur=det, categorie=TEST_LOGICIEL)
    st, coeffs, raison, det = parser_strict_fichier_T("H=1\n")
    test_negatif("Parser : ligne 'H=' seule -> NON_DET, resultat None", "H=1", "parser_strict_fichier_T", NON_DET, st, raison, det, "parser H=", categorie=NON_DET, resultat_obtenu=coeffs, exige_resultat_none=True)
```python
    for _txt, _nom, _det_att in [
        ("\n".join(["c_0=1", "c_0=2"] + ["c_%d=0" % i for i in range(1, 40)]), "duplique", "parser duplique"),
        ("\n".join(["c_%d=0" % i for i in range(40)] + ["c_40=1"]), "hors plage", "parser hors plage"),
        ("\n".join(["c_0=abc"] + ["c_%d=0" % i for i in range(1, 40)]), "mal forme", "parser malforme"),
        ("\n".join(["c_%d=0" % i for i in range(40)] + ["FOO=1"]), "inconnue", "parser inconnue"),
        ("\n".join(["c_%d=0" % i for i in range(39)]), "manquant", "parser manquant"),
    ]:
        st, coeffs, raison, det = parser_strict_fichier_T(_txt); test_negatif("Parser : %s -> ECHEC, resultat None" % _nom, _nom, "parser_strict_fichier_T", ECHEC, st, raison, det, _det_att, categorie=TEST_LOGICIEL, resultat_obtenu=coeffs, exige_resultat_none=True)
    st_conv, det_conv = verifier_convention_historique(); ajouter("C12 : convention historique SHA -> NON_DET", st_conv, det_conv, obligatoire=True, raison=det_conv, detecteur="verifier_convention_historique", categorie=NON_DET)
    _coeffs_test = [0] * 39 + [1]
    _ser_test = "\n".join(str(_coeffs_test[i]) for i in range(39, -1, -1)) + "\n"
    _sha_test = hashlib.sha256(_ser_test.encode("utf-8")).hexdigest()
    st_auth, raison_auth, det_auth = valider_authenticite_T(_coeffs_test, _sha_test)
    ajouter("C12 : authenticite historique -> NON_DET meme avec bon SHA (convention non etablie)", OK if st_auth == NON_DET else ECHEC, raison_auth, obligatoire=True, raison=raison_auth, detecteur=det_auth, categorie=NON_DET)
    st_sha, raison_sha, det_sha = valider_sha_avec_convention_test(_coeffs_test, _sha_test, "test-canonique")
    ajouter("C12 : SHA avec convention de test -> OK, distinct de l'authentification historique", OK if st_sha == OK else ECHEC, raison_sha, obligatoire=True, raison=raison_sha, detecteur=det_sha, categorie=TEST_LOGICIEL)
    ajouter("authenticite_historique", NON_DET, "authenticite_historique = NON DETERMINE", obligatoire=True, raison="convention non demontree", detecteur="verifier_convention_historique", categorie=NON_DET)
    ajouter("Certification locale GMN", NON_DET, "CERTIFICATION LOCALE = NON_DET : calcul local effectif non implemente", obligatoire=True, raison="calcul local manquant", detecteur="valider_v2_gmn", categorie=NON_DET)
    ajouter("Exhaustivite des branches", NON_DET, "EXHAUSTIVITE = NON_DET : enumeration effective non demontree", obligatoire=True, raison="enumeration manquante", detecteur="verifier_branches_completes", categorie=NON_DET)
    ajouter("Indice local en 2", NON_DET, "INDICE LOCAL EN 2 : NON CALCULE", obligatoire=True, raison="calcul non effectue", detecteur="indice local", categorie=OUVERT)
    ajouter("Maximalite de Z[beta]", NON_DET, "MAXIMALITE : NON DEMONTREE", obligatoire=True, raison="demonstration manquante", detecteur="maximalite", categorie=OUVERT)
    ajouter("Egalite Z[beta]=O_K", NON_DET, "EGALITE : NON DEMONTREE", obligatoire=True, raison="demonstration manquante", detecteur="egalite ordre", categorie=OUVERT)
    st_find, chemin_T, note_find = trouver_fichier_T(); ajouter("Fichier T trouve (si present)", st_find, str(chemin_T) + " " + note_find, obligatoire=False, raison=note_find, detecteur="trouver_fichier_T", categorie=NON_DET)
    st_e, hull_e, raison_e, det_e = calculer_enveloppe_inf([(0, Fraction(4)), (1, Fraction(2)), (2, Fraction(0))])
    ajouter("Regression : enveloppe colineaires, st2 defini", OK if (st_e == OK and hull_e == [(0, Fraction(4)), (2, Fraction(0))]) else ECHEC, "hull=%s" % (hull_e,), obligatoire=True, raison=raison_e, detecteur=det_e, categorie=TEST_LOGICIEL)
    st_pa, res_pa, raison_pa, det_pa = poly_add([1, 0, 0], [2])
    ajouter("Regression : poly_add [1,0,0]+[2]=[3]", OK if (st_pa == OK and res_pa == [3] and det_pa == "poly_add") else ECHEC, "res=%s" % (res_pa,), obligatoire=True, raison=raison_pa, detecteur=det_pa, categorie=TEST_LOGICIEL)
    fin = datetime.datetime.now()
    n_tests = len(resultats); n_pass = len([r for r in resultats if r.statut == OK]); n_fail = len([r for r in resultats if r.statut == ECHEC]); n_non_det = len([r for r in resultats if r.statut == NON_DET]); echecs = [r.nom for r in resultats if r.statut == ECHEC]
    ok_compteurs = (n_tests == n_pass + n_fail + n_non_det) and (len(echecs) == n_fail)
    print("[V5.5.6.1] CONTROLE COMPTEURS : n_tests=%d n_pass=%d n_fail=%d n_non_det=%d len(echecs)=%d coherent=%s" % (n_tests, n_pass, n_fail, n_non_det, len(echecs), ok_compteurs))
    print("[V5.5.6.1] ===== RAPPORT FINAL =====")
    print("[V5.5.6.1] 1. Calculs arithmetiques (CALCULE) :")
    for r in resultats:
        if r.categorie == CALCULE:
            print("[V5.5.6.1]   %s : %s (%s)" % (r.nom, r.statut, r.detail))
    print("[V5.5.6.1] 2. Tests logiciels (TEST_LOGICIEL) :")
    for r in resultats:
        if r.categorie == TEST_LOGICIEL:
            print("[V5.5.6.1]   %s : %s (%s) detecteur=%s" % (r.nom, r.statut, r.detail, r.detecteur))
    print("[V5.5.6.1] 3. Resultats formels : CALCUL_FORMEL_OK pour GF(2), expansion, v1, red1, residuel, u_j arithmetique, t1 calcul, poly_add, poly_mul.")
    print("[V5.5.6.1] 4. Candidats GMN : CANDIDAT_GMN pour v1, red1, residuel, u_j, t1. Aucun candidat ne devient une certification.")
    print("[V5.5.6.1] 5. Hypotheses etablies : aucune hypothese GMN locale etablie (liste vide, hors definitions).")
    print("[V5.5.6.1] 6. Hypotheses non etablies : calcul local, valuations locales, invariants ordre 2, branches, ordre 2, convention historique, certification phi2.")
    print("[V5.5.6.1] 7. Certifications locales : NON_DET.")
    print("[V5.5.6.1] 8. Exhaustivite des branches : NON_DET.")
    print("[V5.5.6.1] 9. Indice local en 2 : NON CALCULE.")
    print("[V5.5.6.1] 10. Maximalite : NON DEMONTREE. Z[beta] = O_K : NON DEMONTRE.")
    print("[V5.5.6.1] DEMONTRE : aucune proposition GMN demontree par une procedure et un argument explicitement presents (categorie reservee, jamais attribuee a un test logiciel).")
    print("[V5.5.6.1] CONDITIONNEL :")
    for r in resultats:
        if r.categorie == CONDITIONNEL:
            print("[V5.5.6.1]   %s : %s (%s)" % (r.nom, r.statut, r.detail))
    print("[V5.5.6.1] OUVERT :")
    for r in resultats:
        if r.categorie == OUVERT:
            print("[V5.5.6.1]   %s : %s (%s)" % (r.nom, r.statut, r.detail))
    print("[V5.5.6.1] POINTS NON DETERMINES :")
    for r in resultats:
        if r.categorie == NON_DET:
            print("[V5.5.6.1]   %s : %s (%s)" % (r.nom, r.statut, r.detail))
    print("[V5.5.6.1] Rapporte mais non reproduit : T(X)=X^38(X+1) mod 2 ; T'(X)=X^38 mod 2 ; gcd(T,T')=X^38 ; v2(Disc(T))=1608 ; polygones, pentes, residuels, factorisations historiques.")
    print("[V5.5.6.1] Version Python : %s" % sys.version.split()[0])
    print("[V5.5.6.1] Nombre de tests : %d" % n_tests)
    print("[V5.5.6.1] Nombre de PASS : %d" % n_pass)
    print("[V5.5.6.1] Nombre de FAIL : %d" % n_fail)
    print("[V5.5.6.1] Nombre de NON_DET : %d" % n_non_det)
    print("[V5.5.6.1] Controle compteurs coherent : %s" % ok_compteurs)
    print("[V5.5.6.1] Liste des echecs : %s" % echecs)
    sg, det_sg = statut_global(resultats); print("[V5.5.6.1] Conclusion globale : %s (%s)" % (sg, det_sg)); print("[V5.5.6.1] Aucun PASS GLOBAL.")
    print("[V5.5.6.1] Liste des points mathematiques non determines : certification locale, exhaustivite des branches, valuations locales, invariants ordre 2, ordre 2, convention historique, certification phi2, indice local en 2, maximalite de Z[beta], Z[beta]=O_K.")
    print("[V5.5.6.1] Debut : %s ; Fin : %s" % (debut.isoformat(), fin.isoformat())); print("[V5.5.6.1] Fonctions : %s" % ", ".join(sorted(set(fonctions)))); print("[V5.5.6.1] Exceptions : %s" % exceptions)
    print("[V5.5.6.1] INDICE LOCAL EN 2 : NON CALCULE"); print("[V5.5.6.1] Maximalite de Z[beta] : NON DEMONTREE"); print("[V5.5.6.1] Z[beta] = O_K : NON DEMONTRE")
if __name__ == "__main__":
    main()
# Verification (a executer, non pretendue executee ici) :
#   python3 --version
#   python3 -m py_compile AUDIT_STRICT_INVARIANTS_GMN_V5.5.6.1.py
#   sha256sum AUDIT_STRICT_INVARIANTS_GMN_V5.5.6.1.py
#   python3 AUDIT_STRICT_INVARIANTS_GMN_V5.5.6.1.py
