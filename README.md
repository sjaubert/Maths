# Projets de Mathématiques Appliquées (S. Jaubert)

Ce dépôt regroupe différents projets de modélisation mathématique et de simulation numérique.

## 1. Modèles d'Évolution (Systèmes Dynamiques)

**[Accéder à l&#39;application interactive en ligne](https://sjaubert.github.io/Maths/)**

Une application interactive R Shiny permettant de visualiser les portraits de phase de systèmes d'équations différentielles non-linéaires.

### Fonctionnalités

- **Visualisation dynamique** : Tracé des lignes de champ et des trajectoires pour trois systèmes complexes.
- **Interactivité** : Cliquez sur le graphique pour choisir les conditions initiales $(x_0, y_0)$.
- **Modèles inclus** :
  1. $\dot{x} = \sin(x^2+y^2), \dot{y} = \sin(xy)$
  2. $\dot{x} = \sin(x)\sin(y), \dot{y} = \cos(xy)$
  3. $\dot{x} = y(y-1)(y+1), \dot{y} = \sin(x+y)$

📂 **Code source :** [`modele_evolution/`](./modele_evolution/)

---

## 2. Disparité dans les Groupes Aléatoires (Paradoxe de la Parité)

Une démonstration mathématique et statistique d'un résultat contre-intuitif sur la répartition paritaire dans des groupes aléatoires.

### Le Problème

Si l'on divise aléatoirement une population de 10 000 personnes (5 000 H / 5 000 F) en deux groupes égaux, l'écart moyen entre hommes et femmes n'est pas nul, mais suit une **loi découlant de la distribution hypergéométrique**.

Pour $N=10 000$, l'espérance de l'écart est $E[|H-F|] \approx 40$.

### Contenu

- **Démonstration théorique** (LaTeX/PDF) : Preuve complète utilisant l'approximation normale.
- **Simulation Python** : Script de vérification empirique sur 10 000 tirages.
- **Visualisation** : Graphiques de la distribution des écarts.

📂 **Documents et scripts :** [`parite_bb/`](./parite_bb/)

---

## Technologies utilisées

- **R / Shiny** : Interface web interactive, `ggplot2` pour les graphiques, intégrateur RK4 personnalisé.
- **Python** : Simulations numériques (`numpy`, `matplotlib`).
- **LaTeX** : Rédaction scientifique.
- **GitHub Pages / Shinylive** : Déploiement de l'application R sans serveur (WebAssembly).

---

*Auteur : S. Jaubert — 2026*
