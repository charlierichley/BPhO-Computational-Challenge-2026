# Renders z = 0 plane of hydrogenic orbitals using Matplotlib

import matplotlib.pyplot as plt
import numpy as np
from scipy.special import factorial, lpmv
from random import randint

# Physical constants
h = 6.62607015 * 1e-34
m_e = 9.1093837 * 1e-31
e = 1.60217663 * 1e-19
epsilon = 8.8541878188 * 1e-12
h_bar = h / (2 * np.pi)
u = 1.66053906660 * 1e-27

# Parameters / quantum numbers
Z = 1
n = 4
l = 2
A = 12
m = 0

M = A * u

def orbital(l):
    orbitals = {0:"s", 1:"p", 2:"d", 3:"f", 4:"g", 5:"h", 6:"i", 7:"k"}
    return orbitals[l].upper()

def coordinates(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    # could be a zero division error
    theta = np.arccos(z/r)
    phi = np.arctan2(y,x)
    return (r, theta, phi)

def choose_m(l):
    return randint(-l, l)

def reduced_mass(M):
    return m_e / ((m_e/M) + 1)

def zeta_term(x, l, n, k):
    numerator = factorial(l + n) * (-x)**k
    denominator = factorial(2*l + k + 1) * factorial(n-l-1-k) * factorial(k)
    return numerator/denominator

def zeta(x, l, n):
    return sum(zeta_term(x,l,n, k) for k in range(0, n-l))

def R(r, n, l):
    numerator = 4 * np.pi * epsilon * (h_bar**2)
    mu = reduced_mass(M)
    denominator = mu * Z * (e**2)
    a = numerator / denominator

    x = 2 * r / (a * n)
    t1 = np.sqrt(factorial(n-l-1) / (2*n * factorial(n+l)))
    t2 = (2 / (a*n))**(3/2)
    t3 = (x**l) * np.exp(-x/2)
    t4 = zeta(x, l, n)
    return t1 * t2 * t3 * t4

def Y(m, l, theta, phi):
    t1 = (-1) ** m
    numerator = (2*l + 1) * factorial(l-m)
    denominator = 4 * np.pi * factorial(l + m)
    t2 = np.sqrt(numerator/denominator)
    t3 = lpmv(m, l, np.cos(theta))
    t4 = np.exp(1j * m * phi)
    return t1 * t2 * t3 * t4

def omega(theta, phi, l, m):
    if m < 0:
        return Y(-m, l, theta, phi) - Y(m, l, theta, phi)
    if m == 0:
        return Y(0, l, theta, phi)
    # Else, m must be > 0
    return Y(m, l, theta, phi) + Y(-m, l, theta, phi)

def wave_function(n, l, m, theta, phi, r):
    return R(r, n, l) * omega(theta, phi, l, m)

x_max = 6
y_max = 6
x_min = -x_max
y_min = -y_max

n_points = 1000
x = np.linspace(x_min, x_max, n_points)
y = np.linspace(y_min, y_max, n_points)
X_PLOT = x
Y_PLOT = y
x = x * 1e-10
y = y * 1e-10
X_arr, Y_arr = np.meshgrid(x, y)
z = 0

r, theta, phi = coordinates(X_arr, Y_arr, z)
prob_density = np.abs(wave_function(n, l, m, theta, phi, r))**2
PD_PLOT = prob_density / prob_density.max()

mesh = plt.pcolormesh(X_PLOT, Y_PLOT, PD_PLOT, cmap="jet", shading="auto")
plt.gca().set_aspect("equal")
plt.colorbar(mesh, label=None)
plt.xlabel("x /Angstroms")
plt.ylabel("y /Angstroms")
orbital = orbital(l)
plt.title(f"Z={Z}, A={A}, orbital {n}{orbital}, M={m}") # Z = 0 slice

plt.show()