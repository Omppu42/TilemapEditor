from enum import Enum

import pygame
pygame.init()

font_20 = pygame.font.Font(None, 20)
font_25 = pygame.font.Font(None, 25)
font_30 = pygame.font.Font(None, 30)
font_35 = pygame.font.Font(None, 35)
font_50 = pygame.font.Font(None, 50)

class State(Enum):
    BRUSH = 0
    ERASE = 1
    COLOR_PICKER = 2

saved_last_time = 0