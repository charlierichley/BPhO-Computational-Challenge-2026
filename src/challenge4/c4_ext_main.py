# Photoelectric effect simulation using Pygame

from c4_ext_drawing import *
from c4_ext_physics import *
from c4_ext_shared import *

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame
import numpy as np
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.dropdown import Dropdown
import colour

# Initialising window
pygame.init()
x_max, y_max = (900, 600)
screen = pygame.display.set_mode((x_max, y_max))
pygame.display.set_caption("Photoelectric Effect Simulation")
title_font = pygame.font.SysFont("arial", 32, bold=True)
background_color = (255, 255, 255)

# Get data for metals from a CSV file
with open("work_functions.csv") as my_file:
    data = my_file.read().splitlines()

# Work functions data processed into a dictionary
work_functions = {}
metals = []
for line in data:
    line = line.split(",")
    if line[0] != "Material":
        work_functions[line[0]] = float(line[1])
        metals.append(line[0])

# Load battery
battery = pygame.image.load("battery.png").convert_alpha()
battery = pygame.transform.rotate(battery, 90)
b_w, b_h = battery.get_size()
b_sf = 0.2
battery = pygame.transform.scale(battery, (b_sf * b_w, b_sf * b_h))

# Load lamp
lamp = pygame.image.load("lamp.png").convert_alpha()
lamp = pygame.transform.rotate(lamp, 18)
l_w, l_h = lamp.get_size()
l_sf = 0.17
lamp = pygame.transform.scale(lamp, (l_sf * l_w, l_sf * l_h))

# Load ammeter
ammeter = pygame.image.load("ammeter.png").convert_alpha()
a_w, a_h = ammeter.get_size()
a_sf = 0.13
ammeter = pygame.transform.scale(ammeter, (a_sf * a_w, a_sf * a_h))

setup_dict = draw_setup(screen, battery, lamp, ammeter)
left_cutoff = setup_dict["left_cutoff"]
right_cutoff = setup_dict["right_cutoff"]
bx = setup_dict["bx"]
by = setup_dict["by"]

# Initial physical parameters
d = 0.05 # metres
intensity = 100 # intensity
lamda = 430 * 1e-9 # metres
f = c / lamda
N_electrons = 90
metal = "Sodium (Na)"
work_function = work_functions[metal] * e
K_max = find_K_max(f, work_function)

# Visual parameters
const_electron_emission = 0.1
pixel_d = right_cutoff - left_cutoff
m_per_pixel = d / pixel_d
visual_time_scale = 0.000001 / 50
plate_buffer = 0.83
emission_buffer = 0.0
const_current_scale = 1e18 / 3
max_alpha = 150

rgb_colour = find_rgb_colour(lamda * 1e9)
alpha = find_alpha(intensity, 0, max_alpha)
V_stopping = find_V_stopping(f, work_function)

# For each electron: store kinetic energy, position, velocity, acceleration.
energies = np.zeros(N_electrons)
positions = np.zeros((N_electrons, 2)) # initial position is at x = 0, with y later chosen uniformly in the range between plate_bottom and plate_top
velocities = np.zeros(N_electrons)
accelerations = np.zeros(N_electrons)
active = np.zeros(N_electrons, dtype=bool) # if electrons are in motion, or have they already reached detector / not been emitted yet

# Initialising arrays for calculating current
past_hits = []
past_currents = []
avg_current = 0
current_arr_size = 30

# Drawing essentials (metals dropdown menu, sliders)
metal_dropdown = draw_metal_choices(screen, metals, initial_metal=metal)["metal_dropdown"]
sliders_dict = create_sliders(screen, bx, by, display_font, V=0, intensity=100, wavelength=lamda)
voltage_slider = sliders_dict["voltage_slider"]
intensity_slider = sliders_dict["intensity_slider"]
wavelength_slider = sliders_dict["wavelength_slider"]

running = True
clock = pygame.time.Clock()
frames = 0

while running:
    dt = clock.tick(60) / 1000 # dt in seconds
    screen.fill(background_color)
    intensity_changed = False
    lamda_changed = False

    # Draw setup and obtain necessary parameters from the returned dictionary
    setup_dict = draw_setup(screen, battery, lamp, ammeter)
    left_cutoff = setup_dict["left_cutoff"]
    right_cutoff = setup_dict["right_cutoff"]
    plate_top = setup_dict["plate_top"]
    plate_bottom = setup_dict["plate_bottom"]

    V = voltage_slider.getValue()
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # Check if wavelength slider has changed, and if it has, update lamda
    if slider_changed(wavelength_slider, lamda * 1e9):
        lamda = wavelength_slider.getValue() * 1e-9
        f = c / lamda
        K_max = find_K_max(f, work_function)
        lamda_changed = True

    E_photons = photon_energy_lamda(lamda)

    # In each timestep dt, update arrays of energies, positions, velocities, accelerations.
    for indx, active_status in enumerate(active):
        if active_status == True:

            # Find acceleration due to electric field
            acceleration = find_acceleration(V, d)
            accelerations[indx] = acceleration

            # Update positions and velocities
            velocities[indx] += acceleration * dt * visual_time_scale
            velocity = velocities[indx]
            positions[indx][0] += velocity * dt * visual_time_scale

    # Check if electrons are emitted
    if E_photons > work_function:

        emission_buffer += const_electron_emission * intensity * dt
        n_emitted = int(emission_buffer)
        emission_buffer -= n_emitted
        new_energies = np.random.uniform(0, K_max, size=n_emitted)

        # Emit electrons until counter reaches n_emitted
        counter = 0
        for indx, active_status in enumerate(active):
            if counter == n_emitted:
                break

            if active_status == False:
                active[indx] = True

                # Updating values of the emitted electrons
                new_energy = new_energies[counter]
                energies[indx] = new_energy
                velocities[indx] = find_v(new_energy)

                individual_plate_buffer = (1 - plate_buffer) / 2
                plate_height = plate_bottom - plate_top

                plate_top_buffer = plate_top + individual_plate_buffer * plate_height
                plate_bottom_buffer = plate_bottom - individual_plate_buffer * plate_height

                # Choose y coordinate of emitted electron
                positions[indx][1] = np.random.uniform(plate_bottom_buffer, plate_top_buffer)

                counter += 1

    # Count number of hits of electrons to right detector
    hits = np.sum(active & (positions[:, 0] >= d))

    # Reset all particles
    reset_particles(active, positions, velocities, accelerations, energies, d)

    # Animate each electron
    draw_electrons(screen, positions, active, left_cutoff, m_per_pixel)

    # Draw voltage display (text box)
    v_str = str(round(V, 1)) + " V"
    voltage_text = display_font.render(v_str, True, (0,0,0))
    voltage_box = pygame.Rect(bx + 23, by + 73, 60, 20)
    pygame.draw.rect(screen, (0,0,0), voltage_box, width=2)
    voltage_text_rect = voltage_text.get_rect(center=voltage_box.center)
    screen.blit(voltage_text, voltage_text_rect)

    # Update intensity slider
    if slider_changed(intensity_slider, intensity):
        intensity = intensity_slider.getValue()
        intensity_changed = True

    # Draw text boxes for intensity and wavelength
    update_intensity_slider(screen, intensity)
    update_wavelength_slider(screen, lamda * 1e9)

    # Update metal choice
    new_metal = metal_dropdown.getSelected()
    if new_metal is not None:
        # Calculating new work function and K_max of the metal
        metal = new_metal
        work_function = work_functions[metal] * e
        K_max = find_K_max(f, work_function)

    # Update current display (in arbitrary units)
    current = find_current(hits, dt) * const_current_scale

    if len(past_currents) < current_arr_size:
        past_currents.append(current)
    else:
        past_currents.pop(0)
        past_currents.append(current)

    if frames % 30 == 0:
        avg_current = np.mean(past_currents)

    update_current(screen, avg_current, smaller_font)

    if lamda_changed or intensity_changed:
        lamda_nm = lamda * 1e9

        if 360 <= lamda_nm <= 780:
            # Visible light
            rgb_colour = find_rgb_colour(lamda_nm)
        elif lamda_nm > 780:
            # IR radiation
            rgb_colour = (200, 200, 200)
        else:
            # UV radiation
            rgb_colour = (180, 180, 180)

        # Scale intensity with alpha between 0 and max_alpha
        alpha = find_alpha(intensity, 0, max_alpha)

    # Draw information panel
    V_stopping = find_V_stopping(f, work_function)
    draw_info_panel(screen, metal, E_photons, V_stopping, work_functions, intensity)

    # Draw lamp last so it does not interfere with other objects
    # Coordinates: (lamp_l, lamp_r, bottom_buffer, top_buffer)
    draw_lamp_light(screen, (260, 75), (312, 100), (201.5, 296.25), (201.5, 171.75), rgb_colour + (alpha, ))

    frames += 1
    pygame_widgets.update(events)
    pygame.display.update()
