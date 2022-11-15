import pygame, time
from block import Block
from manager import Manager, State
from sidebar import Sidebar
from util_logger import logger
import export, import_map

pygame.init()

class UI:
    def __init__(self, scr_size, screen, cell_size: int):
        self.scr_size: tuple = scr_size
        self.scr_w, self.scr_h = self.scr_size
        self.viewport_w: int = self.scr_w // 4 * 3
        self.sidebar_pos = (self.viewport_w, 0)
        self.cell_size: int = cell_size
        self.manager = Manager(self)
        self.cells_r_c: tuple = (200, 30)
        self.screen = screen
        self.sidebar = Sidebar(self, self.scr_size, self.sidebar_pos, self.viewport_w, self.screen)
        self.blocks = []
        self.total_mouse_change: tuple = (0, 0)

        self.grid_bot_surf = pygame.Surface((self.cells_r_c[0]*self.cell_size, 1))
        self.grid_bot_surf.fill((0,0,0))

        self.grid_right_surf = pygame.Surface((1, self.cells_r_c[1]*self.cell_size))
        self.grid_right_surf.fill((0,0,0))

        self.current_palette = self.manager.palette_manager.current_palette #if changing this, check palette change_palette function
        self.tile_selection_rects = [pygame.Rect(x["pos"], (self.cell_size, self.cell_size)) for x in self.current_palette.palette_data] #make sidebar tiles' rects
        self.tile_to_place_id = 0

        for i in range(self.cells_r_c[1]):
            for j in range(self.cells_r_c[0]):
                self.blocks.append(Block((j, i), self.cell_size, self.screen, self.sidebar.buttons["GridButton"].is_clicked(), self.manager.palette_manager))

        self.detele_tiles = -1 #-1 off, 1 on
        self.del_borders_w = 7
        self.del_font = pygame.font.Font(None, 50)
        logger.log("Initialized UI")
                

    def on_mouse_click(self):
        mouse_pos = pygame.mouse.get_pos()  
        self.change_tile(mouse_pos)
        self.detele_tiles = -1

        for x in self.sidebar.buttons:
            if self.sidebar.buttons[x].check_clicked(mouse_pos):
                if x == "ExportButton":
                    export.export_tilemap(self)
                elif x == "ImportButton":
                    import_map.import_tilemap(self)
                elif x == "LoadPaletteButton":
                    self.manager.palette_manager.change_palette_ask()
                elif x == "AddTileButton":
                    self.manager.palette_manager.add_tile()
                elif x == "RemoveTileButton":
                    self.detele_tiles *= -1

        
        

    def change_tile(self, mouse_pos):
        for x in self.tile_selection_rects:
            if not x.collidepoint(mouse_pos): continue

            if self.manager.state is not State.BRUSH: #select brush when clicking any tile from selection
                self.manager.change_state(State.BRUSH, self.sidebar.buttons["BrushButton"])

            for _id, value in enumerate(self.current_palette.palette_data):
                if x[0] == value["pos"][0] and x[1] == value["pos"][1]: #Get id of block clicked on
                    if self.detele_tiles == -1:
                        self.tile_to_place_id = _id
                    elif self.detele_tiles == 1:
                        self.manager.palette_manager.remove_tile(_id)


    def update(self):
        self.draw_blocks()
        self.sidebar.update()

        if self.detele_tiles == 1:
            pygame.draw.rect(self.screen, (255,0,0), (0,0, self.scr_w, self.del_borders_w))
            pygame.draw.rect(self.screen, (255,0,0), (0,0, self.del_borders_w, self.scr_h))
            pygame.draw.rect(self.screen, (255,0,0), (self.scr_w-self.del_borders_w, 0, self.del_borders_w, self.scr_h))
            pygame.draw.rect(self.screen, (255,0,0), (0, self.scr_h-self.del_borders_w, self.scr_w, self.del_borders_w))

            text = self.del_font.render("CLICK TILE TO DELETE", True, (255,0,0))
            text_shadow = pygame.font.Font(None, 50).render("CLICK TILE TO DELETE", True, (0,0,0))
            
            text_rect = text.get_rect(center=(self.scr_w//2, self.scr_h//2))
            text_shadow_rect = text_shadow.get_rect(center=(self.scr_w//2-3, self.scr_h//2+2))

            self.screen.blit(text_shadow, text_shadow_rect)
            self.screen.blit(text, text_rect)


    def draw_blocks(self):
        movement_vec = self.get_movement_vec()
        self.total_mouse_change = (self.total_mouse_change[0]+movement_vec[0], self.total_mouse_change[1]+movement_vec[1])
        blocks_to_update = [x for x in self.blocks if x.org_pos[0]+self.total_mouse_change[0] > -100 and x.org_pos[0]+self.total_mouse_change[0] < self.viewport_w+100
                                                     and x.org_pos[1]+self.total_mouse_change[1] > -100 and x.org_pos[1]+self.total_mouse_change[1] < self.scr_h+100]
        for x in blocks_to_update:
            x.update(self.total_mouse_change) #draw blocks

        if self.sidebar.buttons["GridButton"].just_clicked:
            if self.sidebar.buttons["GridButton"].is_clicked():
                [block.update_surf(True) for block in self.blocks]
            else:
                [block.update_surf(False) for block in self.blocks]

        if self.sidebar.buttons["GridButton"].is_clicked():
            self.screen.blit(self.grid_bot_surf, (self.total_mouse_change[0], self.cells_r_c[1]*self.cell_size+self.total_mouse_change[1]))
            self.screen.blit(self.grid_right_surf, (self.cells_r_c[0]*self.cell_size+self.total_mouse_change[0], self.total_mouse_change[1]))


    def get_movement_vec(self): #get mouse movement from previous frame
        if not pygame.mouse.get_pressed()[2]: 
            return (0, 0)

        if pygame.mouse.get_pressed()[2]:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] == 0 or mouse_pos[1] == 0 or mouse_pos[0] > self.viewport_w or mouse_pos[1] == self.scr_h-1: #if offscreen
                pygame.mouse.get_rel()
                return (0,0)
            rel = pygame.mouse.get_rel()
            return rel