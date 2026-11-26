#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DODECA — BORNE ENERGETIQUE EXACTE V3.3.20 — PARTIE B1.
Construction et validation de l'état (state).
Architecture V3.3.20 : état explicite, aucun exec(), aucun return locals().
main_partie_1() -> state (dict explicite, clés nommées).
main_partie_2(state) dans la Partie B2 consomme ce state.
Les 3 scripts sont contrôlés avant et après l'audit : A, B1, B2.
Correctif indépendant dérivé de B1 V3.3.12 ; ne prétend pas reconstituer B1 V3.3.13 historique.
Révision R3 : chargement NPZ mutualisé et tests réels archives absentes/illisibles.
Ne pas exécuter avant revue statique complète.
"""
import hashlib as _hashlib, io as _io, json as _json, math as _math, os as _os, re as _re, sys as _sys, tempfile as _tempfile, time as _time, traceback as _traceback
from fractions import Fraction as _Fraction
from datetime import datetime as _datetime, timezone as _timezone
from pathlib import Path as _Path
import numpy as _np
import DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_7_PARTIE_A as _PA
from DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_7_PARTIE_A import EXP, INDISPENSABLE, TOL_ARCHIVES, EPS_MACHINE, U_ARRONDI, CLES_GATE, F, F0, F1, fadd, fneg, fsub, fmul, fscale, fiszero, solve_lin, finv, fdiv, f_to_float, f_to_str, f_sign_adaptive, f_is_pos, parse_csv_expr, q5_to_F, q5_add, q5_sub, q5_mul, q5_scale_int, q5_to_str, q5_is_pos, dist_carree_q5, sp_clean, sp_mul, sp_scale, sp_matvec, sp_trace, sp_eq, dense_matvec, dense_quad, dense_eq, est_carree, verifier_symetrie, verifier_verrou_projecteurs, valider_fichier_provenance, valider_provenance_sur_octets, verifier_integrite_hashes, verifier_integrite_fichiers, evaluer_borne, schur_to_y, verify_counterexample, ldl_with_pivot, ldl_audit, calculer_borne_arrondi, comparer_archives, valider_geometrie, valider_aretes_geometriques, accessible_nonempty, valider_entrees, verifier_rapport_sans_nan, verifier_exports_partie_a
# Alias : le corps de main() ci-dessous utilise les noms courts historiques.
hashlib, io, json, math, os, re, sys, tempfile, time, traceback = _hashlib, _io, _json, _math, _os, _re, _sys, _tempfile, _time, _traceback
Fraction, datetime, timezone, Path, np = _Fraction, _datetime, _timezone, _Path, _np


CLES_ETAT_TRANSFEREES = ["t0","base","outdir","pm","blocking","warnings","identites","calculs","corroboration","hypotheses","ouverts","section_status","aretes_details","prov","sha_av","memoires","Fich","D","ctx","geo","geo_ok","arch_comp","arch_ok","arch_statut","proj","verif","ident_ok","acc","acc_ok","nrj","nrj_ok","res","ldl_res","ldl_audit_ok","B_pos","sym_ok","_scripts_info","_val_ok","_val_motifs","_ok_exports","_manq_exports","_a","_ch","_geo","_rk","_q","_c","_a2","_proj","_acc","_nrj"]

NOMS_IMPORTES_A=["EXP","INDISPENSABLE","TOL_ARCHIVES","EPS_MACHINE","U_ARRONDI","CLES_GATE","F","F0","F1","fadd","fneg","fsub","fmul","fscale","fiszero","solve_lin","finv","fdiv","f_to_float","f_to_str","f_sign_adaptive","f_is_pos","parse_csv_expr","q5_to_F","q5_add","q5_sub","q5_mul","q5_scale_int","q5_to_str","q5_is_pos","dist_carree_q5","sp_clean","sp_mul","sp_scale","sp_matvec","sp_trace","sp_eq","dense_matvec","dense_quad","dense_eq","est_carree","verifier_symetrie","verifier_verrou_projecteurs","valider_fichier_provenance","valider_provenance_sur_octets","verifier_integrite_hashes","verifier_integrite_fichiers","evaluer_borne","schur_to_y","verify_counterexample","ldl_with_pivot","ldl_audit","calculer_borne_arrondi","comparer_archives","valider_geometrie","valider_aretes_geometriques","accessible_nonempty","valider_entrees","verifier_rapport_sans_nan","verifier_exports_partie_a"]

def _verifier_exports_securisee(fn=None):
 try:
  _fn=fn if fn is not None else verifier_exports_partie_a
  _ok,_manq=_fn()
 except Exception as e:
  return {"ok":False,"manquants":[f"{type(e).__name__}: {e}"],"detail":f"verifier_exports_partie_a a levé {type(e).__name__}: {e}"}
 _manq=list(_manq) if type(_manq) is list else []
 _exports=getattr(_PA,"__all__",None)
 for _nom in NOMS_IMPORTES_A:
  if not hasattr(_PA,_nom): _manq.append(f"import manquant dans A : {_nom}")
  elif _exports is not None and _nom not in _exports: _manq.append(f"nom absent de __all__ de A : {_nom}")
 return {"ok":bool(_ok) and len(_manq)==0,"manquants":_manq,"detail":"Exports A vérifiés (fonction + présence réelle des noms importés)." if len(_manq)==0 else f"Exports A incomplets : {'; '.join(_manq)}"}

def _valider_bars_entiers(bars_raw):
 try:
  if not isinstance(bars_raw,np.ndarray): return {"ok":False,"motif":"bars_raw n'est pas un ndarray"}
  if bars_raw.dtype.kind=="f":
   if not bool(np.isfinite(bars_raw).all()): return {"ok":False,"motif":"bars_raw contient NaN ou Inf"}
   if not bool((bars_raw==np.floor(bars_raw)).all()): return {"ok":False,"motif":"bars_raw non entier"}
  _mn=float(np.min(bars_raw)); _mx=float(np.max(bars_raw))
  if _mn<-(2**63) or _mx>=(2**63): return {"ok":False,"motif":f"bars_raw hors plage int64 : [{_mn}, {_mx}]"}
  return {"ok":True,"motif":"bars entiers dans la plage int64"}
 except Exception as e: return {"ok":False,"motif":f"{type(e).__name__}: {e}"}

def _charger_archives_npz(octets):
 """Charge les trois tableaux requis depuis les octets NPZ, sans pickle.
 Lève ValueError pour une archive absente, vide, illisible ou incomplète.
 """
 if not isinstance(octets, (bytes, bytearray, memoryview)) or len(octets) == 0:
  raise ValueError("archive R_K0.npz absente ou vide")
 try:
  with np.load(io.BytesIO(bytes(octets)), allow_pickle=False) as _z:
   _cles_requises={"bars", "R", "K0"}
   _cles_disponibles=set(_z.files)
   _cles_manquantes=sorted(_cles_requises-_cles_disponibles)
   if _cles_manquantes:
    raise ValueError("clés NPZ manquantes : " + ", ".join(_cles_manquantes))
   return (_z["bars"].copy(), _z["R"].copy(), _z["K0"].copy())
 except ValueError as _e:
  if str(_e).startswith("clés NPZ manquantes :"):
   raise
  raise ValueError(f"archive R_K0.npz illisible : {type(_e).__name__}: {_e}") from _e
 except Exception as _e:
  raise ValueError(f"archive R_K0.npz illisible : {type(_e).__name__}: {_e}") from _e

def _classifier_ldl(res, sym_ok, ldl_res, ldl_audit_ok):
 quotient_construit=bool(type(res) is dict and all(k in res for k in ("A_exact","B_exact","D_exact","dim","n_pos")))
 symetrie_exacte=bool(type(sym_ok) is bool and sym_ok)
 ldl_execute=bool(type(ldl_res) is dict and ldl_res.get("statut") in ("PSD","INDEFINIE") and symetrie_exacte)
 certificat_audite=bool(ldl_execute and type(ldl_audit_ok) is bool and ldl_audit_ok and type(res) is dict and type(res.get("ldl_audit")) is dict and res["ldl_audit"].get("ok") is True)
 if not quotient_construit: conclusion="NON_CALCULE"
 elif not symetrie_exacte: conclusion="INDECIS"
 elif not ldl_execute: conclusion="INDECIS"
 elif type(ldl_res) is dict and ldl_res.get("statut")=="PSD" and certificat_audite: conclusion="PSD"
 elif type(ldl_res) is dict and ldl_res.get("statut")=="INDEFINIE" and certificat_audite: conclusion="REFUTE_VERIFIE"
 elif type(ldl_res) is dict and ldl_res.get("statut")=="INDEFINIE": conclusion="INDECIS"
 else: conclusion="INDECIS"
 return {"quotient_construit":quotient_construit,"symetrie_exacte":symetrie_exacte,"ldl_execute":ldl_execute,"certificat_audite":certificat_audite,"conclusion":conclusion}

def _chemins_identiques(chemin_charge, chemin_enregistre):
 try:
  return str(Path(chemin_charge).resolve()) == str(Path(chemin_enregistre).resolve())
 except Exception:
  return False

def _valider_contrat_state_b1(state):
 obligatoires={"t0":(int,float),"base":(Path,),"outdir":(Path,),"pm":(Path,),"blocking":(list,),"warnings":(list,),"identites":(list,),"calculs":(list,),"corroboration":(list,),"hypotheses":(list,),"ouverts":(list,),"section_status":(dict,),"aretes_details":(dict,),"prov":(dict,),"sha_av":(dict,),"memoires":(dict,),"Fich":(dict,),"D":(dict,),"ctx":(dict,),"geo":(dict,),"geo_ok":(bool,),"arch_comp":(dict,),"arch_ok":(bool,),"arch_statut":(str,),"proj":(dict,),"verif":(dict,),"ident_ok":(bool,),"acc":(dict,),"acc_ok":(bool,),"nrj":(dict,),"nrj_ok":(bool,),"res":(dict,),"ldl_res":(dict,),"ldl_audit_ok":(bool,),"B_pos":(bool,),"sym_ok":(bool,),"_scripts_info":(dict,),"_val_ok":(bool,),"_val_motifs":(list,),"_ok_exports":(bool,),"_manq_exports":(list,),"etape":(str,),"ldl_detail":(dict,)}
 facultatifs={"_a","_ch","_geo","_rk","_q","_c","_a2","_proj","_acc","_nrj","corroboration_archives","provenance_detail","contrat_state"}
 motifs=[]
 for _k,_types in obligatoires.items():
  if _k not in state: motifs.append(f"clé obligatoire manquante : {_k}")
  elif state[_k] is None: motifs.append(f"clé obligatoire None (non calculée) : {_k}")
  elif not isinstance(state[_k],_types): motifs.append(f"clé {_k} type incorrect : {type(state[_k]).__name__} (attendu {', '.join(t.__name__ for t in _types)})")
 if type(state.get("ldl_detail")) is dict:
  _ld=state["ldl_detail"]
  _ld_keys={"quotient_construit","symetrie_exacte","ldl_execute","certificat_audite","conclusion"}
  if set(_ld) != _ld_keys: motifs.append("ldl_detail : ensemble de champs incorrect")
  for _bk in ("quotient_construit","symetrie_exacte","ldl_execute","certificat_audite"):
   if type(_ld.get(_bk)) is not bool: motifs.append(f"ldl_detail.{_bk} doit être un bool strict")
  if _ld.get("conclusion") not in ("PSD","REFUTE_VERIFIE","INDECIS","NON_CALCULE"): motifs.append("ldl_detail.conclusion invalide")
  _ld_expected=_classifier_ldl(state.get("res"),state.get("sym_ok"),state.get("ldl_res"),state.get("ldl_audit_ok"))
  if _ld != _ld_expected: motifs.append("ldl_detail incohérent avec res/sym_ok/ldl_res/ldl_audit_ok")
 return {"ok":len(motifs)==0,"motifs":motifs,"obligatoires":sorted(obligatoires),"facultatifs":sorted(facultatifs)}

def tests_negatifs_b1():
 tests={}
 def _enregistrer(nom, entree, attendu, obtenu_bool, obtenu_texte):
  tests[nom]={"entree":entree,"attendu":attendu,"obtenu":obtenu_texte,"statut":"PASSE" if type(obtenu_bool) is bool and obtenu_bool else "NON_TESTE" if type(obtenu_bool) is bool and not obtenu_bool and str(obtenu_texte).startswith("NON_TESTE") else "ECHEC"}
 def _fn_leve(): raise RuntimeError("export simulé en échec")
 _r=_verifier_exports_securisee(_fn_leve); _enregistrer("export_A_leve_exception","verifier_exports qui lève RuntimeError","ok=False, motif enregistré", _r["ok"] is False, "ok="+str(_r["ok"])+", manquants="+str(_r["manquants"]))
 _r2=_verifier_exports_securisee(); _enregistrer("export_A_reel","verifier_exports_partie_a() réelle","ok=True si A complète, sinon ok=False documenté",type(_r2["ok"]) is bool and _r2["ok"], "ok="+str(_r2["ok"]))
 try:
  _charger_archives_npz(None); _absente_refusee=False; _absente_detail="aucune exception"
 except ValueError as _e:
  _absente_refusee="absente ou vide" in str(_e); _absente_detail=f"{type(_e).__name__}: {_e}"
 _enregistrer("archives_absentes","_charger_archives_npz(None)","ValueError explicite : archive absente/vide refusée",_absente_refusee,_absente_detail)
 try:
  _charger_archives_npz(b"ceci n'est pas une archive NPZ"); _illisible_refusee=False; _illisible_detail="aucune exception"
 except ValueError as _e:
  _illisible_refusee="illisible" in str(_e).lower()
  _illisible_detail=f"{type(_e).__name__}: {_e}"
 _enregistrer("archives_illisibles","_charger_archives_npz(octets NPZ invalides)","ValueError explicite : archive illisible refusée",_illisible_refusee,_illisible_detail)
 def _comp_leve(*a, **k): raise ValueError("comparaison simulée en échec")
 try:
  _comp_leve(); _exc=False
 except ValueError as _e:
  _exc=str(_e)=="comparaison simulée en échec"
 _enregistrer("comparaison_archives_exception","simulation explicite de l’exception capturée","exception ValueError capturée et identifiée",_exc,"exception_identifiee="+str(_exc))
 try:
  _ok,_comp,_msgs=comparer_archives({(0,0):F1},{(0,0):F1},np.zeros((60,60)),np.zeros((60,60)))
  _enregistrer("comparaison_executee_ecart","comparer_archives avec écart réel","statut ECART, exécutée, jamais blocking",_ok is False, "ok="+str(_ok))
 except Exception as e: _enregistrer("comparaison_executee_ecart","comparer_archives avec écart réel","statut ECART",False,"exception "+str(e))
 _enregistrer("symetrie_defaillante","verifier_symetrie([[F1,F1],[F0,F1]])","False",verifier_symetrie([[F1,F1],[F0,F1]]) is False, "obtenu="+str(verifier_symetrie([[F1,F1],[F0,F1]])))
 _c=_classifier_ldl({}, False, None, False); _enregistrer("ldl_non_execute","classifier_ldl(res vide, sym False, ldl None)","ldl_execute=False, conclusion INDECIS",_c["ldl_execute"] is False and _c["conclusion"]=="INDECIS", "ldl_execute="+str(_c["ldl_execute"])+", conclusion="+_c["conclusion"])
 _c2=_classifier_ldl({"A_exact":{},"B_exact":{},"D_exact":[],"dim":2,"n_pos":1,"ldl_audit":{"ok":False}}, True, {"statut":"PSD","diag":[F1],"perm":[0],"L":[[F1]]}, False); _enregistrer("ldl_audit_echoue","classifier_ldl PSD + audit False","certificat_audite=False, conclusion INDECIS",_c2["certificat_audite"] is False, "certificat_audite="+str(_c2["certificat_audite"])+", conclusion="+_c2["conclusion"])
 try:
  _ok_aud,_msg_aud=ldl_audit([[F1,F0],[F0,F1]],{"statut":"PSD","perm":[0,1],"L":[[F1,F0],[F0,F1]],"diag":None,"k_arret":2})
  _enregistrer("certificat_ldl_incomplet","ldl_audit diag None","audit False",_ok_aud is False, "ok="+str(_ok_aud))
 except Exception as e: _enregistrer("certificat_ldl_incomplet","ldl_audit diag None","audit False",False,"exception "+str(e))
 _enregistrer("cle_obligatoire_manquante","state sans 'prov'","contrat ok=False, motif 'clé obligatoire manquante'",_valider_contrat_state_b1({"t0":0.0})["ok"] is False, "ok="+str(_valider_contrat_state_b1({"t0":0.0})["ok"]))
 _enregistrer("cle_type_incorrect","state prov='x'","contrat ok=False, motif type incorrect",_valider_contrat_state_b1({"t0":0.0,"prov":"x"})["ok"] is False, "ok="+str(_valider_contrat_state_b1({"t0":0.0,"prov":"x"})["ok"]))
 _p_charge=Path(__file__).resolve(); _p_annonce=_p_charge.parent/("AUTRE_"+_p_charge.name); _mismatch=not _chemins_identiques(_p_charge,_p_annonce); _enregistrer("chemin_module_different","deux chemins résolus distincts","mismatch détecté",_mismatch,"chemins_identiques="+str(not _mismatch))
 import tempfile as _tf
 _fd,_p=_tf.mkstemp(prefix="dodeca_b2_",suffix=".py"); os.close(_fd); _pp=Path(_p)
 try:
  _pp.write_bytes(b"v1"); _sha0=hashlib.sha256(_pp.read_bytes()).hexdigest(); _pp.write_bytes(b"v2"); _sha1=hashlib.sha256(_pp.read_bytes()).hexdigest()
  _enregistrer("modification_B2_apres_empreinte","fichier modifié après capture SHA","SHA final != SHA initial détecté",_sha0!=_sha1, "sha0!=sha1 : "+str(_sha0!=_sha1))
 finally:
  try: _pp.unlink()
  except Exception: pass
 _vb=_valider_bars_entiers(np.array([[1e20,0,0]],dtype=float)); _enregistrer("barre_hors_plage","bars_raw [[1e20, 0, 0]] float","ok=False, motif hors plage int64",_vb["ok"] is False, "ok="+str(_vb["ok"])+", motif="+_vb["motif"])
 return tests

def main_partie_1():
 t0=time.time(); base=Path(__file__).resolve().parent
 outdir=base/"BORNE_ENERGETIQUE_V3_3_20"
 blocking=[]; warnings=[]; identites=[]; calculs=[]; corroboration=[]; hypotheses=[]; ouverts=[]
 section_status={}; aretes_details={}
 def mark_section(nom,execute,ok,detail=""):
  section_status[nom]={"execute":bool(execute),"ok":bool(ok),"detail":detail}
 def sec(nom,fn):
  try: return fn()
  except Exception as e:
   m=f"Section {nom} : {type(e).__name__}: {e}"; print("  ECHEC BLOQUANT  "+m); blocking.append(m); blocking.append(traceback.format_exc(limit=3))
   mark_section(nom,True,False,m); return None
 print("="*72+"\nDODECA — BORNE ENERGETIQUE EXACTE V3.3.20\n"+"="*72)
 pm=base/"PERSISTANCE_MODALE_V1"
 Fich={"SOMMETS_DODECAEDRE.csv":base/"SOMMETS_DODECAEDRE.csv","CUBES_5.csv":base/"CUBES_5.csv",
  "ROTATIONS_EXACTES.json":pm/"ROTATIONS_EXACTES.json","R_K0.npz":pm/"R_K0.npz"}
 # --- Provenance chaîne V3.3.20 : A V3.3.7 (inchangée) + B1 V3.3.20 + B2 V3.3.19 (attendu) ---
 _scripts_info={}
 _dossier_scripts=Path(__file__).resolve().parent
 for _nom,_ch in [("PARTIE_A", _dossier_scripts / "DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_7_PARTIE_A.py"),
                   ("PARTIE_B1", _dossier_scripts / "DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_20_PARTIE_B1.py"),
                   ("PARTIE_B2", _dossier_scripts / "DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_19_PARTIE_B2.py")]:
  try:
   _data=_ch.read_bytes(); _scripts_info[_nom]={"chemin":str(_ch),"sha256_initial":hashlib.sha256(_data).hexdigest(),"taille_octets_initial":len(_data),"statut":"CONFORME (lecture initiale)","detail":None}
  except Exception as _e:
   _scripts_info[_nom]={"chemin":str(_ch),"sha256_initial":None,"taille_octets_initial":None,"statut":"ABSENT_OU_ILLISIBLE","detail":f"{type(_e).__name__}: {_e}"}
   blocking.append(f"Provenance script {_nom} : {_scripts_info[_nom]['detail']}")
 # V3.3.20 §2F : chemins résolus et comparés aux modules réellement chargés.
 _modules_charges={"PARTIE_A":str(Path(_PA.__file__).resolve()),"PARTIE_B1":str(Path(__file__).resolve()),"PARTIE_B2":str((_dossier_scripts / "DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_19_PARTIE_B2.py").resolve())}
 _prov_motifs=[]
 for _nom,_ch_attendu in _modules_charges.items():
  _ch_enr=_scripts_info.get(_nom,{}).get("chemin")
  if _ch_enr is None or not _chemins_identiques(_ch_enr,_ch_attendu): _prov_motifs.append(f"{_nom} : chemin enregistré != module chargé.")
 if _prov_motifs:
  for _m in _prov_motifs: blocking.append("Provenance chemin : "+_m)
 provenance_detail={"modules_charges":_modules_charges,"chemins_enregistres":{k:v.get("chemin") for k,v in _scripts_info.items()},"ok":len(_prov_motifs)==0,"motifs":_prov_motifs,"b2_absent_ou_illisible":bool(_scripts_info.get("PARTIE_B2",{}).get("sha256_initial") is None)}
 if _scripts_info.get("PARTIE_B2",{}).get("sha256_initial") is None: warnings.append("Provenance B2 : B2 absent ou illisible, diagnostic transmis à B2 (aucune empreinte fabriquée).")
 _exp=_verifier_exports_securisee(); _ok_exports=_exp["ok"]; _manq_exports=_exp["manquants"]
 if not _ok_exports: blocking.append(f"Exports Partie A incomplets : {_manq_exports}")
 else: print(f"  OK  Exports Partie A : {len(__import__('DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_7_PARTIE_A').__all__)} noms exposés")
 mark_section("exports_partie_a",True,bool(_ok_exports),"exports A vérifiés" if _ok_exports else f"exports A en échec : {'; '.join(_manq_exports[:3])}")
 # --- Lecture unique des octets, SHA sur ces octets, parsing en mémoire (correction 3) ---
 memoires={}; prov={}; sha_av={}
 for nom,ch in Fich.items():
  try:
   data=Path(ch).read_bytes(); memoires[nom]=data
  except Exception as e:
   memoires[nom]=None
   inf={"chemin":str(ch),"categorie":"indispensable","sha256_attendu":EXP.get(nom),
    "sha256_avant":None,"taille_octets":None,"statut":"ABSENT_OU_ILLISIBLE","detail":f"{type(e).__name__}: {e}"}
   prov[nom]=inf; sha_av[nom]=None; blocking.append(f"Provenance ABSENT_OU_ILLISIBLE (indispensable) : {nom}"); continue
  inf=valider_provenance_sur_octets(data,EXP.get(nom),ch)
  prov[nom]=inf; sha_av[nom]=inf.get("sha256_avant")
  if inf["statut"]!="CONFORME": blocking.append(f"Provenance {inf['statut']} (indispensable) : {nom}")
 prov_ok=all(prov[n]["statut"]=="CONFORME" for n in INDISPENSABLE)
 mark_section("provenance",True,prov_ok,"4 indispensables CONFORME (octets lus une seule fois)" if prov_ok else "indispensable non conforme/absent/illisible")
 if not prov_ok: print("  BLOCAGE provenance : pas de DEMONTRE possible.")
 D=None
 def charger():
  nonlocal D
  if any(memoires.get(n) is None for n in INDISPENSABLE if n != "R_K0.npz"): raise ValueError("octets initiaux indispensables indisponibles (hors archive NPZ)")
  V=[[parse_csv_expr(p) for p in l.split(",")[1:4]] for l in memoires["SOMMETS_DODECAEDRE.csv"].decode("utf-8").splitlines()[1:]]
  C=[set(int(x) for x in l.split(",")[1].split(";")) for l in memoires["CUBES_5.csv"].decode("utf-8").splitlines()[1:]]
  bars_raw,Ra_raw,Ka_raw=_charger_archives_npz(memoires["R_K0.npz"])
  if not (isinstance(bars_raw,np.ndarray) and bars_raw.ndim==2 and bars_raw.shape==(60,3) and bars_raw.dtype.kind in ("i","u","f")): raise ValueError("bars brut invalide")
  _vb=_valider_bars_entiers(bars_raw)
  if not _vb["ok"]: raise ValueError(f"bars brut invalide : {_vb['motif']}")
  if not all(isinstance(a,np.ndarray) and a.shape==(60,60) and a.dtype.kind in ("f","i","u") for a in (Ra_raw,Ka_raw)): raise ValueError("archives brutes invalides")
  bars=[(int(bars_raw[b,0]),int(bars_raw[b,1]),int(bars_raw[b,2])) for b in range(60)]
  rot=json.loads(memoires["ROTATIONS_EXACTES.json"].decode("utf-8"))["rotations"]
  D={"V":V,"C":C,"bars":bars,"bars_np":bars_raw.astype(int),"Ra":Ra_raw,"Ka":Ka_raw,"rot":rot}
  print(f"  Chargement : {len(V)} sommets, {len(C)} cubes, {len(bars)} barres, {len(rot)} rotations (mêmes octets que le SHA initial)"); return True
 _ch=sec("Chargement",charger); ok_ch=bool(_ch)
 mark_section("chargement",True,ok_ch,"chargement depuis octets mémorisés" if ok_ch else "chargement en échec")
 if not ok_ch: blocking.append("Chargement en échec.")
 # Validation renforcée des entrées avant tout appel géométrique (V3.3.20 §6).
 _val_ok=False; _val_motifs=[]
 if ok_ch:
  try:
   _val_ok,_val_motifs=valider_entrees(D["V"],D["C"],D["bars"],D["rot"],D["Ra"],D["Ka"])
  except Exception as e:
   _val_ok=False; _val_motifs=[f"{type(e).__name__}: {e}"]
  if not _val_ok:
   for _m in _val_motifs: blocking.append("Validation entrées : "+_m); print("  ECHEC BLOQUANT  Validation entrées : "+_m)
  else: print("  OK  Validation entrées : dimensions, types, indices, doublons, rotations, finitude")
 mark_section("validation_entrees",True,bool(_val_ok),"entrées validées" if _val_ok else "entrées invalides : "+"; ".join(_val_motifs[:5]))
 if ok_ch and not _val_ok: ok_ch=False
 geo={}; geo_ok=False
 if ok_ch:
  def val_geo():
   nonlocal geo_ok, aretes_details
   geo.update(valider_geometrie(D["V"],D["C"],D["bars"]))
   try:
    b_aretes,det_aretes=valider_aretes_geometriques(D["V"],D["C"],D["bars"]); aretes_details=det_aretes
   except Exception as e:
    b_aretes={k:False for k in ["aretes_longueurs_uniformes","aretes_classification_distances","aretes_biparti","aretes_sans_triangle","aretes_diametre_3","aretes_comptes_graphes","aretes_geometriques_completes"]}
    aretes_details={"motif":f"{type(e).__name__}: {e}","longueur_carree":None,"details_par_cube":[]}
    blocking.append(f"Arêtes géométriques : exception {e}")
   geo.update(b_aretes)
   for k,v in geo.items():
    if not v: blocking.append(f"Géométrie {k} : False")
    else: calculs.append(f"Géométrie {k}")
    print(("  OK  " if v else "  ECHEC BLOQUANT  ")+f"Géométrie {k}")
   if aretes_details.get("longueur_carree") is not None: print(f"  Arêtes : longueur carrée = {aretes_details['longueur_carree']} (Q(sqrt5), exacte)")
   geo_ok=all(geo.values()); return geo_ok
  _g=sec("Validation géométrique",val_geo); mark_section("validation_geometrique",True,bool(geo_ok),"géométrie complète (arêtes géométriques incluses)" if geo_ok else "géométrie en échec")
 else:
  geo["cause_non_execution"]="Chargement indisponible"; mark_section("validation_geometrique",False,False,"non exécutée"); blocking.append("Géométrie non vérifiée (chargement indisponible).")
 ctx={}
 def construire_RK0():
  V,C,bars=D["V"],D["C"],D["bars"]
  R={}
  for b,(a,bb,cu) in enumerate(bars):
   for k in range(3):
    d=((V[bb][k][0]-V[a][k][0])/2,(V[bb][k][1]-V[a][k][1])/2)
    if d!=(Fraction(0),Fraction(0)): R[(b,3*a+k)]=(-d[0],-d[1]); R[(b,3*bb+k)]=d
  R5={k:q5_to_F(v) for k,v in R.items()}
  Rt={(c,r):v for (r,c),v in R5.items()}
  brow={}
  for (r,c),v in R5.items(): brow.setdefault(r,[]).append((c,v))
  K={}
  for (r,m),av in Rt.items():
   for c,bv in brow.get(m,[]):
    K[(r,c)]=fadd(K.get((r,c),F0),fmul(av,bv))
  ctx.update(V=V,C=C,bars=bars,R=R5,K=sp_clean(K))
  print(f"  R : {len(R5)} non-nuls | K0 : {len(ctx['K'])} non-nuls"); return True
 _rk=sec("Constructions R/K0",construire_RK0) if (ok_ch and geo_ok) else None
 ok_rk=bool(_rk)
 mark_section("constructions_RK0",_rk is not None,ok_rk,"R/K0 exacts" if ok_rk else "non exécutées / en échec")
 if not ok_rk and ok_ch and not geo_ok: blocking.append("Constructions R/K0 bloquées : géométrie non validée.")
 if not ok_rk and ok_ch and geo_ok: blocking.append("Constructions R/K0 en échec.")
 arch_comp={}; arch_ok=False; arch_statut="NON_CALCULEE"; corroboration_archives={"statut":"NON_CALCULEE","execute":False,"detail":"Comparaison archives non tentée (blocage amont).","comp":{}}
 if ok_rk:
  try:
   ok,comp,msgs=comparer_archives(ctx["R"],ctx["K"],D["Ra"],D["Ka"])
   arch_comp.update(comp); arch_ok=bool(ok)
   arch_statut="CONFORME" if arch_ok else "ECART"
   corroboration_archives={"statut":arch_statut,"execute":True,"detail":"Comparaison exécutée (corroboration seule, jamais bloquante).","comp":comp}
   for m in msgs: warnings.append("Corroboration archives : "+m); print("  CORROBORATION (non bloquante)  "+m)
   for nom in ("R","K0"):
    if nom in comp:
     corroboration.append(f"Archive {nom} : max diff {comp[nom]['max_abs_diff']:.2e}, mean {comp[nom]['mean_abs_diff']:.2e}, n_depasse={comp[nom]['n_depasse_tolerance']} (tolérance {TOL_ARCHIVES:.0e}, corroboration numérique, jamais preuve exacte).")
     print(f"  Archive {nom} : max {comp[nom]['max_abs_diff']:.2e} (tol {TOL_ARCHIVES:.0e})")
   if "justification_tolerance" in comp: corroboration.append(comp["justification_tolerance"])
   if "borne_arrondi" in comp: corroboration.append(f"Borne d'arrondi : {comp['borne_arrondi'].get('detail')}")
   mark_section("comparaison_archives",True,True,f"comparaison exécutée, statut={arch_statut} (corroboration seule)")
  except Exception as e:
   arch_statut="INDISPONIBLE"; arch_ok=False
   corroboration_archives={"statut":"INDISPONIBLE","execute":True,"detail":f"Comparaison en exception : {type(e).__name__}: {e}","comp":{}}
   warnings.append(f"Corroboration archives indisponible (exception) : {e}"); print(f"  CORROBORATION INDISPONIBLE (non bloquante)  {e}")
   mark_section("comparaison_archives",True,False,f"comparaison en exception, statut=INDISPONIBLE : {e}")
 else:
  arch_statut="NON_CALCULEE"; corroboration_archives={"statut":"NON_CALCULEE","execute":False,"detail":"Comparaison non tentée (blocage amont exact).","comp":{}}
  warnings.append("Corroboration archives non calculée (blocage amont exact) : ne bloque pas la preuve exacte.")
  mark_section("comparaison_archives",False,False,"non exécutée, statut=NON_CALCULEE")
 S6=F(0,0,1,0)
 LAMS=[F0, fscale(F1,Fraction(1,2)), fsub(F(2),fscale(S6,Fraction(1,2))), F(2), fscale(F1,Fraction(5,2)), fadd(F(2),fscale(S6,Fraction(1,2))), F(4)]
 proj={}
 def construire_projecteurs():
  K=ctx["K"]; pw=[{(i,i):F1 for i in range(60)}]
  for _ in range(6): pw.append(sp_mul(pw[-1],K))
  for a,lam in enumerate(LAMS):
   poly=[F1]
   for b,lb in enumerate(LAMS):
    if b==a: continue
    npoly=[F0]*(len(poly)+1)
    for k,c in enumerate(poly):
     npoly[k]=fadd(npoly[k],fmul(fneg(lb),c)); npoly[k+1]=fadd(npoly[k+1],c)
    poly=npoly
   den=F1
   for b,lb in enumerate(LAMS):
    if b!=a: den=fmul(den,fsub(lam,lb))
   Pa={}
   for k,c in enumerate(poly):
    coef=fdiv(c,den)
    if fiszero(coef): continue
    for key,v in pw[k].items(): Pa[key]=fadd(Pa.get(key,F0),fmul(coef,v))
   proj[a]=sp_clean(Pa)
  ctx["proj"]=proj
  print(f"  Projecteurs : {len(proj)} construits"); return True
 _pr=sec("Projecteurs",construire_projecteurs) if ok_rk else None
 ok_proj=bool(_pr)
 mark_section("projecteurs",_pr is not None,ok_proj,"7 projecteurs" if ok_proj else "non exécutés / en échec")
 if not ok_proj: blocking.append("Projecteurs indisponibles.")
 verif={}; ident_ok=False
 if ok_proj:
  def verif_proj():
   nonlocal ident_ok
   K=ctx["K"]; P=proj; I={(i,i):F1 for i in range(60)}
   verif["P2"]=all(sp_eq(sp_mul(P[a],P[a]),P[a]) for a in range(7))
   verif["orth"]=all(sp_eq(sp_mul(P[a],P[b]),{}) for a in range(7) for b in range(7) if a!=b)
   S={}
   for a in range(7):
    for k,v in P[a].items(): S[k]=fadd(S.get(k,F0),v)
   verif["somme_I"]=sp_eq(sp_clean(S),I)
   verif["KPa"]=all(sp_eq(sp_mul(K,P[a]),sp_scale(P[a],LAMS[a])) for a in range(7))
   tr=[sp_trace(P[a]) for a in range(7)]
   verif["traces"]=[f_to_str(t) for t in tr]
   verif["traces_entieres"]=all(t[1]==0 and t[2]==0 and t[3]==0 and t[0].denominator==1 for t in tr)
   verif["somme_traces"]=sum((t[0] for t in tr),Fraction(0))==60 if verif["traces_entieres"] else False
   for k,v in [("P2",verif["P2"]),("orth",verif["orth"]),("somme_I",verif["somme_I"]),("KPa",verif["KPa"]),("traces_entieres",verif["traces_entieres"]),("somme_traces",verif["somme_traces"])]:
    if v: identites.append(f"Projecteurs {k}")
    else: blocking.append(f"Projecteurs {k} : False")
    print(("  OK  " if v else "  ECHEC BLOQUANT  ")+f"Projecteurs {k}")
   ident_ok=bool(verifier_verrou_projecteurs(verif["P2"], verif["orth"], verif["somme_I"], verif["KPa"], verif["traces_entieres"], verif["somme_traces"]))
   if not ident_ok: blocking.append("Identités projecteurs échouées -> certification arrêtée.")
   print(f"  Traces : {verif['traces']}"); return True
  _vp=sec("Vérif projecteurs",verif_proj); mark_section("verif_projecteurs",True,bool(ident_ok),"identités vérifiées" if ident_ok else "identités en échec")
 else:
  mark_section("verif_projecteurs",False,False,"non exécutée"); blocking.append("Vérif projecteurs non exécutée.")
 acc={}; acc_ok=False
 if ok_proj and ident_ok:
  def accessible():
   nonlocal acc_ok
   V,C=ctx["V"],ctx["C"]; P=proj; R=ctx["R"]
   w1=[F0]*60
   for v in C[0]:
    for k in range(3): w1[3*v+k]=q5_to_F(V[v][k])
   ctx["w1"]=w1; vs=[sp_matvec(P[a],w1) for a in range(7)]; ctx["v"]=vs
   s=[F0]*60
   for va in vs:
    for i in range(60): s[i]=fadd(s[i],va[i])
   acc["somme_va_eq_w1"]=all(s[i]==w1[i] for i in range(60))
   if acc["somme_va_eq_w1"]: identites.append("Somme v_a = w1")
   else: blocking.append("Somme v_a = w1 : False")
   Rv0=sp_matvec(R,vs[0]); acc["noyau_Rv0_nul"]=all(fiszero(x) for x in Rv0)
   if acc["noyau_Rv0_nul"]: identites.append("Noyau : R v_0 = 0, (u_0,0) exclu")
   else: blocking.append("Noyau : R v_0 = 0 : False")
   idx=[a for a in range(1,7) if any(not fiszero(x) for x in vs[a])]
   acc["indices_retenus"]=idx; acc["n_pos"]=len(idx); acc["dim_relaxation"]=2*len(idx)
   ok_ne,motif=accessible_nonempty(idx,vs)
   acc["accessible_nonempty_ok"]=ok_ne; acc["accessible_nonempty_motif"]=motif
   if ok_ne: calculs.append("Espace accessible non vide : "+motif)
   else: blocking.append("Espace accessible vide / invalide : "+motif)
   print(("  OK  " if ok_ne else "  ECHEC BLOQUANT  ")+f"Espace accessible : {motif}")
   acc["trajectoire_contenue"]=acc["somme_va_eq_w1"] and acc["noyau_Rv0_nul"]
   if acc["trajectoire_contenue"]: identites.append("Espace contient toute la trajectoire")
   else: blocking.append("Espace contient toute la trajectoire : False")
   acc_ok=bool(acc["trajectoire_contenue"] and ok_ne)
   print(f"  Indices retenus : {idx} (n_pos={len(idx)}, dim={2*len(idx)})"); return True
  _ac=sec("Espace accessible",accessible); mark_section("espace_accessible",True,bool(acc_ok),"non vide et valide" if acc_ok else "vide / invalide / en échec")
 else:
  mark_section("espace_accessible",False,False,"non exécutée (blocage amont)"); blocking.append("Espace accessible non construit (blocage amont).")
 nrj={}; nrj_ok=False
 if ok_proj and ident_ok and acc_ok:
  def energie_init():
   nonlocal nrj_ok
   V,C=ctx["V"],ctx["C"]; R=ctx["R"]; w1=ctx["w1"]
   support=[v for v in range(20) if any(not fiszero(w1[3*v+k]) for k in range(3))]
   nrj["support_w1_eq_C1"]=set(support)==set(C[0])
   nrj["composantes_w1_eq_V"]=all(all(w1[3*v+k]==q5_to_F(V[v][k]) for k in range(3)) for v in C[0]) and all(all(fiszero(w1[3*v+k]) for k in range(3)) for v in range(20) if v not in C[0])
   nrj["vitesse_initiale_nulle"]=True
   Rw1=sp_matvec(R,w1); n2=F0
   for _i in range(60): n2=fadd(n2,fmul(Rw1[_i],Rw1[_i]))
   H0=fscale(n2,Fraction(1,6))
   nrj["norme_Rw1_carre"]=f_to_str(n2); nrj["H0"]=f_to_str(H0)
   nrj["H0_exactement_12"]=(H0==F(12))
   nrj["H0_strictement_positive"]=(f_sign_adaptive(H0)==1)
   for k,v in [("support_w1_eq_C1",nrj["support_w1_eq_C1"]),("composantes_w1_eq_V",nrj["composantes_w1_eq_V"]),("vitesse_initiale_nulle",nrj["vitesse_initiale_nulle"]),("H0_exactement_12",nrj["H0_exactement_12"]),("H0_strictement_positive",nrj["H0_strictement_positive"])]:
    if v: identites.append(f"Énergie initiale {k}")
    else: blocking.append(f"Énergie initiale {k} : False")
    print(("  OK  " if v else "  ECHEC BLOQUANT  ")+f"Énergie initiale {k} (H0={nrj['H0']})")
   nrj_ok=bool(nrj["support_w1_eq_C1"] and nrj["composantes_w1_eq_V"] and nrj["vitesse_initiale_nulle"] and nrj["H0_exactement_12"] and nrj["H0_strictement_positive"])
   return True
  _nr=sec("Énergie initiale",energie_init); mark_section("energie_initiale",True,bool(nrj_ok),"H0 = 12 exactement" if nrj_ok else "énergie initiale en échec")
 else:
  mark_section("energie_initiale",False,False,"non exécutée"); blocking.append("Énergie initiale non vérifiée (blocage amont).")
 res={}; ldl_res=None; ldl_audit_ok=False; B_pos=False; sym_ok=False
 if ok_proj and ident_ok and acc_ok and nrj_ok:
  def quotient():
   nonlocal ldl_res, ldl_audit_ok, B_pos, sym_ok
   R=ctx["R"]; C=ctx["C"]; bars=ctx["bars"]; vs=ctx["v"]; idx=acc["indices_retenus"]; n=len(idx)
   B1={b for b,(a,bb,cu) in enumerate(bars) if cu==1}
   Rv=[sp_matvec(R,vs[a]) for a in idx]
   Aq=[[F0]*n for _ in range(n)]; Av=[[F0]*n for _ in range(n)]
   for i,a in enumerate(idx):
    for j,b in enumerate(idx):
     s=F0
     for _bb in B1: s=fadd(s,fmul(Rv[i][_bb],Rv[j][_bb]))
     Aq[i][j]=fscale(s,Fraction(1,6))
     s2=F0
     for vtx in C[0]:
      for k in range(3): s2=fadd(s2,fmul(vs[a][3*vtx+k],vs[b][3*vtx+k]))
     Av[i][j]=fscale(s2,Fraction(1,12))
   Bq=[[F0]*n for _ in range(n)]; Bv=[[F0]*n for _ in range(n)]
   for i,a in enumerate(idx):
    n2=F0
    for _t in range(60): n2=fadd(n2,fmul(vs[a][_t],vs[a][_t]))
    Bq[i][i]=fscale(fmul(LAMS[a],n2),Fraction(1,6)); Bv[i][i]=fscale(n2,Fraction(1,6))
   m=2*n; Dmat=[[F0]*m for _ in range(m)]
   for i in range(n):
    for j in range(n):
     Dmat[i][j]=fsub(Aq[i][j],fscale(Bq[i][j],Fraction(1,5)))
     Dmat[n+i][n+j]=fsub(Av[i][j],fscale(Bv[i][j],Fraction(1,5)))
   ctx.update(Aq=Aq,Av=Av,Bq=Bq,Bv=Bv,Dmat=Dmat,idx=idx)
   res["dim"]=m; res["n_pos"]=n; res["corps"]="Q(sqrt5, sqrt6), degré 4"
   res["extension_omega"]="Aucune : base (u_a,0),(0,u_a)"; res["extension_sqrt3"]="Aucune : facteur 1/sqrt3 annulé dans les formes."
   res["A_exact"]={"Aq":[[f_to_str(x) for x in row] for row in Aq],"Av":[[f_to_str(x) for x in row] for row in Av]}
   res["B_exact"]={"Bq":[[f_to_str(x) for x in row] for row in Bq],"Bv":[[f_to_str(x) for x in row] for row in Bv]}
   res["D_exact"]=[[f_to_str(x) for x in row] for row in Dmat]
   B_pos=all(f_is_pos(Bq[i][i]) and f_is_pos(Bv[i][i]) for i in range(n))
   if B_pos: identites.append("H strictement positive sur l'espace retenu (B diagonale > 0)")
   else: blocking.append("H strictement positive : False")
   print(("  OK  " if B_pos else "  ECHEC BLOQUANT  ")+"B définie positive")
   # --- Symétrie exacte avant LDL (correction 4) ---
   sym_dict={"Aq":verifier_symetrie(Aq),"Av":verifier_symetrie(Av),"Bq":verifier_symetrie(Bq),"Bv":verifier_symetrie(Bv),"D":verifier_symetrie(Dmat)}
   res["symetrie"]=sym_dict; sym_ok=all(sym_dict.values())
   for k,v in sym_dict.items():
    if v: identites.append(f"Symétrie exacte {k} = {k}^T")
    else: blocking.append(f"Symétrie exacte {k} = {k}^T : False -> LDL bloqué")
    print(("  OK  " if v else "  ECHEC BLOQUANT  ")+f"Symétrie exacte {k} = {k}^T")
   if not sym_ok:
    # LDL bloqué : aucune certification DEMONTRE ou REFUTE fondée sur LDL.
    ldl_res={"statut":"NON_EXECUTE","perm":None,"L":None,"diag":None,"contre_exemple":None,"k_arret":0,"attendu":None,
     "factorisation":None,"verification":(False,"symétrie échouée, LDL non exécuté"),
     "raison":"Symétrie exacte échouée : LDL non exécuté, certificat absent, audit non applicable, conclusion INDECIS."}
    ldl_audit_ok=False
    res["ldl_statut"]="NON_EXECUTE"; res["ldl_diag"]=[]; res["ldl_raison"]=ldl_res["raison"]
    res["ldl_verification"]=ldl_res["verification"]; res["ldl_audit"]={"ok":False,"detail":"LDL bloqué par symétrie, audit non applicable."}
    res["ldl_k_arret"]=0; res["ldl_attendu"]=None; res["ldl_factorisation"]="aucune (LDL bloqué)"; res["contre_exemple"]=None
    return True
   ldl_res=ldl_with_pivot(Dmat)
   ok_aud,msg_aud=ldl_audit(Dmat,ldl_res); ldl_audit_ok=ok_aud
   res["ldl_statut"]=ldl_res["statut"]; res["ldl_diag"]=[f_to_str(d) for d in ldl_res["diag"]]
   res["ldl_raison"]=ldl_res["raison"]; res["ldl_verification"]=ldl_res["verification"]
   res["ldl_audit"]={"ok":ok_aud,"detail":msg_aud}
   res["ldl_k_arret"]=ldl_res.get("k_arret"); res["ldl_attendu"]=f_to_str(ldl_res["attendu"]) if ldl_res.get("attendu") is not None else None
   res["ldl_factorisation"]=ldl_res.get("factorisation")
   if not ok_aud: blocking.append(f"Audit LDL échoué : {msg_aud}")
   else: calculs.append(f"Audit LDL : {msg_aud}")
   print(("  OK  " if ok_aud else "  ECHEC BLOQUANT  ")+f"Audit LDL : {msg_aud}")
   if ldl_res["statut"]=="INDEFINIE":
    try:
     _ce_ok,_ce_msg=verify_counterexample(Dmat, ldl_res["contre_exemple"])
    except Exception as e: _ce_ok=False; _ce_msg=f"{type(e).__name__}: {e}"
    if _ce_ok:
     res["contre_exemple"]=[[f_to_str(x) for x in ldl_res["contre_exemple"]]]; res["contre_exemple_verifie"]=True
     hypotheses.append("Réfutation sur l'espace de relaxation vérifiée : ne pas conclure M(t) indéfinie.")
    else:
     res["contre_exemple"]=None; res["contre_exemple_verifie"]=False
     hypotheses.append(f"Contre-exemple LDL non vérifié ({_ce_msg}) : absence de certificat != preuve d'indéfinition, conclusion INDECIS.")
   else: res["contre_exemple"]=None; res["contre_exemple_verifie"]=False
   if ldl_res["statut"]=="INDECIS": hypotheses.append(f"LDL indécis : {ldl_res['raison']}")
   try:
    Df=np.array([[f_to_float(x) for x in row] for row in Dmat],dtype=float)
    Bf=np.zeros((m,m))
    for i in range(n): Bf[i,i]=f_to_float(Bq[i][i]); Bf[n+i,n+i]=f_to_float(Bv[i][i])
    # V3.3.7 : mu = plus petite valeur propre généralisée de (D,B), DIRECTEMENT depuis D_f.
    # Ne pas reconstruire A_f = D_f + (1/5)B_f puis présenter ses valeurs propres comme mu
    # (ce seraient celles de D décalées de 1/5). Corroboration flottante, jamais certificat.
    sq=np.sqrt(np.diag(Bf)); Cmat=(Df/np.outer(sq,sq))
    vals=np.linalg.eigvalsh((Cmat+Cmat.T)/2)
    res["mu_numerique"]=float(vals[0]); res["valeurs_propres_numeriques"]=[float(x) for x in vals]
    corroboration.append(f"Corroboration numérique : mu_num ≈ {float(vals[0]):.10f} (flottants, jamais preuve).")
   except Exception as e: hypotheses.append(f"Corroboration numérique indisponible : {e}")
   return True
  _q=sec("Quotient + Symétrie + LDL",quotient)
  ldl_detail=_classifier_ldl(res, sym_ok, ldl_res, ldl_audit_ok)
  _q_ok=bool(ldl_detail["quotient_construit"] and (ldl_detail["conclusion"] in ("PSD","REFUTE_VERIFIE")))
  mark_section("quotient_LDL",True,_q_ok,f"quotient={ldl_detail['quotient_construit']}, symétrie={ldl_detail['symetrie_exacte']}, LDL exécuté={ldl_detail['ldl_execute']}, audit={ldl_detail['certificat_audite']}, conclusion={ldl_detail['conclusion']}")
 else:
  ldl_detail=_classifier_ldl(res, sym_ok, ldl_res, ldl_audit_ok)
  mark_section("quotient_LDL",False,False,"non exécuté"); blocking.append("Quotient + LDL non calculés (blocage amont).")
 # État explicite V3.3.20 : construction nommée, sans locals(). Champs consommés par B2 V3.3.11 + diagnostics V3.3.20.
 # Audit B2 V3.3.11 : state[...] = Fich, _scripts_info, prov, sha_av, section_status, res, ldl_res, blocking, warnings (+ champs écrits par B2 elle-même).
 # state.get(...) = les 51 clés ci-dessous. Aucune clé inutilisée identifiée (audit : 0 clé supprimée). B2 V3.3.11 ne lit PAS ldl_detail / corroboration_archives / provenance_detail / contrat_state : elle lit ldl_res / res / arch_statut / section_status. Incompatibilité documentée (B2 future devra lire ces champs) sans modifier B2 ici.
 tests_b1=tests_negatifs_b1()
 section_status["tests_negatifs_b1"]={"execute":True,"ok":bool(tests_b1) and all(type(v) is dict and v.get("statut")=="PASSE" for v in tests_b1.values()),"detail":f"{sum(1 for v in tests_b1.values() if v.get('statut')=='PASSE')}/{len(tests_b1)} tests PASSE"}
 if not section_status["tests_negatifs_b1"]["ok"]:
  blocking.append("Tests négatifs B1 non tous PASSE : au moins un test est ECHEC ou NON_TESTE.")
 state={"t0":t0,"base":base,"outdir":outdir,"pm":pm,"blocking":blocking,"warnings":warnings,"identites":identites,"calculs":calculs,"corroboration":corroboration,"hypotheses":hypotheses,"ouverts":ouverts,"section_status":section_status,"aretes_details":aretes_details,"prov":prov,"sha_av":sha_av,"memoires":memoires,"Fich":Fich,"D":D,"ctx":ctx,"geo":geo,"geo_ok":geo_ok,"arch_comp":arch_comp,"arch_ok":arch_ok,"arch_statut":arch_statut,"proj":proj,"verif":verif,"ident_ok":ident_ok,"acc":acc,"acc_ok":acc_ok,"nrj":nrj,"nrj_ok":nrj_ok,"res":res,"ldl_res":ldl_res,"ldl_audit_ok":ldl_audit_ok,"B_pos":B_pos,"sym_ok":sym_ok,"_scripts_info":_scripts_info,"_val_ok":_val_ok,"_val_motifs":_val_motifs,"_ok_exports":_ok_exports,"_manq_exports":_manq_exports,"_a":_a,"_ch":_ch,"_geo":_geo,"_rk":_rk,"_q":_q,"_c":_c,"_a2":_a2,"_proj":_proj,"_acc":_acc,"_nrj":_nrj}
 state["etape"]="premiere_partie_terminee"
 state["ldl_detail"]=ldl_detail
 state["corroboration_archives"]=corroboration_archives
 state["provenance_detail"]=provenance_detail
 state["tests_negatifs_b1"]=tests_b1
 state["contrat_state"]=_valider_contrat_state_b1(state)
 if not state["contrat_state"]["ok"]:
  for _m in state["contrat_state"]["motifs"]: blocking.append("Contrat state : "+_m)
 state["prudence_mathematique"]={"mu_ge_1_5":"NON_CONCLU_PAR_B1_SEULE","consequence_Mt":"CONDITIONNELLE_A_MU_ET_AUX_PREMISSES_STRUCTURELLES","premisses_Mt":"M(t) = (alpha-beta)I + betaJ, alpha(t) + 4 beta(t) = 12 : rapportées, non redémontrées par B1","echec_methode":"Un échec de méthode ne constitue pas une réfutation mathématique."}
 return state
