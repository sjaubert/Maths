import numpy as np
from scipy.optimize import brentq

def eq(x, u):
    return 3*x**3 - 56*x**2 + u**2*(u+3)*x - 56*u**2

def area(x, u):
    c = u + 3
    return x*(3*x**2 + c*u**2) / (2*(x**2 + u**2))

for u in [5, 6, 7, 8, 9, 10, 12]:
    # Find root of eq(x, u) = 0 for x > 0
    xs = np.linspace(0.1, 50, 5000)
    vs = [eq(x, u) for x in xs]
    for i in range(len(xs)-1):
        if vs[i]*vs[i+1] < 0:
            root = brentq(eq, xs[i], xs[i+1], args=(u,))
            c = u + 3
            h = c*u/root
            a = area(root, u)
            same = "oui" if abs(u - root) < 0.01 else "non"
            print(f"u={u:5.2f}  c={c:5.2f}  x={root:7.4f}  h={h:7.4f}  Area={a:5.2f}  EC=CD? {same}")
            break
