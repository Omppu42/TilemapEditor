import pygame, tkinter
from enum import Enum
from util import get_cell_from_mousepos
from palette import PaletteManager
from util_logger import logger
from tkinter import filedialog
pygame.init()

class State(Enum):
    BRUSH = 0
    ERASE = 1
    COLOR_PICKER = 2

class Manager:
    def __init__(self, ui):
        self.ui = ui
        self.state = State.BRUSH
        self.palette_manager = PaletteManager(ui)
        logger.log("Initialized Manager")

    def mouse_update(self, mouse_pos: tuple):
        for dropdown in self.ui.dropdown_lists:
            if dropdown.drawing:
                return   #if hovering on any dropdowns

        if mouse_pos[0] > self.ui.viewport_w: return

        block = get_cell_from_mousepos(self.ui, mouse_pos)
        if block is None: return

        self.ui.detele_tiles = -1

        if len(self.ui.manager.palette_manager.current_palette.tile_list) > 0 and self.state == State.BRUSH:
            block.tile_id = self.ui.tile_to_place_id
            self.update_block_surf(block)

        elif self.state == State.ERASE:
            block.tile_id = -1
            self.update_block_surf(block)

        elif self.state == State.COLOR_PICKER:
            if block.tile_id == -1: return #if clicked on air
            self.update_block_surf(block)
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
    

    def update_block_surf(self, block):
        block.update_surf(self.ui.sidebar.buttons["GridButton"].is_clicked())


    def reset_map(self):
        for block in self.ui.blocks:
            block.tile_id = -1
            self.update_block_surf(block)

    
    def remove_index_map(self, index: int):
        for block in self.ui.blocks:
            if not block.tile_id is index: continue
            
            block.tile_id = -1
            self.update_block_surf(block)
    
    
    def ask_filedialog(self, initialdir: str = None, title: str = None) -> str:
        root = tkinter.Tk()
        root.withdraw()
        dest_folder = filedialog.askdirectory(initialdir=initialdir, title=title)
        root.destroy()
        return dest_folder