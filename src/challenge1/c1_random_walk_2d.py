# Visualisation of 2D random walks with n steps of size s using Matplotlib

import matplotlib.pyplot as plt
import numpy as np
from random import uniform

# Returns points of random walk
def random_walk(n: int, s: int):
    x = []
    y = []
    current_x = 0
    current_y = 0
    for i in range(n):
        x.append(current_x)
        y.append(current_y)
        angle = uniform(0, 2*np.pi)
        current_x += (s * np.cos(angle))
        current_y += (s * np.sin(angle))
    return [x, y]

# Adjusting the plot settings - axes, background etc.
plt.style.use("dark_background")
plt.xlim(-100, 100)
plt.ylim(-100, 100)
plt.xlabel('x')
plt.ylabel('y')

# Number of walks being plotted
iteration_number = 50

# Creating an array of colours from the matplotlib library, specifically the gist_ncar type.
colors = plt.cm.gist_ncar(np.linspace(0, 1, iteration_number))
n = 5000 # Step number
s = 1 # Step size
for i in range(iteration_number):
# Plotting the random walk
    t = random_walk(n, s)
    plt.plot(t[0], t[1], marker = "o", markersize = 0.1, markeredgecolor='none', linewidth = 0.35, color = colors[i])

# Increasing resolution and adjusting title
plt.savefig("random_walk.png", dpi=600)
plt.title(f"Random walk - {n} steps of size {s}")
plt.show()