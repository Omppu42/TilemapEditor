import pygame, tkinter
from enum import Enum
from util_logger import logger
from tkinter import filedialog

import block as block_file
import palette
import settings
import data
import ui
import sidebar

pygame.init()

class State(Enum):
    BRUSH = 0
    ERASE = 1
    COLOR_PICKER = 2

class Manager:
    def __init__(self):
        self.state = State.BRUSH
        logger.log("Initialized Manager")

    def mouse_update(self, mouse_pos: tuple):
        for dropdown in data.dropdowns:
            if dropdown.drawing:
                return   #if hovering on any dropdowns

        if mouse_pos[0] > settings.VIEWPORT_W: return

        block = block_file.Block.get_cell_from_mousepos(mouse_pos)
        if block is None: return

        ui.ui_obj.detele_tiles = -1

        if len(palette.pm_obj.current_palette.tile_list) > 0 and self.state == State.BRUSH:
            block.tile_id = ui.ui_obj.tile_to_place_id
            self.update_block_surf(block)

        elif self.state == State.ERASE:
            block.tile_id = -1
            self.update_block_surf(block)

        elif self.state == State.COLOR_PICKER:
            if block.tile_id == -1: return #if clicked on air
            self.update_block_surf(block)
            ui.ui_obj.tile_to_place_id = block.tile_id


    def handle_tool_hotkeys(self, event):
        if event.key == pygame.K_p:
            self.change_state(State.BRUSH, sidebar.s_obj.buttons["BrushButton"])

        elif event.key == pygame.K_o:
            self.change_state(State.COLOR_PICKER, sidebar.s_obj.buttons["ColorPickButton"])

        elif event.key == pygame.K_e:
            self.change_state(State.ERASE, sidebar.s_obj.buttons["EraserButton"])

        elif event.key == pygame.K_g:
            sidebar.s_obj.buttons["GridButton"].clicked *= -1
            sidebar.s_obj.buttons["GridButton"].set_color(sidebar.s_obj.buttons["GridButton"].clicked)
            sidebar.s_obj.buttons["GridButton"].just_clicked = True


    def change_state(self, state: State, button_to_activate):
        self.state = state
        button_to_activate.just_clicked = True
    

    def update_block_surf(self, block):
        block.update_surf(sidebar.s_obj.buttons["GridButton"].is_clicked())


    def reset_map(self):
        for block in ui.ui_obj.blocks:
            block.tile_id = -1
            self.update_block_surf(block)

    
    def remove_index_map(self, index: int):
        for block in ui.ui_obj.blocks:
            if not block.tile_id is index: continue
            
            block.tile_id = -1
            self.update_block_surf(block)
    
    
    def ask_filedialog(self, initialdir: str = None, title: str = None) -> str:
        root = tkinter.Tk()
        root.withdraw()
        dest_folder = filedialog.askdirectory(initialdir=initialdir, title=title)
        root.destroy()
        return dest_folder
    


m_obj: Manager = None
def create_manager() -> None:
    global m_obj
    m_obj = Manager()