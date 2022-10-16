import pygame, time
from block import Block
from manager import Manager, State
from init_tiles import Tiles
import button

pygame.init()

class UI:
    def __init__(self, scr_size, screen, cell_size: int):
        self.manager = Manager(self)
        self.cell_size: int = cell_size
        self.scr_size: tuple = scr_size
        self.scr_w, self.scr_h = self.scr_size
        self.cells_r_c: tuple = (200, 30)
        self.viewport_w: int = self.scr_w // 4 * 3
        self.screen = screen
        self.sidebar = Sidebar(self, self.scr_size, self.viewport_w, (200,200,200), self.screen)
        self.blocks = []
        self.total_mouse_change: tuple = (0, 0)

        self.grid_bot_surf = pygame.Surface((self.cells_r_c[0]*self.cell_size, 1))
        self.grid_bot_surf.fill((0,0,0))

        self.grid_right_surf = pygame.Surface((1, self.cells_r_c[1]*self.cell_size))
        self.grid_right_surf.fill((0,0,0))

        self.tiles_cls = Tiles(self.cell_size)
        self.tiles_dict = self.tiles_cls.init_tiles(self.sidebar.pos)
        self.tile_selection_rects = [pygame.Rect(self.tiles_dict[x][1], (self.cell_size, self.cell_size)) for x in self.tiles_dict] #make sidebar tiles' rects
        self.tile_to_place_id = 0

        for i in range(self.cells_r_c[0]):
            for j in range(self.cells_r_c[1]):
                self.blocks.append(Block((i, j), self.cell_size, self.screen, self.sidebar.buttons["GridButton"].is_clicked(), self.tiles_dict))


    def on_mouse_click(self):
        mouse_pos = pygame.mouse.get_pos()  

        for x in self.sidebar.buttons:
            self.sidebar.buttons[x].check_clicked(mouse_pos)

        self.change_tile(mouse_pos)
        

    def change_tile(self, mouse_pos):
        for x in self.tile_selection_rects:
            if not x.collidepoint(mouse_pos): continue

            if self.manager.state is not State.BRUSH: #select brush when clicking any tile from selection
                self.manager.change_state(State.BRUSH, self.sidebar.buttons["BrushButton"])

            for _id, value in self.tiles_dict.items():
                if x[0] == value[1][0] and x[1] == value[1][1]: #Get id of block clicked on
                    self.tile_to_place_id = _id
                

    def get_cell_from_mousepos(self, pos: tuple) -> Block:
        cell = ((pos[0]-self.total_mouse_change[0])//self.cell_size, 
                 (pos[1]-self.total_mouse_change[1])//self.cell_size)

        block = next((x for x in self.blocks if x.pos_on_grid == cell), None)
        return block


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


class Sidebar:
    def __init__(self, ui, scr_size: tuple, viewport_w: int, color, screen):
        self.ui = ui
        self.scr_w, self.scr_h = scr_size
        self.size = (self.scr_w - viewport_w + 10, self.scr_h)
        self.pos = (viewport_w, 0)
        self.col = color
        self.screen = screen

        self.buttons = {"GridButton" : button.GridButton((1125, 550), (32, 32), self.screen), 
                        "BrushButton" : button.ToolButton((930, 550), (32, 32), self.screen, ui.manager, State.BRUSH, "Assets\\brush.png"),
                        "EraserButton" : button.ToolButton((970, 550), (32, 32), self.screen, ui.manager, State.ERASE, "Assets\\eraser.png"),
                        "ColorPickButton" : button.ToolButton((1010, 550), (32, 32), self.screen, ui.manager, State.COLOR_PICKER, "Assets\\color_picker.png")}

        self.buttons["BrushButton"].set_state(1) #set brush to be on
        self.brushes_group = button.ButtonGroup([self.buttons["BrushButton"], self.buttons["EraserButton"], self.buttons["ColorPickButton"]])

        self.selected_tile_highlight = pygame.Surface((ui.cell_size+6, ui.cell_size+6)) #selected tile highlight
        self.selected_tile_highlight.fill((255, 255, 0))
        self.selected_bg = pygame.Surface((ui.cell_size, ui.cell_size))
        self.selected_bg.fill(self.col)

    def update(self):
        surf = pygame.Surface(self.size)
        surf.fill(self.col)
        self.screen.blit(surf, self.pos)

        self.brushes_group.update() #Brush buttons

        for x in self.buttons:
            self.buttons[x].update() #Brush and grid buttons

        for x in self.ui.tiles_dict:
            if x == self.ui.tile_to_place_id: #Tile selection highlighting
                self.screen.blit(self.selected_tile_highlight, (self.ui.tiles_dict[x][1][0] - 3, self.ui.tiles_dict[x][1][1] - 3))
                self.screen.blit(self.selected_bg, (self.ui.tiles_dict[x][1][0], self.ui.tiles_dict[x][1][1]))
            self.screen.blit(self.ui.tiles_dict[x][0], self.ui.tiles_dict[x][1])