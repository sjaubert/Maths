# Démonstration : Disparité dans les groupes aléatoires

Ce repository contient une démonstration mathématique rigoureuse d'un résultat statistique contre-intuitif concernant la parité lors de la partition aléatoire de populations.

## 📊 Le problème

Soit une population de **10 000 personnes** composée de manière paritaire :

- 5 000 hommes (H)
- 5 000 femmes (F)

On tire au hasard **5 000 personnes** pour former le Groupe 1, les 5 000 restants constituant le Groupe 2.

### ❓ Question intuitive (fausse)

La plupart des gens pensent que chaque groupe aura environ 2 500 H et 2 500 F, respectant la parité.

### ✅ Résultat mathématique (vrai)

L'espérance de la différence absolue |H - F| dans chaque groupe vaut :

```
E[|H - F|] = √(N / (2π))
```

où N est l'effectif total.

**Pour N = 10 000 :** E[|H - F|] ≈ **39,9 personnes** 🤯

### 🎯 Paradoxe

Plus la population totale augmente, plus la disparité absolue **augmente** (bien que la disparité relative diminue) !

| Population (N) | E[\|H-F\|] | Proportion |
|---------------|----------|------------|
| 1 000         | 12,6     | 2,52%      |
| 10 000        | 39,9     | 0,80%      |
| 100 000       | 126,2    | 0,25%      |

## 📁 Contenu du repository

### Documents principaux

- **`demonstration_parite.tex`** - Démonstration mathématique complète en LaTeX avec :
  - Modélisation par loi hypergéométrique
  - Calcul rigoureux de l'espérance
  - Approximation normale et formule asymptotique
  - Applications pratiques

- **`demonstration_parite.html`** - Version HTML interactive avec :
  - Explications visuelles
  - Tableaux récapitulatifs
  - Design moderne et responsive
  - Adapté pour présentation pédagogique

- **`Disparité_dans_les_groupes_aléatoires.pdf`** - Version PDF compilée de la démonstration LaTeX

### Simulations

- **`simulation_parite.py`** - Script Python pour :
  - Simuler 10 000 tirages aléatoires
  - Calculer l'espérance simulée de |H-F|
  - Générer des visualisations comparatives
  - Vérifier empiriquement le résultat théorique

- **`simulation_parite.png`** - Graphiques générés montrant :
  - Distribution de |H-F|
  - Comparaison théorique vs simulé
  - Évolution avec la taille de population
  - Box plots pour différentes tailles

### Documents de référence

- **`BB_repartition_aleatoire_groupes_2026_01_15.pdf`** - Document externe analysé (attention : contient des erreurs conceptuelles - traite le cas binomial au lieu d'hypergéométrique)

## 🚀 Utilisation

### Exécuter la simulation

```bash
python simulation_parite.py
```

La simulation affichera :

- L'espérance théorique : ~39,89
- L'espérance simulée (sur 10 000 tirages)
- Distribution des résultats
- Graphiques de visualisation

### Compiler le LaTeX

```bash
pdflatex demonstration_parite.tex
pdflatex demonstration_parite.tex  # 2ème passage pour les références
```

### Visualiser le HTML

Ouvrez simplement `demonstration_parite.html` dans votre navigateur.

## 📚 Concepts mathématiques

### Loi hypergéométrique

Le nombre d'hommes X dans le Groupe 1 suit une loi hypergéométrique H(N, K, n) :

```
E[X] = n × K/N = 2500
Var(X) = n × (K/N) × (1-K/N) × (N-n)/(N-1) ≈ 1250
σ(X) ≈ 35,36
```

### Espérance de |Z| pour une loi normale

Pour Z ~ N(0, σ²) :

```
E[|Z|] = σ × √(2/π)
```

### Formule finale

Avec D = |2X - n| et l'approximation normale :

```
E[D] = 2σ(X) × √(2/π) ≈ √(N/(2π))
```

## ⚠️ Distinction importante

Ce résultat concerne une **partition de taille fixe** (tirage sans remise, loi hypergéométrique).

Le cas où les tailles de groupes varient (tirage avec remise, loi binomiale) donnerait E[|H-F|] ≈ √(2N/π), soit environ le double.

## 🎓 Applications

- **Essais cliniques** : Déséquilibres naturels malgré la randomisation
- **Sondages** : Écarts attendus dans les échantillons représentatifs
- **Justice** : Composition des jurys tirés au sort
- **Enseignement** : Répartition aléatoire en classes

## 👤 Auteur

S. Jaubert - Janvier 2026

## 📄 Licence

Ce travail est mis à disposition à des fins pédagogiques et scientifiques.

---

**Note :** Ce résultat illustre un principe fondamental : *le hasard ne produit pas l'uniformité*. La variabilité aléatoire croît en valeur absolue avec la taille du système, même si elle décroît relativement.
