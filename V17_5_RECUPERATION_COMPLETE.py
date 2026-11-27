#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V17_5_RECUPERATION_COMPLETE.py

Récupération sûre des six fichiers V17.5 depuis une archive ZIP SOURCE.

IMPORTANT :
- Ce script ne contient pas les octets originaux V17.5 : ils ne peuvent pas
  être reconstruits à partir des seules empreintes SHA-256.
- Il faut lui fournir l'archive ZIP originale contenant les six fichiers.
- Il vérifie l'archive, les noms, les tailles et les SHA-256 AVANT toute écriture.
- Il n'écrase aucun fichier existant.
- Il écrit les six fichiers dans un nouveau sous-dossier et produit un journal.

Usage :
    python V17_5_RECUPERATION_COMPLETE.py chemin/vers/archive_V17_5.zip

Python 3.9+
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import zipfile
from pathlib import Path, PurePosixPath

ATTENDUS = {
    "V17_5_SCRIPT.py": {
        "sha256": "24bd11260ed1f0b96cf71d02763e542f6cf44f8736aa5c4ffc8b646bc31cfec2",
        "size": 20715,
    },
    "V17_5_THEOREME_NON_CONFINEMENT.txt": {
        "sha256": "2e03f3989c54893fdf0c8b7dce371629f823d1a992f380945816dc1b3a3577d5",
        "size": 4702,
    },
    "V17_5_CERTIFICAT_MINEUR.txt": {
        "sha256": "67025da155d06da43c00f722a7097ce696d3a6c16b54e7edb9254c2ef1909933",
        "size": 2508,
    },
    "V17_5_RAPPORT.json": {
        "sha256": "3a843bb6c44a9a7e369ced727cb1432433836af2725057e3381c882e956f13d0",
        "size": 9774,
    },
    "V17_5_JOURNAL.txt": {
        "sha256": "1d849e09ef8c3239f61bfcb9aed107cffae928685937aa1689912bd324c403af",
        "size": 2357,
    },
    "V17_5_MANIFESTE_SHA256.json": {
        "sha256": "daba764729e69a125025fc1c45c059c84c269724f243b684c28c6dd419894437",
        "size": None,  # Taille non communiquée ; SHA-256 obligatoire.
    },
}

NOM_JOURNAL = "V17_5_RECUPERATION_JOURNAL.txt"


class RecuperationError(Exception):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verifier_archive(zip_path: Path):
    if not zip_path.is_file():
        raise RecuperationError(f"Archive introuvable : {zip_path}")

    rapports = []
    contenus = {}

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            # Vérification CRC de tous les membres de l'archive.
            mauvais_membre = zf.testzip()
            if mauvais_membre is not None:
                raise RecuperationError(
                    f"CRC ZIP invalide pour le membre : {mauvais_membre}"
                )

            infos = zf.infolist()
            noms = [info.filename for info in infos]

            if len(noms) != len(set(noms)):
                raise RecuperationError("L'archive contient des noms de membres dupliqués.")

            attendus = set(ATTENDUS)
            presents = set(noms)

            if presents != attendus:
                manquants = sorted(attendus - presents)
                inattendus = sorted(presents - attendus)
                raise RecuperationError(
                    "Liste des membres incorrecte. "
                    f"Manquants={manquants}; inattendus={inattendus}"
                )

            for info in infos:
                nom = info.filename
                chemin = PurePosixPath(nom)

                # Seuls les six noms simples à la racine sont admis.
                if (
                    chemin.is_absolute()
                    or len(chemin.parts) != 1
                    or ".." in chemin.parts
                    or "\\" in nom
                    or info.is_dir()
                ):
                    raise RecuperationError(f"Chemin ZIP dangereux ou inattendu : {nom!r}")

                donnees = zf.read(info)
                spec = ATTENDUS[nom]
                taille = len(donnees)
                empreinte = sha256(donnees)

                if spec["size"] is not None and taille != spec["size"]:
                    raise RecuperationError(
                        f"Taille incorrecte pour {nom}: {taille}, "
                        f"attendu {spec['size']} octets."
                    )

                if empreinte != spec["sha256"]:
                    raise RecuperationError(
                        f"SHA-256 incorrect pour {nom}: {empreinte}, "
                        f"attendu {spec['sha256']}."
                    )

                contenus[nom] = donnees
                rapports.append(
                    f"OK | {nom} | {taille} octets | SHA-256 {empreinte}"
                )

    except zipfile.BadZipFile as exc:
        raise RecuperationError(f"Archive ZIP invalide : {exc}") from exc

    return contenus, rapports


def ecrire_sans_ecrasement(destination: Path, contenus: dict, rapports: list):
    destination.mkdir(parents=True, exist_ok=False)

    # Les données ont toutes été vérifiées avant d'arriver ici.
    ecrits = []
    try:
        for nom in sorted(ATTENDUS):
            cible = destination / nom
            if cible.exists():
                raise RecuperationError(f"Refus d'écraser un fichier existant : {cible}")
            with cible.open("xb") as f:
                f.write(contenus[nom])
            ecrits.append(cible)

        texte = [
            "JOURNAL DE RÉCUPÉRATION V17.5",
            "Statut : SUCCÈS — six fichiers vérifiés avant écriture.",
            "",
            *rapports,
            "",
            "Contrôles :",
            "- Archive ZIP lisible : OK",
            "- CRC des membres : OK",
            "- Noms exacts et uniques : OK",
            "- Chemins dangereux : aucun",
            "- Tailles connues : OK",
            "- Six SHA-256 : OK",
            "- Écrasement de fichiers : aucun",
        ]
        journal = destination / NOM_JOURNAL
        with journal.open("x", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(texte) + "\n")
    except Exception:
        # Retire uniquement les fichiers créés par cette exécution.
        for chemin in reversed(ecrits):
            try:
                chemin.unlink()
            except OSError:
                pass
        try:
            destination.rmdir()
        except OSError:
            pass
        raise


def main():
    if len(sys.argv) != 2:
        print(
            "Usage : python V17_5_RECUPERATION_COMPLETE.py archive_V17_5.zip",
            file=sys.stderr,
        )
        return 2

    archive = Path(sys.argv[1]).expanduser().resolve()
    parent = archive.parent
    destination = parent / "V17_5_RECUPERATION_VERIFIEE"

    if destination.exists():
        print(
            f"ARRÊT : le dossier de destination existe déjà : {destination}\n"
            "Aucun fichier n'a été modifié. Renommez ou déplacez ce dossier "
            "avant de relancer.",
            file=sys.stderr,
        )
        return 2

    try:
        contenus, rapports = verifier_archive(archive)
        ecrire_sans_ecrasement(destination, contenus, rapports)
    except Exception as exc:
        print(f"ÉCHEC — aucune extraction effectuée : {exc}", file=sys.stderr)
        return 1

    print("RÉCUPÉRATION RÉUSSIE")
    print(f"Dossier : {destination}")
    print(f"Journal : {destination / NOM_JOURNAL}")
    for ligne in rapports:
        print(ligne)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
