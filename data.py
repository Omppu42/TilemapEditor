import pygame
import dropdown

dropdowns = None

font_25 = pygame.font.Font(None, 25)
font_30 = pygame.font.Font(None, 30)
font_35 = pygame.font.Font(None, 35)
font_50 = pygame.font.Font(None, 50)

def init_data() -> None:
    global dropdowns
    dropdowns = dropdown.create_dropdowns()

    #buttons = 