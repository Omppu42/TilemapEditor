import pygame, time
import button
from manager import State
pygame.init()

class Sidebar:
    def __init__(self, ui, scr_size: tuple, viewport_w: int, screen):
        self.ui = ui
        self.scr_w, self.scr_h = scr_size
        self.size = (self.scr_w - viewport_w + 10, self.scr_h)
        self.pos = (viewport_w, 0)
        self.col = (200,200,200)
        self.screen = screen

        self.buttons = {"GridButton" : button.GridButton((1125, 550), (32, 32), self.screen), 
                        "BrushButton" : button.ToolButton((930, 550), (32, 32), self.screen, ui.manager, State.BRUSH, "Assets\\brush.png", hover_text="Paint (P)"),
                        "EraserButton" : button.ToolButton((970, 550), (32, 32), self.screen, ui.manager, State.ERASE, "Assets\\eraser.png", hover_text="Eraser (E)"),
                        "ColorPickButton" : button.ToolButton((1010, 550), (32, 32), self.screen, ui.manager, State.COLOR_PICKER, "Assets\\color_picker.png", hover_text="Color Picker (O)")}

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

        self.update_hover()

        for x in self.ui.tiles_dict:
            if x == self.ui.tile_to_place_id: #Tile selection highlighting
                self.screen.blit(self.selected_tile_highlight, (self.ui.tiles_dict[x][1][0] - 3, self.ui.tiles_dict[x][1][1] - 3))
                self.screen.blit(self.selected_bg, (self.ui.tiles_dict[x][1][0], self.ui.tiles_dict[x][1][1]))
            self.screen.blit(self.ui.tiles_dict[x][0], self.ui.tiles_dict[x][1])


    def update_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        for x in self.buttons.values():
            if x.rect.collidepoint(mouse_pos): #if mouse hovering button
                if x.hover_start_time == 0:
                    x.hover_start_time = time.time() #set hovering start time
                
                if time.time() - x.hover_start_time >= x.hover_delay: #hovered for hover_delay amount of time
                    self.screen.blit(x.hover_text_render, x.hover_text_rect)

            else: #not hovering
                x.hover_start_time = 0
            