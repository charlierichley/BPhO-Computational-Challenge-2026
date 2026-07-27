# 2D Brownian motion simulation
# N particles mass m radius r moving randomly,
# with one larger particle mass M radius R.

from random import uniform
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib.patches import Circle

# Physical constants
particle_ratio = 5 # Ratio between radii of small and large particle
N_particles = 300
T = 100 # temperature in C
avogadro = 6.022 * (10 ** 23)
m = (28.96 * (10 ** -3)) / avogadro # mass of the smaller particles
M = particle_ratio * m # mass of large particle
r = 0.16 # radius of small particle
R = particle_ratio * r # radius of larger particle
C = 1 # coefficient of restitution (changing the 'stickiness' of collisions)
k_B = 1.38 * (10 ** -23) # Boltzmann's constant
v = np.sqrt(3 * k_B *(T + 273) / m) # velocity of smaller particles
V = np.sqrt( 3 * k_B * (T + 273) / M) # velocity of large particle
Kn = 15 # Knudsen's number
v = v / 1000
V = V / 1000
a = 7 * R
x_max = a
y_max = a
x_min = 0
y_min = 0

dt = 0.01 * Kn * r / v
t_max = 200 # picoseconds

velocities = []
positions = []
plt.tight_layout()

large_x = a / 2
large_y = a / 2
v2_angle = uniform(0, 2 * np.pi)
vx2 = V * np.cos(v2_angle)
vy2 = V * np.sin(v2_angle)

const = 5.6
buffer = (0.035 * const / a)

def distance_between(x1, y1, x2, y2):
    return np.sqrt((x2-x1)**2 + (y2-y1) **2)

def randomize_velocities(p, velocity, N, large_x, large_y):
    for i in range(N):
        angle = uniform(0, 2 * np.pi)
        while True:
            position_x = uniform(x_min + buffer, x_max - buffer)
            position_y = uniform(y_min + buffer, y_max - buffer)
            # We need to check that the balls are not overlapping
            if distance_between(large_x, large_y, position_x, position_y) > (r + R):
                p.append([position_x, position_y])
                break
        velocity.append([v * np.cos(angle), v * np.sin(angle)])
    return

randomize_velocities(positions, velocities, N_particles, large_x, large_y)

small_size = 30
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("2D Brownian Motion Simulation")
pos_array = np.array(positions)
scat_small = ax.scatter(pos_array[:, 0], pos_array[:, 1], marker='.', color='blue', s=small_size)
line2 = ax.plot(large_x, large_y, color='red', linewidth='1')[0]

large_circle = Circle((large_x, large_y), R, edgecolor='red', facecolor='none')
ax.add_patch(large_circle)

def bounce(x1,y1,vx1,vy1, m1, R1, x2, y2, vx2, vy2, m2, R2, C):
    d = distance_between(x1, y1, x2, y2)
    effective_radius = 0.2
    if d <= (effective_radius * R1 + R2): # there is a collision
        vector = np.array([x2 - x1, y2 - y1])

        # Convert x and y speeds into an initial velocity vector
        position_1 = np.array([x1, y1])
        position_2 = np.array([x2, y2])
        u1 = np.array([vx1, vy1])
        u2 = np.array([vx2, vy2])
        mag = np.linalg.norm(vector)
        if mag != 0:
            unit_vector = vector / mag  # the unit vector between the two particles
        else:
            return False
        dx = x2 - x1
        dy = y2 - y1

        delta = (effective_radius * R1 + R2 - d) / 2
        unit_vector_1 = (-1 * delta * unit_vector)
        unit_vector_2 = (delta * unit_vector)
        vector_1 = position_1 + unit_vector_1
        vector_2 = position_2 + unit_vector_2
        x_1 = vector_1[0]
        y_1 = vector_1[1]
        x_2 = vector_2[0]
        y_2 = vector_2[1]

        # Dot product between velocities and unit vector between particles
        if np.dot(u2 - u1, unit_vector) < 0:
            V = (m1*u1 + m2*u2) / (m1 + m2)
            v1 = V - C*(u1-V)
            v2 = V - C*(u2-V)
            vx1 = v1[0]
            vy1 = v1[1]
            vx2 = v2[0]
            vy2 = v2[1]
            return [vx1, vy1, vx2, vy2, x_1, y_1, x_2, y_2]
        else:
            return [x_1, y_1, x_2, y_2]
    return False
    # we must return the new positions and velocties

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_aspect('equal', adjustable='box')
past_positions = []

# Threshold for randomizing the velocities of small particles
time_threshold = 3 * (Kn * r / v)
t = 0

def update(frame):
    global t, large_x, large_y, vx2, vy2

    t += dt
    # Randomizing velocities of smaller particles
    if t > time_threshold:
        t = 0
        for lst in velocities:
            angle = uniform(0, 2 * np.pi)
            lst[0] = v * np.cos(angle)
            lst[1] = v * np.sin(angle)

    if (large_x <= x_min + R or large_x >= x_max - R): # collision with x axis
        vx2 *= -1
    if (large_y <= y_min + R or large_y >= y_max - R): # collision with y axis
        vy2 *= -1

    past_positions.append([large_x, large_y])
    counter = 0
    large_x += (vx2 * dt)
    large_y += (vy2 * dt)
    for counter, lst in enumerate(positions):
        vx1 = velocities[counter][0]
        vy1 = velocities[counter][1]
        lst[0] += (vx1 * dt)
        lst[1] += (vy1 * dt)

        # Bounce function
        x1 = lst[0]
        y1 = lst[1]
        bounce_list = bounce(x1, y1, vx1, vy1, m, r, large_x, large_y, vx2, vy2, M, R, C)
        if (bounce_list) != False:
            length = len(bounce_list)
            if length == 8:
                velocities[counter][0] = bounce_list[0]
                velocities[counter][1] = bounce_list[1]
                vx2 = bounce_list[2]
                vy2 = bounce_list[3]
                lst[0] = bounce_list[4]
                lst[1] = bounce_list[5]
                large_x = bounce_list[6]
                large_y = bounce_list[7]
            elif length == 4:
                lst[0] = bounce_list[0]
                lst[1] = bounce_list[1]
                large_x = bounce_list[2]
                large_y = bounce_list[3]

        # Making sure the particle does not leave the box (collision with boundary)
        if lst[0] > (x_max - buffer) or lst[0] < (0 + buffer):
            velocities[counter][0] *= -1
            lst[0] += (velocities[counter][0] * dt)
        if lst[1] > (y_max - buffer) or lst[1] < (0 + buffer):
            velocities[counter][1] *= -1
            lst[1] += (velocities[counter][1] * dt)

    data1 = np.stack(positions)
    scat_small.set_offsets(data1)

    data2 = np.array(past_positions)
    line2.set_data(data2[:, 0], data2[:, 1])
    large_circle.center = (large_x, large_y)
    return (scat_small, large_circle, line2)

ani = animation.FuncAnimation(fig=fig, func=update, frames=int(t_max / dt), interval= 50)
plt.show()
