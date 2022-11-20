import pygame, time
import export, import_map, button
from manager import State
pygame.init()

class Sidebar:
    def __init__(self, ui, scr_size: tuple, pos: tuple, viewport_w: int, screen):
        self.ui = ui
        self.scr_w, self.scr_h = scr_size
        self.size = (self.scr_w - viewport_w + 10, self.scr_h)
        self.pos = pos
        self.col = (200,200,200)
        self.screen = screen

        self.buttons = {"GridButton" : button.ToolButton((1150, 550), (32, 32), self.screen, ui.manager, "Assets\\grid_button.png", hover_text="Grid (G)", init_state=1), 
                        "BrushButton" : button.ToolButton((931, 550), (32, 32), self.screen, ui.manager, "Assets\\brush.png", state_when_clicked=State.BRUSH,  hover_text="Paint (P)", can_toggle_off=False, init_state=1),
                        "EraserButton" : button.ToolButton((971, 550), (32, 32), self.screen, ui.manager, "Assets\\eraser.png", state_when_clicked=State.ERASE, hover_text="Eraser (E)", can_toggle_off=False),
                        "ColorPickButton" : button.ToolButton((1011, 550), (32, 32), self.screen, ui.manager, "Assets\\color_picker.png", state_when_clicked=State.COLOR_PICKER, hover_text="Color Picker (O)", can_toggle_off=False),
                        "PageLeftButton" : button.TextButton((self.scr_w-self.size[0]+16, self.scr_h//2-56), (16, 48), self.screen, "<", 20, hover_col=(220,220,220)),
                        "PageRightButton" : button.TextButton((self.scr_w-30, self.scr_h//2-56), (16, 48), self.screen,  ">", 20, hover_col=(220,220,220))}

        self.brushes_group = button.ButtonGroup([self.buttons["BrushButton"], self.buttons["EraserButton"], self.buttons["ColorPickButton"]])

        self.selected_tile_highlight = pygame.Surface((ui.cell_size+6, ui.cell_size+6)) #selected tile highlight
        self.selected_tile_highlight.fill((255, 255, 0))
        self.selected_bg = pygame.Surface((ui.cell_size, ui.cell_size))
        self.selected_bg.fill(self.col)
        self.font = pygame.font.Font(None, 30)
        self.tiles_page = 0
        self.left_button_active = False
        self.right_button_active = True


    def on_mouse_click(self, mouse_pos):
        for x in self.buttons:
             if self.buttons[x].check_clicked(mouse_pos):
                if x == "PageLeftButton" and self.left_button_active:
                    self.tiles_page -= 1
                    self.ui.tile_to_place_id = self.ui.current_palette.palette_data[self.tiles_page][0]["id"]

                elif x == "PageRightButton" and self.right_button_active:
                    self.tiles_page += 1
                    self.ui.tile_to_place_id = self.ui.current_palette.palette_data[self.tiles_page][0]["id"]


    def update(self):
        surf = pygame.Surface(self.size)
        surf.fill(self.col)
        self.screen.blit(surf, self.pos)

        self.brushes_group.update() #Brush buttons

        for x in self.buttons:
            if not self.toggle_left_right(x):
                continue
            self.buttons[x].update()
        
        mousepos = pygame.mouse.get_pos()
        for x in self.buttons.values():
            x.update_hover(mousepos)

        if len(self.ui.manager.palette_manager.current_palette.tile_list) == 0:
            self.draw_empty_palette()

        if self.ui.manager.palette_manager.current_palette.pages > 1:
            self.draw_page_num()

        self.ui.manager.palette_manager.current_palette_text()

        for val in self.ui.current_palette.palette_data[self.tiles_page]:
            if val["id"] == self.ui.tile_to_place_id: #Tile selection highlighting
                self.screen.blit(self.selected_tile_highlight, (val["pos"][0] - 3, val["pos"][1] - 3))
                self.screen.blit(self.selected_bg, val["pos"])
            self.screen.blit(val["image"], val["pos"])
    

    def toggle_left_right(self, btn_name: str) -> bool:
        """Returns False if should not continue the for loop"""
        current_palette = self.ui.manager.palette_manager.current_palette
        if btn_name == "PageLeftButton":
            if current_palette.pages <= 1 or self.tiles_page == 0:
                self.left_button_active = False
                return False
            else:
                self.left_button_active = True

        if btn_name == "PageRightButton":
            if current_palette.pages <= 1 or self.tiles_page == current_palette.pages - 1:
                self.right_button_active = False
                return False
            else:
                self.right_button_active = True

        return True


    def draw_empty_palette(self):
        col = 150
        text = self.font.render("PALETTE IS EMPTY", True, (col,col,col))
        text2 = self.font.render("PRESS ADD TILE", True, (col,col,col))

        text_rect = text.get_rect(center=(self.size[0]//2+self.pos[0], self.scr_h//2-20))
        text_rect2 = text2.get_rect(center=(self.size[0]//2+self.pos[0], self.scr_h//2+10))
        
        self.screen.blit(text, text_rect)
        self.screen.blit(text2, text_rect2)


    def draw_page_num(self):
        text = self.font.render(f"{self.tiles_page + 1}", True, (150,150,150))
        text_rect = text.get_rect(center=(self.size[0]//2+self.pos[0]-8, 510))

        self.screen.blit(text, text_rect)