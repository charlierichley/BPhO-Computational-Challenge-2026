import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from matplotlib.figure import Figure

k_B = 1.381 * (10**-23)
h = 6.626 * (10**-34)
R = 8.314

def heat_capacity(x):
    numerator = (x ** 2) * np.exp(x)
    denominator = (np.exp(x) - 1)
    return (3 * R * numerator / (denominator ** 2))

def calculate_T_E(T_D):
    return T_D * ((np.pi / 6) ** (1/3))

def calculate_x(T_D, T):
    f_E = k_B * calculate_T_E(T_D) / h
    x = h * f_E / (k_B *T)
    return x

elements = {}
elements["Gold"] = [170, "Au"]
elements["Copper"] = [343.5, "Cu"]
elements["Titanium"] = [420, "Ti"]
elements["Aluminium"] = [428, "Al"]
elements["Iron"] = [470, "Fe"]
elements["Silicon"] = [645, "Si"]
elements["Carbon"] = [2230, "C"]

plt.style.use("dark_background")
fig, ax = plt.subplots()
ax.set_title("Einstein model of heat capacity")
ax.set_xlabel("Temperature / K")
ax.set_ylabel("Molar heat capacity / J$mol^{-1}K^{-1}$")

dT = 0.1
T_min = 5
T_max = 800

def return_points(T_D):
    global dT, T_min, T_max
    T = T_min
    points = []
    while T < T_max:
        T += dT
        x = calculate_x(T_D, T)
        C = heat_capacity(x)
        points.append([T, C])
    return points

for element, lst in elements.items():
    T_D = lst[0]
    symbol = lst[1]
    points = np.array(return_points(T_D))
    line, = ax.plot(points[:, 0], points[:, 1], label=f"{element} ({symbol})")

plot = ax.get_position()
ax.set_position([plot.x0, plot.y0, plot.width * 0.8, plot.height])

ax.legend(loc="center left", bbox_to_anchor=(1,0.5))
plt.show()