import pygame
from block import Block
pygame.init()

def get_cell_from_mousepos(ui, pos: tuple) -> Block:
        cell = ((pos[0] - ui.total_mouse_change[0]) // ui.cell_size, 
                 (pos[1] - ui.total_mouse_change[1]) // ui.cell_size)

        block = next((x for x in ui.blocks if x.pos_on_grid == cell), None)
        return block