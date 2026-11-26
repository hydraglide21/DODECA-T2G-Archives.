# Addendum R3 — chronologie B2 et raccord statique du contrat d'état
Date : 21 novembre 2026

## 1. Corpus historique récupéré
Les sources B2 V3.3.13, V3.3.14, V3.3.15, V3.3.16, V3.3.17 et V3.3.18 ont été matérialisées depuis la Bibliothèque et analysées statiquement. Les six passent `ast.parse`. Aucune n'a été exécutée.

Empreintes des copies examinées :
- `DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_13_PARTIE_B2.py` — 67,185 octets — SHA-256 `812a20f840215df480a5e6cc73412bd59ee7408ce2d022f7a8edd3ce583c377c` — syntaxe AST : OK
- `DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_14_PARTIE_B2.py` — 68,490 octets — SHA-256 `d7148be54b051df6bdae0cd2de583558cd9410252934ab759141a618a79a49ec` — syntaxe AST : OK
- `DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_15_PARTIE_B2.py` — 71,118 octets — SHA-256 `9e4e2a77e3a1794657632176657414bda970f233bfdfc9e55a8174cc2c459da0` — syntaxe AST : OK
- `DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_16_PARTIE_B2.py` — 72,918 octets — SHA-256 `163db4d972de8a5543275b2ce262278e7a2fa5c39daaf8660a13ce74c6753de8` — syntaxe AST : OK
- `DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_17_PARTIE_B2.py` — 73,315 octets — SHA-256 `4c9ebd5b9a382121089ebcc1b616bf117ebab16c407809ea0028745d75fe79eb` — syntaxe AST : OK
- `DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_18_PARTIE_B2.py` — 73,318 octets — SHA-256 `e0b561dd41ebfaeb3a546b14d7d8f7e7b0ae7e53d4a5e8bd827aa24cb8a91683` — syntaxe AST : OK

## 2. Évolution de la dépendance B1
- B2 V3.3.13 à V3.3.17 importent et verrouillent B1 V3.3.13.
- B2 V3.3.18 importe et verrouille B1 V3.3.19.
- B2 V3.3.18 verrouille également son propre nom/version V3.3.18.

Le diff V3.3.17 → V3.3.18 montre explicitement la bascule de dépendance B1 V3.3.13 vers B1 V3.3.19, ainsi que les mises à jour des identifiants/version de chaîne, de l'attestation d'archivage et des commentaires associés. Il ne faut donc pas traiter V3.3.18 comme un simple changement cosmétique de numéro.

## 3. Raccord du schéma `state` : B1 candidat R2 face au contrat B2 V3.3.18
La revue statique du constructeur d'état de B1 R2 et de `valider_contrat_state` dans B2 V3.3.18 donne les constats suivants :
- B1 R2 construit explicitement les champs de base exigés par le contrat B2 (`base`, `outdir`, `prov`, `Fich`, `sha_av`, `section_status`, `_scripts_info`, `res`, `ldl_res`, `blocking`, `warnings`, etc.).
- B1 R2 ajoute aussi les champs de diagnostic que B2 V3.3.18 sait contrôler : `ldl_detail`, `corroboration_archives`, `arch_statut`, `provenance_detail`, `contrat_state`.
- `ldl_detail` produit par B1 R2 contient les cinq champs attendus : `quotient_construit`, `symetrie_exacte`, `ldl_execute`, `certificat_audite`, `conclusion`. Les quatre premiers sont booléens stricts par construction dans `_classifier_ldl`.
- B2 V3.3.18 vérifie également les neuf sections de `section_status`; B1 R2 crée ces sections (certaines peuvent être marquées non exécutées si un blocage amont survient, ce qui est un état de rapport et non une absence de clé).

**Conclusion limitée :** le schéma d'état B1 R2 paraît structurellement aligné sur le contrat explicite de B2 V3.3.18. Cela ne prouve ni l'exécution correcte, ni la compatibilité complète avec B2 V3.3.19, qui reste la cible réelle de B1 R2.

## 4. Verrou de provenance : incompatibilité toujours certaine
Même si le schéma `state` est proche, B2 V3.3.18 exige le chemin et le module B1 V3.3.19, et son propre nom B2 V3.3.18. B1 R2 annonce B1 V3.3.20 et le fichier B2 V3.3.19. La paire ne peut donc pas être certifiée par B2 V3.3.18. Aucun renommage ne doit être utilisé pour contourner ces gardes.

## 5. B2 V3.3.19
Une recherche de titre exact dans la Bibliothèque n'a pas retourné la source `DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_19_PARTIE_B2.py`. Le corpus B2 récupéré ici s'arrête à V3.3.18. L'absence dans cette recherche ne prouve pas l'inexistence d'une copie dans toute archive externe ; elle signifie que la source n'est pas actuellement disponible pour audit.

## 6. Empreinte du candidat B1 R2
- `DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_20_PARTIE_B1_CANDIDAT_R2.py` — 40,473 octets — SHA-256 `631eb6b20ffc8377a926a35b0fa29ef2987ba52586617f597e3ecb24f61374c0` — syntaxe AST : OK

## 7. Décision
1. Conserver B1 R2 comme candidat corrigé statiquement, non exécuté.
2. Ne pas l'associer à B2 V3.3.18.
3. La compatibilité structurelle apparente avec le contrat B2 V3.3.18 est une information utile, mais elle ne remplace pas l'audit de B2 V3.3.19.
4. La prochaine pièce nécessaire reste la source originale B2 V3.3.19 ; ensuite seulement, terminer le diff du contrat et préparer une éventuelle validation dynamique, soumise à autorisation.
5. La conclusion mathématique antérieure `mu = 0` n'est pas modifiée par cet audit logiciel.

**Périmètre :** analyse de sources, hashes et AST uniquement. Aucun script projet exécuté ; aucune preuve mathématique recalculée ; aucune source originale modifiée.
