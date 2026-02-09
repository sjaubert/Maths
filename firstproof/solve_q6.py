
import networkx as nx
import numpy as np
import random
from itertools import combinations

def get_laplacian(G):
    n = len(G.nodes)
    nodes = list(G.nodes)
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    
    L = np.zeros((n, n))
    
    # Degrees on diagonal
    for i, node in enumerate(nodes):
        L[i, i] = G.degree(node)
        
    # -1 for edges
    for u, v in G.edges:
        i, j = node_to_idx[u], node_to_idx[v]
        L[i, j] = -1
        L[j, i] = -1
        
    return L

def get_subgraph_laplacian(G, S):
    # Construct Laplacian of G_S (edges only within S) on full vertex set V
    # Nodes in V, edges in E(S,S)
    n = len(G.nodes)
    nodes = list(G.nodes)
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    
    L_S = np.zeros((n, n))
    
    # Iterate over edges in G. If both endpoints in S, add to L_S
    for u, v in G.edges:
        if u in S and v in S:
            i, j = node_to_idx[u], node_to_idx[v]
            L_S[i, i] += 1
            L_S[j, j] += 1
            L_S[i, j] -= 1
            L_S[j, i] -= 1
            
    return L_S

def is_epsilon_light(L, L_S, epsilon):
    # Check if epsilon * L - L_S is Positive Semidefinite
    M = epsilon * L - L_S
    # Check eigenvalues
    try:
        evals = np.linalg.eigvalsh(M)
        return np.all(evals >= -1e-8) # Tolerance for numerical errors
    except np.linalg.LinAlgError:
        return False

def check_graph(G, epsilon, name="Graph"):
    n = len(G.nodes)
    L = get_laplacian(G)
    nodes = list(G.nodes)
    
    max_s_size = 0
    best_S = [] # Initialize here
    
    # Strategy: 
    # For small N (< 15), brute force (Iterate from largest size down)
    
    if n <= 14:
        # Brute force
        found = False
        # Iterate k from n down to 0
        for k in range(n, -1, -1):
            for S_combo in combinations(nodes, k):
                S = set(S_combo)
                L_S = get_subgraph_laplacian(G, S)
                if is_epsilon_light(L, L_S, epsilon):
                    max_s_size = k
                    best_S = S
                    found = True
                    break
            if found:
                break
    else:
        # Randomized search
        # Try random subsets of various sizes
        # Focus on sizes around expected optimal (epsilon * n?)
        
        # Greedy Addition
        S_curr = set()
        candidates = list(nodes)
        
        # Try multiple random restarts for greedy
        for _ in range(10):
            random.shuffle(candidates)
            S_temp = set()
            for u in candidates:
                S_next = S_temp.union({u})
                L_S_next = get_subgraph_laplacian(G, S_next)
                if is_epsilon_light(L, L_S_next, epsilon):
                    S_temp = S_next
            if len(S_temp) > max_s_size:
                max_s_size = len(S_temp)
                best_S = S_temp
                
        # Also try random sampling
        for _ in range(50):
            k = random.randint(max(0, int(epsilon*n - 2)), min(n, int(epsilon*n + 5)))
            S_rand = set(random.sample(nodes, k))
            L_S = get_subgraph_laplacian(G, S_rand)
            if is_epsilon_light(L, L_S, epsilon):
                if k > max_s_size:
                    max_s_size = k
                    best_S = S_rand

    ratio = max_s_size / (epsilon * n) if epsilon > 0 else 0
    print(f"{name} (N={n}, eps={epsilon}): Max |S|={max_s_size}, Ratio={ratio:.4f}")
    return ratio

# --- Main Simulation ---
print("Running simulations for Q6...")
epsilons = [0.1, 0.3, 0.5, 0.7, 0.9]

results = {}

for eps in epsilons:
    print(f"\n--- Epsilon = {eps} ---")
    min_ratio = 100.0
    
    # 1. Path Graph
    for N in [5, 10, 14]:
        G = nx.path_graph(N)
        r = check_graph(G, eps, f"Path-{N}")
        min_ratio = min(min_ratio, r)

    # 2. Cycle Graph
    for N in [5, 10, 14]:
        G = nx.cycle_graph(N)
        r = check_graph(G, eps, f"Cycle-{N}")
        min_ratio = min(min_ratio, r)

    # 3. Complete Graph
    for N in [5, 8, 12]:
        G = nx.complete_graph(N)
        r = check_graph(G, eps, f"Complete-{N}")
        min_ratio = min(min_ratio, r)

    # 4. Star Graph
    for N in [5, 10, 14]:
        G = nx.star_graph(N-1)
        r = check_graph(G, eps, f"Star-{N}")
        min_ratio = min(min_ratio, r)
        
    # 5. Random Graph (ER)
    # Using small N for random because brute force is slow, but need accurate max |S|
    for N in [10, 14]:
        G = nx.erdos_renyi_graph(N, 0.5, seed=42)
        r = check_graph(G, eps, f"ER-{N}-p0.5")
        min_ratio = min(min_ratio, r)

    results[eps] = min_ratio

print("\n--- Summary of Minimum Ratios ---")
for eps, r in results.items():
    print(f"Epsilon={eps}: Min Ratio = {r:.4f}")
