# Rapport d'Investigation - Question 6 (First Proof)

## Existence d'ensembles $\epsilon$-light

**Date** : 9 Février 2026  
**Question** : Existe-t-il une constante $c > 0$ telle que pour tout graphe $G$ et tout $\epsilon \in (0,1)$, il existe un sous-ensemble $S \subseteq V$ "$\epsilon$-light" ($\epsilon L - L_S \succeq 0$) de taille $|S| \ge c \epsilon |V|$ ?

### 1. Méthodologie

Nous avons mené des simulations numériques sur des graphes de petite taille ($N \le 15$) pour différents types (Chemin, Cycle, Complet, Étoile, Aléatoire ER).
Pour chaque graphe et chaque $\epsilon$, nous avons cherché la taille maximale $|S|_{max}$ d'un sous-ensemble $\epsilon$-light par force brute ou heuristique.
Nous avons calculé le ratio $R = \frac{|S|_{max}}{\epsilon |V|}$. Si ce ratio reste borné loin de 0, cela supporte la réponse OUI. Si $R \to 0$ pour certaines familles, la réponse est NON.

### 2. Résultats Expérimentaux (N $\le$ 15)

| Epsilon | Ratio Min Observé | Graphe Limitant |
|---------|-------------------|-----------------|
| 0.1     | **0.83**          | Complet $K_{12}$ |
| 0.3     | **0.67**          | Complet $K_5$ / $K_8$ |
| 0.5     | **0.80**          | Cycle $C_5$ / $K_5$ |
| 0.7     | **0.57**          | Cycle $C_5$ |
| 0.9     | **0.56**          | $C_{14}$ |

**Observations :**

1. **Graphes Complets** : Le ratio est proche de 1. Théoriquement, on peut montrer que pour $K_n$, tout ensemble de taille $k \le \epsilon n$ convient.
2. **Cycles** : Le ratio diminue vers ~0.55 pour $\epsilon$ grand. Cela suggère que pour des graphes peu connectés, on est limité à des ensembles de taille $\approx n/2$ (proche des ensembles indépendants) quand la contrainte spectrale devient active.
3. **Général** : Sur tous les cas testés, on a toujours trouvé un ensemble de taille au moins $0.5 \epsilon |V|$.

### 3. Analyse Théorique Préliminaire

#### Lien avec les Ensembles Indépendants

Un ensemble indépendant $S$ (aucune arête interne) a $L_S = 0$. La condition $\epsilon L - 0 \succeq 0$ est toujours vraie pour $\epsilon \ge 0$.
Donc $|S|_{max} \ge \alpha(G)$ (nombre d'indépendance).
Si la conjecture est vraie, elle implique $\alpha(G) \ge c \epsilon |V|$ pour $\epsilon \to 0$.
Or, on sait que $\alpha(G) \ge \frac{|V|}{\Delta+1}$ ($\Delta$ = degré max).
Pour $\epsilon \approx 1/\Delta$, cela donne $\frac{1}{\Delta+1} \approx c \frac{1}{\Delta} \Rightarrow c \approx 1$.
Cependant, pour des graphes expanseurs de degré constant $d$, $\alpha(G)$ est linéaire en $N$, donc ça tient.

#### Cas Difficiles Potentiels

Les graphes expanseurs de **très haut degré** pourraient poser problème si $\epsilon$ est fixé (ex: 0.5).
Si la densité d'arêtes induites dans tout grand sous-ensemble est élevée (propriété des graphes aléatoires denses), alors $L_S$ sera "grand".

### 4. Conclusion Provisoire

Les données sur les petits graphes ne montrent **pas de contre-exemple évident**. Le ratio semble être borné inférieurement par une constante $c \approx 0.5$.
Il est possible que la réponse soit **OUI**, potentiellement en lien avec les résultats célèbres de Spielman et Srivastava (auteurs du papier) sur la sparsification spectrale, bien que le problème soit ici différent (sous-ensemble induit vs repondération).

**Suggestion** : La réponse est probablement **OUI**.
