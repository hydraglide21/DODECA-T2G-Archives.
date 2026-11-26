#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V16.2 — Audit de raccord lambda : V15C4 / V9 CRT / témoins indépendants.

But :
- relire les polynômes exacts H, S10 et S11 déjà archivés ;
- vérifier lambda = -S10/S11 modulo H pour les 4 premiers V15C4 ;
- convertir correctement la base r vers beta avec beta = D*r, D = lc(H) ;
- raccorder les vecteurs V15C4 aux résidus CRT V9 et au témoin 227 ;
- contrôler les 20 anciennes fractions V9 sur les 250 premiers CRT et
  sur les témoins indépendants 227, 4057 et 4211.

Ce script NE collecte aucun nouveau premier et NE déclare jamais une
fraction rationnelle exacte sur la seule base du CRT.
Dépendance : SymPy.
Tous les fichiers d'entrée doivent être dans le même dossier que ce script.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parent

FILES = {
    "resultant": ROOT / "RESULTANT_SCHUR_T2G_V10_EXACT.txt",
    "s10": ROOT / "S10_reduit_num.txt",
    "s11": ROOT / "S11_reduit_num.txt",
    "v15": ROOT / "V15C4_MODULAR_LAMBDA.json",
    "crt": ROOT / "V9_CRT_RESIDUES_001.json",
    "rr": ROOT / "V9_RATIONAL_RECONSTRUCTION_001.json",
    "v6": ROOT / "RAPPORT_RECONSTRUCTION_CRT_LAMBDA_V6.json",
}

r = sp.symbols("r")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def require_files() -> None:
    missing = [str(p.name) for p in FILES.values() if not p.is_file()]
    if missing:
        raise FileNotFoundError(
            "Fichiers manquants dans le dossier du script : " + ", ".join(missing)
        )


def read_assignment(path: Path, key: str) -> str:
    prefix = key + "="
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line.split("=", 1)[1].strip()
    raise ValueError(f"Ligne {key}= absente de {path.name}")


def mod_poly(poly: sp.Poly, p: int) -> sp.Poly:
    """Réduit un polynôme rationnel modulo p, sans conversion flottante."""
    expr = 0
    for (i,), coeff in poly.terms():
        coeff = sp.Rational(coeff)
        den = int(coeff.q) % p
        if den == 0:
            raise ZeroDivisionError(
                f"Dénominateur de coefficient divisible par p={p}"
            )
        c = (int(coeff.p) % p) * pow(den, -1, p) % p
        expr += c * r**i
    return sp.Poly(expr, r, modulus=p)


def poly_from_coefficients(coefficients, p: int) -> sp.Poly:
    if len(coefficients) != 39:
        raise ValueError(f"Vecteur lambda de longueur {len(coefficients)}, attendu 39")
    expr = sum((int(c) % p) * r**i for i, c in enumerate(coefficients))
    return sp.Poly(expr, r, modulus=p)


def mod_int(value: int, p: int) -> int:
    return int(value) % int(p)


def load_exact_polynomials():
    resultant_text = FILES["resultant"].read_text(encoding="utf-8")
    h_expr = read_assignment(FILES["resultant"], "H")
    H = sp.Poly(sp.sympify(h_expr, locals={"r": r}), r, domain=sp.QQ)
    S10 = sp.Poly(
        sp.sympify(FILES["s10"].read_text(encoding="utf-8"), locals={"r": r}),
        r, domain=sp.QQ
    )
    S11 = sp.Poly(
        sp.sympify(FILES["s11"].read_text(encoding="utf-8"), locals={"r": r}),
        r, domain=sp.QQ
    )

    if H.degree() != 39:
        raise AssertionError(f"deg(H)={H.degree()}, attendu 39")
    if S10.degree() != 38 or S11.degree() != 38:
        raise AssertionError(
            f"Degrés inattendus : deg(S10)={S10.degree()}, deg(S11)={S11.degree()}"
        )
    if any(c.q != 1 for c in H.all_coeffs() + S10.all_coeffs() + S11.all_coeffs()):
        raise AssertionError("Un coefficient exact n'est pas entier.")

    # D est le coefficient dominant de H : beta = D*r.
    Dq = H.LC()
    if Dq.q != 1 or int(Dq) == 0:
        raise AssertionError("Le coefficient dominant D de H n'est pas un entier non nul.")
    D = int(Dq)

    # Vérification exacte de l'inversibilité de S11 modulo H.
    gcd_poly = sp.gcd(S11, H)
    if gcd_poly.degree() != 0:
        raise AssertionError(
            f"S11 n'est pas inversible modulo H : degré du PGCD = {gcd_poly.degree()}"
        )

    return H, S10, S11, D, gcd_poly


def main() -> None:
    require_files()

    H, S10, S11, D, gcd_poly = load_exact_polynomials()

    v15 = json.loads(FILES["v15"].read_text(encoding="utf-8"))
    crt = json.loads(FILES["crt"].read_text(encoding="utf-8"))
    rr = json.loads(FILES["rr"].read_text(encoding="utf-8"))
    v6 = json.loads(FILES["v6"].read_text(encoding="utf-8"))

    if v15.get("status") != "PASS_MODULAR_LAMBDA_VECTORS":
        raise AssertionError("Statut V15C4 inattendu.")
    if crt.get("number_of_coordinates") != 39:
        raise AssertionError("Le CRT V9 ne contient pas 39 coordonnées.")
    if crt.get("number_of_primes") != len(crt.get("collection_primes", [])):
        raise AssertionError("Nombre de premiers incohérent dans V9.")
    if len(crt.get("residues_beta_power_basis", [])) != 39:
        raise AssertionError("Le vecteur CRT V9 n'a pas 39 coordonnées.")

    primes = [int(p) for p in crt["collection_primes"]]
    if len(set(primes)) != len(primes):
        raise AssertionError("Doublons dans la liste des premiers CRT.")
    M = math.prod(primes)
    if M != int(crt["crt_modulus"]):
        raise AssertionError("Le module CRT n'est pas le produit des 250 premiers.")

    crt_beta = [int(x) for x in crt["residues_beta_power_basis"]]
    v6_by_prime = {int(x["p"]): x for x in v6["modular_results"]}

    modular_checks = []
    for entry in v15["results"]:
        p = int(entry["p"])
        Hp = mod_poly(H, p)
        s10p = mod_poly(S10, p)
        s11p = mod_poly(S11, p)
        lamp = poly_from_coefficients(entry["lambda_coefficients_r0_to_r38"], p)

        if Hp.degree() != 39:
            raise AssertionError(f"p={p}: degré de H réduit incorrect.")
        if sp.gcd(s11p, Hp).degree() != 0:
            raise AssertionError(f"p={p}: S11 non inversible modulo H.")
        identity = (s11p * lamp + s10p).rem(Hp)
        if not identity.is_zero:
            raise AssertionError(f"p={p}: S11*lambda + S10 n'est pas nul modulo H.")

        # beta = D*r, donc le coefficient de beta^i est a_i / D^i.
        Dinv = pow(D % p, -1, p)
        beta_vector = [
            int(c) * pow(Dinv, i, p) % p
            for i, c in enumerate(entry["lambda_coefficients_r0_to_r38"])
        ]

        if p == 227:
            witness = v6_by_prime.get(p)
            if witness is None:
                raise AssertionError("Témoin V6 p=227 absent.")
            expected = [int(x) % p for x in witness["root_beta_power_basis"]]
            comparison = "V6_holdout_227"
        elif p in primes:
            expected = [x % p for x in crt_beta]
            comparison = "V9_CRT"
        else:
            expected = None
            comparison = "identity_only"

        mismatches = []
        if expected is not None:
            mismatches = [
                i for i, (x, y) in enumerate(zip(beta_vector, expected)) if x != y
            ]
            if mismatches:
                raise AssertionError(
                    f"p={p}: désaccord base beta aux coordonnées {mismatches[:8]}"
                )

        modular_checks.append({
            "prime": p,
            "identity_S11_lambda_plus_S10_mod_H": "PASS",
            "basis_conversion_beta_equals_D_times_r": "PASS",
            "comparison": comparison,
            "coordinate_mismatches": len(mismatches),
        })

    # Contrôle des anciennes fractions V9 sur le CRT complet et sur les témoins.
    rr_results = rr.get("results", [])
    reconstructed = [x for x in rr_results if x.get("status") == "RECONSTRUCTED"]
    holdout_primes = (227, 4057, 4211)
    holdout_vectors = {}
    for p in holdout_primes:
        item = v6_by_prime.get(p)
        if item is None:
            raise AssertionError(f"Témoin indépendant p={p} absent du rapport V6.")
        holdout_vectors[p] = [int(x) for x in item["root_beta_power_basis"]]

    fraction_checks = []
    for item in reconstructed:
        i = int(item["coordinate"])
        num = int(item["numerator"])
        den = int(item["denominator"])
        if not (0 <= i < 39) or den <= 0:
            raise AssertionError(f"Fraction V9 mal formée à la coordonnée {i}.")
        if math.gcd(num, den) != 1:
            raise AssertionError(f"Fraction V9 non réduite à la coordonnée {i}.")

        crt_bad = []
        crt_tested = 0
        for p in primes:
            if den % p == 0:
                continue
            crt_tested += 1
            if (num - crt_beta[i] * den) % p != 0:
                crt_bad.append(p)
        if crt_bad:
            raise AssertionError(
                f"Fraction V9 coordonnée {i}: ne concorde pas avec le CRT "
                f"(premiers {crt_bad[:5]})."
            )

        holdouts = {}
        for p in holdout_primes:
            if den % p == 0:
                holdouts[str(p)] = "NON_TESTABLE_DENOMINATOR_DIVISIBLE"
            else:
                residue = holdout_vectors[p][i] % p
                holdouts[str(p)] = (
                    "PASS" if (num - residue * den) % p == 0 else "FAIL"
                )

        fraction_checks.append({
            "coordinate": i,
            "matches_all_available_CRT_primes": crt_tested == len(primes),
            "crt_primes_tested": crt_tested,
            "independent_holdouts": holdouts,
        })

    holdout_pass_count = {
        str(p): sum(
            1 for item in fraction_checks
            if item["independent_holdouts"][str(p)] == "PASS"
        )
        for p in holdout_primes
    }
    holdout_fail_count = {
        str(p): sum(
            1 for item in fraction_checks
            if item["independent_holdouts"][str(p)] == "FAIL"
        )
        for p in holdout_primes
    }

    report = {
        "schema": "DODECA_T2G_V16_2_LAMBDA_RECONCILIATION_AUDIT",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "MODULAR_RACCORD_PASS__RATIONAL_RECONSTRUCTION_NOT_CERTIFIED",
        "scope": (
            "Audit des données archivées uniquement. Aucun nouveau premier collecté. "
            "Aucune fraction rationnelle déclarée exacte."
        ),
        "basis": "beta = D*r, D = leading_coefficient(H)",
        "D_digits": len(str(abs(D))),
        "exact_polynomials": {
            "degree_H": H.degree(),
            "degree_S10": S10.degree(),
            "degree_S11": S11.degree(),
            "gcd_S11_H_degree": gcd_poly.degree(),
            "S11_invertible_mod_H_over_Q": True,
        },
        "crt": {
            "prime_count": len(primes),
            "coordinate_count": len(crt_beta),
            "modulus_digits": len(str(M)),
            "product_matches_stored_modulus": True,
        },
        "v15c4_modular_checks": modular_checks,
        "v9_old_rational_candidates": {
            "reconstructed_count": len(reconstructed),
            "crt_congruence": "PASS" if all(
                x["matches_all_available_CRT_primes"] for x in fraction_checks
            ) else "FAIL",
            "holdout_pass_count": holdout_pass_count,
            "holdout_fail_count": holdout_fail_count,
            "details": fraction_checks,
        },
        "input_sha256": {
            key: sha256(path) for key, path in FILES.items()
        },
        "next_mathematical_step": (
            "Déterminer les 39 coefficients rationnels de -S10/S11 dans "
            "Q[r]/(H) par une méthode exacte ou une borne de reconstruction "
            "justifiée, puis vérifier les identités exactes. Les candidats V9 "
            "qui échouent aux témoins sont rejetés."
        ),
    }

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = ROOT / f"RAPPORT_V16_2_AUDIT_LAMBDA_{stamp}.json"
    if report_path.exists():
        raise FileExistsError(f"Refus d'écraser un rapport existant : {report_path}")
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    print("=== V16.2 — AUDIT DE RACCORDEMENT LAMBDA ===")
    print("PGCD exact(S11,H) : degré", gcd_poly.degree(), "=> PASS")
    print("Premiers CRT V9 :", len(primes), "| module :", len(str(M)), "chiffres")
    print("Contrôles V15C4 :", len(modular_checks), "=> PASS")
    print("Anciennes fractions V9 :", len(reconstructed))
    print("Échecs aux témoins :", holdout_fail_count)
    print("Rapport créé :", report_path.name)
    print("STATUT :", report["status"])


if __name__ == "__main__":
    main()
