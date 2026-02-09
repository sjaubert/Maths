# Solution Proposée - Question 10 (First Proof)

## Solveur PCG pour Décomposition Tensorielle avec Contraintes RKHS

**Auteur** : Tentative de résolution par IA  
**Date** : 9 février 2026

---

## 1. Rappel du Problème

On cherche à résoudre le système linéaire :

$$\left[(Z \otimes K)^\top S S^\top (Z \otimes K) + \lambda (I_r \otimes K)\right] \text{vec}(W) = (I_r \otimes K) \text{vec}(B)$$

où :

- $K \in \mathbb{R}^{n \times n}$ : matrice noyau RKHS (symétrique définie positive)
- $Z \in \mathbb{R}^{M \times r}$ : produit de Khatri-Rao des matrices de facteurs (modes ≠ k)
- $S \in \mathbb{R}^{N \times q}$ : matrice de sélection des $q$ entrées observées
- $W \in \mathbb{R}^{n \times r}$ : inconnue
- $B = TZ \in \mathbb{R}^{n \times r}$ : MTTKRP
- $N = nM$, avec $n, r < q \ll N$

Le coût d'un solveur direct est $O(n^3 r^3)$. **Objectif** : faire mieux avec PCG.

---

## 2. Structure de la Matrice du Système

Définissons :
$$\mathbf{A} = (Z \otimes K)^\top S S^\top (Z \otimes K) + \lambda (I_r \otimes K)$$

Cette matrice $\mathbf{A}$ de taille $nr \times nr$ est :

- **Symétrique définie positive** (somme de deux matrices s.d.p.)
- Bien conditionnée grâce au terme de régularisation $\lambda (I_r \otimes K)$

---

## 3. Produit Matrice-Vecteur Efficace

Le cœur du PCG est le calcul efficace de $\mathbf{A} \cdot \text{vec}(W)$.

### 3.1 Décomposition en deux termes

$$\mathbf{A} \cdot \text{vec}(W) = \underbrace{(Z \otimes K)^\top S S^\top (Z \otimes K) \text{vec}(W)}_{\text{Terme données}} + \underbrace{\lambda (I_r \otimes K) \text{vec}(W)}_{\text{Terme régularisation}}$$

### 3.2 Terme de régularisation : $\lambda (I_r \otimes K) \text{vec}(W)$

En utilisant l'identité $(A \otimes B) \text{vec}(X) = \text{vec}(BXA^\top)$ :

$$(I_r \otimes K) \text{vec}(W) = \text{vec}(KW)$$

**Coût** : $O(n^2 r)$ — une multiplication matricielle $K \times W$.

### 3.3 Terme données : $(Z \otimes K)^\top S S^\top (Z \otimes K) \text{vec}(W)$

On procède en **3 étapes** :

#### Étape (a) : Calcul de $\mathbf{y} = S^\top (Z \otimes K) \text{vec}(W) \in \mathbb{R}^q$

Par l'identité de Kronecker :
$$(Z \otimes K) \text{vec}(W) = \text{vec}(K W Z^\top) \in \mathbb{R}^{nM}$$

Mais on ne forme **jamais** cette matrice $nM$-dimensionnelle !

**Observation clé** : $S$ sélectionne $q$ entrées. Soit $\Omega = \{(i_\ell, j_\ell)\}_{\ell=1}^q$ l'ensemble des indices observés (où $i_\ell \in [n]$, $j_\ell \in [M]$).

Pour chaque entrée observée $\ell$ :
$$y_\ell = [KWZ^\top]_{i_\ell, j_\ell} = (KW)_{i_\ell, :} \cdot Z_{j_\ell, :}^\top$$

**Algorithme** :

1. Calculer $P = KW$ de taille $n \times r$ — coût $O(n^2 r)$
2. Pour chaque $\ell \in [q]$ : $y_\ell = \langle P_{i_\ell, :}, Z_{j_\ell, :} \rangle$ — coût $O(qr)$

**Coût total étape (a)** : $O(n^2 r + qr)$

#### Étape (b) : Calcul de $(Z \otimes K)^\top S \mathbf{y} \in \mathbb{R}^{nr}$

On doit calculer :
$$(Z \otimes K)^\top S \mathbf{y} = \sum_{\ell=1}^{q} y_\ell \cdot [(Z \otimes K)^\top]_{:, \text{idx}(\ell)}$$

où $\text{idx}(\ell) = i_\ell + n(j_\ell - 1)$ est l'indice linéaire.

**Observation** : La colonne $\text{idx}(\ell)$ de $(Z \otimes K)^\top = (Z^\top \otimes K)$ est :
$$Z_{j_\ell, :}^\top \otimes K_{:, i_\ell}$$

Donc :
$$(Z \otimes K)^\top S \mathbf{y} = \sum_{\ell=1}^{q} y_\ell \cdot (Z_{j_\ell, :}^\top \otimes K_{:, i_\ell})$$

En dévectorisant vers une matrice $n \times r$ :
$$D = \sum_{\ell=1}^{q} y_\ell \cdot K_{:, i_\ell} \cdot Z_{j_\ell, :} = K \cdot \left(\sum_{\ell=1}^{q} y_\ell \cdot e_{i_\ell} \cdot Z_{j_\ell, :}\right)$$

**Algorithme efficace** :

1. Initialiser $G = 0_{n \times r}$
2. Pour chaque $\ell \in [q]$ : $G_{i_\ell, :} \mathrel{+}= y_\ell \cdot Z_{j_\ell, :}$ — coût $O(qr)$  
3. Calculer $D = KG$ — coût $O(n^2 r)$

**Coût total étape (b)** : $O(n^2 r + qr)$

### 3.4 Coût total d'un produit matrice-vecteur

$$\boxed{O(n^2 r + qr) \text{ par itération PCG}}$$

**Remarque importante** : On évite tout calcul de complexité $O(N) = O(nM)$ ou $O(M)$.

---

## 4. Choix du Préconditionneur

### 4.1 Préconditionneur proposé

$$\mathbf{M} = \lambda (I_r \otimes K) + \text{diag}\left((Z \otimes K)^\top S S^\top (Z \otimes K)\right)$$

En pratique, on utilise une approximation plus simple :

$$\mathbf{M}_{\text{simple}} = \lambda (I_r \otimes K)$$

### 4.2 Justification

1. **Structure exploitable** : $(I_r \otimes K)^{-1} = I_r \otimes K^{-1}$
2. **Pré-calcul** : $K^{-1}$ peut être calculé une fois par Cholesky en $O(n^3)$
3. **Application rapide** : $\mathbf{M}^{-1} \text{vec}(W) = \lambda^{-1} \text{vec}(K^{-1} W)$ coûte $O(n^2 r)$

### 4.3 Alternative : Préconditionneur diagonal

Si $K$ est mal conditionné, on peut utiliser :
$$\mathbf{M}_{\text{diag}} = \text{diag}(\mathbf{A})$$

Le calcul de la diagonale de $\mathbf{A}$ coûte $O(qr^2 + nr)$.

---

## 5. Algorithme PCG Complet

```
ENTRÉES : K, Z, S (indices Ω), B, λ, tolérance ε
SORTIE : W solution

1. Précalculs :
   - Factorisation Cholesky : K = LL^T              [O(n³)]
   - Inverse triangulaire pour appliquer K^{-1}    [préparé]

2. Initialisation :
   - W₀ = 0 (ou warm start)
   - r₀ = vec(B) − A·vec(W₀)                       [O(n²r + qr)]
   - z₀ = M^{-1} r₀ = λ^{-1} vec(K^{-1}·mat(r₀))   [O(n²r)]
   - p₀ = z₀
   - ρ₀ = r₀^T z₀

3. Boucle PCG (k = 0, 1, 2, ...) :
   a. q_k = A · p_k                                 [O(n²r + qr)]
   b. α_k = ρ_k / (p_k^T q_k)
   c. x_{k+1} = x_k + α_k p_k
   d. r_{k+1} = r_k − α_k q_k
   e. Si ||r_{k+1}|| < ε : STOP
   f. z_{k+1} = M^{-1} r_{k+1}                      [O(n²r)]
   g. ρ_{k+1} = r_{k+1}^T z_{k+1}
   h. β_k = ρ_{k+1} / ρ_k
   i. p_{k+1} = z_{k+1} + β_k p_k

4. Retourner W = mat(x_final)
```

---

## 6. Analyse de Complexité

| Opération | Coût |
|-----------|------|
| Factorisation de $K$ (une fois) | $O(n^3)$ |
| Produit $\mathbf{A} \cdot v$ par itération | $O(n^2 r + qr)$ |
| Application $\mathbf{M}^{-1}$ par itération | $O(n^2 r)$ |
| **Coût total par itération** | $O(n^2 r + qr)$ |

### Nombre d'itérations

Le nombre d'itérations du CG est borné par :
$$k \leq O\left(\sqrt{\kappa(\mathbf{M}^{-1}\mathbf{A})} \log(1/\varepsilon)\right)$$

où $\kappa$ est le conditionnement. Avec le préconditionneur $\mathbf{M} = \lambda(I_r \otimes K)$ :
$$\kappa(\mathbf{M}^{-1}\mathbf{A}) \approx 1 + \frac{\|S^\top(Z \otimes K)\|^2}{\lambda \sigma_{\min}(K)}$$

En pratique, quelques dizaines d'itérations suffisent.

### Complexité totale

$$\boxed{O\left(n^3 + k_{\max}(n^2 r + qr)\right)}$$

**Comparaison avec solveur direct** : $O(n^3 r^3)$

**Gain** : Facteur $r^3 / (r + q/n^2 \cdot k_{\max})$ — significatif quand $r$ n'est pas trop petit.

---

## 7. Pourquoi ça fonctionne

### 7.1 Évitement des calculs $O(N)$

Le point clé est que $S$ est **très creux** : seulement $q$ entrées non-nulles sur $N$.

- On ne forme jamais $Z \otimes K$ (taille $nM \times nr$)
- On n'accède qu'aux $q$ lignes/colonnes pertinentes
- Les produits Kronecker sont évalués "à la volée" uniquement aux indices observés

### 7.2 Exploitation de la structure tensorielle

L'identité $(A \otimes B)\text{vec}(X) = \text{vec}(BXA^\top)$ permet de :

- Travailler avec des matrices $n \times r$ au lieu de vecteurs $nr$
- Réutiliser les multiplications matricielles optimisées (BLAS niveau 3)

---

## 8. Améliorations possibles

1. **Préconditionneur bloc-diagonal** : Si $Z^\top Z$ est disponible, utiliser :
   $$\mathbf{M} = (Z^\top Z) \otimes K + \lambda (I_r \otimes K) = ((Z^\top Z + \lambda I_r) \otimes K)$$
   Inversion : $O(r^3 + n^3)$

2. **Warm start** : Réutiliser la solution de l'itération ALS précédente

3. **Critère d'arrêt adaptatif** : Tolérance décroissante au fil des itérations ALS externes

4. **Stochastic CG** : Pour $q$ très grand, échantillonner les termes de $S$

---

## 9. Conclusion

La méthode PCG proposée résout le système en :

$$O\left(n^3 + k_{\max}(n^2 r + qr)\right)$$

au lieu de $O(n^3 r^3)$ pour un solveur direct, tout en évitant explicitement toute opération de complexité $O(N) = O(nM)$.

**Points clés** :

- Produits matrice-vecteur exploitant la structure Kronecker et la parcimonie de $S$
- Préconditionneur basé sur le terme de régularisation
- Complexité quasi-linéaire en $q$ (nombre d'observations)
