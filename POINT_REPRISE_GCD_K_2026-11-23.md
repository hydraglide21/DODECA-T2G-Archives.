# DODECA T2g — point de reprise sur le PGCD dans le corps K

Date : 23 novembre 2026

## Objet

Résoudre le blocage d'identification de la valeur propre commune `lambda_star` pour les polynômes exacts `F_red(lambda,r)` et `G(lambda,r)`, avec `H(r)=0`, `deg(H)=39`.

## Sources vérifiées dans cette session

- `RESULTANT_SCHUR_T2G_V10_EXACT.txt`
  - SHA-256 : `9f0be9c7e0f1ab226efae0c98fdc64ab5dfa443cb57322d48b03f856ec4e70dc`
- `AUDIT_T2G_UNICITE_MOD227.py`
  - SHA-256 : `06040fdc9df99736df2cb2241e9aad2c906391a758f71ce65da9d1ebec83ddc1`
- `RAPPORT_AUDIT_T2G_UNICITE_MOD227.json`
  - SHA-256 après réexécution : `d7bb358c548131711cdff74521d9b3a195f45b18b216642d4cdb0090653711a1`

## Reproduction effectuée

Le script V13 `AUDIT_T2G_UNICITE_MOD227.py` a été réexécuté sur le fichier V10 présent. Il vérifie :

1. identité exacte `RESULTANT = c * H**3`, avec `c != 0` ;
2. `T(beta)=D**39 H(beta/D)` monique entier de degré 39 ;
3. irréductibilité de `T mod 227` ;
4. PGCD de `F` et `G` de degré 1 dans `F_227[beta]/(T)` ;
5. annulation des deux polynômes sur la racine modulaire calculée.

Conséquence : `H` est irréductible sur Q ; dans `K=Q[r]/(H)`, le résultant nul donne un PGCD de degré au moins 1, et la bonne réduction modulo 227 de degré 1 borne le degré exact par 1. Le PGCD exact dans `K[lambda]` est donc de degré exactement 1.

La racine exacte existe et est unique dans K. Ses 39 coefficients rationnels dans la base puissance de `beta` ne sont pas encore reconstruits.

## Diagnostic du faux candidat sous-résultant

Deux calculs ont été distingués :

- sous-résultant dans le corps de fonctions `Q(r)[lambda]` ;
- PGCD après passage au corps de nombres `K[lambda]`, où `H(r)=0`.

Le sous-résultant générique de degré 1 dans `Q(r)[lambda]`, même calculé avec le domaine correct `QQ.frac_field(r)`, ne se réduit pas à la racine modulaire V13 de p=227. Ce n'est pas un contre-exemple au résultat V13 : le PGCD recherché apparaît après spécialisation par `H`; le sous-résultant générique de `Q(r)` n'est pas le PGCD dans `K`.

Résultat de comparaison modulo 227 :
- candidat issu du sous-résultant générique : SHA-256 de son vecteur résiduel `ef04387aae45df0e7b6a84f15fd17b0b9396ce7422c99af2352aa0974c9fe672` ;
- racine modulaire V13 archivée : SHA-256 `87cc9eae8d5ebb7827559baf90cbf0517aa0e768b8995d652e063a465ceb7366` ;
- égalité : FAUX.

Le candidat générique doit donc être écarté pour l'identification de `lambda_star` dans K.

## Tentative exacte directe

Une arithmétique exacte explicite dans `Q[r]/(H)` a été essayée avec réduction des coefficients modulo H et inversion par Euclide polynomial. Le premier reste a été calculé ; le deuxième calcul a subi une explosion de taille/coût et n'a pas abouti dans le temps disponible. Aucun résultat de cette tentative n'est revendiqué.

## État scientifique

- **Démontré / reproduit ici** : identité exacte du résultant ; irréductibilité de H par bonne réduction ; PGCD exact de degré 1 dans K, par l'argument résultant + réduction modulaire ; existence et unicité de `lambda_star` dans K.
- **Vérifié modulo 227** : vecteur de `lambda_star` en base `1,beta,...,beta^38` et annulation de F,G.
- **Réfuté comme candidat** : formule issue du sous-résultant générique sur Q(r).
- **Ouvert** : expression exacte des 39 coefficients rationnels de `lambda_star` ; calcul exact du vecteur noyau 13 composantes ; raccord exact aux matrices réduites.
- **Non reproduit ici** : ancien CRT du noyau sur 12 primes et son échec aux deux primes holdout. Ne pas réutiliser les fractions rejetées.

## Prochaine étape

Calculer le PGCD dans `K[lambda]` directement, sans passer par le sous-résultant générique de `Q(r)`. Voie recommandée : calcul modulaire du PGCD dans `F_p[beta]/(T)` sur une famille de primes, CRT coefficient par coefficient pour les 39 coefficients de `lambda_star`, reconstruction rationnelle avec bornes explicites, puis validation sur des primes holdout indépendantes avant toute utilisation du noyau 13x13.
