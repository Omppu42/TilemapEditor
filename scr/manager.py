import pygame, tkinter
from enum import Enum
from util.util_logger import logger
from tkinter import filedialog

from settings.data import State

import util.util as util
import GUI.dropdown as dropdown
import block as block_file
import settings.settings as settings

import palette
import ui
import sidebar
import input_overrides


pygame.init()



class Manager:
    def __init__(self):
        self.state = State.BRUSH
        self.loaded_tilemap = None

        # When selecting Tile > Remove tile, turns to True. When True and clicked on a tile from tile selection, remove the tile
        self.remove_palette_tiles = False 

        logger.debug("Initialized Manager")

    def mouse_update(self):
        mouse_pos = input_overrides.get_mouse_pos()

        # If clicked on the sidebar
        if mouse_pos[0] > settings.VIEWPORT_W: return

        _block = block_file.Block.get_cell_from_mousepos(mouse_pos)
        if _block is None: return

        # If clicked on canvas, toggle remove_palette_tiles to False
        self.remove_palette_tiles = False

        match (self.state):
            case State.BRUSH:
                if len(palette.pm_obj.current_palette.tile_list) == 0: return  #check that there are tiles in the palette
                _block.tile_id = palette.pm_obj.selected_tile_id
                self.update_block_surf(_block)
            
            case State.ERASE:
                _block.tile_id = -1
                self.update_block_surf(_block)

            case State.COLOR_PICKER:
                if _block.tile_id == -1: return #if clicked on air
                palette.pm_obj.selected_tile_id = _block.tile_id

                # Find the page that the tile is on
                tile_page = util.get_tile_page_from_index(palette.pm_obj.selected_tile_id)
                sidebar.s_obj.set_tile_selection_page(tile_page)
                
                self.equip_brush()


    # KEY EVENTS -------------
    def equip_brush(self) -> None:
        if self.state == State.BRUSH: return

        self.state = State.BRUSH
        sidebar.s_obj.buttons_dict["BrushButton"].just_clicked = True

    def equip_eraser(self) -> None:
        self.state = State.ERASE
        sidebar.s_obj.buttons_dict["EraserButton"].just_clicked = True

    def equip_color_picker(self) -> None:
        self.state = State.COLOR_PICKER
        sidebar.s_obj.buttons_dict["ColorPickButton"].just_clicked = True

    def toggle_grid(self) -> None:
        sidebar.s_obj.buttons_dict["GridButton"].clicked *= -1
        sidebar.s_obj.buttons_dict["GridButton"].set_color()
        sidebar.s_obj.buttons_dict["GridButton"].just_clicked = True

    
    def on_tile_deleted(self, index: int) -> None:
        """When deleting a tile from tile selection, block id's don't shift accordingly.Index is the index of the block that was deleted, taken from the order list."""
        for block in ui.ui_obj.blocks:
            if block.tile_id > index:
                block.tile_id -= 1

            self.update_block_surf(block)


    def update_block_surf(self, block):
        block.update_surf(sidebar.s_obj.buttons_dict["GridButton"].is_clicked())


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