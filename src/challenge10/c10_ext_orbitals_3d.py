# GUI displaying classical and quantum mismatch probabilities with adjustable detector angles

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
import numpy as np
from math import cos, sin, atan2, ceil, dist, pi, degrees, radians

# Initialising window
pygame.init()
x_max, y_max = (900, 600)
screen = pygame.display.set_mode((x_max, y_max))
pygame.display.set_caption("Quantum Cryptography Simulation")
title_font = pygame.font.SysFont("arial", 32, bold=True)

def show_title(surface, coords, color="white"):
    title_text = title_font.render("Classical vs Quantum Mismatch Probabilities", True, color)
    surface.blit(title_text, title_text.get_rect(center=coords))

def quantum_probability(theta, phi):
    p_match = cos(theta - phi)**2
    p_mismatch = sin(theta - phi)**2
    return (p_match, p_mismatch)

def classical_probability(theta, phi):
    p_match = (cos(theta)**2) * (cos(phi)**2) + (sin(theta)**2) * (sin(phi)**2)
    p_mismatch = 1 - (cos(theta)**2) * (cos(phi)**2) - (sin(theta)**2)*(sin(phi)**2)
    return (p_match, p_mismatch)

# Functions to convert between proportional coordinates and pixels, using global x_max and y_max values
def pxy(x, y):
    return (x_max * x, y_max * y)

def px(x):
    return x_max * x

def py(y):
    return y_max * y

def px_inv(x):
    return x / x_max

def py_inv(y):
    return y / y_max

# Drawing arrow as the X and Y axes of detector
def draw_arrow(surface, start, end, color="white", line_width=2, head_size=20):
    start = pygame.Vector2(start)
    end = pygame.Vector2(end)

    line = pygame.draw.line(surface, color, start, end, line_width)

    arrow_direction = (end - start).normalize()
    CONST_ANGLE = 140 # for rotation, to form the triangle
    left = arrow_direction.rotate(CONST_ANGLE) * head_size
    right = arrow_direction.rotate(-1 * CONST_ANGLE) * head_size

    arrowhead_coords = [end, end + left , end + right]

    arrowhead = pygame.draw.polygon(surface, color, arrowhead_coords)
    return (line, arrowhead, arrowhead_coords)

# Normal line, dashed and verticaly upwards. Angles measured anticlockwise from normal
def normal_line(surface, start, end, dash_length=5, color="white"):
    start_x, start_y = start
    end_x, end_y = end

    delta = end_y - start_y
    n = ceil(abs((end_y - start_y) / dash_length))
    delta_per_n = delta / n

    for i in range(0, n, 2):
        pygame.draw.line(surface, color, (start_x, start_y + delta_per_n * i), (start_x, start_y + delta_per_n * (i + 1)))

def draw_detector(surface, centre_x, centre_y, end_x, end_y, detector_color="white", normal_color="white", normal_length=0.2):
    p_x, p_y = pxy(centre_x, centre_y)
    line, arwhead_x, arrowhead_coords_x = draw_arrow(surface, (p_x, p_y), pxy(end_x, end_y), color=detector_color)

    dx = px(end_x - centre_x)
    dy = py(end_y - centre_y)
    line_y, arowwhead_y, arrowhead_coords_y = draw_arrow(surface, (p_x, p_y), (p_x + dy, p_y - dx), color=detector_color)

    normal = normal_line(surface, start=pxy(centre_x, centre_y), end=pxy(centre_x, centre_y - normal_length), color=normal_color)

    return (arrowhead_coords_x, arrowhead_coords_y)

def centroid(coords):
    coords = np.array(coords)
    length = len(coords)

    x = coords[:,0]
    y = coords[:,1]
    return np.sum(x) / length, np.sum(y) / length

def update_detector(centre_x, centre_y, x_end, y_end, mx, my, length_arrow, is_Y=False):
    dx = mx - px(centre_x)
    dy = my - py(centre_y)
    angle = atan2(dy, dx)

    if is_Y == True:
        angle += np.pi / 2

    x_end = px_inv(px(centre_x) + length_arrow * cos(angle))
    y_end = py_inv(py(centre_y) + length_arrow * sin(angle))
    return (x_end, y_end)

def label_arrow(surface, arrowhead_coords, label, centre_x, centre_y, font_name="arial", font_size=18, color="white", buffer=15):
    x, y = arrowhead_coords[0]

    if font_name.endswith(".ttf") == True:
        font_label = pygame.font.Font(font_name, font_size)
    else:
        font_label = pygame.font.SysFont(font_name, font_size)

    text = font_label.render(label, True, color)
    dx = x - px(centre_x)
    dy = y - py(centre_y)
    unit_vector = pygame.Vector2(dx, dy).normalize()

    label_x = x + unit_vector[0] * buffer
    label_y = y + unit_vector[1] * buffer
    label_coords = label_x, label_y

    # Ensure constant distance
    text_rectangle = text.get_rect(center=(label_x, label_y))
    surface.blit(text, text_rectangle)

def draw_angle(surface, centre_x, centre_y, theta, arc_radius=20, color="yellow", thickness=1, font_name="arial", font_size=14, font_color="white", const_angle_label = 1.1):
    start_angle = np.pi / 2
    end_angle = start_angle - theta

    pygame.draw.arc(surface, color, (px(centre_x)-arc_radius, py(centre_y)-arc_radius, 2*arc_radius, 2*arc_radius), start_angle, end_angle, thickness)

    if font_name.endswith(".ttf") == True:
        font = pygame.font.Font(font_name, font_size)
    else:
        font = pygame.font.SysFont(font_name, font_size)

    theta_deg = degrees(-theta) % 360
    theta_deg_str = f"{theta_deg:.0f}°"
    angle_text = font.render(theta_deg_str, True, font_color)

    arc_centre_angle = (start_angle + end_angle) / 2
    const_angle_label *= arc_radius

    x_delta = (arc_radius + const_angle_label) * cos(arc_centre_angle)
    y_delta = - (arc_radius + const_angle_label) * sin(arc_centre_angle)

    if theta_deg >= 180:
        x_delta *= -1
        y_delta *= -1

    rect = angle_text.get_rect(center=(px(centre_x) + x_delta, py(centre_y) + y_delta))
    surface.blit(angle_text, rect)
    return theta_deg_str

# Parameters for plotting
centre_xa, centre_ya = (0.25, 0.6)
x_end_xa, y_end_xa = (0.1, 0.5)

centre_xb, centre_yb = (0.7, 0.6)
x_end_xb, y_end_xb = (0.55, 0.5)

normal_length = 0.2
arrow_move_threshold = 30
arc_radius = 18
y_buffer_label = 50

# Colour parameters
detector_color_a = (0, 125, 255)
detector_color_b = (0, 220, 80)
classical_colour = (255, 80, 80)
quantum_colour = (180, 255, 0)
angle_color = "#F6FF4D"

# Constants for box around probability and distance from detector
normal_buffer = 110
width_box = 110
height_box = 50

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0,0,0))
    mx, my = pygame.mouse.get_pos()

    # Detector A
    arrowhead_coords_xa, arrowhead_coords_ya = draw_detector(screen, centre_xa, centre_ya, x_end_xa, y_end_xa, detector_color=detector_color_a, normal_color="white", normal_length=normal_length)
    length_arrow_a = dist(pxy(centre_xa, centre_ya), pxy(x_end_xa, y_end_xa)) # uses proportional coordinates

    centroid_xa = centroid(arrowhead_coords_xa)
    centroid_ya = centroid(arrowhead_coords_ya)

    # X_A detetor activated
    if pygame.Vector2((mx, my)).distance_to(centroid_xa) < arrow_move_threshold:
        x_end_xa, y_end_xa = update_detector(centre_xa, centre_ya, x_end_xa, y_end_xa, mx, my, length_arrow_a)

    # Y_A detector activated
    if pygame.Vector2((mx, my)).distance_to(centroid_ya) < arrow_move_threshold:
        x_end_xa, y_end_xa = update_detector(centre_xa, centre_ya, x_end_xa, y_end_xa, mx, my, length_arrow_a, is_Y=True)

    # Detector B
    arrowhead_coords_xb, arrowhead_coords_yb = draw_detector(screen, centre_xb, centre_yb, x_end_xb, y_end_xb, detector_color=detector_color_b, normal_color="white")
    length_arrow_b = dist(pxy(centre_xb, centre_yb), pxy(x_end_xb, y_end_xb))

    centroid_xb = centroid(arrowhead_coords_xb)
    centroid_yb = centroid(arrowhead_coords_yb)

    # X_B detector activated
    if pygame.Vector2((mx, my)).distance_to(centroid_xb) < arrow_move_threshold:
        x_end_xb, y_end_xb = update_detector(centre_xb, centre_yb, x_end_xb, y_end_xb, mx, my, length_arrow_b)

    # Y_B detector activated
    if pygame.Vector2((mx, my)).distance_to(centroid_yb) < arrow_move_threshold:
        x_end_xb, y_end_xb = update_detector(centre_xb, centre_yb, x_end_xb, y_end_xb, mx, my, length_arrow_b, is_Y=True)

    # Labelling arrows (detector axes)
    font_size_arrow = 15
    label_arrow(screen, arrowhead_coords_xa, "X", centre_xa, centre_ya, font_size=font_size_arrow)
    label_arrow(screen, arrowhead_coords_ya, "Y", centre_xa, centre_ya, font_size=font_size_arrow)
    label_arrow(screen, arrowhead_coords_xb, "X", centre_xb, centre_yb, font_size=font_size_arrow)
    label_arrow(screen, arrowhead_coords_yb, "Y", centre_xb, centre_yb, font_size=font_size_arrow)

    # theta is the angle X_A makes with the vertical normal
    x_end_a, y_end_a = arrowhead_coords_xa[0]
    dx_theta = px_inv(x_end_a) - centre_xa
    dy_theta = -(py_inv(y_end_a) - centre_ya)
    theta = atan2(dx_theta, dy_theta)

    # phi is the angle X_B makes with the vertical normal
    x_end_b, y_end_b = arrowhead_coords_xb[0]
    dx_phi = px_inv(x_end_b) - centre_xb
    dy_phi = -(py_inv(y_end_b) - centre_yb)
    phi = atan2(dx_phi, dy_phi)

    # Drawing angles with an arc and labelling
    theta_deg_str = draw_angle(screen, centre_xa, centre_ya, theta, arc_radius=arc_radius, color=angle_color)
    phi_deg_str = draw_angle(screen, centre_xb, centre_yb, phi, arc_radius=arc_radius, color=angle_color)

    # Calculating classical and quantum mismatch probabilities
    classical_match, classical_mismatch = classical_probability(theta, phi)
    quantum_match, quantum_mismatch = quantum_probability(theta, phi)

    # Creating fonts
    small_font = pygame.font.SysFont("arial", 12)
    large_font = pygame.font.SysFont("arial", 18)
    detector_label_font = pygame.font.SysFont("arial", 22)

    # Labelling Detector A
    xa_label = px(centre_xa)
    ya_label = py(centre_ya) + length_arrow_a + y_buffer_label
    detector_a_text = detector_label_font.render(f"Detector A: θ = {theta_deg_str}", True, detector_color_a)
    screen.blit(detector_a_text, detector_a_text.get_rect(center=(xa_label, ya_label)))

    # Labelling Detector B
    xb_label = px(centre_xb)
    yb_label = py(centre_yb) + length_arrow_b + y_buffer_label
    detector_b_text = detector_label_font.render(f"Detector B: φ = {phi_deg_str}", True, detector_color_b)
    screen.blit(detector_b_text, detector_b_text.get_rect(center=(xb_label, yb_label)))

    # Creating text for displaying probabilities
    classical_text = small_font.render(f"P(mismatch): {classical_mismatch:.2f}",True, classical_colour)
    classical_text_label = large_font.render(f"Classical probability", True, classical_colour)
    quantum_text = small_font.render(f"P(mismatch): {quantum_mismatch:.2f}", True, quantum_colour)
    quantum_text_label = large_font.render(f"Quantum probability", True, quantum_colour)

    # Classical probability labelling
    normal_ymax_a = py(centre_ya) - py(normal_length)
    screen.blit(classical_text, classical_text.get_rect(center=(px(centre_xa), normal_ymax_a - normal_buffer)))
    pygame.draw.rect(screen, "white", (px(centre_xa) - width_box / 2, normal_ymax_a - normal_buffer - height_box / 2, width_box, height_box), width=1, border_radius=10)
    screen.blit(classical_text_label, classical_text_label.get_rect(center=(px(centre_xa), normal_ymax_a - normal_buffer - height_box)))

    # Quantum probability labelling
    normal_ymax_b = py(centre_yb) - py(normal_length)
    screen.blit(quantum_text, quantum_text.get_rect(center=(px(centre_xb), normal_ymax_b - normal_buffer)))
    pygame.draw.rect(screen, "white", (px(centre_xb) - width_box / 2, normal_ymax_b - normal_buffer - height_box / 2, width_box, height_box), width=1, border_radius=10)
    screen.blit(quantum_text_label, quantum_text_label.get_rect(center=(px(centre_xb), normal_ymax_b - normal_buffer - height_box)))

    show_title(screen, (x_max / 2, y_max / 30))
    pygame.display.update()
