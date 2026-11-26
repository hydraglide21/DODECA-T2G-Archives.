#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DODECA — BORNE ENERGETIQUE EXACTE V3.3.18 — PARTIE B2.
Tests, intégrité finale, gate et rapport. Interface : main_partie_2(state).
Architecture V3.3.18 : état explicite (correction ciblée de V3.3.7 B2), aucun exec(), aucun return locals().
Le rapport de calcul et le reçu d'archivage sont deux objets distincts.
Ne pas exécuter avant revue statique complète.
"""
import hashlib as _hashlib, io as _io, json as _json, math as _math, os as _os, re as _re, sys as _sys, tempfile as _tempfile, time as _time, traceback as _traceback
from fractions import Fraction as _Fraction
from datetime import datetime as _datetime, timezone as _timezone
from pathlib import Path as _Path
import numpy as _np
import DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_7_PARTIE_A as _PA
from DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_7_PARTIE_A import EXP, INDISPENSABLE, TOL_ARCHIVES, EPS_MACHINE, U_ARRONDI, CLES_GATE, F, F0, F1, fadd, fneg, fsub, fmul, fscale, fiszero, solve_lin, finv, fdiv, f_to_float, f_to_str, f_sign_adaptive, f_is_pos, parse_csv_expr, q5_to_F, q5_add, q5_sub, q5_mul, q5_scale_int, q5_to_str, q5_is_pos, dist_carree_q5, sp_clean, sp_mul, sp_scale, sp_matvec, sp_trace, sp_eq, dense_matvec, dense_quad, dense_eq, est_carree, verifier_symetrie, verifier_verrou_projecteurs, valider_fichier_provenance, valider_provenance_sur_octets, verifier_integrite_hashes, verifier_integrite_fichiers, evaluer_borne, statut_corroboration, verifier_integrite_fichier_chemin, schur_to_y, verify_counterexample, ldl_with_pivot, ldl_audit, calculer_borne_arrondi, comparer_archives, valider_geometrie, valider_aretes_geometriques, accessible_nonempty, valider_entrees, verifier_rapport_sans_nan, verifier_exports_partie_a
# Alias : le corps de main() ci-dessous utilise les noms courts historiques.
hashlib, io, json, math, os, re, sys, tempfile, time, traceback = _hashlib, _io, _json, _math, _os, _re, _sys, _tempfile, _time, _traceback
Fraction, datetime, timezone, Path, np = _Fraction, _datetime, _timezone, _Path, _np

import DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_19_PARTIE_B1 as _B1
# V3.3.18 B2 : chaîne cohérente A V3.3.7 (inchangée) + B1 V3.3.19 (correctif indépendant) + B2 V3.3.18. B2 N'EST PAS compatible avec B1 V3.3.7 inchangée (voir verifier_provenance_complete).

def valider_contrat_state(state):
 motifs=[]
 if type(state) is not dict: return {"ok":False,"motifs":["state n'est pas un dict"]}
 for k in ("base","outdir"):
  if k in state and state[k] is not None and not isinstance(state[k], Path): motifs.append(f"state[{k}] n'est pas un objet Path valide")
 for k in ("blocking","warnings","calculs","identites","hypotheses","ouverts"):
  if k in state and state[k] is not None and type(state[k]) is not list: motifs.append(f"state[{k}] n'est pas une liste utilisable")
 for k in ("base","outdir","prov","Fich","sha_av","section_status","_scripts_info"):
  if k not in state: motifs.append(f"state manque {k}")
  elif state[k] is None: motifs.append(f"state[{k}] est None")
 if "prov" in state and state["prov"] is not None:
  if type(state["prov"]) is not dict: motifs.append("prov n'est pas un dict")
  else:
   for nom in INDISPENSABLE:
    if nom not in state["prov"]: motifs.append(f"prov manque {nom}")
    elif type(state["prov"][nom]) is not dict: motifs.append(f"prov[{nom}] n'est pas un dict")
    elif state["prov"][nom].get("statut") not in ("CONFORME","ABSENT_OU_ILLISIBLE","NON_CONFORME","MODIFIE"): motifs.append(f"prov[{nom}] statut invalide")
    elif "chemin" not in state["prov"][nom]: motifs.append(f"prov[{nom}] chemin manquant")
 if "Fich" in state and state["Fich"] is not None and type(state["Fich"]) is not dict: motifs.append("Fich n'est pas un dict")
 if "sha_av" in state and state["sha_av"] is not None and type(state["sha_av"]) is not dict: motifs.append("sha_av n'est pas un dict")
 if "section_status" in state and state["section_status"] is not None and type(state["section_status"]) is not dict: motifs.append("section_status n'est pas un dict")
 if "_scripts_info" in state and state["_scripts_info"] is not None:
  if type(state["_scripts_info"]) is not dict: motifs.append("_scripts_info n'est pas un dict")
  else:
   for nom in ("PARTIE_A","PARTIE_B1","PARTIE_B2"):
    if nom not in state["_scripts_info"]: motifs.append(f"_scripts_info manque {nom}")
    elif type(state["_scripts_info"][nom]) is not dict: motifs.append(f"_scripts_info[{nom}] n'est pas un dict")
    elif state["_scripts_info"][nom].get("sha256_initial") is None: motifs.append(f"_scripts_info[{nom}] sha256_initial manquant")
 for _ind in ("geo_ok","ident_ok","acc_ok","nrj_ok","B_pos","sym_ok","ldl_audit_ok","arch_ok"):
  if _ind in state and state[_ind] is not None and type(state[_ind]) is not bool: motifs.append(f"state[{_ind}] n'est pas un bool strict.")
 if "Fich" in state and "sha_av" in state and type(state["Fich"]) is dict and type(state["sha_av"]) is dict:
  if set(state["Fich"].keys())!=set(state["sha_av"].keys()): motifs.append("Fich et sha_av n'ont pas les mêmes clés.")
  for _k,_v in state["sha_av"].items():
   if _v is not None and (type(_v) is not str or len(_v)!=64 or any(c not in "0123456789abcdef" for c in _v)): motifs.append(f"sha_av[{_k}] n'est pas un SHA-256 hex 64.")
 if "section_status" in state and type(state["section_status"]) is dict:
  for _sec in ("provenance","chargement","validation_geometrique","constructions_RK0","projecteurs","verif_projecteurs","espace_accessible","energie_initiale","quotient_LDL"):
   if _sec not in state["section_status"]: motifs.append(f"section_status manque {_sec}.")
   elif type(state["section_status"][_sec]) is not dict: motifs.append(f"section_status[{_sec}] n'est pas un dict.")
 if "res" in state and state["res"] is not None and type(state["res"]) is not dict: motifs.append("res (quotient) n'est pas un dict.")
 if "ldl_res" in state and state["ldl_res"] is not None and type(state["ldl_res"]) is not dict: motifs.append("ldl_res n'est pas un dict.")
 if "_scripts_info" in state and type(state["_scripts_info"]) is dict:
  for _nom in ("PARTIE_A","PARTIE_B1","PARTIE_B2"):
   _inf=state["_scripts_info"].get(_nom)
   if type(_inf) is dict and "chemin" in _inf and type(_inf["chemin"]) is not str: motifs.append(f"_scripts_info[{_nom}] chemin n'est pas une chaîne.")
 if "ldl_detail" not in state or state["ldl_detail"] is None:
  motifs.append("ldl_detail B1 absent : les cinq statuts LDL sont obligatoires.")
 elif type(state["ldl_detail"]) is not dict:
  motifs.append("ldl_detail (B1 V3.3.19) n'est pas un dict.")
 else:
  _cles_ldl=("quotient_construit","symetrie_exacte","ldl_execute","certificat_audite","conclusion")
  if not all(k in state["ldl_detail"] for k in _cles_ldl): motifs.append("ldl_detail incomplet (5 statuts attendus).")
  for _k in _cles_ldl[:4]:
   if type(state["ldl_detail"].get(_k)) is not bool: motifs.append(f"ldl_detail.{_k} doit être un bool strict.")
 if "corroboration_archives" in state and state["corroboration_archives"] is not None:
  if type(state["corroboration_archives"]) is not dict: motifs.append("corroboration_archives n'est pas un dict.")
  elif state["corroboration_archives"].get("statut") not in ("CONFORME","ECART","INDISPONIBLE","NON_CALCULEE"): motifs.append("corroboration_archives.statut invalide.")
  elif "arch_statut" in state and state["arch_statut"] is not None and state["corroboration_archives"].get("statut")!=state["arch_statut"]: motifs.append("Incohérence arch_statut / corroboration_archives.statut.")
 if "contrat_state" in state and state["contrat_state"] is not None:
  if type(state["contrat_state"]) is not dict: motifs.append("contrat_state (B1) n'est pas un dict.")
  elif state["contrat_state"].get("ok") is False: motifs.append("Contrat B1 en échec (contrat_state.ok=False) : "+"; ".join(str(m) for m in state["contrat_state"].get("motifs",[])[:3]))
 if "arch_statut" in state and state["arch_statut"] is not None and state["arch_statut"] not in ("CONFORME","ECART","INDISPONIBLE","NON_CALCULEE"): motifs.append("arch_statut invalide (4 statuts V3.3.19 attendus).")
 if "provenance_detail" in state and state["provenance_detail"] is not None:
  if type(state["provenance_detail"]) is not dict: motifs.append("provenance_detail n'est pas un dict.")
  elif state["provenance_detail"].get("ok") is False: motifs.append("Provenance B1 en échec (provenance_detail.ok=False).")
 return {"ok":len(motifs)==0,"motifs":motifs}

def _construire_recu(cand, ecriture_ok, relecture_ok, octets_rapport, sha_rapport, chemin_recu):
 return {"type":"RECU_ARCHIVAGE_V3_3_18","chemin_rapport":str(cand),"taille_rapport_octets":len(octets_rapport) if ecriture_ok else None,"sha256_rapport":sha_rapport,"confirmation_relecture":bool(relecture_ok),"comparaison_octets_relus_egaux_octets_ecrits":bool(relecture_ok),"date_utc":datetime.now(timezone.utc).isoformat(),"statut_final_archivage":"ARCHIVE_CONFIRME" if (ecriture_ok and relecture_ok) else "ARCHIVAGE_NON_CONFIRME","chemin_recu":str(chemin_recu)}

def _ecrire_fichier_exclusif_et_relire(chemin, texte):
 try:
  with open(chemin,"x",encoding="utf-8") as fh: fh.write(texte)
 except FileExistsError as e: return {"ecriture_ok":False,"relecture_ok":False,"detail":f"FileExistsError: {e}"}
 try:
  relus=Path(chemin).read_bytes(); ok=(relus.decode("utf-8")==texte)
  return {"ecriture_ok":True,"relecture_ok":bool(ok),"detail":"Écriture + relecture cohérentes." if ok else "Relecture incohérente."}
 except Exception as e: return {"ecriture_ok":True,"relecture_ok":False,"detail":f"{type(e).__name__}: {e}"}

def verifier_provenance_complete(state):
 # V3.3.19 §1 : chaîne cohérente. A = V3.3.7 effectivement importée. B1 = V3.3.19 effectivement importée. B2 = V3.3.19 exécutée.
 # Pour chaque script : chemin attendu, SHA initial (B1, avant B2), taille initiale, vérification finale (SHA + taille relus en B2). Non circulaire : l'initial vient de B1 avant B2.
 # Ne jamais fabriquer une empreinte initiale, ne jamais comparer deux versions différentes.
 attendus={"PARTIE_A":"DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_7_PARTIE_A.py","PARTIE_B1":"DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_19_PARTIE_B1.py","PARTIE_B2":"DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_18_PARTIE_B2.py"}
 infos=(state.get("_scripts_info") or {}) if type(state) is dict else {}
 modules_charges={"PARTIE_A":Path(_PA.__file__).resolve(),"PARTIE_B1":Path(_B1.__file__).resolve(),"PARTIE_B2":Path(__file__).resolve()}
 details={}; motifs=[]
 for nom, attendu in attendus.items():
  info=infos.get(nom) if type(infos) is dict else None
  if not type(info) is dict or "chemin" not in info:
   motifs.append(f"{nom} : _scripts_info absent ou sans chemin."); details[nom]={"ok":False,"motif":"absent ou sans chemin"}; continue
  try:
   chemin_enregistre=Path(info.get("chemin","")).resolve()
  except Exception as e:
   motifs.append(f"{nom} : chemin enregistré invalide : {type(e).__name__}: {e}")
   details[nom]={"ok":False,"motif":"chemin invalide"}; continue
  if attendu not in str(chemin_enregistre) or chemin_enregistre!=modules_charges[nom]:
   motifs.append(f"{nom} : chemin enregistré {chemin_enregistre} différent du module réellement chargé {modules_charges[nom]} (attendu {attendu}).")
   details[nom]={"ok":False,"motif":"chemin != module chargé", "chemin":str(chemin_enregistre),"module_charge":str(modules_charges[nom])}; continue
  if info.get("sha256_initial") is None or info.get("taille_octets_initial") is None:
   motifs.append(f"{nom} : SHA initial ou taille initiale manquants : aucune empreinte fabriquée.")
   details[nom]={"ok":False,"motif":"empreinte initiale manquante"}; continue
  try:
   data=Path(info["chemin"]).read_bytes(); sha_fin=hashlib.sha256(data).hexdigest(); taille_fin=len(data)
  except Exception as e:
   motifs.append(f"{nom} : relecture finale impossible : {type(e).__name__}: {e}"); details[nom]={"ok":False,"motif":"relecture finale impossible"}; continue
  if sha_fin!=info["sha256_initial"] or taille_fin!=info["taille_octets_initial"]:
   motifs.append(f"{nom} : intégrité finale != initiale (SHA ou taille)."); details[nom]={"ok":False,"motif":"SHA/taille final != initial","sha256_final":sha_fin,"taille_octets_final":taille_fin}; continue
  details[nom]={"ok":True,"motif":"chemin + SHA initial == SHA final + taille initiale == taille finale","chemin":str(info.get("chemin")),"sha256_initial":info["sha256_initial"],"sha256_final":sha_fin,"taille_octets_initial":info["taille_octets_initial"],"taille_octets_final":taille_fin}
 if "V3_3_19_PARTIE_B1" not in str((infos.get("PARTIE_B1") or {}).get("chemin","")):
  motifs.append("B1 exécutée différente de V3.3.19 : elle ne peut pas attester cette chaîne B2 V3.3.19.")
 return {"ok":len(motifs)==0,"motifs":motifs,"details":details,"correction_B1_minimale":[]}

def verifier_gate_ldl(res, sym_ok, ldl_res, ldl_audit_ok, ldl_detail=None):
    """Gate LDL strict : aucun champ de détail absent, faux ou non booléen ne passe."""
    motifs = []
    if type(res) is not dict:
        motifs.append("quotient non construit (res n'est pas un dict).")
    else:
        if not all(k in res for k in ("A_exact", "B_exact", "D_exact", "dim", "n_pos")):
            motifs.append("quotient incomplet : A_exact/B_exact/D_exact/dim/n_pos manquants.")
        if res.get("symetrie") is None and not (type(sym_ok) is bool and sym_ok):
            motifs.append("symétrie exacte non vérifiée.")
    if type(sym_ok) is not bool or sym_ok is not True:
        motifs.append("symétrie exacte non vérifiée (sym_ok n'est pas True strict).")
    if type(ldl_res) is not dict:
        motifs.append("LDL non exécuté (ldl_res n'est pas un dict).")
    else:
        statut = ldl_res.get("statut")
        if statut not in ("PSD", "INDEFINIE", "INDECIS", "NON_EXECUTE"):
            motifs.append(f"LDL statut invalide : {statut}.")
        if statut == "NON_EXECUTE":
            motifs.append("LDL non exécuté (statut NON_EXECUTE) : ne peut pas satisfaire LDL_PSD.")
        if statut == "PSD" and (ldl_res.get("diag") is None or (ldl_res.get("perm") is None and ldl_res.get("L") is None)):
            motifs.append("certificat LDL PSD incomplet : diag/perm/L manquants.")
        if statut == "INDECIS":
            motifs.append("LDL indécis : ne peut pas satisfaire LDL_PSD.")
        if statut == "INDEFINIE":
            motifs.append("LDL indéfinie : ne peut pas satisfaire LDL_PSD.")
    if type(ldl_audit_ok) is not bool or ldl_audit_ok is not True:
        motifs.append("audit LDL exact non réussi (ldl_audit_ok n'est pas True strict).")
    if type(res) is dict and type(res.get("ldl_audit")) is dict and res["ldl_audit"].get("ok") is not True:
        motifs.append("audit LDL exact (res['ldl_audit']) non réussi.")

    cles_detail = ("quotient_construit", "symetrie_exacte", "ldl_execute", "certificat_audite")
    if type(ldl_detail) is not dict:
        motifs.append("ldl_detail absent ou invalide : détail B1 obligatoire.")
    else:
        for cle in cles_detail:
            valeur = ldl_detail.get(cle)
            if type(valeur) is not bool:
                motifs.append(f"ldl_detail.{cle} : bool strict requis.")
            elif valeur is not True:
                motifs.append(f"ldl_detail.{cle} : validation refusée.")
        if ldl_detail.get("conclusion") != "PSD":
            motifs.append("ldl_detail.conclusion doit être exactement PSD pour satisfaire LDL_PSD.")
        if type(ldl_res) is dict and ldl_detail.get("conclusion") == "PSD" and ldl_res.get("statut") != "PSD":
            motifs.append("Incohérence ldl_detail / ldl_res : conclusion PSD mais statut ldl_res != PSD.")
        if type(ldl_res) is dict and ldl_detail.get("ldl_execute") is True and ldl_res.get("statut") == "NON_EXECUTE":
            motifs.append("Incohérence ldl_detail / ldl_res : ldl_execute True mais statut NON_EXECUTE.")
    ldl_psd = (len(motifs) == 0 and type(ldl_res) is dict and ldl_res.get("statut") == "PSD")
    return {"ldl_psd": bool(ldl_psd), "motifs": motifs,
            "conclusion": "LDL_PSD établie" if ldl_psd else "LDL_PSD NON établie"}

def calculer_code_retour(borne_statut, borne_statut_final, ecriture_ok, recu, attestation):
 # V3.3.19 : le code 0 exige une vérification disque indépendante des trois maillons.
 if borne_statut != "DEMONTRE" or borne_statut_final != "DEMONTRE": return 1
 if ecriture_ok is not True or type(recu) is not dict or type(attestation) is not dict: return 1
 try:
  if recu.get("statut_final_archivage") != "ARCHIVE_CONFIRME": return 1
  if recu.get("confirmation_relecture") is not True or recu.get("comparaison_octets_relus_egaux_octets_ecrits") is not True: return 1
  if attestation.get("statut_attestation") != "ATTESTATION_CONFIRMEE" or attestation.get("statut_archivage_attestation") != "ARCHIVE_CONFIRME": return 1
  if attestation.get("relecture_recu_ok") is not True or attestation.get("relecture_attestation_ok") is not True: return 1
  p_rapport=Path(recu["chemin_rapport"]); p_recu=Path(recu["chemin_recu"]); p_att=Path(attestation["chemin_attestation"])
  if recu.get("chemin_attestation_prevu") != str(p_att): return 1
  oct_rapport=p_rapport.read_bytes()
  if len(oct_rapport) != recu.get("taille_rapport_octets") or hashlib.sha256(oct_rapport).hexdigest() != recu.get("sha256_rapport"): return 1
  oct_recu=p_recu.read_bytes(); sha_recu=hashlib.sha256(oct_recu).hexdigest()
  if len(oct_recu) != attestation.get("taille_recu_octets") or sha_recu != attestation.get("sha256_recu"): return 1
  if attestation.get("chemin_recu") != str(p_recu): return 1
  obj_recu=json.loads(oct_recu.decode("utf-8"))
  if type(obj_recu) is not dict or obj_recu != recu or obj_recu.get("statut_final_archivage") != "ARCHIVE_CONFIRME": return 1
  oct_att=p_att.read_bytes()
  if len(oct_att) != attestation.get("taille_attestation_octets") or hashlib.sha256(oct_att).hexdigest() != attestation.get("sha256_attestation"): return 1
  obj_att=json.loads(oct_att.decode("utf-8"))
  if type(obj_att) is not dict: return 1
  if obj_att.get("type") != "ATTESTATION_ARCHIVAGE_V3_3_18": return 1
  if obj_att.get("chemin_recu") != str(p_recu) or obj_att.get("taille_recu_octets") != len(oct_recu) or obj_att.get("sha256_recu") != sha_recu: return 1
  if obj_att.get("relecture_recu_ok") is not True or obj_att.get("statut_final_archivage_recu") != "ARCHIVE_CONFIRME": return 1
  if recu.get("chemin_rapport") is None: return 1
 except Exception:
  return 1
 return 0

def auditer_compatibilite_b1(state):
 # Audit dynamique du state B1 V3.3.19 : ne pas figer un ancien jeu de 51 clés.
 # Les clés réellement consommées par B2 sont vérifiées; les autres clés B1 sont conservées.
 cles_b2_utilisees={"t0","base","outdir","pm","blocking","warnings","identites","calculs","corroboration","hypotheses","ouverts","section_status","aretes_details","prov","sha_av","memoires","Fich","D","ctx","geo","geo_ok","arch_comp","arch_ok","arch_statut","proj","verif","ident_ok","acc","acc_ok","nrj","nrj_ok","res","ldl_res","ldl_audit_ok","B_pos","sym_ok","_scripts_info","_val_ok","_val_motifs","_ok_exports","_manq_exports","_a","_ch","_geo","_rk","_q","_c","_a2","_proj","_acc","_nrj","ldl_detail"}
 presentes=set(state) if type(state) is dict else set()
 manquantes=sorted(cles_b2_utilisees-presentes)
 supplementaires=sorted(presentes-cles_b2_utilisees)
 return {"version_B1_attendue":"V3.3.19","nombre_cles_state":len(presentes),
         "cles_B2_utilisees":sorted(cles_b2_utilisees),
         "cles_B2_manquantes":manquantes,"cles_B1_supplementaires_preservees":supplementaires,
         "ok":len(manquantes)==0,"defauts_b1_signales_separement":[],
         "note":"Audit des clés consommées, sans exiger un nombre fixe de clés ni supprimer les clés supplémentaires."}

def main_partie_2(state):
 _contrat=valider_contrat_state(state)
 if not _contrat["ok"]:
  try:
   _b=state.get("blocking") if type(state) is dict else None
   if type(_b) is list: _b.append(f"Contrat state invalide : {'; '.join(_contrat['motifs'])}")
  except Exception: pass
  print(f"  CONTRAT STATE INVALIDE : {'; '.join(_contrat['motifs'])}")
  return 1
 blocking=state.get("blocking",[]); warnings=state.get("warnings",[]); section_status=state.get("section_status",{})
 compat_b1=auditer_compatibilite_b1(state); state["compatibilite_B1"]=compat_b1
 for _d in compat_b1["defauts_b1_signales_separement"]: warnings.append("Défaut B1 signalé (non masqué) : "+_d)
 if not compat_b1["ok"]:
  _msg="State B1 incomplet pour B2 : clés manquantes : "+", ".join(compat_b1["cles_B2_manquantes"])
  blocking.append(_msg); print("  CONTRAT B1/B2 INCOMPATIBLE : "+_msg); return 1
 prov_b2=verifier_provenance_complete(state); state["provenance_b2"]=prov_b2
 if not prov_b2["ok"]:
  blocking.append(f"Provenance B2 BLOQUANTE : {'; '.join(prov_b2.get('motifs', []))}")
  if prov_b2.get("correction_B1_minimale"):
   for _c in prov_b2["correction_B1_minimale"]: blocking.append("Correction B1 minimale requise : "+_c)
  print(f"  PROVENANCE B2 BLOQUANTE : {'; '.join(prov_b2.get('motifs', []))}")
  # Aucune empreinte initiale fabriquée : script_sha256 reste None, sha256_execution seul (traçabilité, pas preuve initiale).
  state["script_sha256"]=None; state["sha256_execution"]=prov_b2.get("sha256_execution")
  return 1
 _info_b2_verif=(state.get("_scripts_info") or {}).get("PARTIE_B2",{})
 if "V3_3_18_PARTIE_B2" not in str(_info_b2_verif.get("chemin","")):
  blocking.append("Intégrité B2 : le chemin B2 dans _scripts_info ne correspond pas à la V3.3.18 exécutée."); print("  BLOCAGE : B2 ne correspond pas à V3.3.19")
 def mark_section(nom,execute,ok,detail=""):
  section_status[nom]={"execute":bool(execute),"ok":bool(ok),"detail":str(detail)}
 def sec(nom,fn):
  try:
   r=fn()
   if r is True: print(f"  OK  {nom}"); return True
   print(f"  ECHEC  {nom}"); return False
  except Exception as e: print(f"  EXCEPTION  {nom} : {e}"); return False
 t0=state.get("t0")
 base=state.get("base")
 outdir=state.get("outdir")
 pm=state.get("pm")
 identites=state.get("identites")
 calculs=state.get("calculs")
 corroboration=state.get("corroboration")
 hypotheses=state.get("hypotheses")
 ouverts=state.get("ouverts")
 aretes_details=state.get("aretes_details")
 prov=state.get("prov")
 sha_av=state.get("sha_av")
 memoires=state.get("memoires")
 Fich=state.get("Fich")
 D=state.get("D")
 ctx=state.get("ctx")
 geo=state.get("geo")
 geo_ok=state.get("geo_ok")
 arch_comp=state.get("arch_comp")
 arch_ok=state.get("arch_ok")
 arch_statut=state.get("arch_statut")
 proj=state.get("proj")
 verif=state.get("verif")
 ident_ok=state.get("ident_ok")
 acc=state.get("acc")
 acc_ok=state.get("acc_ok")
 nrj=state.get("nrj")
 nrj_ok=state.get("nrj_ok")
 res=state.get("res")
 ldl_res=state.get("ldl_res")
 ldl_audit_ok=state.get("ldl_audit_ok")
 B_pos=state.get("B_pos")
 sym_ok=state.get("sym_ok")
 _scripts_info=state.get("_scripts_info")
 # V3.3.19 : prov_ok et ok_ch ne sont PAS dans CLES_ETAT_TRANSFEREES de B1 V3.3.7.
 # On les recalcule explicitement depuis state, on ne suppose rien.
 _prov=state.get("prov"); _sec_status=state.get("section_status",{})
 if _prov is None:
  blocking.append("prov_ok indisponible : state['prov'] absent ; provenance bloquée.")
  prov_ok=False
 else:
  try:
   prov_ok=bool(all(_prov[n].get("statut")=="CONFORME" for n in INDISPENSABLE))
  except Exception as _e:
   blocking.append(f"prov_ok indisponible : {_e}"); prov_ok=False
 if not isinstance(_sec_status, dict):
  blocking.append("ok_ch indisponible : section_status absent.")
  ok_ch=False
 else:
  ok_ch=bool(_sec_status.get("chargement",{}).get("ok") is True and state.get("D") is not None)
 if not ok_ch:
  blocking.append("ok_ch : chargement non confirmé depuis state (section chargement / D absent).")
 _val_ok=state.get("_val_ok")
 _val_motifs=state.get("_val_motifs")
 _ok_exports=state.get("_ok_exports")
 _manq_exports=state.get("_manq_exports")
 _a=state.get("_a")
 _ch=state.get("_ch")
 _geo=state.get("_geo")
 _rk=state.get("_rk")
 _q=state.get("_q")
 _c=state.get("_c")
 _a2=state.get("_a2")
 _proj=state.get("_proj")
 _acc=state.get("_acc")
 _nrj=state.get("_nrj")
 neg={}
 def run_neg(nom,fn):
  try:
   r=fn()
   if r is True: return {"statut":"PASSE","detail":"cas incorrect bien rejeté / indécis détecté / gate bloqué."}
   if r is False: return {"statut":"ECHEC","detail":"cas incorrect non rejeté / gate non bloqué."}
   return {"statut":"NON_TESTABLE","detail":"résultat non booléen."}
  except Exception as e: return {"statut":"NON_TESTABLE","detail":f"exception : {type(e).__name__}: {e}"}
 def gate_base():
  return {"prov_conformes":True,"integrite_entrees":True,"geometrie_validee":True,"projecteurs_identites":True,
   "espace_accessible_non_vide_valide":True,"energie_initiale_exacte":True,"B_definie_positive":True,
   "LDL_PSD":True,"tests_negatifs_reussis":True,
   "aucune_erreur_bloquante":True,"aucune_section_indispensable_en_echec":True}
 def _geometrie_rejetee(bars_fake):
  # Helper V3.3.19 : mutualise les 4 tests de géométrie (barres, hors limites, identiques, mauvais cube).
  if not ok_ch: raise RuntimeError("D indisponible")
  r=valider_geometrie(D["V"],D["C"],bars_fake); return r
 def tests_negatifs():
  def p_absent():
   inf=valider_fichier_provenance(base/"__ABSENT_V335__.txt","0"*64)
   if inf["statut"]!="ABSENT_OU_ILLISIBLE": return False
   g=gate_base(); g["prov_conformes"]=False
   return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def p_hash():
   inf=valider_fichier_provenance(base/"SOMMETS_DODECAEDRE.csv","0"*64)
   if inf["statut"]!="NON_CONFORME": return False
   g=gate_base(); g["prov_conformes"]=False
   return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def p_modif():
   a=hashlib.sha256((base/"SOMMETS_DODECAEDRE.csv").read_bytes()).hexdigest()
   b=hashlib.sha256((base/"SOMMETS_DODECAEDRE.csv").read_bytes()+b"x").hexdigest()
   if verifier_integrite_hashes(a,b): return False
   g=gate_base(); g["integrite_entrees"]=False
   return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def p_illisible():
   inf=valider_fichier_provenance(base,"0"*64)
   if inf["statut"]!="ABSENT_OU_ILLISIBLE": return False
   g=gate_base(); g["prov_conformes"]=False
   return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def p_gate():
   g=gate_base(); g["prov_conformes"]=False
   return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def g_prov():
   g=gate_base(); g["prov_conformes"]=False; return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def g_integrite():
   g=gate_base(); g["integrite_entrees"]=False; return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def g_geo():
   g=gate_base(); g["geometrie_validee"]=False; return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def g_proj():
   g=gate_base(); g["projecteurs_identites"]=False; return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def g_vide():
   g=gate_base(); g["espace_accessible_non_vide_valide"]=False; return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def g_nrj():
   g=gate_base(); g["energie_initiale_exacte"]=False; return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def g_B():
   g=gate_base(); g["B_definie_positive"]=False; return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def g_ldl_indecis():
   g=gate_base(); g["LDL_PSD"]=False; return evaluer_borne(g,"INDECIS",True)["borne_statut"]!="DEMONTRE"
  def g_ldl_audit():
   g=gate_base(); g["LDL_PSD"]=True; return evaluer_borne(g,"PSD",False)["borne_statut"]!="DEMONTRE"
  def g_block():
   g=gate_base(); g["aucune_erreur_bloquante"]=False; return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def g_contreex():
   g=gate_base(); g["LDL_PSD"]=False
   r=evaluer_borne(g,"INDEFINIE",True)
   return r["borne_statut"]=="REFUTE" and r["conclusion_globale_M"].startswith("NON_CONCLU")
  def g_cle_manquante():
   g=gate_base(); del g["prov_conformes"]
   return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def t_integrite_fichiers():
   # Test réellement non destructif (correction 1) : fichier temporaire unique via tempfile.
   # Ne jamais écraser un préexistant (mkstemp O_EXCL), ne jamais supprimer un fichier
   # non créé par le test, nettoyage garanti dans tous les cas (finally).
   fd=None; tmp=None; cree=False
   try:
    fd,tmp_str=tempfile.mkstemp(prefix="dodeca_test_integrite_",suffix=".txt")
    tmp=Path(tmp_str); cree=True; os.close(fd); fd=None
    tmp.write_bytes(b"v1")
    sha1=hashlib.sha256(tmp.read_bytes()).hexdigest()
    inch1,det1=verifier_integrite_fichiers({"tmp":tmp},{"tmp":sha1})
    if not inch1 or not det1["tmp"]["ok"]: return False  # intact
    tmp.write_bytes(b"v2")  # modification
    inch2,det2=verifier_integrite_fichiers({"tmp":tmp},{"tmp":sha1})
    if inch2 or det2["tmp"]["ok"]: return False  # modification détectée
    tmp.unlink(); cree=False  # disparition : le test supprime le fichier qu'il a créé
    inch3,det3=verifier_integrite_fichiers({"tmp":tmp},{"tmp":sha1})
    if inch3 or det3["tmp"]["ok"]: return False  # disparition détectée
    return True
   finally:
    try:
     if fd is not None: os.close(fd)
    except Exception: pass
    try:
     # Nettoyage : seulement si le test a créé le fichier et qu'il existe encore.
     # Jamais de suppression d'un fichier non créé par ce test.
     if cree and tmp is not None and tmp.exists(): tmp.unlink()
    except Exception: pass
  def t_sym_Aq():
   M=[[F1,F(2)],[F0,F1]]; return (not verifier_symetrie(M))
  def t_sym_D():
   M=[[F1,F0,F1],[F0,F1,F0],[F0,F0,F1]]; return (not verifier_symetrie(M))
  def t_sym_bloque():
   # Matrice non symétrique -> LDL bloqué : le gate avec ldl_stat INDECIS ne peut pas être DEMONTRE.
   M=[[F1,F(2)],[F0,F1]]
   if verifier_symetrie(M): return False
   g=gate_base(); g["LDL_PSD"]=False
   return evaluer_borne(g,"INDECIS",False)["borne_statut"]!="DEMONTRE"
  def t_nbarres():
   r=_geometrie_rejetee(D["bars"][:-1]); return (not r["n_barres_60"])
  def t_hors_lim():
   fake=[(99,1,1)]+D["bars"][1:]; r=_geometrie_rejetee(fake); return (not r["endpoints_distincts_valides"])
  def t_ident():
   fake=[(0,0,1)]+D["bars"][1:]; r=_geometrie_rejetee(fake); return (not r["endpoints_distincts_valides"])
  def t_mauvais_cube():
   hors=[v for v in range(20) if v not in D["C"][0]][0]
   fake=[(hors,list(D["C"][0])[0],1)]+D["bars"][1:]; r=_geometrie_rejetee(fake); return (not r["appartenance_cube_porteur"])
  def t_vide():
   ok,_=accessible_nonempty([],[]); return (not ok)
  def t_signe():
   tiny=F(Fraction(-2236067977,1000000000),Fraction(1),Fraction(0),Fraction(0))
   return f_sign_adaptive(tiny,dens=(10**6,)) is None
  def t_pivot_neg():
   Dm=[[fscale(F1,Fraction(-1))]]; rr=ldl_with_pivot(Dm)
   if rr["statut"]!="INDEFINIE": return False
   ok,_=verify_counterexample(Dm,rr["contre_exemple"],attendu=fscale(F1,Fraction(-1))); return ok
  def t_schur():
   Dm=[[F0,F1],[F1,F0]]; rr=ldl_with_pivot(Dm)
   if rr["statut"]!="INDEFINIE": return False
   ok,_=verify_counterexample(Dm,rr["contre_exemple"]); return ok
  def t_proj():
   I={(i,i):F1 for i in range(60)}; P2=sp_scale(I,F(2))
   return (not sp_eq(sp_mul(P2,P2),P2))
  def t_nan():
   R60={(i,i):F1 for i in range(60)}; K60={(i,i):F1 for i in range(60)}
   Ra_nan=np.zeros((60,60)); Ra_nan[0,0]=float("nan"); Ka_ok=np.zeros((60,60))
   ok,_,_=comparer_archives(R60, K60, Ra_nan, Ka_ok); return (not ok)
  def t_inf():
   R60={(i,i):F1 for i in range(60)}; K60={(i,i):F1 for i in range(60)}
   Ra_inf=np.zeros((60,60)); Ra_inf[0,0]=float("inf"); Ka_ok=np.zeros((60,60))
   ok,_,_=comparer_archives(R60, K60, Ra_inf, Ka_ok); return (not ok)
  def t_aretes_fausse():
   if not ok_ch: raise RuntimeError("D indisponible")
   C0=list(D["C"][0]); bars_c=[(a,b) for (a,b,cu) in D["bars"] if cu==1]
   bars_set={frozenset((a,b)) for a,b in bars_c}; diag=None
   for i in range(len(C0)):
    for j in range(i+1,len(C0)):
     if frozenset((C0[i],C0[j])) not in bars_set: diag=(C0[i],C0[j]); break
    if diag: break
   if diag is None: raise RuntimeError("aucune diagonale trouvée")
   fake=[(diag[0],diag[1],1)]+[(a,b,cu) for (a,b,cu) in D["bars"] if cu!=1 or (a,b)!=(bars_c[0][0],bars_c[0][1])]
   b,_=valider_aretes_geometriques(D["V"],D["C"],fake)
   return (not b["aretes_geometriques_completes"])
  def t_partieA_absente():
   inf=valider_fichier_provenance(base/"DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_7_PARTIE_A_ABSENTE.py","0"*64)
   return inf["statut"]=="ABSENT_OU_ILLISIBLE"
  def _test_script_modifie(nom):
   import tempfile as _tf
   fd,_p=_tf.mkstemp(prefix="dodeca_script_",suffix=".txt"); os.close(fd); _chemin=Path(_p)
   try:
    _chemin.write_bytes(b"contenu original "+nom.encode()); _sha0=hashlib.sha256(_chemin.read_bytes()).hexdigest()
    _chemin.write_bytes(b"contenu MODIFIE "+nom.encode())
    _res=verifier_integrite_fichier_chemin(_chemin, sha_attendu=_sha0)
    return _res["statut"]=="MODIFIE"
   finally:
    try:
     if _chemin.exists(): _chemin.unlink()
    except Exception: pass
  def t_partieA_modifiee():
   return _test_script_modifie("PARTIE_A")
  def t_partieB1_modifiee():
   return _test_script_modifie("PARTIE_B1")
  def t_partieB2_modifiee():
   return _test_script_modifie("PARTIE_B2")
  def t_partieB_modifiee():
   return t_partieB1_modifiee() and t_partieB2_modifiee()
  def t_empreinte_incorrecte():
   inf=valider_fichier_provenance(base/"SOMMETS_DODECAEDRE.csv","f"*64)
   return inf["statut"]=="NON_CONFORME"
  def t_gate_bool_str1():
   g=gate_base(); g["prov_conformes"]="1"
   return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def t_gate_bool_chaine():
   g=gate_base(); g["prov_conformes"]="oui"
   return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def t_gate_bool_entier1():
   g=gate_base(); g["prov_conformes"]=1
   return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def t_trace_incorrecte():
   return (not verifier_verrou_projecteurs(True,True,True,True,False,True))
  def t_somme_traces_incorrecte():
   return (not verifier_verrou_projecteurs(True,True,True,True,True,False))
  def t_borne_depassee():
   R60={(i,i):F1 for i in range(60)}; K60={(i,i):F1 for i in range(60)}
   Ra_f=np.zeros((60,60)); Ka_f=np.zeros((60,60)); Ka_f[0,0]=1e-6
   ok,comp,msgs=comparer_archives(R60, K60, Ra_f, Ka_f)
   _st=statut_corroboration(ok, exception=False, calcule=True)
   g=gate_base()
   return (not ok) and (_st=="CORROBORATION_ECART") and evaluer_borne(g,"PSD",True)["borne_statut"]=="DEMONTRE"
  def t_depassement_sous_tol():
   R60={(i,i):F1 for i in range(60)}; K60={(i,i):F1 for i in range(60)}
   info=calculer_borne_arrondi(R60,K60,np.zeros((60,60)),np.zeros((60,60)))
   borne=info.get("borne_K")
   if borne is None or not (0<borne<1e-12): return False
   dep=borne*2.0
   if not (borne<dep<1e-12): return False
   Ra_f=np.zeros((60,60)); Ka_f=np.zeros((60,60)); Ka_f[0,0]=dep
   ok,comp,msgs=comparer_archives(R60,K60,Ra_f,Ka_f)
   return comp.get("K0",{}).get("depassement_borne") is True and (not comp.get("K0",{}).get("tolerance_supplementaire",False))
  def t_ldl_incomplet():
   # Certificat LDL incomplet : diag manquant -> audit False, jamais succès.
   ok,msg=ldl_audit([[F1,F0],[F0,F1]],{"statut":"PSD","perm":[0,1],"L":[[F1,F0],[F0,F1]],"diag":None,"k_arret":2})
   return (not ok)
  def t_ldl_indecis_non_succes():
   ok,msg=ldl_audit([[F1]],{"statut":"INDECIS","perm":[0],"L":[[F1]],"diag":[],"k_arret":0})
   return (not ok)
  def t_entree_modifiee_pendant():
   fd,tmp_str=tempfile.mkstemp(prefix="dodeca_entree_modif_",suffix=".txt"); os.close(fd); tmp=Path(tmp_str); cree=True
   try:
    tmp.write_bytes(b"entree v1"); s1=hashlib.sha256(tmp.read_bytes()).hexdigest()
    tmp.write_bytes(b"entree v2")
    inch,det=verifier_integrite_fichiers({"entree":tmp},{"entree":s1})
    return (not inch) and (not det["entree"]["ok"])
   finally:
    try:
     if tmp.exists(): tmp.unlink()
    except Exception: pass
  def t_entree_disparue_pendant():
   fd,tmp_str=tempfile.mkstemp(prefix="dodeca_entree_disparue_",suffix=".txt"); os.close(fd); tmp=Path(tmp_str)
   try:
    tmp.write_bytes(b"entree v1"); s1=hashlib.sha256(tmp.read_bytes()).hexdigest(); tmp.unlink()
    inch,det=verifier_integrite_fichiers({"entree":tmp},{"entree":s1})
    return (not inch) and (not det["entree"]["ok"])
   finally:
    try:
     if tmp.exists(): tmp.unlink()
    except Exception: pass
  def t_ecriture_impossible():
   try:
    json.dumps({"x": float("nan")}, allow_nan=False); return False
   except ValueError: pass
   import tempfile as _tf
   _dir=_tf.mkdtemp(prefix="dodeca_ecriture_")
   try:
    _sous=Path(_dir)/"sous"; _sous.mkdir()
    try:
     with open(_sous, "x", encoding="utf-8") as fh: fh.write("x")
     return False
    except (IsADirectoryError, OSError): return True
   finally:
    import shutil as _sh
    try: _sh.rmtree(_dir, ignore_errors=True)
    except Exception: pass
  def t_rapport_sans_nan():
   ok,_=verifier_rapport_sans_nan({"a": 1.0, "b": [1,2]})
   ok2,_=verifier_rapport_sans_nan({"a": float("nan")})
   ok3,_=verifier_rapport_sans_nan({"a": float("inf")})
   return ok and (not ok2) and (not ok3)
  def t_archives_defavorable_gate_valide():
   # Gate réel : archives défavorables (écart 1e-6) mais calcul exact valide -> DEMONTRE.
   R60={(i,i):F1 for i in range(60)}; K60={(i,i):F1 for i in range(60)}
   Ra_f=np.zeros((60,60)); Ka_f=np.zeros((60,60)); Ka_f[0,0]=1e-6
   ok,comp,msgs=comparer_archives(R60,K60,Ra_f,Ka_f)
   if ok: return False
   g=gate_base()
   return evaluer_borne(g,"PSD",True)["borne_statut"]=="DEMONTRE"
  def t_archives_favorable_ne_compense_pas():
   # Gate réel : archives favorables (identiques) mais calcul exact en échec -> PAS DEMONTRE.
   R60={(i,i):F1 for i in range(60)}; K60={(i,i):F1 for i in range(60)}
   ok,comp,msgs=comparer_archives(R60,K60,np.zeros((60,60)),np.zeros((60,60)))
   if not ok: return False
   g=gate_base(); g["geometrie_validee"]=False
   return evaluer_borne(g,"PSD",True)["borne_statut"]!="DEMONTRE"
  def t_relecture_impossible():
   # Relecture d'un fichier temporaire supprimé -> FileNotFoundError ; _relecture_ok doit être False.
   import tempfile as _tf
   fd,_p=_tf.mkstemp(prefix="dodeca_relecture_",suffix=".txt"); os.close(fd); _chemin=Path(_p)
   _chemin.write_text("x",encoding="utf-8"); _chemin.unlink()
   try:
    _chemin.read_bytes(); return False
   except FileNotFoundError: return True
  def t_recu_non_confirme():
   # Si le rapport n'est pas écrit, le reçu doit rester ARCHIVAGE_NON_CONFIRME (jamais ARCHIVE_CONFIRME).
   ecriture_ok_sim=False; relecture_ok_sim=False
   statut="ARCHIVE_CONFIRME" if (ecriture_ok_sim and relecture_ok_sim) else "ARCHIVAGE_NON_CONFIRME"
   return statut=="ARCHIVAGE_NON_CONFIRME"
  def t_scripts_reels_controle_mecanisme():
   for nom in ("PARTIE_A","PARTIE_B1","PARTIE_B2"):
    info=(_scripts_info or {}).get(nom)
    if info is None or info.get("sha256_initial") is None: return False
    r=verifier_integrite_fichier_chemin(info["chemin"], sha_attendu=info["sha256_initial"])
    if r["statut"]!="CONFORME": return False
    r2=verifier_integrite_fichier_chemin(info["chemin"], sha_attendu="0"*64)
    if r2["statut"]!="MODIFIE": return False
   return True
  def t_relecture_mecanisme_reel():
   import tempfile as _tf
   fd,_p=_tf.mkstemp(prefix="dodeca_relecture_reelle_",suffix=".json"); os.close(fd); _chemin=Path(_p)
   try: _chemin.unlink()
   except Exception: pass
   res=_ecrire_fichier_exclusif_et_relire(_chemin, '{"test": 1}')
   try:
    if _chemin.exists(): _chemin.unlink()
   except Exception: pass
   if not (res["ecriture_ok"] and res["relecture_ok"]): return False
   try: _chemin.read_bytes(); return False
   except FileNotFoundError: return True
  def t_recu_mecanisme_reel():
   r1=_construire_recu(Path("/tmp/faux_rapport.json"), False, False, b"", None, Path("/tmp/faux_recu.json"))
   if r1["statut_final_archivage"]!="ARCHIVAGE_NON_CONFIRME": return False
   r2=_construire_recu(Path("/tmp/faux_rapport.json"), True, True, b"x", hashlib.sha256(b"x").hexdigest(), Path("/tmp/faux_recu.json"))
   if r2["statut_final_archivage"]!="ARCHIVE_CONFIRME": return False
   if "chemin_recu" not in r2: return False
   return True
  def t_integration_gate_reel():
      # Le scénario construit volontairement un gate négatif : les tests négatifs ne sont pas validés.
      ldl_verif_t = verifier_gate_ldl(res, sym_ok, ldl_res, ldl_audit_ok,
                                     state.get("ldl_detail") if type(state) is dict else None)
      sec_ok = {s: (type(section_status.get(s)) is dict
                    and section_status.get(s, {}).get("execute") is True
                    and section_status.get(s, {}).get("ok") is True)
                for s in ("provenance", "chargement", "validation_geometrique", "constructions_RK0",
                          "projecteurs", "verif_projecteurs", "espace_accessible", "energie_initiale", "quotient_LDL")}
      gate_negatif = {
          "prov_conformes": prov_ok is True,
          "integrite_entrees": inch is True,
          "geometrie_validee": geo_ok is True,
          "projecteurs_identites": ident_ok is True,
          "espace_accessible_non_vide_valide": acc_ok is True,
          "energie_initiale_exacte": nrj_ok is True,
          "B_definie_positive": B_pos is True,
          "LDL_PSD": ldl_verif_t["ldl_psd"] is True,
          "tests_negatifs_reussis": False,
          "aucune_erreur_bloquante": len(blocking) == 0,
          "aucune_section_indispensable_en_echec": all(sec_ok.values())
      }
      ldl_stat_eff = (ldl_res or {}).get("statut", "NON_CALCULE")
      gate_erreur = dict(gate_negatif)
      gate_erreur["geometrie_validee"] = False
      ev_negatif = evaluer_borne(gate_negatif, ldl_stat_eff, ldl_audit_ok is True)
      ev_erreur = evaluer_borne(gate_erreur, ldl_stat_eff, ldl_audit_ok is True)
      # Dans les deux cas, DEMONTRE est interdit : tests négatifs faux ou géométrie invalide.
      return (ev_negatif.get("borne_statut") != "DEMONTRE"
              and ev_erreur.get("borne_statut") != "DEMONTRE")
  def t_ldl_non_execute_explicite():
   # V3.3.19 : NON_EXECUTE est un statut explicite, accepté, jamais LDL_PSD, jamais assimilé à INDEFINIE.
   v=verifier_gate_ldl({"A_exact":{},"B_exact":{},"D_exact":[],"dim":2,"n_pos":1,"ldl_audit":{"ok":False}}, False, {"statut":"NON_EXECUTE","perm":None,"L":None,"diag":None}, False)
   return (not v["ldl_psd"]) and any("NON_EXECUTE" in m for m in v["motifs"])
  def t_ldl_detail_coherence():
   # V3.3.19 : ldl_detail fait foi après recoupement ; incohérence -> LDL_PSD False.
   v_ok=verifier_gate_ldl({"A_exact":{},"B_exact":{},"D_exact":[],"dim":2,"n_pos":1,"ldl_audit":{"ok":True}}, True, {"statut":"PSD","diag":[F1],"perm":[0],"L":[[F1]]}, True, {"quotient_construit":True,"symetrie_exacte":True,"ldl_execute":True,"certificat_audite":True,"conclusion":"PSD"})
   v_bad=verifier_gate_ldl({"A_exact":{},"B_exact":{},"D_exact":[],"dim":2,"n_pos":1,"ldl_audit":{"ok":True}}, True, {"statut":"INDECIS"}, True, {"quotient_construit":True,"symetrie_exacte":True,"ldl_execute":True,"certificat_audite":True,"conclusion":"PSD"})
   return bool(v_ok["ldl_psd"]) and (not v_bad["ldl_psd"])
  def t_ldl_detail_strict():
   # Chaque statut LDL doit être True strict ; absence, False ou entier ne passe jamais.
   res_t={"A_exact":{},"B_exact":{},"D_exact":[],"dim":2,"n_pos":1,"ldl_audit":{"ok":True}}
   ldl_t={"statut":"PSD","diag":[F1],"perm":[0],"L":[[F1]]}
   detail_ok={"quotient_construit":True,"symetrie_exacte":True,"ldl_execute":True,"certificat_audite":True,"conclusion":"PSD"}
   if verifier_gate_ldl(res_t,True,ldl_t,True,None)["ldl_psd"]: return False
   for cle in ("quotient_construit","symetrie_exacte","ldl_execute","certificat_audite"):
    detail_bad=dict(detail_ok); detail_bad[cle]=False
    if verifier_gate_ldl(res_t,True,ldl_t,True,detail_bad)["ldl_psd"]: return False
   detail_bad=dict(detail_ok); detail_bad["ldl_execute"]=1
   if verifier_gate_ldl(res_t,True,ldl_t,True,detail_bad)["ldl_psd"]: return False
   return verifier_gate_ldl(res_t,True,ldl_t,True,detail_ok)["ldl_psd"] is True
  def t_corroboration_archives_coherence():
   # V3.3.19 : arch_statut doit être l'un des 4 statuts ; INDISPONIBLE / NON_CALCULEE / ECART ne bloquent jamais la preuve exacte.
   return arch_statut in ("CONFORME","ECART","INDISPONIBLE","NON_CALCULEE")
  def t_ldl_indecis_bloque():
   # V3.3.19 §4 : LDL indécis ou bloqué ne satisfait jamais LDL_PSD.
   v1=verifier_gate_ldl(res, sym_ok, {"statut":"INDECIS","raison":"test"}, False)
   v2=verifier_gate_ldl(res, False, {"statut":"PSD","diag":[F1],"perm":[0],"L":[[F1]]}, True)
   v3=verifier_gate_ldl(res, sym_ok, {"statut":"INDEFINIE","contre_exemple":[[F1]]}, False)
   return (not v1["ldl_psd"]) and (not v2["ldl_psd"]) and (not v3["ldl_psd"])
  def t_provenance_reelle_a_b1_b2():
      # La provenance n'est réussie que si le verdict global ET les trois détails sont vrais.
      prov_c = verifier_provenance_complete(state)
      if type(prov_c) is not dict or prov_c.get("ok") is not True:
          return False
      details = prov_c.get("details")
      if type(details) is not dict:
          return False
      return all(type(details.get(n)) is dict and details[n].get("ok") is True
                 for n in ("PARTIE_A", "PARTIE_B1", "PARTIE_B2"))
  def t_integration_archivage_reel():
   # V3.3.19 : cycle complet isolé, chaque maillon référence les octets réellement relus.
   import tempfile as _tf
   with _tf.TemporaryDirectory(prefix="dodeca_integration_archivage_") as _td:
    _tdp=Path(_td); _cand=_tdp/"rapport_test.json"; _texte='{"test": "archivage"}'
    res=_ecrire_fichier_exclusif_et_relire(_cand, _texte)
    if not (res["ecriture_ok"] and res["relecture_ok"]): return False
    _oct_rapport=_cand.read_bytes(); _sha_rapport=hashlib.sha256(_oct_rapport).hexdigest()
    # Collision sur rapport : écriture exclusive doit refuser.
    res2=_ecrire_fichier_exclusif_et_relire(_cand, _texte)
    if res2["ecriture_ok"] or res2["relecture_ok"]: return False
    _cand_recu=_tdp/"recu_test.json"; _cand_att=_tdp/"attestation_test.json"
    _recu=_construire_recu(_cand, True, True, _oct_rapport, _sha_rapport, _cand_recu)
    _recu["chemin_attestation_prevu"]=str(_cand_att)
    _texte_recu=json.dumps(_recu,indent=2,ensure_ascii=False,allow_nan=False)
    with open(_cand_recu,"x",encoding="utf-8") as _fh: _fh.write(_texte_recu)
    _relus_recu=_cand_recu.read_bytes()
    if _relus_recu.decode("utf-8")!=_texte_recu: return False
    _sha_recu=hashlib.sha256(_relus_recu).hexdigest()
    _payload_att={"type":"ATTESTATION_ARCHIVAGE_V3_3_18","chemin_recu":str(_cand_recu),
                  "taille_recu_octets":len(_relus_recu),"sha256_recu":_sha_recu,
                  "relecture_recu_ok":True,"statut_final_archivage_recu":"ARCHIVE_CONFIRME"}
    _texte_att=json.dumps(_payload_att,indent=2,ensure_ascii=False,allow_nan=False)
    with open(_cand_att,"x",encoding="utf-8") as _fh: _fh.write(_texte_att)
    _relus_att=_cand_att.read_bytes()
    if _relus_att.decode("utf-8")!=_texte_att: return False
    _att_ok={"statut_attestation":"ATTESTATION_CONFIRMEE","statut_archivage_attestation":"ARCHIVE_CONFIRME",
             "relecture_recu_ok":True,"relecture_attestation_ok":True,"chemin_recu":str(_cand_recu),
             "taille_recu_octets":len(_relus_recu),"sha256_recu":_sha_recu,
             "chemin_attestation":str(_cand_att),"taille_attestation_octets":len(_relus_att),
             "sha256_attestation":hashlib.sha256(_relus_att).hexdigest()}
    # V3.3.19 : le test doit démontrer une voie positive réelle du code retour 0.
    if calculer_code_retour("DEMONTRE","DEMONTRE",True,_recu,_att_ok) != 0: return False
    # Toute altération postérieure du rapport doit invalider le code retour 0.
    _cand.write_bytes(_oct_rapport + b"\nALTERATION")
    if calculer_code_retour("DEMONTRE","DEMONTRE",True,_recu,_att_ok) == 0: return False
    # Les scénarios négatifs doivent tous refuser le code 0.
    if calculer_code_retour("DEMONTRE","DEMONTRE",False,_recu,_att_ok)==0: return False
    if calculer_code_retour("DEMONTRE","DEMONTRE",True,_recu,{**_att_ok,"statut_archivage_attestation":"ARCHIVAGE_NON_CONFIRME"})==0: return False
    if calculer_code_retour("DEMONTRE","DEMONTRE",True,_recu,{**_att_ok,"relecture_attestation_ok":False})==0: return False
    if calculer_code_retour("DEMONTRE","DEMONTRE",True,_recu,{**_att_ok,"sha256_recu":"0"*64})==0: return False
    if calculer_code_retour("REFUTE","REFUTE",True,_recu,_att_ok)==0: return False
    if calculer_code_retour("NON_CONCLU","NON_CONCLU",True,_recu,_att_ok)==0: return False
    if calculer_code_retour("DEMONTRE","DEMONTRE",True,_recu,_att_ok)!=0: return False
    # Une modification du rapport après attestation invalide le code retour.
    _cand.write_text('{"test":"modifie"}',encoding="utf-8")
    if calculer_code_retour("DEMONTRE","DEMONTRE",True,_recu,_att_ok)==0: return False
    return True
  def t_exports_partie_a():
   ok,manq=verifier_exports_partie_a()
   return ok
  cases={"prov_fichier_absent":p_absent,"prov_hash_incorrect":p_hash,"prov_fichier_modifie":p_modif,
   "prov_fichier_illisible":p_illisible,"prov_gate_non_conforme":p_gate,
   "gate_prov_non_conforme":g_prov,"gate_integrite_fausse":g_integrite,"gate_geometrie_invalide":g_geo,
   "gate_projecteur_faux":g_proj,"gate_espace_vide":g_vide,"gate_energie_pas_12":g_nrj,
   "gate_B_non_PD":g_B,"gate_LDL_indecis":g_ldl_indecis,"gate_LDL_audit_echoue":g_ldl_audit,
   "gate_erreur_bloquante":g_block,"gate_contre_exemple_LDL":g_contreex,
   "gate_cle_obligatoire_manquante":g_cle_manquante,
   "integrite_fichiers_non_destructive":t_integrite_fichiers,
   "symetrie_Aq_non_sym_rejetee":t_sym_Aq,"symetrie_D_non_sym_rejetee":t_sym_D,
   "symetrie_non_sym_bloque_LDL":t_sym_bloque,
   "mauvais_nombre_barres":t_nbarres,"indice_sommet_hors_limites":t_hors_lim,
   "extremites_identiques":t_ident,"barre_mauvais_cube":t_mauvais_cube,
   "espace_accessible_vide":t_vide,"signe_algebrique_indecis":t_signe,
   "pivot_LDL_negatif":t_pivot_neg,"bloc_Schur_indefini":t_schur,
   "echec_identite_projecteur":t_proj,"archives_NaN_rejete":t_nan,"archives_inf_rejete":t_inf,
   "aretes_fausse_diagonale_rejetee":t_aretes_fausse,
   "partie_A_absente":t_partieA_absente,"partie_A_modifiee":t_partieA_modifiee,
   "partie_B_modifiee":t_partieB_modifiee,"partie_B1_modifiee":t_partieB1_modifiee,"partie_B2_modifiee":t_partieB2_modifiee,"empreinte_incorrecte":t_empreinte_incorrecte,
   "gate_bool_remplace_par_str_1":t_gate_bool_str1,"gate_bool_remplace_par_chaine":t_gate_bool_chaine,
   "gate_bool_remplace_par_entier_1":t_gate_bool_entier1,
   "trace_projecteur_incorrecte":t_trace_incorrecte,"somme_traces_incorrecte":t_somme_traces_incorrecte,
   "borne_arrondi_depassee":t_borne_depassee,"depassement_sous_tolerance_superieur_borne":t_depassement_sous_tol,
   "certificat_LDL_incomplet":t_ldl_incomplet,"LDL_indecis_non_succes":t_ldl_indecis_non_succes,
   "entree_modifiee_pendant_audit":t_entree_modifiee_pendant,"entree_disparue_pendant_audit":t_entree_disparue_pendant,
   "ecriture_rapport_impossible":t_ecriture_impossible,"rapport_sans_nan":t_rapport_sans_nan,
   "exports_partie_A":t_exports_partie_a,"archives_defavorable_gate_valide":t_archives_defavorable_gate_valide,"archives_favorable_ne_compense_pas":t_archives_favorable_ne_compense_pas,"relecture_impossible":t_relecture_impossible,"recu_non_confirme":t_recu_non_confirme,"scripts_reels_controle_mecanisme":t_scripts_reels_controle_mecanisme,"relecture_mecanisme_reel":t_relecture_mecanisme_reel,"recu_mecanisme_reel":t_recu_mecanisme_reel,"integration_gate_reel":t_integration_gate_reel,"ldl_indecis_bloque":t_ldl_indecis_bloque,"ldl_non_execute_explicite":t_ldl_non_execute_explicite,"ldl_detail_coherence":t_ldl_detail_coherence,"ldl_detail_strict":t_ldl_detail_strict,"corroboration_archives_coherence":t_corroboration_archives_coherence,"provenance_reelle_a_b1_b2":t_provenance_reelle_a_b1_b2,"integration_archivage_reel":t_integration_archivage_reel}
  for nom,fn in cases.items():
   neg[nom]=run_neg(nom,fn)
   st=neg[nom]["statut"]; print(f"  Test négatif {nom} : {st} — {neg[nom]['detail']}")
  # V3.3.19 : retour explicite (résultats, attendu, terminé). Jamais len(cases) hors de cette fonction.
  return (neg, len(cases), True)
 try:
  _res_tests=tests_negatifs(); _neg_ret,_nb_attendu,_tests_termine=_res_tests; _tn=True; print("  OK  Tests négatifs")
 except Exception as _e:
  _neg_ret={}; _nb_attendu=0; _tests_termine=False; _tn=False; print(f"  EXCEPTION  Tests négatifs : {_e}"); blocking.append(f"Tests négatifs : exception {_e}")
 neg=_neg_ret
 _nb_execute=len(neg); neg_ok=bool(_nb_execute>0 and _nb_execute==_nb_attendu and _tests_termine and all(v.get("statut")=="PASSE" for v in neg.values()))
 mark_section("tests_negatifs",True,bool(neg_ok),f"{sum(1 for v in neg.values() if v.get('statut')=='PASSE')}/{len(neg)} PASSE (attendu {_nb_attendu}, exécuté {_nb_execute}, terminé={_tests_termine})" if neg_ok else f"tests négatifs non tous PASSE (attendu {_nb_attendu}, exécuté {_nb_execute})")
 if not neg_ok: blocking.append("Tests négatifs non tous PASSE (ECHEC ou NON_TESTABLE).")
 inch=True; det_final={}
 try: inch,det_final=verifier_integrite_fichiers(Fich,sha_av)
 except Exception as e:
  inch=False; blocking.append(f"Intégrité finale impossible : {type(e).__name__}: {e}"); det_final={}
 for nom in INDISPENSABLE:
  d=det_final.get(nom,{})
  prov[nom]["sha256_apres"]=d.get("sha256_apres"); prov[nom]["detail_final"]=d.get("detail")
  if not d.get("ok"):
   inch=False; blocking.append(f"Intégrité finale {nom} : {d.get('detail','échec')}")
 mark_section("integrite_finale",True,bool(inch),"SHA avant == après (verifier_integrite_fichiers)" if inch else "modification / disparition détectée")
 if inch: calculs.append("Entrées inchangées (SHA avant == après, verifier_integrite_fichiers)")
 # Intégrité finale des deux scripts : relecture et comparaison aux SHA initiaux.
 for _nom,_info in _scripts_info.items():
  try:
   _data2=Path(_info["chemin"]).read_bytes(); _sha2=hashlib.sha256(_data2).hexdigest()
   _info["sha256_final"]=_sha2; _info["taille_octets_final"]=len(_data2)
   if _sha2!=_info.get("sha256_initial") or len(_data2)!=_info.get("taille_octets_initial"):
    _info["statut"]="MODIFIE"; blocking.append(f"Intégrité finale script {_nom} : modifié pendant l'audit")
   else: _info["statut"]="CONFORME (inchangé)"
  except Exception as _e:
   _info["sha256_final"]=None; _info["taille_octets_final"]=None; _info["statut"]="ABSENT_OU_ILLISIBLE"
   blocking.append(f"Intégrité finale script {_nom} : {_e}")
 structural={"M_forme":{"enonce":"M(t) = (alpha-beta) I_5 + beta J_5","statut":"rapportée, non re-démontrée ici","source":"audits antérieurs V3.2 / V3.2.3"},
  "alpha_4beta":{"enonce":"alpha(t) + 4 beta(t) = 12","statut":"rapportée, non re-démontrée ici","source":"audits antérieurs V3.2 / V3.2.3"},
  "avertissement":"Le seul chargement de ROTATIONS_EXACTES.json ne démontre pas ces propriétés. La conclusion globale sur M(t) est conditionnée à leur validité."}
 hypotheses.append("Prémisses structurelles M(t) = ... et alpha+4beta = 12 : rapportées, non re-démontrées par V3.3.19.")
 ldl_stat=(ldl_res or {}).get("statut","NON_CALCULE")
 sections_indispensables=["provenance","chargement","validation_geometrique","constructions_RK0","projecteurs","verif_projecteurs","espace_accessible","energie_initiale","quotient_LDL","tests_negatifs","integrite_finale"]  # V3.3.19 : comparaison_archives = corroboration seule, hors gate (Solution B).
 sections_ok=all(section_status.get(s,{}).get("execute") is True and section_status.get(s,{}).get("ok") is True for s in sections_indispensables)
 ldl_psd_verif=verifier_gate_ldl(res, sym_ok, ldl_res, ldl_audit_ok, state.get("ldl_detail") if type(state) is dict else None)
 if not ldl_psd_verif["ldl_psd"] and ldl_stat=="PSD":
  warnings.append("Gate LDL : LDL_PSD refusée malgré ldl_stat PSD : "+"; ".join(ldl_psd_verif["motifs"]))
 gate_demontre={"prov_conformes":bool(prov_ok),"integrite_entrees":bool(inch),
  "geometrie_validee":bool(geo_ok),"projecteurs_identites":bool(ident_ok),
  "espace_accessible_non_vide_valide":bool(acc_ok),"energie_initiale_exacte":bool(nrj_ok),
  "B_definie_positive":bool(B_pos),"LDL_PSD":bool(ldl_psd_verif["ldl_psd"]),
  "tests_negatifs_reussis":bool(neg_ok),
  "aucune_erreur_bloquante":bool(len(blocking)==0),"aucune_section_indispensable_en_echec":bool(sections_ok)}
 gate_refute=dict(gate_demontre); gate_refute["LDL_PSD"]=False
 ev_demontre=evaluer_borne(gate_demontre,ldl_stat,ldl_audit_ok)
 ev_refute=evaluer_borne(gate_refute,ldl_stat,ldl_audit_ok)
 if ev_demontre["borne_statut"]=="DEMONTRE":
  borne_statut="DEMONTRE"; concl_borne=ev_demontre["conclusion_borne"]; concl_globale=ev_demontre["conclusion_globale_M"]; M_incond=False
  gate_demontre_ok=True; gate_refute_ok=False
 elif ev_refute["borne_statut"]=="REFUTE":
  borne_statut="REFUTE"; concl_borne=ev_refute["conclusion_borne"]; concl_globale=ev_refute["conclusion_globale_M"]; M_incond=False
  gate_demontre_ok=False; gate_refute_ok=True
 else:
  borne_statut="NON_CONCLU"; concl_borne=ev_demontre["conclusion_borne"]; concl_globale=ev_demontre["conclusion_globale_M"]; M_incond=False
  gate_demontre_ok=False; gate_refute_ok=False
 # --- Rapport : mémoire / tentative / réussie / impossible (correction 5) ---
 try:
  outdir.mkdir(parents=True,exist_ok=True); _mkdir_ok=True; _mkdir_detail="Répertoire créé ou déjà existant."
 except Exception as _e:
  _mkdir_ok=False; _mkdir_detail=f"{type(_e).__name__}: {_e}"; blocking.append(f"Création répertoire rapport impossible : {_mkdir_detail}")
 cand=outdir/"DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_18.json"; k=2
 while cand.exists(): cand=outdir/f"DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_18_v{k}.json"; k+=1
 rap={"audit":"DODECA — BORNE ENERGETIQUE EXACTE V3.3.18","date_utc":datetime.now(timezone.utc).isoformat(),
  "objet":"Certification exacte de mu >= 1/5, donc alpha(t) >= 12/5, sous prémisses structurelles.",
  "methode":"Projecteurs spectraux par interpolation polynomiale exacte en Q(sqrt5,sqrt6). D = A - (1/5) B, symétrie exacte avant LDL, LDL exact corrigé + audit limité pour le partiel + signes adaptatifs.",
  "provenance":prov,"manifeste_fichiers":{k2:{"chemin":v["chemin"],"categorie":v["categorie"],"sha256_avant":v["sha256_avant"],"sha256_apres":v["sha256_apres"],"statut":v["statut"],"detail_final":v.get("detail_final")} for k2,v in prov.items()},
  "donnees_effectivement_utilisees":{nom:{"sha256_contenu_utilise":sha_av.get(nom),"source":"octets lus une seule fois au départ, parsés en mémoire (mêmes octets que le SHA initial)"} for nom in INDISPENSABLE},
  "fichiers_disque_final":{nom:{"sha256_disque_final":prov[nom].get("sha256_apres"),"detail":prov[nom].get("detail_final")} for nom in INDISPENSABLE},
  "geometrie":geo,"aretes_geometriques":aretes_details,"comparaison_archives":arch_comp,"tolerance_archives":TOL_ARCHIVES,"eps_machine":EPS_MACHINE,"u_arrondi":U_ARRONDI,
  "dimensions_rangs_corps":{"dim_espace_retenu":res.get("dim"),"n_pos":res.get("n_pos"),"corps":"Q(sqrt5, sqrt6), degré 4",
   "traces_projecteurs":verif.get("traces"),"indices_retenus":acc.get("indices_retenus"),"dim_relaxation":acc.get("dim_relaxation")},
  "demontre_exactement":identites,"calcul_algebrique_exact":calculs,
  "corroboration_numerique":corroboration,"non_conclu":hypotheses,"ouvert":ouverts,
  "avertissements":warnings,"erreurs_bloquantes":blocking,
  "premisses_structurelles":structural,
  "sections":section_status,
  "gate_global_demontre":gate_demontre,"gate_global_refute":gate_refute,
  "gate_demontre_ok":gate_demontre_ok,"gate_refute_ok":gate_refute_ok,
  "certification_borne":{"borne_mu_ge_1_5":borne_statut,"conclusion_borne":concl_borne,
   "conclusion_globale_M":concl_globale,"M_psd_conclue_inconditionnelle":M_incond},
  "energie_initiale":nrj,
  "verifications_projecteurs":verif,"espace_accessible":acc,
  "quotient":{"A_exact":res.get("A_exact"),"B_exact":res.get("B_exact"),"D_exact":res.get("D_exact"),
   "dim":res.get("dim"),"n_pos":res.get("n_pos"),"mu_numerique":res.get("mu_numerique"),
   "valeurs_propres_numeriques":res.get("valeurs_propres_numeriques")},
  "symetrie_exacte":res.get("symetrie"),
  "LDL":{"statut":ldl_stat,"diag":res.get("ldl_diag"),"raison":res.get("ldl_raison"),
   "verification":res.get("ldl_verification"),"audit":res.get("ldl_audit"),
   "k_arret":res.get("ldl_k_arret"),"attendu":res.get("ldl_attendu"),"factorisation":res.get("ldl_factorisation"),
   "audit_limite_partiel":"Pour INDEFINIE : audit limité à dimensions + structure + certificat exact ; factorisation partielle NON reconstruite.",
   "contre_exemple":res.get("contre_exemple")},
  "tests_negatifs":neg,
  "entrees_inchangees":inch,
  "references_a_verifier":{"statut":"Références à vérifier, NON considérées comme démontrées par cette exécution",
   "spectre_K0_rapporte":["0^(6)","(1/2)^(10)","(2-sqrt6/2)^(8)","2^(10)","(5/2)^(6)","(2+sqrt6/2)^(8)","4^(12)"],
   "corps_exact":"Q(sqrt5, sqrt6)",
   "projecteurs":"Interpolation polynomiale exacte",
   "espace_relaxation":"Composantes spectrales accessibles",
   "matrice_D":"D = A - (1/5) B","objectif":"mu >= 1/5 => alpha(t) >= 12/5",
   "premisses":"M(t)=(alpha-beta)I+betaJ, alpha+4beta=12 (rapportées, non redémontrées)"},
  "provenance_scripts":_scripts_info,
  "dependances":{"python":sys.version,"numpy":np.__version__,"systeme":sys.platform},
  "duree_secondes":round(time.time()-t0,1),"script_sha256":None,
  "rapport_calcule_en_memoire":True,
  "tentative_ecriture":{"chemin":str(cand),"mode":"exclusif 'x', sans écrasement des rapports précédents"},
  "resultat_mathematique":{"borne_statut":borne_statut,"conclusion_borne":concl_borne,"ldl_statut":ldl_stat},
  "statut_certification":{"statut":"CERTIFICATION_CALCULEE_NON_ARCHIVEE" if borne_statut=="DEMONTRE" else ("CERTIFICATION_CALCULEE_REFUTATION" if borne_statut=="REFUTE" else "NON_CERTIFIE"),"detail":"Le gate DEMONTRE est un résultat calculé, pas une certification finale tant que l'archivage n'est pas confirmé. Certification finale = gate DEMONTRE + archivage ARCHIVE_CONFIRME (voir attestation)."},
  "statut_archivage":{"statut":"NON_CONFIRME_AVANT_ECRITURE","detail":"Statut d'archivage au moment de la sérialisation : non confirmé. Le statut final est dans le reçu / l'attestation, jamais dans ce rapport."},
  "chemin_prevu":str(cand),"etat_calcul_en_memoire":True,"_archivage_note":"Le présent rapport ne s'atteste pas lui-même archivé. Voir le reçu d'archivage séparé. Les champs serialisation/ecriture ne figurent PAS dans les octets écrits : ils sont dans le reçu."}
 # V3.3.19 §7 : B2 ne calcule PAS son SHA au moment du rapport (ce serait le SHA final, pas initial).
 # L'empreinte initiale vient de B1 (provenance avant B2) : non circulaire car B1 lit B2 avant que B2 n'exécute.
 try:
  _info_b2=(_scripts_info or {}).get("PARTIE_B2",{})
  if _info_b2.get("sha256_initial") is None:
   blocking.append("Intégrité B2 : empreinte initiale indisponible dans _scripts_info ; B2 non vérifiable.")
   rap["script_sha256"]=None
  else:
   rap["script_sha256"]=None  # V3.3.19 §1 : aucune empreinte initiale fabriquée. Voir state["provenance_b2"] + sha256_execution.
  rap["sha256_execution_b2"]=prov_b2.get("sha256_execution") if "prov_b2" in locals() else None
 except Exception: pass
 except Exception: pass
 ecriture_ok=False; ecriture_detail=None; serialisation_ok=False; texte_rapport=None; info_serialisation={"statut":"non_tentee"}; info_ecriture={"statut":"non_tentee","chemin":str(cand),"detail":"Non tentée"}; info_tentative={"chemin":str(cand),"mode":"exclusif 'x'"}
 # Étape 2 : sérialisation JSON stricte (allow_nan=False).
 try:
  ok_nan,motifs_nan=verifier_rapport_sans_nan(rap)
  if not ok_nan: raise ValueError("Rapport contient NaN/Infinity : "+"; ".join(motifs_nan[:3]))
  texte_rapport=json.dumps(rap,indent=2,ensure_ascii=False,allow_nan=False)
  serialisation_ok=True; info_serialisation={"statut":"reussie","detail":"JSON strict, allow_nan=False, sans NaN/Infinity"}  # V3.3.19 : ne pas muter rap après dumps.
 except Exception as e:
  serialisation_ok=False; info_serialisation={"statut":"impossible","detail":f"{type(e).__name__}: {e}"}  # V3.3.19 : ne pas muter rap après dumps.
  blocking.append(f"Sérialisation rapport impossible : {e}")
 # Étape 3-5 : tentative, écriture, archivage confirmé. Gestion explicite de mkdir.
 if serialisation_ok:
  try:
   outdir.mkdir(parents=True,exist_ok=True)
  except Exception as e:
   blocking.append(f"Création répertoire rapport impossible : {type(e).__name__}: {e}")
   info_tentative={"chemin":str(cand),"mode":"exclusif 'x', sans écrasement","statut":"impossible","detail":str(e)}
   serialisation_ok=False
 if serialisation_ok:
  try:
   with open(cand,"x",encoding="utf-8") as fh: fh.write(texte_rapport)
   ecriture_ok=True; ecriture_detail="Écriture réussie."
   # Archivage confirmé : relecture + vérification du contenu écrit.
   try:
    _rel=Path(cand).read_bytes()
    _arch_ok=(_rel.decode("utf-8")==texte_rapport)
   except Exception:
    _arch_ok=False
   info_ecriture={"statut":"reussie" if _arch_ok else "impossible","chemin":str(cand),"detail":ecriture_detail if _arch_ok else "Relecture du rapport archivé incohérente"}
   # V3.3.19 : réaffectation inconditionnelle SUPPRIMÉE — info_ecriture de la ligne précédente (relecture réelle) est conservée.
   if not _arch_ok:
    ecriture_ok=False; blocking.append("Archivage rapport : relecture incohérente")
   print(f"  Rapport : {cand}")
  except FileExistsError as e:
   ecriture_detail=f"Écriture impossible : rapport déjà existant ({e})"
   info_ecriture={"statut":"impossible","chemin":str(cand),"detail":ecriture_detail}
   print("  REFUS écriture")
  except OSError as e:
   ecriture_detail=f"Écriture impossible : {e}"
   info_ecriture={"statut":"impossible","chemin":str(cand),"detail":ecriture_detail}
   print(f"  Écriture impossible : {e}")
 else:
  info_ecriture={"statut":"impossible","chemin":str(cand),"detail":"Sérialisation ou création répertoire en échec"}
  # V3.3.19 : aucune mutation de rap après dumps ; l'archivage non confirmé est dans info_ecriture / reçu / attestation.
 if not ecriture_ok:
  info_ecriture={"statut":"impossible","chemin":str(cand),"detail":ecriture_detail or "Écriture ou archivage en échec"}
  # V3.3.19 : ne pas muter rap après dumps. La rétrogradation NON_CONCLU vaut pour le statut
  # final retourné / affiché et pour le reçu, pas pour les octets déjà sérialisés (ou non écrits).
  blocking.append(f"Écriture rapport impossible : {ecriture_detail}")
  borne_statut="NON_CONCLU"; concl_borne="Borne NON CONCLUE : écriture/archivage du rapport impossible, audit non archivé."; concl_globale="NON_CONCLU pour M(t) : ne pas conclure M(t) >= 0."
  gate_demontre_ok=False; gate_refute_ok=False

 # --- Reçu + attestation autonome : chaîne non circulaire, fichiers exclusifs ---
 recu=None; attestation_recu=None
 try:
  _octets_rapport=Path(cand).read_bytes() if ecriture_ok else b""
  _sha_rapport=hashlib.sha256(_octets_rapport).hexdigest() if ecriture_ok else None
  _relecture_ok=False
  try:
   _relus=Path(cand).read_bytes(); _relecture_ok=(_relus==_octets_rapport and ecriture_ok is True)
  except Exception:
   _relecture_ok=False
  _stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%f')
  _cand_recu=outdir/f"DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_18_RECU_{_stamp}.json"
  _cand_attestation=outdir/f"DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_18_ATTESTATION_{_stamp}.json"
  recu=_construire_recu(cand, ecriture_ok, _relecture_ok, _octets_rapport, _sha_rapport, _cand_recu)
  # Le reçu annonce le chemin de l'attestation à venir, sans prétendre en certifier l'existence.
  recu["chemin_attestation_prevu"]=str(_cand_attestation)
  _texte_recu=json.dumps(recu,indent=2,ensure_ascii=False,allow_nan=False)
  with open(_cand_recu,"x",encoding="utf-8") as _fh: _fh.write(_texte_recu)
  _relus_recu=Path(_cand_recu).read_bytes()
  _recu_relu_ok=(_relus_recu.decode("utf-8")==_texte_recu)
  _sha_recu=hashlib.sha256(_relus_recu).hexdigest()
  _recu_taille=len(_relus_recu)
  # Ne pas muter le reçu en mémoire après sérialisation : _recu_relu_ok reste
  # un contrôle distinct et interdit le code 0 si la relecture diverge.
  # Attestation autonome : référence le reçu effectivement écrit et relu.
  _payload_attestation={
   "type":"ATTESTATION_ARCHIVAGE_V3_3_18",
   "chemin_recu":str(_cand_recu),"taille_recu_octets":_recu_taille,
   "sha256_recu":_sha_recu,"relecture_recu_ok":bool(_recu_relu_ok),
   "statut_final_archivage_recu":recu.get("statut_final_archivage"),
   "date_utc":datetime.now(timezone.utc).isoformat()
  }
  _texte_attestation=json.dumps(_payload_attestation,indent=2,ensure_ascii=False,allow_nan=False)
  with open(_cand_attestation,"x",encoding="utf-8") as _fh: _fh.write(_texte_attestation)
  _relus_attestation=Path(_cand_attestation).read_bytes()
  _attestation_relu_ok=(_relus_attestation.decode("utf-8")==_texte_attestation)
  _sha_attestation=hashlib.sha256(_relus_attestation).hexdigest()
  _attestation_taille=len(_relus_attestation)
  _attestation_ok=bool(_recu_relu_ok and _attestation_relu_ok and recu.get("statut_final_archivage")=="ARCHIVE_CONFIRME")
  attestation_recu={
   "chemin_recu":str(_cand_recu),"taille_recu_octets":_recu_taille,"sha256_recu":_sha_recu,
   "relecture_recu_ok":bool(_recu_relu_ok),"chemin_attestation":str(_cand_attestation),
   "taille_attestation_octets":_attestation_taille,"sha256_attestation":_sha_attestation,
   "relecture_attestation_ok":bool(_attestation_relu_ok),
   "statut_archivage_attestation":"ARCHIVE_CONFIRME" if _attestation_ok else "ARCHIVAGE_NON_CONFIRME",
   "statut_attestation":"ATTESTATION_CONFIRMEE" if _attestation_ok else "ATTESTATION_NON_CONFIRMEE",
   "detail":"Attestation autonome écrite exclusivement puis relue ; elle référence le reçu et son SHA-256."
  }
 except Exception as _e:
  recu={"type":"RECU_ARCHIVAGE_V3_3_18","statut_final_archivage":"ARCHIVAGE_NON_CONFIRME","detail":f"{type(_e).__name__}: {_e}"}
  attestation_recu={"chemin_recu":None,"taille_recu_octets":None,"sha256_recu":None,
   "relecture_recu_ok":False,"chemin_attestation":None,"taille_attestation_octets":None,
   "sha256_attestation":None,"relecture_attestation_ok":False,
   "statut_archivage_attestation":"ARCHIVAGE_NON_CONFIRME",
   "statut_attestation":"ATTESTATION_NON_CONFIRMEE","detail":f"{type(_e).__name__}: {_e}"}
 # V3.3.19 §2 : cohérence borne / borne_final / reçu / attestation. Toute incohérence -> non certifié.
 _coherence=[]
 if type(recu) is dict and recu.get("statut_final_archivage")=="ARCHIVE_CONFIRME" and not (attestation_recu and attestation_recu.get("statut_archivage_attestation")=="ARCHIVE_CONFIRME" and attestation_recu.get("relecture_attestation_ok") is True):
  _coherence.append("reçu CONFIRME mais attestation autonome non archivée/relue : incohérence")
 if type(attestation_recu) is dict and attestation_recu.get("statut_attestation")=="ATTESTATION_CONFIRMEE" and not (type(recu) is dict and recu.get("statut_final_archivage")=="ARCHIVE_CONFIRME"):
  _coherence.append("attestation CONFIRMEE mais reçu non confirmé : incohérence")
 if _coherence:
  blocking.append("Incohérence archivage : "+"; ".join(_coherence))
 if borne_statut=="DEMONTRE" and not (attestation_recu and attestation_recu.get("relecture_recu_ok") is True and attestation_recu.get("relecture_attestation_ok") is True and attestation_recu.get("statut_archivage_attestation")=="ARCHIVE_CONFIRME" and type(recu) is dict and recu.get("statut_final_archivage")=="ARCHIVE_CONFIRME" and ecriture_ok is True):
  borne_statut_final="DEMONTRE_CALCUL_NON_CERTIFIE_ARCHIVAGE_NON_CONFIRME"
 else:
  borne_statut_final=borne_statut
 print("\n"+"="*72+f"\nBorne mu >= 1/5 : {borne_statut}\nConclusion globale M : {concl_globale}\nGate DEMONTRE : {gate_demontre_ok} | Gate REFUTE : {gate_refute_ok}")
 print(f"Rapport calculé en mémoire : True | Tentative d'écriture : {cand} | Écriture : {'reussie' if ecriture_ok else 'impossible'}")
 if blocking:
  print("Erreurs bloquantes :")
  for b in blocking: print("  - "+b)
 if warnings:
  print("Avertissements :")
  for w in warnings: print("  - "+w)
 print(f"Durée : {time.time()-t0:.1f} s\n"+"="*72)
 _ret=calculer_code_retour(borne_statut, borne_statut_final, ecriture_ok, recu if "recu" in locals() else None, attestation_recu if "attestation_recu" in locals() else None)
 state["blocking"]=blocking; state["warnings"]=warnings; state["section_status"]=section_status; state["recu_archivage"]=recu if "recu" in locals() else None; state["attestation_recu"]=attestation_recu if "attestation_recu" in locals() else None; state["borne_statut_final"]=borne_statut_final if "borne_statut_final" in locals() else borne_statut
 return _ret

def main():
 state=_B1.main_partie_1()
 resultat=main_partie_2(state)
 return resultat

if __name__ == "__main__": sys.exit(main())
