import pygame, time
from enum import Enum
from util import get_cell_from_mousepos
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

        block = get_cell_from_mousepos(mouse_pos)
        if block is None: return

        if self.state == State.BRUSH:
            block.tile_id = self.ui.tile_to_place_id
            block.update_surf(self.ui.sidebar.buttons["GridButton"].is_clicked())

        elif self.state == State.ERASE:
            block.tile_id = -1
            block.update_surf(self.ui.sidebar.buttons["GridButton"].is_clicked())

        elif self.state == State.COLOR_PICKER:
            if block.tile_id == -1: return #if clicked on air
            self.ui.tile_to_place_id = block.tile_id


    def handle_tool_hotkeys(self, event):
        if event.key == pygame.K_p:
            self.change_state(State.BRUSH, self.ui.sidebar.buttons["BrushButton"])

        elif event.key == pygame.K_o:
            self.change_state(State.COLOR_PICKER, self.ui.sidebar.buttons["ColorPickButton"])

        elif event.key == pygame.K_e:
            self.change_state(State.ERASE, self.ui.sidebar.buttons["EraserButton"])

        elif event.key == pygame.K_g:
            self.ui.sidebar.buttons["GridButton"].clicked *= -1
            self.ui.sidebar.buttons["GridButton"].set_color(self.ui.sidebar.buttons["GridButton"].clicked)
            self.ui.sidebar.buttons["GridButton"].just_clicked = True


    def change_state(self, state: State, button_to_activate):
        self.state = state
        button_to_activate.just_clicked = True