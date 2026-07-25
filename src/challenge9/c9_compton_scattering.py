# Plot of Compton Scattering - fractional wavelength shift, electron recoil speed and electron recoil angle against photon scattering angle

import matplotlib.pyplot as plt
import numpy as np

m_e = 9.1093835611 * 1e-31
h = 6.62607004081 * 1e-34
c = 2.99792458 * 1e8
e = 1.602176620898 * 1e-19

def find_lamda(E):
    return (h * c) / E

def find_delta_lamda(theta):
    return (h * (1 - np.cos(theta))) / (m_e * c)

def find_lamda_dash(delta_lamda, lamda):
    return delta_lamda + lamda

def find_v(lamda, lamda_dash):
    numerator = m_e * (c**2)
    denominator = ((h * c) / lamda) - ((h*c)/lamda_dash) + numerator
    return c * np.sqrt(1 - ((numerator / denominator)**2))

def find_tan_phi(theta, lamda):
    numerator = np.sin(theta)
    denominator = 1 + ((h/(m_e * c * lamda)) * (1 - np.cos(theta))) - np.cos(theta)
    return numerator / denominator

def find_v_max(lamda):
   # Occurs at theta = 180 so the photon bounces back completely
   delta_lamda = find_delta_lamda(np.deg2rad(180))
   lamda_dash = find_lamda_dash(delta_lamda, lamda)
   v_max = find_v(lamda, lamda_dash)
   return v_max

plt.rcParams['toolbar'] = 'None'
fig = plt.figure(figsize=(10, 8))
fig.suptitle("Compton scattering of X-ray photon off an electron")
ax1 = plt.subplot(2, 2, 1)
ax2 = plt.subplot(2, 2, 2)
ax3 = plt.subplot(2, 1, 2)
fig.subplots_adjust(top=0.94, bottom=0.08, hspace=0.28, wspace=0.30)

# Fractional wavelength plot
ax1.grid(alpha=0.15)
ax1.margins(x=0)
ax1.set_xlabel("Photon scattering angle θ /deg")
ax1.set_ylabel(r"$\Delta \lambda / \lambda$")

energies = [50, 100, 200, 500, 1000] # unit: keV
for energy in energies:
    orig_energy = energy
    energy = energy * 1e3 * e
    theta_min = 0
    theta_max = 175
    n_points = 1000
    theta = np.linspace(theta_min, theta_max, 1000)
    theta = np.deg2rad(theta)
    fractional_lamda = find_delta_lamda(theta) / find_lamda(energy)
    ax1.plot(np.rad2deg(theta), fractional_lamda, label=f"{orig_energy}")

ax1.relim()
ax1.autoscale_view()
y_min, y_max = ax1.get_ylim()
CONST_LIMIT = -0.03
ax1.set_ylim(0, y_max * (1 + CONST_LIMIT))

# Recoil angle plot
ax2.grid(alpha=0.15)
ax2.margins(x=0)
ax2.set_xlabel("Photon scattering angle θ /deg")
ax2.set_ylabel(r"Electron recoil angle $\phi$ /deg")

for energy in energies:
   orig_energy = energy
   energy = energy * e * 1e3

   theta_min = 0.001
   theta_max = 175
   n_points = 1000
   theta = np.linspace(theta_min, theta_max, 1000)
   theta = np.deg2rad(theta)

   lamda = find_lamda(energy)

   tan_phi = find_tan_phi(theta, lamda)
   phi = np.rad2deg(np.arctan(tan_phi))

   ax2.plot(np.rad2deg(theta), phi, label=f"{orig_energy}")

# Recoil speed plot
ax3.grid(alpha=0.15)
ax3.margins(x=0)
ax3.set_xlabel("Photon scattering angle θ /deg")
ax3.set_ylabel("Electron recoil speed v/c")

energies = [50, 100, 200, 500, 1000] # unit: keV
for energy in energies:
   orig_energy = energy
   energy = energy * e * 1e3

   theta_min = 0
   theta_max = 175
   n_points = 1000
   theta = np.linspace(theta_min, theta_max, 1000)
   theta = np.deg2rad(theta)

   lamda = find_lamda(energy)
   delta_lamda = find_delta_lamda(theta)
   lamda_dash = find_lamda_dash(delta_lamda, lamda)
   v = find_v(lamda, lamda_dash) / c

   v_max = find_v_max(lamda) / c

   ax3.axhline(y = v_max, color='black', linestyle='--', alpha=0.5, linewidth=0.8)
   ax3.plot(np.rad2deg(theta), v, label=f"{orig_energy}")

ax1.legend(title="Photon energy / keV", framealpha=0.75)
ax2.legend(title="Photon energy / keV", framealpha=0.75)
ax3.legend(title="Photon energy / keV", framealpha=0.7)
plt.show()