# Drawing functions for photoelectric effect simulation

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

# Finds alpha (opacity) on a scale from alpha_min to alpha_max and proportional to intensity
def find_alpha(intensity, alpha_min, alpha_max):
    return alpha_min + (intensity / 100) * (alpha_max - alpha_min)

# Finds RGB tuple (colour) based off of a wavelength in the range of 360-780nm
def find_rgb_colour(lamda_nm):
    xyz = colour.wavelength_to_XYZ(lamda_nm)
    rgb_colour = colour.XYZ_to_sRGB(xyz)
    rgb_colour = np.clip(rgb_colour, 0, 1)
    rgb_colour = tuple((rgb_colour * 255).astype(int))
    return rgb_colour

# Renders a given string at a given point
def render_text(screen, center, string, font):
    text = font.render(string, True, (0,0,0))
    rect = text.get_rect(center=center)
    screen.blit(text, rect)

# Checks if a Pygame widget slider's value has changed
def slider_changed(slider, old):
    new = slider.getValue()
    return (new != old)

# Draws setup of scene: wires, lamp, battery, ammeter, plates, vacuum tube
def draw_setup(screen, battery, lamp, ammeter):
    # Updating l_w, l_h, b_w, b_h
    b_w, b_h = battery.get_size()
    l_w, l_h = lamp.get_size()

    bx, by = (330, 420)

    # Draw battery, lamp and ammeter
    screen.blit(battery, (bx, by))
    rect_l = lamp.get_rect(center=(300,50))
    screen.blit(lamp, rect_l)
    screen.blit(ammeter, (575, 423))

    # Drawing vacuum tube
    tube_color = 0x000000
    w_ellipse = 19
    h_ellipse = 200
    tube_horiz_width = 1
    plate_width = 20
    plate_height = 150

    # Left side of tube
    cx1, cy1 = (180, 234)
    pygame.draw.ellipse(screen, tube_color, rect=(cx1-w_ellipse/2, cy1 - h_ellipse/2,w_ellipse,h_ellipse), width=2)

    # Right side of tube
    cx2, cy2 = (550, 234)
    pygame.draw.ellipse(screen, tube_color, rect=(cx2-w_ellipse/2, cy2 - h_ellipse/2,w_ellipse,h_ellipse), width=2)

    # Horizontal part of vacuum tube
    y_ellipse_top_left = cy1 - h_ellipse / 2
    y_ellipse_top_right = cy2 - h_ellipse / 2

    pygame.draw.line(screen, tube_color, (cx1,y_ellipse_top_left), (cx2, y_ellipse_top_right), tube_horiz_width)
    pygame.draw.line(screen, tube_color, (cx1,y_ellipse_top_left + h_ellipse), (cx2, y_ellipse_top_right + h_ellipse), tube_horiz_width)

    # Draw wires
    wire_color = (139, 90, 43)
    wire_width = 8
    wire_y_difference = 216
    const_horiz_wire_tube = 2
    const_horiz_right_wire = 150

    # Left horizontal wire coming out of postive terminal
    pygame.draw.line(screen, wire_color, (330, 450), (116, 450), wire_width)

    # Left vertical wire up to the required height for vacuum tube
    pygame.draw.line(screen, wire_color, (119, 450), (119, 450 - wire_y_difference), wire_width)

    # Left horizontal wire into vacuum tube
    left_plate_cx, left_plate_cy = cx1 + w_ellipse/2 + const_horiz_wire_tube, cy1
    pygame.draw.line(screen, wire_color, (116,234), (left_plate_cx, left_plate_cy), wire_width)

    # Left plate (rectangle)
    left_plate_x = left_plate_cx - plate_width / 2
    left_plate_y = left_plate_cy - plate_height / 2

    pygame.draw.rect(screen, tube_color, (left_plate_x, left_plate_y, plate_width,plate_height), width=2, border_radius=4)

    # Right horizontal wire out of vacuum tube
    right_plate_cx, right_plate_cy = cx2 - w_ellipse/2 - const_horiz_wire_tube, cy2
    pygame.draw.line(screen, wire_color, (right_plate_cx, right_plate_cy), (right_plate_cx + const_horiz_right_wire + 4, right_plate_cy), wire_width)

    # Right plate (rectangle)
    right_plate_x = right_plate_cx - plate_width / 2
    right_plate_y = right_plate_cy - plate_height / 2

    pygame.draw.rect(screen, tube_color, (right_plate_x, right_plate_y, plate_width, plate_height), width=2, border_radius=4)

    # Right vertical wire down to height of battery
    pygame.draw.line(screen, wire_color, (right_plate_cx + const_horiz_right_wire, right_plate_cy), (right_plate_cx + const_horiz_right_wire, right_plate_cy + wire_y_difference), wire_width)

    # Right horizontal wire into ammeter from right side
    const_ammeter_y = right_plate_cy + wire_y_difference
    pygame.draw.line(screen, wire_color, (right_plate_cx + const_horiz_right_wire + 4, const_ammeter_y), (626, const_ammeter_y), wire_width)

    # Right horizontal wire leaving ammeter into negative terminal of battery
    pygame.draw.line(screen, wire_color, (575, const_ammeter_y), (432, const_ammeter_y), wire_width)

    return {
        "left_cutoff": left_plate_x + plate_width,
        "right_cutoff": right_plate_x,
        "plate_top": left_plate_y,
        "plate_bottom": left_plate_y + 150,
        "bx": bx,
        "by": by,
    }

# Converts metres to pixels by a given scale (m_per_pixel)
def m_to_px(x, m_per_pixel):
    return x / m_per_pixel

# Draws electrons as a circle
def draw_electrons(screen, positions, active, left_cutoff, m_per_pixel):
    for indx in np.where(active)[0]:
        # Convert from metres into pixels
        x_px = m_to_px(positions[indx][0], m_per_pixel) + left_cutoff
        y_px = positions[indx][1]

        pygame.draw.circle(screen, "blue", (int(x_px), int(y_px)), 3)

# Metal dropdown to allow users to choose
def draw_metal_choices(screen, metals, initial_metal="Sodium (Na)"):
    metal_dropdown = Dropdown(screen, 40, 20, 120, 20, name=initial_metal, choices=metals, borderRadius=10, colour=(200,200,200), values=metals, textHAlign='left', font=pygame.font.SysFont("Arial", 14, bold=True))

    return {
        "metal_dropdown": metal_dropdown
    }

# Draws light coming from lamp at a given RGB and opacity (in relation to frequency and intensity respectively)
def draw_lamp_light(screen, lamp_l, lamp_r, bottom_buffer, top_buffer, color):

    # Creating a light beam with alpha proportional to the intensity, and the corresponding colour (if lambda is in visible range of spectrum)
    light_beam = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(light_beam, color, [lamp_l, lamp_r, bottom_buffer, top_buffer])
    screen.blit(light_beam, (0,0))

# Creates sliders to allow users to change the following parameters: voltage, intensity, wavelength
def create_sliders(screen, bx, by, display_font, V=0, intensity=100, wavelength=450 * 1e-9):
    # Slider for voltage
    voltage_slider = Slider(screen, bx + 12, by + 60, 80, 12, min=-12, max=12, step=0.1, colour=(200,200,200), valueColour=(180,180,180), handleRadius=5, initial=0)

    # Slider for intensity
    intensity_slider = Slider(screen, 450, 40, 80, 12, min=0, max=100, step=1, colour=(200,200,200), valueColour=(180,180,180), handleRadius=5, initial=intensity)
    update_intensity_slider(screen, intensity)

    # Slider for wavelength
    wavelength_slider = Slider(screen, 590, 40, 80, 12, min=100, max=850, step=10, colour=(200,200,200), valueColour=(180,180,180), handleRadius=5, initial=wavelength * 1e9)
    update_wavelength_slider(screen, wavelength)

    return {
        "voltage_slider": voltage_slider,
        "intensity_slider": intensity_slider,
        "wavelength_slider": wavelength_slider,
    }

# Updates intensity slider when user input changes
def update_intensity_slider(screen, intensity):
    # Text displaying intensity value
    intensity_str = str(round(intensity)) + " %"
    intensity_box = pygame.Rect(450, 55, 80, 20)
    pygame.draw.rect(screen, (150, 150, 150), intensity_box, width=2)
    render_text(screen, intensity_box.center, intensity_str, display_font)

    # Text displaying "Intensity"
    intensity_label_str = "Intensity"
    render_text(screen, (488,25), intensity_label_str, display_font)

# Updates wavelength slider when user input changes
def update_wavelength_slider(screen, lamda):
    # Text displaying wavelength value
    lamda_str = str(round(lamda)) + " nm"
    lamda_box = pygame.Rect(590, 55, 80, 20)
    pygame.draw.rect(screen, (150, 150, 150), lamda_box, width=2)
    render_text(screen, lamda_box.center, lamda_str, display_font)

    # Text displaying: "Wavelength"
    wavelength_label_str = "Wavelength"
    render_text(screen, (630,25), wavelength_label_str, display_font)

# Updates current display box
def update_current(screen, current, display_font):
    current_str = f"Current: {current:.3f}"

    # Creating a box and text to display the current in
    current_box = pygame.Rect(554, 478, 110, 20)
    pygame.draw.rect(screen, (255,255,255), current_box)
    pygame.draw.rect(screen, (0,0,0), current_box, width=2)
    render_text(screen, current_box.center, current_str, display_font)

# Information panel displaying photon energy, work function, V_stopping, is_emitted (if electrons are emitted)
def draw_info_panel(screen, metal, E_photons, V_stopping, work_functions, intensity):
    work_function = work_functions[metal]
    E_photons_eV = E_photons / e
    is_emitted = (E_photons_eV >= work_function and intensity > 0)

    # Background for box
    rect_center_x = 760
    rect_center_y = 150
    border_radius = 7
    rect = pygame.Rect(0, 0, 220, 100)
    rect.center = (rect_center_x, rect_center_y)
    pygame.draw.rect(screen, (230, 230, 230), rect, border_radius=border_radius)

    # Border of box
    pygame.draw.rect(screen, (0,0,0), rect, width=2, border_radius=border_radius)

    photon_energy_str = "Photon energy: " + str(round(E_photons_eV, 1)) + " eV"
    render_text(screen, (rect_center_x,rect_center_y-30), photon_energy_str, display_font)

    work_function_str = "Work function: " + str(work_function) + " eV"
    render_text(screen, (rect_center_x,rect_center_y-10), work_function_str, display_font)

    V_stopping_str = "Stopping voltage: " + str(round(V_stopping, 1)) + " V"
    render_text(screen, (rect_center_x,rect_center_y+10), V_stopping_str, display_font)

    is_emitted_str = "Electrons emitted: "
    if is_emitted:
        is_emitted_str += "Yes"
    else:
        is_emitted_str += "No"

    render_text(screen, (rect_center_x,rect_center_y+30), is_emitted_str, display_font)