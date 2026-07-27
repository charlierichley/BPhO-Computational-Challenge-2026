# Animation of 3D hydrogenic orbitals morphing between m numbers at fixed n and l quantum numbers using PyVista

import pyvista as pv
import numpy as np
from scipy.special import factorial, lpmv

# Suggested quantum numbers (n,l): (7,6) (8,7) (6,5) (5,4) (4,3)
Z = 1
A = 1
n = 6
l = 5

# Animation parameters
m_min, m_max = -l, l
m_curr = m_min
scale_factor = 1
scale_factor_ds = 0.2

# Physical constants
h = 6.62607015 * 1e-34
m_e = 9.1093837 * 1e-31
e = 1.60217663 * 1e-19
epsilon = 8.8541878188 * 1e-12
h_bar = h / (2 * np.pi)
u = 1.66053906660 * 1e-27
a_0 = 5.29177210544 * 1e-11

M = A * u

# Orbital calculation functions
def coordinates(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(np.divide(z, r, out=np.zeros_like(r), where=r!=0))
    phi = np.arctan2(y,x)
    return (r, theta, phi)

def find_orbital(l):
    orbitals = {0:"s", 1:"p", 2:"d", 3:"f", 4:"g", 5:"h", 6:"i", 7:"k"}
    return orbitals[l].upper()

def find_index(m_min, m_curr):
    return m_curr - m_min

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
    numerator = (2*l + 1) * factorial(l-m)
    denominator = 4 * np.pi * factorial(l + m)
    t1 = np.sqrt(numerator/denominator)

    t2 = lpmv(m, l, np.cos(theta))
    t3 = np.exp(1j * m * phi)
    return t1 * t2 * t3

def omega(theta, phi, l, m):
    if m < 0:
        return Y(-m, l, theta, phi) - Y(m, l, theta, phi)
    if m == 0:
        return Y(0, l, theta, phi)
    return Y(m, l, theta, phi) + Y(-m, l, theta, phi)

def wave_function(n, l, m, theta, phi, r):
    return R(r, n, l) * omega(theta, phi, l, m)

def approximate_radius(n,l):
    # Source: https://phys.libretexts.org/Bookshelves/Quantum_Mechanics/Introductory_Quantum_Mechanics_(Fitzpatrick)/08%3A_Central_Potentials/8.03%3A_Hydrogen_Atom
    return (a_0 / 2) * (3*(n**2) - l*(l+1)) * 1e10  # Multiply by 1e10 to get it in plotting units (Angstroms)

# Initialise window
x_max_px, y_max_px = int(1000*1.5), int(900*1.5)
pv.global_theme.font.family = "times"
pl = pv.Plotter(window_size=(x_max_px, y_max_px), title="Hydrogenic Orbital")

# Graph settings
atom_size = approximate_radius(n, l) # in plotting units (Angstroms)
n_points = 100
CUTOFF = 0.15
coord_cutoff = 1.5 * atom_size
x_max = coord_cutoff
y_max = coord_cutoff
z_max = coord_cutoff
x_min = -x_max
y_min = -y_max
z_min = -z_max

# Initialising arrays
x = np.linspace(x_min, x_max, n_points)
y = np.linspace(y_min, y_max, n_points)
Z_arr = np.linspace(z_min, z_max, n_points)
X_PLOT, Y_PLOT = np.meshgrid(x, y)
x *= 1e-10
y *= 1e-10
Z_arr *= 1e-10
X_arr, Y_arr = np.meshgrid(x, y)

# Creating PD_PLOT with probability densities in 3D array (z, y, x)
PD_PLOT = np.zeros((m_max * 2 +1, n_points, n_points, n_points))
for m in range (m_min, m_max + 1):
    for indx, z in enumerate(Z_arr):
        r, theta, phi = coordinates(X_arr, Y_arr, z)
        wave_func = (np.abs(wave_function(n, l, m, theta, phi, r))) ** 2 # Born interpretation
        PD_PLOT[find_index(m_min, m)][indx] = wave_func

# Initiailise grid and axes
actors = []
title = None
finished = False
#pl.add_axes()
n_labels = 5
grd = pl.show_grid(xtitle="x", ytitle="y", ztitle="z", fmt="%.0f",
                   bounds=[x_min, x_max, y_min, y_max, z_min, z_max], n_xlabels=n_labels, n_ylabels=n_labels,
                   n_zlabels=n_labels)
opacity = 0.08
grd.GetXAxesGridlinesProperty().SetOpacity(opacity)
grd.GetYAxesGridlinesProperty().SetOpacity(opacity)
grd.GetZAxesGridlinesProperty().SetOpacity(opacity)

# Animation update function
def update_plot(step):
    global m_curr, scale_factor, scale_factor_ds, finished, CUTOFF, title, actors

    if finished:
        return

    # Stop rendering and remove old actors
    pl.suppress_rendering = True
    for actor in actors:
        pl.remove_actor(actor)
    actors = []

    # Move onto the next m value, using 1e-10 to combat floating point imprecision
    if scale_factor <= 1e-10:
        m_curr += 1
        scale_factor = 1

    if m_curr >= m_max:
        finished = True

    # Edit graph title
    try:
        orbital_str = str(n) + find_orbital(l)
    except KeyError:
        orbital_str = "N=" + str(n) + ", l=" + str(l)
    title_str = f"Z={Z}, A={A}, orbital {orbital_str}, M={m_curr}"
    title_str = '\n' + title_str

    if step == 0:
        # Create graph title
        title = pl.add_text(title_str, position='upper_edge', color='black', font_size=18)
    else:
        # Edit graph title
        title.set_text('upper_edge', title_str)

    curr_indx = find_index(m_min, m_curr)

    # Normalising the probabilities - scale 0 to 1
    if m_curr == m_max: # last m_curr value, so no interpolation
        PD_PLOT_curr = PD_PLOT[curr_indx]
        max_wave_func = np.max(PD_PLOT_curr)
        PD_PLOT_curr = PD_PLOT_curr / max_wave_func
        values = np.transpose(PD_PLOT_curr, (2, 1, 0))  # reverse the axes

    else: # interpolate between current and next PD_PLOT (probability) value
        PD_PLOT_curr = PD_PLOT[curr_indx]
        PD_PLOT_next = PD_PLOT[curr_indx + 1]
        PD_PLOT_interpolate = scale_factor * PD_PLOT_curr + (1 - scale_factor) * PD_PLOT_next
        max_wave_func = np.max(PD_PLOT_interpolate)
        PD_PLOT_interpolate = PD_PLOT_interpolate / max_wave_func
        values = np.transpose(PD_PLOT_interpolate, (2, 1, 0))  # reverse the axes

    # Plotting at every z slice
    is_first = True
    for indx, z in enumerate(Z_arr):
        slice_values = values[:, :, indx]
        grid = pv.StructuredGrid(X_PLOT, Y_PLOT, z / 1e-10 * np.ones_like(X_PLOT))

        grid["values"] = slice_values.ravel(order="F")
        visible = grid.threshold(CUTOFF, scalars='values')

        if visible.n_points != 0:
            # possible colourmaps: jet, turbo
            if is_first:
                scalar_args = dict(n_labels=10, fmt="%.1f", vertical=True, position_x=0.9, position_y=0.1, width=0.05,
                                   height=0.65, title=None)
            actor = pl.add_mesh(visible, scalars='values', clim=(0,1), cmap='jet', nan_opacity=0, opacity=0.5, show_scalar_bar=is_first, scalar_bar_args=scalar_args)
            actors.append(actor)
            is_first = False

    scale_factor -= scale_factor_ds
    pl.suppress_rendering = False

# Animation
n_frames = int((1/scale_factor_ds * (m_max - m_min))) + 1
pl.add_timer_event(max_steps=n_frames, duration=100, callback=update_plot)

# Adjusting view / angle
pl.camera_position = "iso"
pl.camera.elevation -= 10
pl.camera.zoom(0.92)
pl.show()
