# Plotting energy against quantum number n for a 'particle in a box'

import matplotlib.pyplot as plt
import numpy as np
from math import ceil

h = 6.62607015 * 1e-34
m_e = 9.1093837139 * 1e-31
a = 5 * 1e-11

fig, ax = plt.subplots(figsize=(8,5))
ax.grid(True, alpha=0.2)
ax.set_xlabel('Quantum number', fontsize=13)
ax.set_ylabel('Energy /eV', fontsize=12)
ax.set_title("Particle in a box - energy model")
ax.margins(x=0.02, y=0.03)

def find_energy(n):
   numerator = (h * n) ** 2
   denominator = 8 * m_e * (a ** 2)
   return numerator / denominator

def to_ev(E):
   return E * 6.241509e18

def dummy_curve(n_min, n_max):
   dN = (n_max - n_min) / 1000
   N_arr = np.arange(n_min, n_max + 1, dN)
   return N_arr

n_min = 0
n_max = 50
points = []
if n_min == 0:
   plt_n_min = 1
else:
   plt_n_min = n_min

for n in range(plt_n_min, n_max + 1):
   energy = to_ev(find_energy(n))
   points.append([n, energy])

N_array = dummy_curve(n_min, n_max)
energies = to_ev(find_energy(N_array))
ax.plot(N_array, energies, color='#2186cf', linestyle=(0, (1.2, 0.6)), alpha=0.75)

E_max = max(energies)
n_points = len(points)
points_max = 50

if E_max > 1e5:
   ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0), useMathText=True)

if n_points > points_max:
   n = ceil(n_points / points_max)
   points = points[::n]

points = np.array(points)
ax.plot(points[:, 0], points[:, 1], linestyle='None', marker='x', markersize=4)
plt.show()