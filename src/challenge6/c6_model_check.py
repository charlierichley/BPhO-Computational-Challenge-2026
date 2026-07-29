# Plotting 1 / sqrt(V) against sin(1/2 phi) and calculating gradient, to confirm atomic spacing d

import matplotlib.pyplot as plt
import numpy as np
from math import sqrt, asin, sin, floor
from matplotlib.lines import Line2D

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

def find_sin_phi_over_two(n, d, V):
    return n * h / (2 * d * sqrt(2 * m_e * e * V))

def find_nmax(wavelength, d):
    return floor(2 * d / wavelength)

def choose_colors(iteration_number):
    colors = plt.cm.gist_ncar(np.linspace(0, 0.95, iteration_number))
    return colors

# Setting up plot
plt.rcParams['toolbar'] = 'None'
fig, ax = plt.subplots(figsize=(8,5))
ax.grid(True, alpha=0.2)
ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0), useMathText=True)
ax.set_xlabel(r'$\sin\left(\frac{\phi}{2}\right)$', fontsize=13)
ax.set_ylabel(r'1/$\sqrt{V}$', fontsize=12)
ax.set_title(f"Model of electron diffraction rings: r = {int(r * 1e3)}mm")

d_legend = []
for indx, d in enumerate(d_list):
    voltages = np.arange(V_min, V_max, dV)
    points = []
    for V in voltages:
        lamda = wavelength(V)
        n_max = find_nmax (lamda, d)
        for n in range(1, n_max + 1):
            sin_phi_over_two = find_sin_phi_over_two(n, d, V)
            points.append([sin_phi_over_two, 1 / sqrt(V), n])

    dct = {}
    for lst in points:
        n = lst[2]
        if n in dct:
            dct[n].append(lst[:2])
        else:
            dct[n] = [lst[:2]]

    colors = choose_colors(len(dct))
    i = 0
    for n, lst in dct.items():
        arr = np.array(lst)
        x = arr[:, 0]
        y = arr[:, 1]
        if len(x) > 3:
            m, c = np.polyfit(x, y, 1)
            d_calculated = n * h * m / (2 * sqrt(2 * m_e * e))

        if indx == 0:
            if i == 0:
                ax.plot(x, y, color=colors[i], label=f"{n}")
                d_legend.append(d_calculated)
            else:
                ax.plot(x, y, color=colors[i], label=f"{n}")

        elif indx == 1:
            if i == 0:
                line, = ax.plot(x, y, color=colors[i], linestyle='dashed')
                d_legend.append(d_calculated)
            else:
                ax.plot(x, y, color=colors[i], linestyle='dashed')
        i += 1

handles = []
for i, d_calc in enumerate(d_legend):
    if i % 2 == 0:
        handles.append(Line2D([0],[0], color='black', linestyle='solid', label=f"d = {round(d_calc * 1e9, 3)}nm"))
    else:
        handles.append(Line2D([0],[0], color='black', linestyle='dashed', label=f"d = {round(d_calc * 1e9, 3)}nm"))

legend2 = fig.legend(loc='right', title="n")
fig.legend(handles=handles, loc='upper right')
fig.subplots_adjust(left=0.1, bottom=0.13)
plt.show()
