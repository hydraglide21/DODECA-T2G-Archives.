# Clôture rectifiée du chantier V3.3.12 — 19 novembre 2026 — V2

**Décision : CLÔTURE V3.3.12 À RECTIFIER.**  
**Statut opérationnel : B1/B2 examinées statiquement, non validées ; NE PAS EXÉCUTER EN L’ÉTAT.**

Cette V2 conserve le dossier initial et intègre la contre-expertise indépendante transmise le 19 novembre 2026. Elle ne constitue ni une correction des scripts, ni une exécution, ni une validation de la borne énergétique.

## 1. Historique et périmètre

Scripts visés :
- A : `DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_7_PARTIE_A.py`
- B1 : `DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_12_PARTIE_B1.py`
- B2 : `DODECA_BORNE_ENERGETIQUE_EXACTE_V3_3_12_PARTIE_B2.py`

La contre-expertise Meta déclare avoir audité statiquement les scripts et annexes listés dans son rapport. Elle rapporte pour B1 490 lignes, 39 174 octets, SHA-256 `0ccfed1b8a07efbb680712f0c63de7867a7aecad90552b1cc3cadd630b3b6c57`, et pour B2 922 lignes, 67 632 octets, SHA-256 `646174f2155e1a73ef03d1f82800b9c39b3af705fafd6eb957c7d3f31248a991`. Ces empreintes sont **rapportées par Meta** ; elles ne sont pas recalculées dans cette V2.

Aucun script n'a été lancé dans cette contre-expertise. Aucun test n'a été exécuté. `py_compile` est rapporté OK par Meta pour B1 et B2, mais la compilation ne démontre pas l'exécutabilité des chemins fonctionnels. Aucun fichier source n'a été modifié.

## 2. Rectification concernant les documents de clôture initiaux

Meta rapporte que les fichiers de clôture initiaux étaient absents de son conteneur audité. Dans l'environnement de travail de cette V2, les deux fichiers initiaux ont été retrouvés, lus et leurs tailles et SHA-256 recalculés :

| Fichier initial | Taille | SHA-256 |
|---|---:|---|
| `CLOTURE_CHANTIER_V3_3_12_2026-11-19.md` | 5 728 octets | `93323e88f4d49476adaf7dceea539db8697df1fc39b4fb376c8f51d4a91dfb16` |
| `CLOTURE_CHANTIER_V3_3_12_2026-11-19.json` | 7 060 octets | `61b09696ced60a985166a34252fff52f14b61f6c0d344d0a6bd1d06260c484da` |

Conclusion limitée : les documents existent et sont vérifiables dans l'environnement de cette V2. L'absence constatée par Meta dans son propre conteneur est une différence d'environnement, non une preuve que les fichiers n'ont jamais été créés. La présente V2 ne prétend pas que Meta a pu les lire.

## 3. B1 V3.3.12 — défauts confirmés

**Statut : BLOQUANTE — NE PAS EXÉCUTER.**

1. **Construction de `state` : défaut fatal certain.** Les noms `_a`, `_geo`, `_a2`, `_proj`, `_acc`, `_nrj` sont référencés sans assignation locale correspondante dans `main_partie_1()`. Les variables réellement assignées comprennent notamment `_pr`, `_vp`, `_ac` et `_nr`, ce qui révèle des incohérences de noms. La construction de l'état peut provoquer `UnboundLocalError`.
2. **`_q` conditionnelle : défaut fatal certain sur le chemin de blocage amont.** `_q` est assignée uniquement dans une branche, mais référencée sans condition dans `state`.
3. **Contrat incompatible avec les états de blocage.** `ldl_res` et `D` peuvent valoir `None`, alors que le contrat impose des dictionnaires. Le contrôle diagnostique est donc incohérent avec les chemins d'échec prévus.
4. **Tests négatifs partiellement fictifs ou tautologiques.** Meta identifie notamment des résultats `True` codés en dur pour les archives absentes/illisibles, une comparaison de chemin avec lui-même et un test d'export sans pouvoir discriminant. Ces cas ne doivent pas être comptés comme tests réellement probants.
5. **Contrat effectif B1/B2 non établi.** Les défauts précédents empêchent de démontrer que B1 livre un état exploitable à B2.

Éléments à préserver, sans les confondre avec une validation globale : fonction `main_partie_1()` explicite ; imports explicites ; lecture unique des octets ; validation précoce des entrées ; archives numériques non bloquantes ; séparation des étapes symétrie/quotient/LDL/audit ; distinction des statuts LDL.

**Nuance de provenance :** selon la contre-expertise Meta, B1 compare ses chemins résolus aux modules chargés dans son propre contrôle de provenance. Cette qualité locale de B1 ne résout pas les défauts fatals de construction d'état et ne dispense pas B2 de recouper sa propre provenance avec les modules effectivement chargés.

## 4. B2 V3.3.12 — défauts et nuances rectifiés

**Statut : BLOQUANTE — NE PAS EXÉCUTER avec B1 V3.3.12.**

Défauts certains ou lacunes à conserver au registre :

1. **KeyError sur provenance invalide — bloquant, certain.** `verifier_provenance_complete()` renvoie la clé top-level `motifs`, mais `main_partie_2()` lit `prov_b2['motif']` (rapport Meta : lignes 190 et 193). Le chemin d'erreur peut donc échouer au moment où le diagnostic est nécessaire.
2. **Provenance B2 non recoupée avec les modules réellement chargés — majeur, certain selon Meta.** B2 compare des chaînes de chemins attendus mais ne recoupe pas complètement `_PA.__file__`, `_B1.__file__` et `__file__` avec les modules exécutés. L'ancrage externe indépendant des empreintes reste absent.
3. **Confiance transitive dans le certificat LDL — lacune conditionnelle/indirecte.** B2 ne refait pas indépendamment la reconstruction LDL et les contrôles associés ; elle se fie à un indicateur venant de A/B1. Meta précise que l'audit LDL de A vérifie reconstruction, signes et contre-exemple pour le statut `INDEFINIE`. Il s'agit donc d'une insuffisance de recoupement dans B2, pas d'une absence totale de vérification dans toute la chaîne.
4. **Faux succès du test de provenance — majeur, certain.** Un chemin de test retourne `True` lorsque `prov_c['ok']` est faux dès lors que `details` existe. Un diagnostic présent ne doit pas être confondu avec une provenance conforme.
5. **Test d'intégration de la gate inversé/contradictoire — majeur, certain.** Le test force `tests_negatifs_reussis=False`, alors que la gate exige cette condition pour `DEMONTRE`; le test peut masquer l'incohérence en excluant cette clé de son agrégat.
6. **Test d'archivage sur données synthétiques — moyen, certain.** Le test vérifie des helpers avec des octets et objets fabriqués ; il ne prouve pas le cycle réel rapport écrit → reçu → attestation. Le renommer et le compter uniquement comme test de helpers est nécessaire.
7. **Compatibilité B1 artificielle — moyen, certain.** La comparaison porte sur des ensembles de clés constants et ne vérifie pas réellement le module B1 chargé ; le diagnostic de version est incohérent.
8. **Contrat d'état incomplet — majeur, certain.** Plusieurs objets ensuite consommés ne sont pas regroupés dans une validation exhaustive unique préalable aux calculs.
9. **Classification absence/indécision/réfutation — nuance importante.** La contre-expertise ne confirme pas une confusion générale dans le code effectivement lu : B1 et B2 distinguent les statuts d'absence et d'indécision, et une réfutation passe par un contre-exemple vérifié. Le défaut résiduel est surtout la confiance transitive dans le résultat LDL et l'incohérence de vocabulaire entre composants. Ne pas maintenir comme fait établi une accusation générale « LDL absent = REFUTE ».
10. **Chaîne rapport/reçu/attestation — moyen, certain.** Les liens entre empreintes, chemins, tailles et artefacts ne sont pas établis de bout en bout ; l'attestation n'est pas persistée comme artefact autonome.
11. **Diagnostic de provenance incomplet — majeur, certain.** Le chemin d'échec peut s'arrêter sans rapport structuré persistant ; le défaut `motif`/`motifs` aggrave cette perte de diagnostic.

Éléments à préserver : `main_partie_2(state)` explicite ; séparation conceptuelle rapport/reçu/attestation ; JSON strict ; écritures exclusives et relectures ; archives numériques hors gate de preuve exacte.

## 5. État mathématique — formulation prudente obligatoire

### 5.1 Résultats rapportés et conditions

- \(K_0=R^TR\) est la définition du modèle mécanique construit ; cela implique \(K_0\succeq0\). Cela ne constitue pas, à lui seul, une preuve du spectre annoncé.
- La covariance correcte rapportée est **non signée** : \(RS_g=P_{\tau_g}R\) sur les 60 rotations. La covariance signée \(RS_g=P_gR\) est rapportée fausse sur 59 rotations sur 60 ; elle ne doit pas être réintroduite.
- L'invariance de \(K_0\), le transport des trajectoires par unicité de l'EDO, l'équivariance de l'attribution énergétique et la 2-transitivité sur les cinq cubes sont des prémisses structurelles rapportées dans le dossier historique, mais **non redémontrées par la contre-expertise des scripts A/B1/B2**.
- En conséquence, la forme \(M(t)=(\alpha-\beta)I+\beta J\) est **conditionnelle à ces prémisses**, et non démontrée par la seule clôture V3.3.12.
- La relation \(\alpha(t)+4\beta(t)=12\) est conditionnelle à la conservation de l'énergie totale \(H=12\) et à l'identité de partition énergétique.
- Le spectre exact de \(K_0\) ne doit pas être annoncé comme démontré sur la seule base d'une reconnaissance numérique des valeurs propres.

### 5.2 Identité de partition énergétique

L'identité doit être écrite explicitement avec le signe égal :

\[
\sum_{c=1}^{5}E_c(q,\dot q)
=\frac12\|\dot q\|^2+\frac12\|Rq\|^2.
\]

Avec
\[
E_c(q,\dot q)=
\frac14\sum_{v\in C_c}\|\dot q_v\|^2+
\frac12\sum_{b\in B_c}(Rq)_b^2,
\]
elle découle exactement du comptage si chaque sommet appartient à exactement deux cubes et chaque barre est attribuée à exactement un cube. La contre-expertise rapporte une corroboration numérique, mais ne fournit pas dans son audit un certificat exact autonome de ces incidences. Statut de clôture : **identité combinatoire exacte sous les incidences énoncées ; certificat exact indépendant à joindre pour une validation formelle complète**.

### 5.3 Algèbre de la matrice M

Sous les prémisses précédentes, si
\[
M(t)=(\alpha-\beta)I+\beta J,\qquad \alpha+4\beta=12,
\]
alors les valeurs propres de \(M\) sont \(12\) (multiplicité 1) et \(\alpha-\beta\) (multiplicité 4), d'où
\[
M(t)\succeq0
\iff \alpha-\beta\geq0
\iff \alpha\geq\frac{12}{5}.
\]
Cette implication algébrique est exacte, mais sa conclusion sur le système demeure conditionnelle aux prémisses qui donnent la forme de \(M\) et la conservation/partition.

## 6. Borne énergétique \(\mu\)

**Statut explicite : \(\mu\geq1/5\) — NON DÉMONTRÉE, NON RÉFUTÉE, NON EXÉCUTÉE.**

La chaîne
\[
\mu\geq\frac15
\Longrightarrow \alpha(t)\geq\frac{12}{5}
\Longrightarrow M(t)\succeq0
\]
est une implication **conditionnellement valide**, pas une démonstration achevée.

La première implication exige notamment que toute la trajectoire considérée appartienne à l'espace \(S\) sur lequel la borne \(\mu\) est établie, et que \(\alpha(t)=E_1/H\) le long de cette trajectoire. L'appartenance de la condition initiale précise à \(S\) n'est pas établie dans les éléments audités par Meta. La seconde implication exige la forme de \(M\) et la relation \(\alpha+4\beta=12\), elles-mêmes conditionnelles aux prémisses structurelles.

Aucun résultat d'exécution V3.3.12 n'existe. Les défauts fatals de B1 empêchent même le retour normal de l'état attendu. L'absence de certificat n'est **pas** une réfutation.

## 7. Décision et reprise

- Décision : **CLÔTURE V3.3.12 À RECTIFIER**.
- B1 et B2 : **revues statiquement, non validées ; ne pas exécuter en l'état**.
- Aucun test négatif ou test d'intégration ne doit être présenté comme exécuté ou passé.
- Aucun script n'est corrigé dans cette V2 ; aucune V3.3.13 n'est créée.
- Préserver A V3.3.7, B1/B2 V3.3.12, les rapports, annexes, manifestes et versions antérieures.
- Une correction ponctuelle de B1/B2 ne sera entreprise que sur demande explicite ; elle devra conserver les calculs exacts, éviter une réécriture inutile et être auditée statiquement avant toute exécution autorisée.

## 8. Limites de cette V2

Cette V2 est une rectification documentaire fondée sur :
1. les revues statiques antérieures consignées dans l'historique de travail ;
2. le rapport de contre-expertise Meta transmis par l'utilisateur ;
3. la vérification locale de l'existence, de la taille, du contenu et des SHA-256 des deux documents de clôture initiaux.

Les scripts sources B1/B2 n'ont pas été relancés ni re-hachés pour cette V2. Les empreintes de sources indiquées en section 1 sont celles rapportées par Meta, non recalculées ici. La lecture des documents de clôture initiaux ne vaut pas relecture des scripts sources.

---
*Fin de la clôture rectifiée V3.3.12 — V2.*
