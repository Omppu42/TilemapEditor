import pygame, json, os
from block import Block
from GUI.dropdown import DropDown

from util.util_logger import logger
from util.tkinter_opener import tk_util

from settings import data
from settings import settings

from import_export import ie_interface

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
        self.total_mouse_change: tuple = (0, 0)
        self.del_borders_w = 7

        json_data = {}
        if os.path.isfile(settings.LAST_SESSION_DATA_JSON):
            with open(settings.LAST_SESSION_DATA_JSON, "r") as f:
                data = f.readlines()
                if not data == []:
                    json_data = json.loads("".join(data))

        if "grid_size" in json_data:
            self.set_gridsize(json_data["grid_size"])
        else:
            self.set_gridsize(settings.DEFAULT_GRID_SIZE)

        if "loaded_tilemap" in json_data:
            tilemap_path = json_data["loaded_tilemap"]
            manager.m_obj.loaded_tilemap = tilemap_path
                

        logger.debug("Initialized UI")
                


    def set_gridsize(self, grid_size: tuple, recenter_camera:bool=True):
        self.grid_size_rows_cols = grid_size
        
        if recenter_camera:
            self.total_mouse_change = (100, 50)

        self.grid_bot_surf = pygame.Surface((self.grid_size_rows_cols[0]*settings.CELL_SIZE, 1))
        self.grid_bot_surf.fill((0,0,0))

        self.grid_right_surf = pygame.Surface((1, self.grid_size_rows_cols[1]*settings.CELL_SIZE))
        self.grid_right_surf.fill((0,0,0))

        self.blocks = []

        for i in range(self.grid_size_rows_cols[1]):
            for j in range(self.grid_size_rows_cols[0]):
                self.blocks.append(Block((j, i), settings.CELL_SIZE, self.screen, sidebar.s_obj.buttons_dict["GridButton"].is_clicked()))
  
        logger.log(f"Grid size set to '{grid_size[0]}x{grid_size[1]}'")
  


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
            if sidebar.s_obj.buttons_dict["GridButton"].is_clicked():
                [block.update_surf(True) for block in self.blocks]
            else:
                [block.update_surf(False) for block in self.blocks]

        if sidebar.s_obj.buttons_dict["GridButton"].is_clicked():
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
            options={"Load"    : (ie_interface.Iie_obj.import_tilemap), 
                    "Save"     : (ie_interface.Iie_obj.save_tilemap),
                    "Save As"  : (ie_interface.Iie_obj.export_tilemap),
                    "New"      : (ie_interface.Iie_obj.import_empty_map)} ))

        dropdowns.append( DropDown(
            pos_size=(150, 0, 125, 30), 
            main="Palette", 
            options={"Load"   : (tk_util.queue_func, [palette.pm_obj.change_palette_ask]), 
                    "New"    : (tk_util.queue_func, [palette.pm_obj.create_empty_palette]), 
                    "Delete" : (tk_util.queue_func, [palette.pm_obj.delete_palette])} ))

        dropdowns.append( DropDown(
            pos_size=(280, 0, 125, 30), 
            main="Tiles", 
            options={"New Tile" : (tk_util.queue_func, [palette.pm_obj.add_tile]), 
                    "Remove"   : (self.toggle_delete)} ))

        dropdowns.append( DropDown(
            pos_size=(410, 0, 125, 30), 
            main="Grid", 
            options={"Resize" : (grid_resize.gr_obj.grid_resize_popup)} ))
        
        return dropdowns






dropdowns: "list[DropDown]" = []
ui_obj: UI = None

def create_ui(screen):
    global ui_obj, dropdowns
    ui_obj = UI(screen)
    dropdowns = ui_obj.init_dropdowns()