# Lissage de l'activité — Traitement mathématique

**Problème source :** B. Beauzamy, *Lisser l'activité*, SCM SA, avril 2026 (énoncé RATP, 2016).

---

## 1. Formalisation du problème

### 1.1 Données

- Horizon $T \in \mathbb{N}^\star$ (nombre de jours), fixé.
- Nombre de projets $K \in \mathbb{N}^\star$.
- Pour chaque projet $k \in \{1,\ldots,K\}$ : durée $d_k \in \mathbb{N}^\star$ et profil de charge
$$
P_k = (n_{k,1}, n_{k,2}, \ldots, n_{k,d_k}) \in \mathbb{N}^{d_k}.
$$

La donnée $n_{k,i}$ représente le nombre d'hommes requis le $i$-ème jour du projet $k$. Les $P_k$ et $d_k$ sont **immuables** ; seules les dates de début sont des degrés de liberté.

### 1.2 Variable de décision

Pour chaque projet $k$, on choisit une date de début
$$
s_k \in \mathcal{T}_k := \{1, 2, \ldots, T - d_k + 1\}.
$$

### 1.3 Charge journalière agrégée

$$
\boxed{\;
C_j(s_1,\ldots,s_K) \;=\; \sum_{k=1}^{K} n_{k,\, j - s_k + 1}\,\mathbf{1}_{\{s_k \le j \le s_k + d_k - 1\}},
\quad j = 1,\ldots,T.
\;}
$$

### 1.4 Invariant fondamental

$$
\sum_{j=1}^{T} C_j \;=\; \sum_{k=1}^{K} \sum_{i=1}^{d_k} n_{k,i} \;=:\; S \quad \text{indépendant des } (s_k).
$$

**Conséquence.** La moyenne $\bar{C} = S/T$ est fixe : l'optimisation ne modifie **pas** la quantité totale de travail, seulement sa répartition temporelle. Toute solution admissible vérifie la borne inférieure
$$
\max_{1 \le j \le T} C_j \;\ge\; \left\lceil \frac{S}{T} \right\rceil.
$$

---

## 2. Choix du critère d'optimisation

L'énoncé laisse volontairement le critère ouvert. Cinq formulations légitimes :

| Critère | Formulation | Interprétation métier |
|---|---|---|
| $L^2$ (variance) | $\min \sum_j (C_j - \bar{C})^2$ | Lissage en moyenne quadratique |
| **Min-max** | $\min \max_j C_j$ | **Dimensionnement au pic** |
| Amplitude | $\min (\max_j C_j - \min_j C_j)$ | Écart jour fort / jour creux |
| Dépassement | $\min \sum_j (C_j - c^\star)^+$ | Capacité contractuelle $c^\star$ |
| Variation totale | $\min \sum_j \lvert C_{j+1} - C_j \rvert$ | Régularité jour à jour |

**Équivalence utile (conséquence de l'invariant).**
$$
\arg\min_{s} \sum_{j=1}^{T} (C_j - \bar{C})^2 \;=\; \arg\min_{s} \sum_{j=1}^{T} C_j^{\,2}.
$$

**Choix retenu :** critère min-max. Il correspond exactement au dimensionnement des effectifs — préoccupation centrale dans le cas RATP — et se formule comme une PLNE compacte.

---

## 3. Formulation PLNE (critère min-max)

### 3.1 Variables

- Binaires : $x_{k,t} \in \{0,1\}$ pour $k=1,\ldots,K$ et $t \in \mathcal{T}_k$, avec
$$
x_{k,t} = 1 \iff s_k = t.
$$
- Continue : $M \in \mathbb{R}_+$ représentant le pic de charge.

### 3.2 Contraintes

**Unicité de la date de début** ($K$ égalités) :
$$
\sum_{t \in \mathcal{T}_k} x_{k,t} = 1, \qquad k = 1,\ldots,K.
$$

**Majoration du pic par $M$** ($T$ inégalités) : pour chaque $j \in \{1,\ldots,T\}$,
$$
\sum_{k=1}^{K}\; \sum_{\substack{t \in \mathcal{T}_k \\ t \le j \le t + d_k - 1}} n_{k,\,j-t+1}\, x_{k,t} \;-\; M \;\le\; 0.
$$

Les bornes de la somme interne se réécrivent
$$
t \in \bigl[\,\max(1,\, j - d_k + 1),\; \min(T - d_k + 1,\, j)\,\bigr] \cap \mathbb{Z}.
$$

### 3.3 Objectif

$$
\boxed{\quad \min_{x,\,M} \; M \quad \text{sous les contraintes ci-dessus.} \quad}
$$

### 3.4 Taille du modèle

$$
N_{\text{bin}} = \sum_{k=1}^{K} (T - d_k + 1), \qquad N_{\text{contr}} = K + T.
$$

Pour $K=8$, $T=20$, $\bar d \approx 3{,}8$ : $N_{\text{bin}} \approx 136$, $N_{\text{contr}} = 28$. Résolution en quelques millisecondes par HiGHS. Le modèle reste tractable jusqu'à $N_{\text{bin}} \sim 10^4$.

---

## 4. Implémentation

### 4.1 Dépendances

```python
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
```

Le solveur HiGHS est intégré à SciPy $\ge 1.9$ ; aucune installation externe n'est nécessaire.

### 4.2 Solveur PLNE

```python
def solve_smoothing_minmax(projects, T, time_limit=None):
    """
    Résout le problème de lissage en minimisant le pic de charge.

    Paramètres
    ----------
    projects : list of 1D array-like
        projects[k] = (n_{k,1}, ..., n_{k,d_k}), profil de charge du projet k.
    T : int
        Horizon (nombre de jours).

    Retourne
    --------
    starts : list[int]    dates de début s_k (1-indexées)
    M_star : float        valeur optimale du pic
    C      : np.ndarray   charge agrégée C_j, j=1..T
    status : str          message du solveur
    """
    K = len(projects)
    durations = [len(p) for p in projects]
    if any(d > T for d in durations):
        raise ValueError("Un projet est plus long que l'horizon T.")

    # Disposition des variables : [x_{1,1},...,x_{K,T-d_K+1}, M]
    offsets = [0]
    for k in range(K):
        offsets.append(offsets[-1] + (T - durations[k] + 1))
    n_bin = offsets[-1]
    n_var = n_bin + 1
    M_idx = n_bin

    def var_idx(k, t):          # t en 1-indexé
        return offsets[k] + (t - 1)

    # Contrainte A_eq : chaque projet commence exactement une fois
    A_eq = np.zeros((K, n_var))
    for k in range(K):
        for t in range(1, T - durations[k] + 2):
            A_eq[k, var_idx(k, t)] = 1.0

    # Contrainte A_ub : charge(j) - M <= 0 pour tout j
    A_ub = np.zeros((T, n_var))
    for j in range(1, T + 1):
        for k in range(K):
            d_k = durations[k]
            t_min = max(1, j - d_k + 1)
            t_max = min(T - d_k + 1, j)
            for t in range(t_min, t_max + 1):
                i = j - t + 1
                A_ub[j - 1, var_idx(k, t)] = projects[k][i - 1]
        A_ub[j - 1, M_idx] = -1.0

    # Objectif : minimiser M
    c = np.zeros(n_var)
    c[M_idx] = 1.0

    integrality = np.zeros(n_var)
    integrality[:n_bin] = 1
    lb = np.zeros(n_var)
    ub = np.ones(n_var)
    ub[M_idx] = np.inf

    constraints = [
        LinearConstraint(A_eq, lb=1.0, ub=1.0),
        LinearConstraint(A_ub, lb=-np.inf, ub=0.0),
    ]

    options = {"time_limit": time_limit} if time_limit else {}
    res = milp(c, constraints=constraints, integrality=integrality,
               bounds=Bounds(lb, ub), options=options)
    if not res.success:
        raise RuntimeError(f"Échec MILP : {res.message}")

    x = res.x[:n_bin]
    M_star = float(res.x[M_idx])

    starts = []
    for k in range(K):
        seg = x[offsets[k]:offsets[k + 1]]
        starts.append(int(np.argmax(seg)) + 1)

    C = compute_load(projects, starts, T)
    return starts, M_star, C, res.message


def compute_load(projects, starts, T):
    """Charge agrégée C_j pour un planning donné."""
    C = np.zeros(T, dtype=float)
    for k, s in enumerate(starts):
        d_k = len(projects[k])
        C[s - 1 : s - 1 + d_k] += np.asarray(projects[k], dtype=float)
    return C
```

### 4.3 Heuristique gloutonne de référence

```python
def greedy_minmax(projects, T):
    """Tri par charge totale décroissante, insertion au créneau
    minimisant le pic courant."""
    order = sorted(range(len(projects)), key=lambda k: -sum(projects[k]))
    starts = [None] * len(projects)
    C = np.zeros(T)
    for k in order:
        d_k = len(projects[k])
        best_t, best_peak = 1, np.inf
        for t in range(1, T - d_k + 2):
            C_trial = C.copy()
            C_trial[t - 1 : t - 1 + d_k] += projects[k]
            peak = C_trial.max()
            if peak < best_peak:
                best_peak, best_t = peak, t
        starts[k] = best_t
        C[best_t - 1 : best_t - 1 + d_k] += projects[k]
    return starts, float(C.max()), C
```

---

## 5. Mise en œuvre sur une instance test

### 5.1 Données

$K = 8$ projets, $T = 20$ jours :

$$
\begin{aligned}
P_1 &= (3,1,2,4) & P_5 &= (4,4,4) \\
P_2 &= (2,2,2) & P_6 &= (2,1,1,1,1,2) \\
P_3 &= (5,1) & P_7 &= (3,3) \\
P_4 &= (1,3,3,1,2) & P_8 &= (1,2,3,2,1)
\end{aligned}
$$

Charge totale : $S = 67$. Borne inférieure : $\lceil S/T \rceil = \lceil 67/20 \rceil = 4$. Moyenne : $\bar{C} = 3{,}35$.

### 5.2 Résultats comparatifs

| Stratégie | Pic $M$ | Écart borne inf. |
|---|:---:|:---:|
| Naïve (tous au jour 1) | $21$ | $+17$ |
| Gloutonne | $6$ | $+2$ |
| **PLNE (optimale)** | $\mathbf{5}$ | $\mathbf{+1}$ |

**Dates de début optimales :**
$$
s^\star = (17,\, 12,\, 9,\, 14,\, 1,\, 13,\, 4,\, 4).
$$

**Profils de charge $C_j$ :**

| Stratégie | $C_1,\ldots,C_{20}$ |
|---|---|
| Naïve | $21, 17, 15, 8, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0$ |
| Gloutonne | $4, 4, 4, 3, 6, 3, 4, 4, 6, 3, 2, 4, 3, 4, 4, 3, 3, 1, 2, 0$ |
| PLNE | $4, 4, 4, 4, 5, 3, 2, 1, 5, 1, 0, 2, 4, 4, 4, 4, 5, 5, 2, 4$ |

### 5.3 Analyse

La PLNE atteint $M^\star = 5$, soit un écart unitaire à la borne théorique $\lceil S/T \rceil = 4$. Cet écart est irréductible sur cette instance : aucune combinaison de décalages ne peut ramener le pic à 4, compte tenu de l'indivisibilité des profils $P_k$.

L'heuristique gloutonne dépasse la PLNE aux jours $5$ et $9$ (pic 6) parce qu'elle fige la position des projets de charge élevée sans anticiper les interférences futures.

---

## 6. Remarques méthodologiques

**Dégénérescence.** Plusieurs plannings peuvent partager le même pic $M^\star$. Pour les départager, adopter un schéma lexicographique :

1. Résoudre (P1) : $\min M$ $\longrightarrow M^\star$.
2. Résoudre (P2) : $\min \sum_j (C_j - \bar C)^2$ sous $\max_j C_j \le M^\star$.

(P2) est une programmation quadratique en nombres entiers (PQNE), convexe.

**Linéarisation du critère $L^1$.** Pour minimiser $\sum_j \lvert C_j - \bar C \rvert$ au lieu du pic, introduire $u_j, v_j \ge 0$ et
$$
C_j - \bar C = u_j - v_j, \qquad \min \sum_{j=1}^{T} (u_j + v_j).
$$

Ceci reste une PLNE résolvable par `milp`.

**Complexité.** Le problème est NP-difficile en général (réduction depuis `BIN-PACKING`). En pratique, HiGHS résout l'optimum pour $N_{\text{bin}} \lesssim 10^4$. Au-delà, utiliser :
- Relaxation LP + arrondi ;
- Métaheuristiques (recuit simulé, tabou) ;
- Solveur commercial Gurobi (licence académique gratuite).

---

## 7. Extensions

1. **Profils incertains.** Les $n_{k,i}$ sont des variables aléatoires. Lissage en espérance vs. formulation robuste (distributionally robust optimization).
2. **Fenêtres de disponibilité.** $s_k \in [a_k, b_k] \cap \mathbb{N}$ : ajouter $x_{k,t} = 0$ pour $t \notin [a_k, b_k]$.
3. **Multi-compétences.** $n_{k,i} \in \mathbb{N}^R$ (vecteur sur $R$ ressources) : dupliquer les contraintes de pic par ressource.
4. **Précédences.** Si $k_1 \prec k_2$, ajouter $s_{k_2} \ge s_{k_1} + d_{k_1}$ — on retombe alors sur le RCPSP (*Resource-Constrained Project Scheduling Problem*), très étudié depuis Pritsker (1969).

---

## 8. Angle spectral

Représenter chaque projet par $\mathbf{p}_k \in \mathbb{R}^T$, complétion de $P_k$ par des zéros. Le décalage de $s_k - 1$ jours agit comme une translation. Sur le tore $\mathbb{Z}/T\mathbb{Z}$, la transformée de Fourier discrète donne
$$
\widehat{C}(\nu) \;=\; \sum_{k=1}^{K} \widehat{\mathbf{p}_k}(\nu)\, e^{-2\pi i \nu (s_k - 1)/T},
\qquad \nu = 0,\ldots,T-1.
$$

**Identité de Parseval :**
$$
\sum_{j=1}^{T} C_j^{\,2} \;=\; \frac{1}{T} \sum_{\nu=0}^{T-1} \bigl|\widehat{C}(\nu)\bigr|^{\,2}.
$$

Le mode constant donne $\lvert \widehat{C}(0) \rvert^2 / T = S^2 / T$ (invariant). Minimiser la variance revient à **faire interférer destructivement les modes non nuls** des projets :
$$
\min_{s_1,\ldots,s_K} \; \sum_{\nu=1}^{T-1} \Biggl| \sum_{k=1}^{K} \widehat{\mathbf{p}_k}(\nu)\, e^{-2\pi i \nu (s_k - 1)/T} \Biggr|^{\,2}.
$$

Cette reformulation fournit :
- une **borne inférieure** immédiate pour le critère $L^2$ : $\sum_j C_j^2 \ge S^2 / T$ ;
- une **heuristique spectrale** : ajuster les phases $e^{-2\pi i \nu (s_k-1)/T}$ aux fréquences dominantes.

---

## Annexe A — Instance et dépendances

**Environnement testé :** Python 3.12, NumPy 2.4, SciPy 1.17 (HiGHS intégré).

**Exécution type (instance §5) :**

```
Charge totale S = 67, horizon T = 20
Borne inférieure du pic : ceil(S/T) = 4

[NAÏF]    pic = 21
[GLOUTON] pic = 6
[PLNE]    pic = 5   (HiGHS Status 7: Optimal)
```

---

## Références

- B. Beauzamy, *Lisser l'activité*, Société de Calcul Mathématique SA, avril 2026.
- J. Huangfu, J.A.J. Hall, « Parallelizing the dual revised simplex method », *Math. Prog. Comp.*, 10 (2018), 119–142. [Solveur HiGHS]
- A.A.B. Pritsker, L.J. Watters, P.M. Wolfe, « Multiproject scheduling with limited resources: a zero-one programming approach », *Management Science*, 16 (1969), 93–108.
