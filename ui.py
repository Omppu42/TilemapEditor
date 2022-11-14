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
        logger.log("Initialized UI")
                

    def on_mouse_click(self):
        mouse_pos = pygame.mouse.get_pos()  

        for x in self.sidebar.buttons:
            if self.sidebar.buttons[x].check_clicked(mouse_pos):
                if x == "ExportButton":
                    export.export_tilemap(self)
                elif x == "ImportButton":
                    import_map.import_tilemap(self)

        
        self.change_tile(mouse_pos)
        

    def change_tile(self, mouse_pos):
        for x in self.tile_selection_rects:
            if not x.collidepoint(mouse_pos): continue

            if self.manager.state is not State.BRUSH: #select brush when clicking any tile from selection
                self.manager.change_state(State.BRUSH, self.sidebar.buttons["BrushButton"])

            for _id, value in enumerate(self.current_palette.palette_data):
                if x[0] == value["pos"][0] and x[1] == value["pos"][1]: #Get id of block clicked on
                    self.tile_to_place_id = _id


    def update(self):
        self.draw_blocks()
        self.sidebar.update()


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