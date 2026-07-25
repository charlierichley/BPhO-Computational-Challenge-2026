# Computer model of electron diffraction rings on phosphor screen, plotting radius x against voltage V

import matplotlib.pyplot as plt
import numpy as np
from math import sqrt, asin, sin, floor

# Physical constants
r = 65 * 1e-3
d_list = [0.123 * 1e-9, 0.213 * 1e-9]
V_min = 1 * 1e3
V_max = 5 * 1e3
dV = 0.1 * 1e3
h = 6.62607015 * 1e-34
m_e = 9.1093837 * 1e-31
e = 1.60217663 * 1e-19

def wavelength(V):
    denominator = sqrt(2 * m_e * e * V)
    return h / denominator

def find_angle(wavelength, n, d):
    x = n * wavelength / (2 * d)
    if x > 1: # cannot compute arcsin(x) if x > 1 so the ring doesn't exist
        return False
    phi = asin(x) * 2
    return phi

def find_R(phi):
    return r * sin(phi)

def find_nmax(wavelength, d):
    return floor(2 * d / wavelength)

def choose_colors(iteration_number):
    colors = plt.cm.gist_ncar(np.linspace(0, 0.95, iteration_number))
    return colors

d = d_list[0] # choosing d (atomic spacing)
voltages = np.linspace(V_min, V_max, int((V_max - V_min) / dV))

# Initialising plot
fig, ax = plt.subplots(figsize=(9,5))
ax.grid(True, alpha=0.17)
ax.set_xlabel("Accelerating voltage /V")
ax.set_ylabel("Radii of rings /m")
ax.set_title(f"Model of electron diffraction rings: d = {round(d * 1e9, 3)}nm, r = {int(r * 1e3)}mm")

# At every voltage, plot all possible rings and store the points and n values in dictionary
points = []
dct = {}
for V in voltages:
    lamda = wavelength(V)
    phi = True
    n_max = find_nmax (lamda, d)
    for n in range(1, n_max + 1):
        phi = find_angle(lamda, n, d)
        R = find_R(phi)
        if n in dct:
            dct[n].append([V, R])
        else:
            dct[n] = [[V, R]]

colors = choose_colors(len(dct))
i = 0
for n, lst in dct.items():
    arr = np.array(lst)
    ax.plot(arr[:,0], arr[:,1], color=colors[i], label=f"{n}")
    i += 1

fig.legend(title="n", loc='outside right')
plt.show()