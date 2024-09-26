import pygame, json, os
from block import Block
from manager import State
from util_logger import logger
from tkinter_opener import tk_util

import settings
import manager
import palette
import sidebar

pygame.init()

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.total_mouse_change: tuple = (0, 0)

        json_data = {}
        if os.path.isfile("last_session_data.json"):
            with open("last_session_data.json", "r") as f:
                data = f.readlines()
                if not data == []:
                    json_data = json.loads("".join(data))

        if "GridSize" in json_data:
            self.set_gridsize(json_data["GridSize"])
        else:
            self.set_gridsize((16,16))

        self.tile_selection_rects = [pygame.Rect(x["pos"], (settings.CELL_SIZE, settings.CELL_SIZE)) for x in palette.pm_obj.get_data()[sidebar.s_obj.tiles_page]] #make sidebar tiles' rects
        self.tile_to_place_id = 0

        self.detele_tiles = -1 #-1 off, 1 on
        self.del_borders_w = 7
        self.del_font = pygame.font.Font(None, 50)
        logger.log("Initialized UI")
                


    def set_gridsize(self, grid_size):
        self.cells_r_c = grid_size
        logger.log(f"Set grid size to '{grid_size[0]}x{grid_size[1]}'")
        self.total_mouse_change = (0, 0)

        self.grid_bot_surf = pygame.Surface((self.cells_r_c[0]*settings.CELL_SIZE, 1))
        self.grid_bot_surf.fill((0,0,0))

        self.grid_right_surf = pygame.Surface((1, self.cells_r_c[1]*settings.CELL_SIZE))
        self.grid_right_surf.fill((0,0,0))

        self.blocks = []

        for i in range(self.cells_r_c[1]):
            for j in range(self.cells_r_c[0]):
                self.blocks.append(Block((j, i), settings.CELL_SIZE, self.screen, sidebar.s_obj.buttons["GridButton"].is_clicked()))
  
  
    def on_mouse_click(self):
        mouse_pos = pygame.mouse.get_pos()  
        self.change_tile(mouse_pos)
        self.detele_tiles = -1

        sidebar.s_obj.on_mouse_click(mouse_pos)
        

    def change_tile(self, mouse_pos):
        for x in self.tile_selection_rects:
            if not x.collidepoint(mouse_pos): continue

            if manager.m_obj.state is not State.BRUSH: #select brush when clicking any tile from selection
                manager.m_obj.change_state(State.BRUSH, sidebar.s_obj.buttons["BrushButton"])

            #update tiletoplaceid
            for value in palette.pm_obj.get_data()[sidebar.s_obj.tiles_page]:
                if x[0] == value["pos"][0] and x[1] == value["pos"][1]: #Get id of block clicked on
                    if self.detele_tiles == -1:
                        self.tile_to_place_id = value["id"]
                    elif self.detele_tiles == 1:
                        tk_util.queue_func(palette.pm_obj.remove_tile, value["id"])
                        #palette.pm_obj.remove_tile(value["id"])
            


    def update(self):
        self.draw_blocks()
        sidebar.s_obj.update()

        if self.detele_tiles == 1:
            pygame.draw.rect(self.screen, (255,0,0), (0,0, settings.SCR_W, self.del_borders_w))
            pygame.draw.rect(self.screen, (255,0,0), (0,0, self.del_borders_w, settings.SCR_H))
            pygame.draw.rect(self.screen, (255,0,0), (settings.SCR_W-self.del_borders_w, 0, self.del_borders_w, settings.SCR_H))
            pygame.draw.rect(self.screen, (255,0,0), (0, settings.SCR_H-self.del_borders_w, settings.SCR_W, self.del_borders_w))

            text = self.del_font.render("CLICK TILE TO DELETE", True, (255,0,0))
            text_shadow = pygame.font.Font(None, 50).render("CLICK TILE TO DELETE", True, (0,0,0))
            
            text_rect = text.get_rect(center=(settings.SCR_W//2, settings.SCR_H//2))
            text_shadow_rect = text_shadow.get_rect(center=(settings.SCR_W//2-3, settings.SCR_H//2+2))

            self.screen.blit(text_shadow, text_shadow_rect)
            self.screen.blit(text, text_rect)


    def draw_blocks(self):
        movement_vec = self.get_movement_vec()
        self.total_mouse_change = (self.total_mouse_change[0]+movement_vec[0], self.total_mouse_change[1]+movement_vec[1])
        blocks_to_update = [x for x in self.blocks if x.org_pos[0]+self.total_mouse_change[0] > -100 and x.org_pos[0]+self.total_mouse_change[0] < settings.VIEWPORT_W+100
                                                     and x.org_pos[1]+self.total_mouse_change[1] > -100 and x.org_pos[1]+self.total_mouse_change[1] < settings.SCR_H+100]
        for x in blocks_to_update:
            x.update(self.total_mouse_change) #draw blocks

        if sidebar.s_obj.buttons["GridButton"].just_clicked:
            if sidebar.s_obj.buttons["GridButton"].is_clicked():
                [block.update_surf(True) for block in self.blocks]
            else:
                [block.update_surf(False) for block in self.blocks]

        if sidebar.s_obj.buttons["GridButton"].is_clicked():
            self.screen.blit(self.grid_bot_surf, (self.total_mouse_change[0], self.cells_r_c[1]*settings.CELL_SIZE+self.total_mouse_change[1]))
            self.screen.blit(self.grid_right_surf, (self.cells_r_c[0]*settings.CELL_SIZE+self.total_mouse_change[0], self.total_mouse_change[1]))


    def get_movement_vec(self): #get mouse movement from previous frame
        if not pygame.mouse.get_pressed()[2]: 
            return (0, 0)

        if pygame.mouse.get_pressed()[2]:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] == 0 or mouse_pos[1] == 0 or mouse_pos[0] > settings.VIEWPORT_W or mouse_pos[1] == settings.SCR_H-1: #if offscreen
                pygame.mouse.get_rel()
                return (0,0)
            rel = pygame.mouse.get_rel()
            return rel

    
    def toggle_delete(self):
        self.detele_tiles *= -1




ui_obj: UI = None
def create_ui(screen):
    global ui_obj
    ui_obj = UI(screen)