# Plot of photon energy vs wavelength of photon emissions from hydrogen atoms, due to transitions between electron energy levels

import matplotlib.pyplot as plt

# Physical constants
h = 6.626e-34
c =  299792458

def photon_energy(n):
    return -13.6 / (n ** 2)

def energy_transition(n, m):
    return photon_energy(n) - photon_energy(m)

def wavelength(E):
    return h * c / (E * 1.602e-19)

# Initialising plot
#plt.rcParams['toolbar'] = 'None'
plt.tight_layout()
plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(9,6))
ax.grid(True, alpha=0.17)
ax.set_xlabel("Wavelength /nm")
ax.set_ylabel("Photon energy /eV")
ax.set_title("Bohr model of Hydrogenic atom photon emissions: Z = 1")

# Spetral lines of hydrogen
m_list = [(1, "red"), (2, "orange"), (3, "blue"), (4, "green"), (5, "white")]
m_dict = {1: "Lyman", 2: "Balmer", 3: "Paschen", 4: "Brackett", 5: "Pfund"}

for m, color in m_list:
    n_min = m + 1
    name = m_dict[m]
    if m == 1:
        alpha_vline = 0.5
    else:
        alpha_vline = 0.73
    for n in range(n_min, n_min + 12):
        E = energy_transition(n, m)
        lamda = wavelength(E) * 1e9
        if n == n_min:
            ax.scatter(lamda, E, color=color, s=10, marker='o', linewidths=0.5, label=f"{name}")
        else:
            ax.scatter(lamda, E, color=color, s=10, marker='o', linewidths=0.5)
        ax.vlines(lamda, ymin=0, ymax=E, linestyles=(0, (1, 0.5)), colors=color, linewidth=1.5, alpha=alpha_vline)

# Adjusting plot
ax.set_ylim(0, None)
ax.legend(loc='upper right')
ax.set_xlim(0, 3500)
plt.show()