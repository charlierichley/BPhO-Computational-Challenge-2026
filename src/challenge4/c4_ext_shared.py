# Shared variables for photoelectric effect simulation

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
pygame.init()

# Fonts
display_font = pygame.font.SysFont("arial", 18)
smaller_font = pygame.font.SysFont("arial", 16)

# Physical constants
m_e =  9.1093837139 * 1e-31
e = 1.602176620898 * 1e-19
h = 6.62607015 * 1e-34
c = 299792458