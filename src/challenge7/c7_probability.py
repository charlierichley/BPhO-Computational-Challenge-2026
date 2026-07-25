# Plotting probability density against x for a 'particle in a box'

import matplotlib.pyplot as plt
import numpy as np

def prob(a, n, x):
    return 2 * ((np.sin(n * np.pi * x / a))**2) / a

# Initialising plot
fig, ax = plt.subplots(figsize=(8,5))
ax.grid(True, alpha=0.2)
ax.set_xlabel('x /angstroms', fontsize=13)
ax.set_ylabel('Probability density', fontsize=12)
ax.set_title("Particle in a box - probability model")
ax.margins(x=0, y=0)
ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0), useMathText=True)

a = 5 * 1e-11
n_min = 1
n_max = 3
n_arr = np.arange(n_min, n_max + 1, 1)
n_points = 1000
x_arr = np.linspace(0, a, n_points)

for n in n_arr:
    # Plot the probability at each n at each x.
    ax.plot(x_arr * 1e10, prob(a, n, x_arr), label=f"n = {n}")

ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5))
plt.subplots_adjust(right=0.85)
plt.show()