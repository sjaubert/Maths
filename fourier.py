import numpy as np

T  = 2
N  = 10000
dt = T / N
t  = np.arange(-T/4, T/4 + dt/2, dt)     # support of the pulse
f  = np.ones_like(t)                     # f = 1 on the support

dw = 0.05
w  = np.arange(-1000, 1000 + dw/2, dw)   # frequency grid

def compute_fourier_transform(t, f, w):
    dt = t[1] - t[0]
    return np.sum(f * np.exp(-1j*w*t)) * dt   # transform at one frequency

f_hat = np.zeros(len(w), dtype=complex)
for k in range(len(w)):
    f_hat[k] = compute_fourier_transform(t, f, w[k])

E  = np.sum(f*f) * dt                             # energy in time
Ef = np.sum(np.abs(f_hat)**2) * dw / (2*np.pi)    # energy in frequency
print(E)
print(Ef)