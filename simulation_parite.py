import numpy as np
import matplotlib.pyplot as plt
import math

def simuler_tirage(N_total, n_hommes, n_femmes, n_groupe1, n_simulations=10000):
    """
    Simule le tirage aléatoire de personnes et calcule |H-F| dans le groupe 1
    
    N_total: effectif total
    n_hommes: nombre d'hommes dans la population totale
    n_femmes: nombre de femmes dans la population totale
    n_groupe1: taille du groupe 1
    n_simulations: nombre de simulations à effectuer
    """
    differences = []
    
    for _ in range(n_simulations):
        # Créer la population: 0 = homme, 1 = femme
        population = [0] * n_hommes + [1] * n_femmes
        
        # Tirer aléatoirement n_groupe1 personnes
        groupe1 = np.random.choice(population, size=n_groupe1, replace=False)
        
        # Compter hommes et femmes dans le groupe 1
        n_femmes_g1 = np.sum(groupe1)
        n_hommes_g1 = n_groupe1 - n_femmes_g1
        
        # Calculer |H - F|
        diff = abs(n_hommes_g1 - n_femmes_g1)
        differences.append(diff)
    
    return np.array(differences)

def calculer_esperance_theorique(N_total):
    """
    Calcule l'espérance théorique de |H-F| selon la formule sqrt(N/(2*pi))
    """
    return math.sqrt(N_total / (2 * math.pi))

def demonstration_complete():
    """
    Démonstration complète du résultat
    """
    # Paramètres du problème
    N_total = 10000
    n_hommes = 5000
    n_femmes = 5000
    n_groupe1 = 5000
    n_simulations = 10000
    
    print("=" * 70)
    print("DÉMONSTRATION: Disparité dans les groupes aléatoires")
    print("=" * 70)
    print()
    print(f"Population totale: {N_total} personnes")
    print(f"  - Hommes: {n_hommes}")
    print(f"  - Femmes: {n_femmes}")
    print(f"Taille du groupe 1: {n_groupe1}")
    print(f"Nombre de simulations: {n_simulations}")
    print()
    
    # Simulation
    print("Simulation en cours...")
    differences = simuler_tirage(N_total, n_hommes, n_femmes, n_groupe1, n_simulations)
    
    # Calculs
    esperance_simulee = np.mean(differences)
    ecart_type_simule = np.std(differences)
    esperance_theorique = calculer_esperance_theorique(N_total)
    
    # Résultats
    print()
    print("RÉSULTATS:")
    print("-" * 70)
    print(f"Espérance théorique de |H-F|: {esperance_theorique:.2f}")
    print(f"Espérance simulée de |H-F|:   {esperance_simulee:.2f}")
    print(f"Écart-type simulé:             {ecart_type_simule:.2f}")
    print()
    print(f"Différence minimale observée:  {np.min(differences)}")
    print(f"Différence maximale observée:  {np.max(differences)}")
    print(f"Médiane:                       {np.median(differences):.2f}")
    print()
    
    # Statistiques intéressantes
    parite_parfaite = np.sum(differences == 0)
    parite_proche = np.sum(differences <= 10)
    
    print(f"Parité parfaite (|H-F| = 0):       {parite_parfaite} fois ({100*parite_parfaite/n_simulations:.2f}%)")
    print(f"Parite proche (|H-F| <= 10):        {parite_proche} fois ({100*parite_proche/n_simulations:.2f}%)")
    print()
    
    # Visualisations
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Démonstration: Disparité dans les groupes aléatoires", fontsize=16, fontweight='bold')
    
    # 1. Histogramme de |H-F|
    ax1 = axes[0, 0]
    ax1.hist(differences, bins=50, density=True, alpha=0.7, color='steelblue', edgecolor='black')
    ax1.axvline(esperance_simulee, color='red', linestyle='--', linewidth=2, label=f'Espérance simulée: {esperance_simulee:.2f}')
    ax1.axvline(esperance_theorique, color='orange', linestyle='--', linewidth=2, label=f'Espérance théorique: {esperance_theorique:.2f}')
    ax1.set_xlabel('|H - F| (différence absolue)', fontsize=11)
    ax1.set_ylabel('Densité de probabilité', fontsize=11)
    ax1.set_title('Distribution de |H-F| (10 000 simulations)', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Comparaison avec différentes tailles de population
    ax2 = axes[0, 1]
    tailles = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000]
    esperances_theo = [calculer_esperance_theorique(N) for N in tailles]
    esperances_sim = []
    
    for N in tailles:
        diffs = simuler_tirage(N, N//2, N//2, N//2, 1000)
        esperances_sim.append(np.mean(diffs))
    
    ax2.plot(tailles, esperances_theo, 'o-', color='orange', linewidth=2, markersize=8, label='Théorique: √(N/(2π))')
    ax2.plot(tailles, esperances_sim, 's--', color='steelblue', linewidth=2, markersize=6, label='Simulé')
    ax2.set_xlabel('Taille de la population (N)', fontsize=11)
    ax2.set_ylabel('E[|H-F|]', fontsize=11)
    ax2.set_title('Espérance de |H-F| en fonction de N', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Distribution cumulative
    ax3 = axes[1, 0]
    ax3.hist(differences, bins=50, density=True, cumulative=True, alpha=0.7, color='green', edgecolor='black')
    ax3.axhline(0.5, color='red', linestyle='--', linewidth=1.5, label='Médiane (50%)')
    ax3.set_xlabel('|H - F|', fontsize=11)
    ax3.set_ylabel('Probabilité cumulée', fontsize=11)
    ax3.set_title('Distribution cumulative de |H-F|', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Box plot pour différentes tailles
    ax4 = axes[1, 1]
    tailles_box = [1000, 5000, 10000, 20000]
    data_box = []
    labels_box = []
    
    for N in tailles_box:
        diffs = simuler_tirage(N, N//2, N//2, N//2, 1000)
        data_box.append(diffs)
        labels_box.append(f'N={N}\n(théo: {calculer_esperance_theorique(N):.1f})')
    
    bp = ax4.boxplot(data_box, labels=labels_box, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
    ax4.set_ylabel('|H - F|', fontsize=11)
    ax4.set_title('Distribution de |H-F| pour différentes tailles', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('c:/Users/s.jaubert/projets/Maths/simulation_parite.png', dpi=300, bbox_inches='tight')
    print("Graphique sauvegardé: simulation_parite.png")
    print()
    
    return differences, esperance_theorique, esperance_simulee

if __name__ == "__main__":
    differences, e_theo, e_sim = demonstration_complete()
    
    print("=" * 70)
    print("CONCLUSION:")
    print("-" * 70)
    print("Contrairement à l'intuition, la parité parfaite est RARE !")
    print(f"L'espérance de |H-F| vaut environ {e_theo:.2f} personnes.")
    print("Plus la population totale augmente, plus la disparité AUGMENTE !")
    print("=" * 70)
