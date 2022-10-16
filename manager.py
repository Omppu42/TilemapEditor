import pygame, time
from enum import Enum
pygame.init()

class State(Enum):
    BRUSH = 0
    ERASE = 1
    COLOR_PICKER = 2

class Manager:
    def __init__(self, ui):
        self.ui = ui
        self.state = State.BRUSH

    def mouse_update(self, mouse_pos: tuple):
        if mouse_pos[0] > self.ui.viewport_w: return

        block = self.ui.get_cell_from_mousepos(mouse_pos)
        if block is None: return

        if self.state == State.BRUSH:
            block.tile_id = self.ui.tile_to_place_id
            block.update_surf(self.ui.sidebar.buttons["GridButton"].is_clicked())
        elif self.state == State.ERASE:
            block.tile_id = -1
            block.update_surf(self.ui.sidebar.buttons["GridButton"].is_clicked())
        elif self.state == State.COLOR_PICKER:
            if block.tile_id >= 0:
                self.ui.tile_to_place_id = block.tile_id
                self.state = State.BRUSH #Change back to brush after picking new tile
                self.ui.sidebar.buttons["BrushButton"].just_clicked = True
