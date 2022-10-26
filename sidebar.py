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

        self.buttons = {"GridButton" : button.GridButton((1150, 500), (32, 32), self.screen), 
                        "BrushButton" : button.ToolButton((920, 500), (32, 32), self.screen, ui.manager, State.BRUSH, "Assets\\brush.png", hover_text="Paint (P)"),
                        "EraserButton" : button.ToolButton((960, 500), (32, 32), self.screen, ui.manager, State.ERASE, "Assets\\eraser.png", hover_text="Eraser (E)"),
                        "ColorPickButton" : button.ToolButton((1000, 500), (32, 32), self.screen, ui.manager, State.COLOR_PICKER, "Assets\\color_picker.png", hover_text="Color Picker (O)"),
                        "ExportButton" : button.TextButton((915, 550), (128, 16), self.screen, "EXPORT MAP", 20, hover_col=(190,190,190)),
                        "ImportButton" : button.TextButton((915, 575), (128, 16), self.screen, "IMPORT MAP", 20, hover_col=(190,190,190)),
                        "ExportPaletteButton" : button.TextButton((1060, 550), (128, 16), self.screen, "EXPORT PALETTE", 20, hover_col=(200,200,200)),
                        "ImportPaletteButton" : button.TextButton((1060, 575), (128, 16), self.screen, "IMPORT PALETTE", 20, hover_col=(200,200,200))}
                        #TODO: make new buttons functional
                        
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
        
        mousepos = pygame.mouse.get_pos()
        for x in self.buttons.values():
            x.update_hover(mousepos)

        for _id, val in enumerate(self.ui.tiles_data):
            if _id == self.ui.tile_to_place_id: #Tile selection highlighting
                self.screen.blit(self.selected_tile_highlight, (val["pos"][0] - 3, val["pos"][1] - 3))
                self.screen.blit(self.selected_bg, val["pos"])
            self.screen.blit(val["image"], val["pos"])
            