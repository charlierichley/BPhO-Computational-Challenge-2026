# Plot of the Planck Spectrum

import numpy as np
import matplotlib.pyplot as plt

# Physical constants
k_B = 1.381 * (10**-23)
h = 6.626 * (10**-34)
c = 2.998 * (10**8)

# Planck's radiation law
def B(lamda, T):
    first_term = 2 * h * (c ** 2) / (lamda ** 5)
    exponential = np.exp(h * c / (lamda * k_B * T))
    return (first_term * (1 / (exponential - 1)))

# Initialising plot
plt.style.use("dark_background")
fig, ax = plt.subplots()
ax.set_title("Solar Irradiance vs Wavelength")
ax.set_xlabel("Wavelength / nm")
ax.set_ylabel("Irradiance / $Wm^{-2}/nm$")

def return_points(d_lamda, T):
    lamda = 100
    points = []
    while lamda < 2500:
        points.append([lamda, (B(lamda * 10 ** -9, T) * np.pi / 10 ** 9)])
        lamda += d_lamda
    return points

def choose_colors(n):
    colors = plt.cm.autumn(np.linspace(0, 1, n))
    return colors

d_lamda = 0.1
temperatures = [4000, 5000, 6000]
colors = choose_colors(len(temperatures))

for i, item in enumerate(temperatures):
    points = np.array(return_points(d_lamda, item))
    line, = ax.plot(points[:, 0], points[:, 1], label=f"{item} K", color = colors[i])

ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0), useMathText=True)
ax.legend()
plt.show()