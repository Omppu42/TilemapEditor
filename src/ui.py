import pygame, json, os
from block import Block
from GUI.dropdown import DropDown

from util.util_logger import logger
from util.tkinter_opener import tk_util
from util.util import RunnableFunc
from util import file_utils

from settings import data
from settings import settings

from import_export import ie_interface
from import_export import tilemap_util

import manager
import sidebar
import input_overrides
import grid_resize
import palette

pygame.init()

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.blocks = []
        self.grid_bot_surf = None
        self.grid_right_surf = None
        self.grid_size_rows_cols = (0, 0) #Initialized in set_gridsize()
        
        self.total_mouse_change: tuple = (0, 0)
        self.del_borders_w = 7

        self.__init_last_session_data()

        logger.debug("Initialized UI")
                
    def __init_last_session_data(self) -> None:
        json_data = file_utils.load_json_data_dict(settings.LAST_SESSION_DATA_JSON)

        if "grid_size" in json_data:
            self.set_gridsize(tuple(json_data["grid_size"]))
        else:
            self.set_gridsize(settings.DEFAULT_GRID_SIZE)

        if "grid_draw" in json_data:
            if json_data["grid_draw"] == False:
                manager.m_obj.toggle_grid()

        if not "loaded_tilemap" in json_data: return

        tilemap_path = json_data["loaded_tilemap"]
        if tilemap_path == None: return
        
        if tilemap_util.is_valid_tilemap(tilemap_path):
            manager.m_obj.loaded_tilemap = tilemap_path
        else:
            logger.warning(f"Tilemap at path '{tilemap_path}' was deleted between sessions. Opening an empty tilemap")

    def set_gridsize(self, grid_size: tuple, recenter_camera:bool=True):
        self.grid_size_rows_cols = grid_size
        
        if recenter_camera:
            self.total_mouse_change = settings.DEFAULT_GIRD_OFFSET

        self.grid_bot_surf = pygame.Surface((self.grid_size_rows_cols[0]*settings.CELL_SIZE, 1))
        self.grid_bot_surf.fill((0,0,0))

        self.grid_right_surf = pygame.Surface((1, self.grid_size_rows_cols[1]*settings.CELL_SIZE))
        self.grid_right_surf.fill((0,0,0))

        self.blocks = []

        for i in range(self.grid_size_rows_cols[1]):
            for j in range(self.grid_size_rows_cols[0]):
                self.blocks.append(Block((j, i), settings.CELL_SIZE, self.screen, manager.m_obj.grid_on))
  
        logger.debug(f"Grid size set to '{grid_size[0]}x{grid_size[1]}'")
  


    def update(self):
        self.draw_blocks()
        sidebar.s_obj.update()

        if manager.m_obj.remove_palette_tiles:
            pygame.draw.rect(self.screen, (255,0,0), (0,0, settings.SCR_W, self.del_borders_w))
            pygame.draw.rect(self.screen, (255,0,0), (0,0, self.del_borders_w, settings.SCR_H))
            pygame.draw.rect(self.screen, (255,0,0), (settings.SCR_W-self.del_borders_w, 0, self.del_borders_w, settings.SCR_H))
            pygame.draw.rect(self.screen, (255,0,0), (0, settings.SCR_H-self.del_borders_w, settings.SCR_W, self.del_borders_w))

            text =        data.font_50.render("CLICK TILE TO DELETE", True, (255,0,0))
            text_shadow = data.font_50.render("CLICK TILE TO DELETE", True, (0,0,0))
            
            text_rect = text.get_rect(center=(settings.SCR_W//2, settings.SCR_H//2))
            text_shadow_rect = text_shadow.get_rect(center=(settings.SCR_W//2-3, settings.SCR_H//2+2))

            self.screen.blit(text_shadow, text_shadow_rect)
            self.screen.blit(text, text_rect)


    def draw_blocks(self):
        movement_vec = self.get_movement_vec()
        self.total_mouse_change = (self.total_mouse_change[0]+movement_vec[0], self.total_mouse_change[1]+movement_vec[1])
        blocks_to_update = [x for x in self.blocks if x.org_pos[0]+self.total_mouse_change[0] > -100 and x.org_pos[0]+self.total_mouse_change[0] < settings.VIEWPORT_W+100
                                                     and x.org_pos[1]+self.total_mouse_change[1] > -100 and x.org_pos[1]+self.total_mouse_change[1] < settings.SCR_H+100]
        for _block in blocks_to_update:
            _block.update(self.total_mouse_change) #draw blocks

        if sidebar.s_obj.buttons_dict["GridButton"].just_clicked:
            [block.update_surf(manager.m_obj.grid_on) for block in self.blocks]

        if manager.m_obj.grid_on:
            self.screen.blit(self.grid_bot_surf, (self.total_mouse_change[0], self.grid_size_rows_cols[1]*settings.CELL_SIZE+self.total_mouse_change[1]))
            self.screen.blit(self.grid_right_surf, (self.grid_size_rows_cols[0]*settings.CELL_SIZE+self.total_mouse_change[0], self.total_mouse_change[1]))


    def get_movement_vec(self): #get mouse movement from previous frame
        if not input_overrides.get_mouse_pressed()[2]: 
            return (0, 0)

        if input_overrides.get_mouse_pressed()[2]:
            mouse_pos = input_overrides.get_mouse_pos()
            if mouse_pos[0] == 0 or mouse_pos[1] == 0 or mouse_pos[0] > settings.VIEWPORT_W or mouse_pos[1] == settings.SCR_H-1: #if offscreen
                pygame.mouse.get_rel()
                return (0,0)
            rel = pygame.mouse.get_rel()
            return rel

    
    def toggle_delete(self):
        manager.m_obj.remove_palette_tiles = not manager.m_obj.remove_palette_tiles

    
    def init_dropdowns(self) -> list:
        dropdowns = []

        dropdowns.append( DropDown(
            pos_size=(5, 0, 140, 30), 
            main="Tilemap", 
            options={"Load"    : ie_interface.Iie_obj.import_tilemap, 
                     "Save"    : ie_interface.Iie_obj.save_tilemap,
                     "Save As" : ie_interface.Iie_obj.export_tilemap,
                     "New"     : RunnableFunc(ie_interface.Iie_obj.import_empty_map_ask_save, args=[ui_obj]) } ))

        dropdowns.append( DropDown(
            pos_size=(150, 0, 125, 30), 
            main="Palette", 
            options={"Load"  : RunnableFunc(tk_util.queue_func, args=[palette.pm_obj.change_palette_ask]), 
                    "New"    : RunnableFunc(tk_util.queue_func, args=[palette.pm_obj.create_empty_palette]), 
                    "Delete" : RunnableFunc(tk_util.queue_func, args=[palette.pm_obj.delete_palette])} ))

        dropdowns.append( DropDown(
            pos_size=(280, 0, 125, 30), 
            main="Tiles", 
            options={"New Tile" : RunnableFunc(tk_util.queue_func, args=[palette.pm_obj.add_tile]), 
                    "Remove"    : self.toggle_delete} ))

        dropdowns.append( DropDown(
            pos_size=(410, 0, 125, 30), 
            main="Grid", 
            options={"Resize" : grid_resize.gr_obj.grid_resize_popup} ))
        
        return dropdowns






dropdowns: "list[DropDown]" = []
ui_obj: UI = None

def create_ui(screen):
    global ui_obj, dropdowns
    ui_obj = UI(screen)
    dropdowns = ui_obj.init_dropdowns()