import numpy as np

def simulated_annealing(projects, T, initial_temp=10.0, cooling_rate=0.99, iter_per_temp=1000):
    K = len(projects)
    durations = [len(p) for p in projects]
    
    # Initialize randomly
    current_starts = [np.random.randint(1, T - durations[k] + 2) for k in range(K)]
    
    def compute_load(starts):
        C = np.zeros(T, dtype=float)
        for k, s in enumerate(starts):
            d_k = len(projects[k])
            C[s - 1 : s - 1 + d_k] += np.asarray(projects[k], dtype=float)
        return C
    
    def cost(starts):
        C = compute_load(starts)
        # Cost is L2 norm (sum of squares) + a heavy penalty for max peak to keep it lexicographic-like
        # Actually just sum of squares is best for smoothing
        return np.sum(C**2)

    current_cost = cost(current_starts)
    best_starts = list(current_starts)
    best_cost = current_cost
    
    temp = initial_temp
    
    for _ in range(1000):
        for _ in range(iter_per_temp):
            # Neighbor: shift one project randomly
            k = np.random.randint(K)
            old_s = current_starts[k]
            
            # valid range
            min_s, max_s = 1, T - durations[k] + 1
            if min_s == max_s: continue
                
            new_s = np.random.randint(min_s, max_s + 1)
            while new_s == old_s:
                new_s = np.random.randint(min_s, max_s + 1)
                
            current_starts[k] = new_s
            new_cost = cost(current_starts)
            
            if new_cost < current_cost or np.random.rand() < np.exp((current_cost - new_cost) / temp):
                current_cost = new_cost
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_starts = list(current_starts)
            else:
                current_starts[k] = old_s # revert
        temp *= cooling_rate
        
    return best_starts, best_cost

projects = [
    [3,1,2,4],
    [2,2,2],
    [5,1],
    [1,3,3,1,2],
    [4,4,4],
    [2,1,1,1,1,2],
    [3,3],
    [1,2,3,2,1]
]
T = 20
best_s, best_c = simulated_annealing(projects, T)
C = np.zeros(T, dtype=float)
for k, s in enumerate(best_s):
    d_k = len(projects[k])
    C[s - 1 : s - 1 + d_k] += np.asarray(projects[k], dtype=float)

print("Best Starts:", best_s)
print("Peak:", C.max())
print("Profile:", C)
print("L2 norm sum:", np.sum(C**2))
