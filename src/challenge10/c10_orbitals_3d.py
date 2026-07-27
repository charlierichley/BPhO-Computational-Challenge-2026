# Renders hydrogenic orbitals in 3D using PyVista

import pyvista as pv
import numpy as np
from scipy.special import factorial, lpmv

# Choosing quantum numbers
Z = 1
A = 1
m = 3
n = 8
l = 7
# Suggested parameters (n,l) with m=l: (7,6) (8,7) (6,5) (5,4) (4,3)

# Physical constants
h = 6.62607015 * 1e-34
m_e = 9.1093837 * 1e-31
e = 1.60217663 * 1e-19
epsilon = 8.8541878188 * 1e-12
h_bar = h / (2 * np.pi)
u = 1.66053906660 * 1e-27

# Orbital calculation functions
def coordinates(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(np.divide(z, r, out=np.zeros_like(r), where=r!=0))
    phi = np.arctan2(y,x)
    return (r, theta, phi)

def orbital(l):
    orbitals = {0:"s", 1:"p", 2:"d", 3:"f", 4:"g", 5:"h", 6:"i", 7:"k"}
    return orbitals[l].upper()

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
    return Y(m, l, theta, phi) + Y(-m, l, theta, phi)

def wave_function(n, l, m, theta, phi, r):
    return R(r, n, l) * omega(theta, phi, l, m)

# Graph settings
n_points = 250
CUTOFF = 0.15
x_max = 45
y_max = 45
z_max = 45
x_min = -x_max
y_min = -y_max
z_min = -z_max

x = np.linspace(x_min, x_max, n_points)
y = np.linspace(y_min, y_max, n_points)
Z_arr = np.linspace(z_min, z_max, n_points)
X_PLOT, Y_PLOT = np.meshgrid(x, y)
x *= 1e-10
y *= 1e-10
Z_arr *= 1e-10
X_arr, Y_arr = np.meshgrid(x, y)

# Creating PD_PLOT with probability densities in 3D array (z, y, x)
M = A * u
PD_PLOT = np.zeros((n_points, n_points, n_points))
for indx, z in enumerate(Z_arr):
    r, theta, phi = coordinates(X_arr, Y_arr, z)
    wave_func = (np.abs(wave_function(n, l, m, theta, phi, r))) ** 2
    PD_PLOT[indx] = wave_func

# Normalising the probabilites - scale 0 to 1
max_wave_func = np.max(PD_PLOT)
PD_PLOT = PD_PLOT / max_wave_func
values = np.transpose(PD_PLOT, (2,1,0)) # reverse the axes
x_max_px, y_max_px = int(1000*1.5), int(900*1.5)
pl = pv.Plotter(window_size=(x_max_px, y_max_px), title="Hydrogenic Orbital")

# Plotting at every z slice
for indx, z in enumerate(Z_arr):
    slice_values = values[:, :, indx]
    grid = pv.StructuredGrid(X_PLOT, Y_PLOT, z / 1e-10 * np.ones_like(X_PLOT))

    grid["values"] = slice_values.ravel(order="F")
    visible = grid.threshold(CUTOFF, scalars='values')

    scalar_args = dict(n_labels=10, fmt="%.1f", vertical=True, position_x=0.9, position_y=0.1, width=0.05, height=0.65, title=None)
    if visible.n_points != 0:
        # possible colourmaps: jet, turbo
        pl.add_mesh(visible, scalars='values', cmap='jet', nan_opacity=0, opacity=0.5, show_scalar_bar=True, scalar_bar_args=scalar_args)

# Adjusting graph layout
#pl.add_axes()
orbital = orbital(l)
pv.global_theme.font.family = "times"
title = pl.add_title(f"Z={Z}, A={A}, orbital {n}{orbital}, M={m}")

n_labels = 5
grd = pl.show_grid(xtitle="x", ytitle="y", ztitle="z", fmt="%.0f", bounds=[x_min, x_max, y_min, y_max, z_min, z_max], n_xlabels=n_labels, n_ylabels=n_labels, n_zlabels=n_labels)
opacity = 0.08
grd.GetXAxesGridlinesProperty().SetOpacity(opacity)
grd.GetYAxesGridlinesProperty().SetOpacity(opacity)
grd.GetZAxesGridlinesProperty().SetOpacity(opacity)

# Adjusting view / angle
pl.camera_position = "iso"
pl.camera.elevation -= 10
pl.camera.zoom(0.92)
pl.show()
pl.screenshot("3d_orbital_plot.png", scale=10)
