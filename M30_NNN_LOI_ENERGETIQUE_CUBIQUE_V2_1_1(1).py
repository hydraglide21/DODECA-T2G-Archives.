#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M30_NNN_LOI_ENERGETIQUE_CUBIQUE_V2_1_1.py

Contre-expertise statique et algébrique de V2.1.
Ne modifie aucun script antérieur.

Corrections V2.1.1 :
  1. Substitution simultanée xreplace pour les transformations de q.
  2. Test effectif de l'indépendance d'orientation, sans condition toujours vraie.
  3. Extraction des coefficients APRÈS réduction modulo
     cxh^2+sxh^2=1, ..., s5^2=5 ; le rang est certifié par un
     mineur exact non nul dans Q(sqrt(5)), et non par Matrix.rank()
     sur des symboles formels.

Le script ne doit être exécuté qu'après accord explicite de l'utilisateur.
"""

import itertools
import sympy as sp

I = sp.I
s5 = sp.symbols("s5", real=True)
phi = (1 + s5) / 2
c = (3 - s5) / 4
k2 = -c
kc = (3 + s5) / 2
kth = (5 + s5) / 16
Bcoef = (3 * s5 - 1) / 8

# Variables de demi-angle
cxh, cyh, czh = sp.symbols("cxh cyh czh", real=True)
sxh, syh, szh = sp.symbols("sxh syh szh", real=True)
CH = [cxh, cyh, czh]
SH = [sxh, syh, szh]
ANGVARS = [cxh, sxh, cyh, syh, czh, szh]
CX = [2 * CH[i]**2 - 1 for i in range(3)]
SX = [2 * CH[i] * SH[i] for i in range(3)]
X = [1 - CX[i] for i in range(3)]

relations = [
    CH[i]**2 + SH[i]**2 - 1 for i in range(3)
] + [s5**2 - 5]
GB = sp.groebner(
    relations, cxh, sxh, cyh, syh, czh, szh, s5,
    order="lex", domain=sp.QQ
)

def red(expr):
    """Réduction exacte modulo les relations trigonométriques et s5²=5."""
    expr = sp.expand(sp.simplify(expr))
    return sp.factor(GB.reduce(expr)[1])

def check(name, condition, detail=""):
    ok = bool(condition)
    print(f"[{'OK' if ok else 'ECHEC'}] {name}" +
          (f" : {detail}" if detail else ""))
    if not ok:
        raise AssertionError(name)

def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))

def canonical(v):
    """Représentant non orienté : premier coefficient non nul positif."""
    v = tuple(int(x) for x in v)
    for x in v:
        if x:
            return v if x > 0 else tuple(-a for a in v)
    raise ValueError("Direction nulle")

def sin_half_dot(R):
    """Calcule sin(q.R/2) exactement par additions d'angles."""
    s = sp.Integer(0)
    cc = sp.Integer(1)
    for i in range(3):
        if R[i] == 1:
            si, ci = SH[i], CH[i]
        elif R[i] == -1:
            si, ci = -SH[i], CH[i]
        else:
            continue
        s_new = sp.expand(s * ci + cc * si)
        c_new = sp.expand(cc * ci - s * si)
        s, cc = s_new, c_new
    return sp.expand(s)

def phase_exp(R):
    """e^(i q.R), exprimé avec les variables de demi-angle."""
    value = sp.Integer(1)
    for i in range(3):
        if R[i] == 1:
            value *= (CH[i] + I * SH[i])**2
        elif R[i] == -1:
            value *= (CH[i] - I * SH[i])**2
    return sp.expand(value)

def red_complex(expr):
    re, im = sp.expand_complex(sp.expand(expr)).as_real_imag()
    return red(re), red(im)

def split_matrix(M):
    Mr, Mi = sp.zeros(M.rows, M.cols), sp.zeros(M.rows, M.cols)
    for i in range(M.rows):
        for j in range(M.cols):
            Mr[i, j], Mi[i, j] = red_complex(M[i, j])
    return Mr, Mi

print("=" * 76)
print("M30 — CONTRE-EXPERTISE V2.1.1")
print("Sélection exacte des trois raideurs NNN")
print("=" * 76)

# ------------------------------------------------------------------
# 1. Directions NNN, ordre V1
# ------------------------------------------------------------------
print("\n--- 1. Directions NNN : ordre V1 ---")
NNN = [
    (1, 1, 0), (1, -1, 0),
    (1, 0, 1), (1, 0, -1),
    (0, 1, 1), (0, 1, -1),
]
check("Six directions NNN distinctes",
      len(NNN) == 6 and len(set(NNN)) == 6)
INDEX = {r: i for i, r in enumerate(NNN)}

def plane_of(R):
    return next(i for i, value in enumerate(R) if value == 0)

for (i, j), label in [((0, 1), "xy"), ((2, 3), "xz"), ((4, 5), "yz")]:
    check(f"Paire {i},{j} associée au plan {label}",
          plane_of(NNN[i]) == plane_of(NNN[j])
          and NNN[i] != NNN[j])
check("Trois plans distincts",
      len({plane_of(NNN[0]), plane_of(NNN[2]), plane_of(NNN[4])}) == 3)

# ------------------------------------------------------------------
# 2. Groupe cubique O_h et représentation de permutation non orientée
# ------------------------------------------------------------------
print("\n--- 2. Groupe O_h ---")
GROUP = []
for perm in itertools.permutations(range(3)):
    for signs in itertools.product((-1, 1), repeat=3):
        Gm = sp.zeros(3)
        for i in range(3):
            Gm[i, perm[i]] = signs[i]
        GROUP.append(Gm)

check("48 matrices cubiques distinctes",
      len(GROUP) == 48 and len({tuple(g) for g in GROUP}) == 48)

def permutation_representation(Gm):
    U = sp.zeros(6)
    for j, r in enumerate(NNN):
        image = canonical(tuple(Gm * sp.Matrix(r)))
        U[INDEX[image], j] = 1
    return U

REP = [permutation_representation(g) for g in GROUP]
check("Représentation de permutation construite", len(REP) == 48)

# ------------------------------------------------------------------
# 3. Projecteurs A1g, Eg, T2g
# ------------------------------------------------------------------
print("\n--- 3. Projecteurs cubiques ---")
Ppair = sp.zeros(6)
for i, j in ((0, 1), (2, 3), (4, 5)):
    for a in (i, j):
        for b in (i, j):
            Ppair[a, b] = sp.Rational(1, 2)

one = sp.ones(6, 1)
PA = one * one.T / 6
PE = Ppair - PA
PT = sp.eye(6) - Ppair

for label, P, expected_rank in (
    ("A1g", PA, 1), ("Eg", PE, 2), ("T2g", PT, 3)
):
    check(f"P_{label} symétrique et idempotent",
          P == P.T and P * P == P)
    check(f"rang(P_{label}) = {expected_rank}",
          P.rank() == expected_rank)

check("Projecteurs orthogonaux et somme I6",
      PA + PE + PT == sp.eye(6)
      and PA * PE == sp.zeros(6)
      and PA * PT == sp.zeros(6)
      and PE * PT == sp.zeros(6))

for U in REP:
    for P in (PA, PE, PT):
        assert U * P * U.T == P
print("[OK] PA, PE, PT invariants sous les 48 éléments de O_h")

# ------------------------------------------------------------------
# 4. Couplage D centré et indépendance d'orientation
# ------------------------------------------------------------------
print("\n--- 4. Couplage D(q), convention centrée ---")
D = sp.zeros(6, 3)
for row, R in enumerate(NNN):
    sh = sin_half_dot(R)
    rhat = sp.Matrix([sp.Rational(v, 1) / sp.sqrt(2) for v in R])
    D[row, :] = (2 * I * sh) * rhat.T

# Vérification effective, six directions et trois composantes.
for R in NNN:
    Rm = tuple(-v for v in R)
    sh, shm = sin_half_dot(R), sin_half_dot(Rm)
    for k in range(3):
        lhs = red(sh * sp.Integer(R[k]))
        rhs = red(shm * sp.Integer(Rm[k]))
        check(f"Orientation indépendante pour R={R}, composante {k}",
              lhs == rhs)
print("[OK] D_R est invariant sous R -> -R.")

# ------------------------------------------------------------------
# 5. Covariance correcte du couplage sous O_h
# ------------------------------------------------------------------
print("\n--- 5. Covariance du couplage ---")

def covariance_row_permutation(Gm):
    """
    Pour D(Gq), la ligne j correspond à canonical(G^T R_j).
    Le facteur de signe de sin est compensé par celui du vecteur Rhat.
    """
    W = sp.zeros(6)
    GT = Gm.T
    for j, R in enumerate(NNN):
        image = canonical(tuple(GT * sp.Matrix(R)))
        W[j, INDEX[image]] = 1
    return W

def covariance_check(Gm):
    # (Gq)_i = sign_i * q_{perm_i}
    perm, signs = [], []
    for i in range(3):
        j = next(j for j in range(3) if Gm[i, j] != 0)
        perm.append(j)
        signs.append(int(Gm[i, j]))

    substitutions = {}
    for i in range(3):
        substitutions[CH[i]] = CH[perm[i]]
        substitutions[SH[i]] = signs[i] * SH[perm[i]]

    # xreplace garantit une substitution simultanée.
    D_Gq = D.xreplace(substitutions)
    W = covariance_row_permutation(Gm)
    residual = D_Gq - W * D * Gm.T
    return all(red(residual[i, j]) == 0
               for i in range(residual.rows)
               for j in range(residual.cols))

for idx, Gm in enumerate(GROUP):
    check(f"Covariance D(Gq)=W(G) D(q) G^T, élément {idx}",
          covariance_check(Gm))
print("[OK] Covariance vérifiée sur les 48 éléments de O_h.")

# Vérifier aussi que W est une représentation de permutation orthogonale.
for Gm in GROUP:
    W = covariance_row_permutation(Gm)
    check("W(G) orthogonale", W * W.T == sp.eye(6))
print("[OK] Matrices W(G) orthogonales.")

# ------------------------------------------------------------------
# 6. A(q) = K_NN + K_TRI
# ------------------------------------------------------------------
print("\n--- 6. Construction de A(q) ---")
NN_OR = [
    (1, 0, 0), (-1, 0, 0),
    (0, 1, 0), (0, -1, 0),
    (0, 0, 1), (0, 0, -1),
]
TRI_PAIRS = [
    (a, b) for a, b in itertools.combinations(NN_OR, 2)
    if dot(a, b) == 0
]
check("12 paires TRI orthogonales", len(TRI_PAIRS) == 12)

K_NN = sp.zeros(3)
for R in NN_OR:
    axis = next(i for i in range(3) if R[i] != 0)
    rv = sp.Matrix(R)
    K_NN += kc * X[axis] * (rv * rv.T)

K_TRI = sp.zeros(3)
for a, b in TRI_PAIRS:
    av, bv = sp.Matrix(a), sp.Matrix(b)
    g = -(av * phase_exp(b) + bv * phase_exp(a) - (av + bv))
    K_TRI += kth * (g * g.H)

K_NN = K_NN.applyfunc(red)
K_TRI = K_TRI.applyfunc(red)
A = (K_NN + K_TRI).applyfunc(red)

# ------------------------------------------------------------------
# 7. Matrice cible M_P
# ------------------------------------------------------------------
print("\n--- 7. Matrice cible M_P ---")
Ddiag = []
for i in range(3):
    j, k = (i + 1) % 3, (i + 2) % 3
    Ddiag.append(
        (kc + 2*k2) * X[i]
        + (k2 + 4*kth) * (X[j] + X[k])
        - k2 * X[i] * (X[j] + X[k])
    )

MP = sp.zeros(3)
for i in range(3):
    for j in range(3):
        MP[i, j] = Ddiag[i] if i == j else Bcoef * SX[i] * SX[j]
MP = MP.applyfunc(red)

# ------------------------------------------------------------------
# 8. Identité préalable A - 2 MP = c D†D
# ------------------------------------------------------------------
print("\n--- 8. Identité préalable ---")
DtD = (D.H * D).applyfunc(red)
pre_residual = (A - 2*MP - c*DtD).applyfunc(red)
check("A - 2 MP = c D^dagger D",
      pre_residual == sp.zeros(3))
print("[INFO] Les phases se compensent dans D†D ; cela n'est pas")
print("       supposé pour D†P_iD, recalculés ci-dessous.")

# ------------------------------------------------------------------
# 9. Matrices M_i = D† P_i D
# ------------------------------------------------------------------
print("\n--- 9. Matrices D† P_i D ---")
MA_re, MA_im = split_matrix(D.H * PA * D)
ME_re, ME_im = split_matrix(D.H * PE * D)
MT_re, MT_im = split_matrix(D.H * PT * D)
print("[OK] Parties réelles et imaginaires réduites exactement.")

# ------------------------------------------------------------------
# 10. Construction correcte du système sur Q(sqrt(5))
# ------------------------------------------------------------------
print("\n--- 10. Système linéaire sur Q(sqrt(5)) ---")
da, de, dt = sp.symbols("delta_A delta_E delta_T")
unique_rows = []

# Important : chaque coefficient trigonométrique est d'abord réduit
# modulo les relations, puis extrait comme coefficient d'un monôme
# des SIX variables trigonométriques seulement. s5 reste dans le
# corps des coefficients, et n'est PAS une variable polynomiale.
for parts in (
    (MA_re, ME_re, MT_re),
    (MA_im, ME_im, MT_im),
):
    M1, M2, M3 = parts
    for i in range(3):
        for j in range(i, 3):
            # Extraire séparément les coefficients des trois matrices :
            # aucune variable delta n'est introduite dans le polynôme
            # soumis à la réduction de Gröbner.
            polys = [
                sp.Poly(M[i, j], *ANGVARS, domain="EX")
                for M in (M1, M2, M3)
            ]
            coefficient_maps = [poly.as_dict() for poly in polys]
            monomials = sorted(
                set().union(*(set(d.keys()) for d in coefficient_maps))
            )
            for monomial in monomials:
                row = [
                    red(d.get(monomial, sp.Integer(0)))
                    for d in coefficient_maps
                ]
                if any(v != 0 for v in row) and row not in unique_rows:
                    unique_rows.append(row)

print(f"Lignes distinctes après réduction/déduplication : {len(unique_rows)}")
check("Système non vide", len(unique_rows) > 0)

# Chaque entrée doit être de la forme a + b*s5, a,b rationnels.
def in_quadratic_field(expr):
    expr = red(expr)
    p = sp.Poly(expr, s5, domain=sp.QQ)
    return p.degree() <= 1

for row in unique_rows:
    for entry in row:
        check("Coefficient dans Q(sqrt(5))", in_quadratic_field(entry))

# Mineur exact : un déterminant non nul établit directement le rang 3.
print("\n--- 11. Certificat de rang par mineur exact ---")
minor_certificate = None
for indices in itertools.combinations(range(len(unique_rows)), 3):
    minor = sp.Matrix([unique_rows[k] for k in indices])
    determinant = red(minor.det())
    if determinant != 0:
        minor_certificate = (indices, determinant)
        break

check("Existence d'un mineur 3x3 exact non nul",
      minor_certificate is not None)
indices, determinant = minor_certificate
print(f"Lignes du mineur : {indices}")
print(f"Déterminant exact réduit : {determinant}")
check("Déterminant appartient à Q(sqrt(5))",
      in_quadratic_field(determinant))

# Un mineur non nul donne rang >= 3 ; avec trois colonnes, rang = 3.
print("[OK] Rang exact = 3 (mineur non nul et trois colonnes).")
print("[OK] Noyau trivial : la seule solution est delta_A=delta_E=delta_T=0.")
print("[OK] Donc lambda_A=lambda_E=lambda_T=c.")

# ------------------------------------------------------------------
# 12. Revalidation du raccord à la solution sélectionnée
# ------------------------------------------------------------------
print("\n--- 12. Raccord exact à la solution sélectionnée ---")
Kv_solution = c * (PA + PE + PT)
check("Kv(c,c,c) = c I6", Kv_solution == c*sp.eye(6))
Keff_solution = (A - D.H * Kv_solution * D).applyfunc(red)
eff_residual = (Keff_solution - 2*MP).applyfunc(red)
check("Keff(c,c,c) = 2 MP, identité matricielle",
      eff_residual == sp.zeros(3))

# ------------------------------------------------------------------
# 13. Positivité et translations
# ------------------------------------------------------------------
print("\n--- 13. Positivité et translations ---")
check("c > 0 dans Q(sqrt(5))", 3 > 0 and 3**2 > 5)
print("Kv = c I6 est définie positive.")
print("Par complément de Schur (Kv > 0),")
print("K_complet >= 0 ssi Keff >= 0.")
print("Comme Keff = 2 MP, la positivité complète est conditionnée")
print("au certificat indépendant de positivité de MP.")

subs_q0 = {
    cxh: 1, cyh: 1, czh: 1,
    sxh: 0, syh: 0, szh: 0,
}
D0 = D.subs(subs_q0).applyfunc(sp.simplify)
A0 = A.subs(subs_q0).applyfunc(red)
check("D(0)=0", D0 == sp.zeros(6, 3))
check("A(0)=0", A0 == sp.zeros(3))

Kcomplete0 = sp.zeros(9)
Kcomplete0[:3, :3] = A0
Kcomplete0[:3, 3:] = D0.H * Kv_solution
Kcomplete0[3:, :3] = Kv_solution * D0
Kcomplete0[3:, 3:] = Kv_solution

for i in range(3):
    translation = sp.zeros(9, 1)
    translation[i, 0] = 1
    check(f"Translation {i} dans ker K_complet(0)",
          Kcomplete0 * translation == sp.zeros(9, 1))

# ------------------------------------------------------------------
# 14. Résumé
# ------------------------------------------------------------------
print("\n" + "=" * 76)
print("RÉSUMÉ V2.1.1")
print("=" * 76)
print("CONTRÔLES EXACTS :")
print("  - Ordre V1 des six directions NNN.")
print("  - Projecteurs A1g, Eg, T2g invariants sous O_h (48 éléments).")
print("  - Couplage centré et indépendance d'orientation effectivement testée.")
print("  - Covariance du couplage vérifiée sur les 48 éléments.")
print("  - A - 2 MP = c D†D.")
print("  - Système réduit dans Q(sqrt(5)) ; mineur exact non nul.")
print("  - Unicité : lambda_A=lambda_E=lambda_T=c.")
print("  - Keff(c,c,c)=2 MP.")
print("  - Trois translations dans le noyau à q=0.")
print("CONDITIONNEL :")
print("  - K_complet >= 0 dépend du certificat indépendant MP >= 0.")
print("OUVERT :")
print("  - Origine physique des variables internes.")
print("  - Origine premier principe de c et de l'égalité des raideurs.")
print("Aucun script antérieur modifié.")
print("Ce script n'a pas été exécuté par sa rédaction.")
