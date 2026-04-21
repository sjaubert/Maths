import numpy as np
import time

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

def cost_l2(starts):
    C = np.zeros(T, dtype=float)
    for k, s in enumerate(starts):
        C[s - 1 : s - 1 + len(projects[k])] += np.asarray(projects[k], dtype=float)
    return np.sum(C**2), C

def sa(projects, T, iters=10000):
    K = len(projects)
    durations = [len(p) for p in projects]
    starts = [np.random.randint(1, T - durations[k] + 2) for k in range(K)]
    
    current_cost, _ = cost_l2(starts)
    best_starts, best_cost = list(starts), current_cost
    
    temp = 1000.0
    for i in range(iters):
        t_current = temp * (1 - i/iters)
        if t_current < 0.01: t_current = 0.01
        
        k = np.random.randint(K)
        old_s = starts[k]
        d_k = durations[k]
        if T - d_k + 1 <= 1: continue
        new_s = np.random.randint(1, T - d_k + 2)
        
        starts[k] = new_s
        new_cost, _ = cost_l2(starts)
        
        if new_cost < current_cost or np.random.rand() < np.exp((current_cost - new_cost) / t_current):
            current_cost = new_cost
            if current_cost < best_cost:
                 best_cost = current_cost
                 best_starts = list(starts)
        else:
            starts[k] = old_s
            
    return best_starts, cost_l2(best_starts)[1]

st = time.time()
best_s, C = sa(projects, T, 100000)
en = time.time()

print("Starts:", best_s)
print("Profile:", [int(c) for c in C])
print("Max:", C.max())
print("L2:", np.sum(C**2))
print("Time:", en-st)
