# Physics functions for photoelectric effect simulation

import numpy as np

from c4_ext_shared import *

def threshold_frequency(W):
    return W / h

def photon_energy_f(f):
    return h * f

def photon_energy_lamda(lamda):
    return h * c / lamda

def is_emitted(E, W):
    if E > W:
        return True
    return False

def find_K_max(f, W):
    if is_emitted(photon_energy_f(f), W):
        return h*f - W
    else: return 0

def find_V_stopping(f, W):
    if is_emitted(photon_energy_f(f), W):
        return np.abs(((h * f)-W)/e)
    else: return 0

def update_velocity(v, a, dt):
    return v + (a * dt)

def update_position(x, v, dt):
    return x + (v * dt)

def find_acceleration(V, d):
    return (e * V)/(m_e * d)

def find_current(N, dt):
    return (N * e)/dt

def find_v(E):
    return np.sqrt((2*E)/m_e)

def reset_particles(is_active,pos, vel, acc, energy, d):
    # If particle x value is not in range 0 to d, reset it as it either has reached right plate, or gone back into left plate
    mask = (pos[:, 0] >= d) | (pos[:, 0] < 0)
    is_active[mask] = False
    pos[mask, 0] = 0
    pos[mask, 1]= 0
    vel[mask] = 0
    acc[mask] = 0
    energy[mask] = 0