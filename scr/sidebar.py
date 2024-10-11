import pygame

from util.tkinter_opener import tk_util
from util.util_logger import logger
from settings.data import State

import settings.data as data
import settings.settings as settings
import util.util as util
import GUI.button as button

import mouse
import manager
import palette


pygame.init()

class Sidebar:
    BG_COLOR = (200,200,200)
    TILE_HIGHLIGHT_W = 3

    def __init__(self, screen):
        self.size = (settings.SCR_W - settings.VIEWPORT_W + 10, settings.SCR_H)
        self.pos = (settings.VIEWPORT_W, 0)
        self.screen = screen

        # MAIN BG SURFACE --------
        self.sidebar_bg_surf = pygame.Surface(self.size)
        self.sidebar_bg_surf.fill(Sidebar.BG_COLOR)

        # BUTTONS -------------
        self.buttons_dict = {"GridButton" : button.ToolButton(self.screen, (1150, 550), (32, 32), 
                                                              "Assets\\grid_button.png", hover_text="Grid (G)", init_state=1), 
                            "BrushButton" : button.ToolButton(self.screen, (931, 550), (32, 32),  
                                                              "Assets\\brush.png", state_when_clicked=State.BRUSH,  hover_text="Paint (P)", can_toggle_off=False, init_state=1),
                           "EraserButton" : button.ToolButton(self.screen, (971, 550), (32, 32),  
                                                              "Assets\\eraser.png", state_when_clicked=State.ERASE, hover_text="Eraser (E)", can_toggle_off=False),
                        "ColorPickButton" : button.ToolButton(self.screen, (1011, 550), (32, 32), 
                                                              "Assets\\color_picker.png", state_when_clicked=State.COLOR_PICKER, hover_text="Tile Picker (O)", can_toggle_off=False),
                         "PageLeftButton" : button.TextButton(self.screen, (settings.SCR_W-self.size[0]+16, settings.SCR_H//2-56), (16, 48),  
                                                              "<", 20, hover_col=(220,220,220)),
                        "PageRightButton" : button.TextButton(self.screen, (settings.SCR_W-30, settings.SCR_H//2-56), (16, 48),
                                                              ">", 20, hover_col=(220,220,220))}

        self.brushes_group = button.ButtonGroup([self.buttons_dict["BrushButton"], self.buttons_dict["EraserButton"], self.buttons_dict["ColorPickButton"]])

        # TILE SELECTION ---------- 
        # Yellow highlight
        self.selected_tile_highlight = pygame.Surface((settings.CELL_SIZE + Sidebar.TILE_HIGHLIGHT_W*2, settings.CELL_SIZE + Sidebar.TILE_HIGHLIGHT_W*2)) 
        self.selected_tile_highlight.fill((255, 255, 0))

        # To the highlight surface draw a rectangle to make the surface seem hollow
        # Used to correct for PNG tiles to not fill the whole tile yellow
        pygame.draw.rect(self.selected_tile_highlight, Sidebar.BG_COLOR, (Sidebar.TILE_HIGHLIGHT_W, Sidebar.TILE_HIGHLIGHT_W, settings.CELL_SIZE, settings.CELL_SIZE))

        self.tiles_page = 0
        self.tile_selection_rects = None # Make sidebar tiles' rects

        logger.debug("Initialized Sidebar")


    # GETTERS AND SETTERS ---------
    def set_tile_selection_page(self, page: int) -> None:
        if palette.pm_obj.get_total_pages() - 1 < page or page < 0:
            logger.error(f"Trying to set tile selection page to an invalid page ({page})")
            return
        
        self.tiles_page = page
        self.update_page_arrows()


    # PRIVATE --------------------
    def __check_click_buttons(self, mouse_pos) -> None:
        """Check each button to see if the button was clicked and execute code accordingly"""
        for _name, _button in self.buttons_dict.items():
            # If this button is not clicked, continue
            if not _button.check_clicked(): continue

            # Check if the button name matches
            if _name == "PageLeftButton":
                # Make tiles_page wrap around to last page in case something went wrong to avoid errors  
                self.tiles_page = (self.tiles_page - 1) if self.tiles_page > 0 else palette.pm_obj.get_total_pages() - 1
                palette.pm_obj.select_nth_tile_on_page(0)
                self.update_page_arrows()

            elif _name == "PageRightButton":
                # Make tiles_page wrap around to 0 in case something went wrong to avoid errors 
                self.tiles_page = (self.tiles_page + 1) % palette.pm_obj.get_total_pages()
                palette.pm_obj.select_nth_tile_on_page(0)
                self.update_page_arrows()


    def __check_tile_change(self, mouse_pos):
        """After clicking, check if clicked on a tile from tileselection and make the appropriate action. (Change selected tile or delete the tile from the palette)"""        
        for _rect in self.tile_selection_rects:
            # If this rect is not the one clicked, continue looping
            if not _rect.collidepoint(mouse_pos): continue

            # Select brush when clicking any tile from selection
            manager.m_obj.equip_brush()

            # Find the corresponding tile from palette data that matches the _rect that was clicked
            for _tile in palette.pm_obj.get_data_current_page():
                # Check if the rect x any y are the same as the position in palette_data
                if _rect[0] == _tile["pos"][0] and _rect[1] == _tile["pos"][1]:
                    # If removing tiles from palette is active, remove this tile
                    if manager.m_obj.remove_palette_tiles:
                        tk_util.queue_func(palette.pm_obj.remove_tile, _tile["id"])
                    # If not, equip the tile that was clicked on
                    else:
                        palette.pm_obj.selected_tile_id = _tile["id"]

                    return # return since there can only be one clicked tile


    # PUBLIC ---------------------
    def select_tile_row_col(self, col: int, row: int) -> None:
        """Row and col should go from from 0 to TILES_PER_ROW - 1"""
        _total_tiles = palette.pm_obj.get_tiles_count()

        new_id = (col + row * settings.TILES_PER_ROW) + self.tiles_page * settings.TILES_PER_PAGE

        # Make sure no invalid IDs
        if new_id >= _total_tiles:
            new_id = _total_tiles - 1

        palette.pm_obj.selected_tile_id = new_id


    def arrowkeys_tile_selection_move(self, event) -> None:
        _total_pages = palette.pm_obj.get_total_pages() - 1  # from 0 
        _selected_row = util.get_tile_row_from_index(palette.pm_obj.selected_tile_id) # from 0 to TILES_PER_ROW - 1
        _selected_col = util.get_tile_column_from_index(palette.pm_obj.selected_tile_id) # from 0 to TILES_PER_COL - 1
        manager.m_obj.equip_brush()

        match (event.key):
            case (pygame.K_LEFT):
                # On first page left edge
                if self.tiles_page <= 0 and _selected_col <= 0: return

                # Not on first page and on left edge
                if _selected_col <= 0:
                    # Flip page -1 and select the tile on same col but on opposite edge
                    self.set_tile_selection_page(self.tiles_page - 1) 
                    self.select_tile_row_col(settings.TILES_PER_ROW - 1, _selected_row)
                    return
                
                palette.pm_obj.selected_tile_id -= 1

            case (pygame.K_RIGHT):
                # On last page right edge
                if self.tiles_page >= _total_pages and _selected_col >= settings.TILES_PER_ROW - 1: return
                # If the next tile is outside the tile count
                if palette.pm_obj.selected_tile_id + 1 >= palette.pm_obj.get_tiles_count(): return

                # If on the edge
                if _selected_col >= settings.TILES_PER_ROW - 1:
                    # Flip page +1 and select the tile on same col but on opposite edge
                    self.set_tile_selection_page(self.tiles_page + 1) 
                    self.select_tile_row_col(0, _selected_row)
                    return

                palette.pm_obj.selected_tile_id += 1


            case (pygame.K_UP):
                # If on the top row
                if _selected_row <= 0: return

                palette.pm_obj.selected_tile_id -= settings.TILES_PER_ROW

            case (pygame.K_DOWN):
                # If on the bottom row
                if _selected_row >= settings.TILES_PER_COL - 1: return
                # If there is no tile below
                if palette.pm_obj.selected_tile_id + settings.TILES_PER_ROW >= palette.pm_obj.get_tiles_count(): return

                palette.pm_obj.selected_tile_id += settings.TILES_PER_ROW


    def post_init(self) -> None:
        self.create_tile_selection_rects()
        self.update_page_arrows()


    def create_tile_selection_rects(self) -> None:
        self.tile_selection_rects = [pygame.Rect(_tile["pos"], (settings.CELL_SIZE, settings.CELL_SIZE)) for _tile in palette.pm_obj.get_data_current_page()]


    def on_left_mouse_click(self):
        mouse_pos = mouse.get_pos_override()

        self.__check_click_buttons(mouse_pos)
        self.__check_tile_change(mouse_pos)

        manager.m_obj.remove_palette_tiles = False


    def update(self):
        self.screen.blit(self.sidebar_bg_surf, self.pos)

        self.brushes_group.update() #Brush buttons

        for _button in self.buttons_dict.values():
            _button.update()

        # Empty palette
        if len(palette.pm_obj.get_current_tiles()) == 0:
            self.draw_empty_palette()

        # Page number
        if palette.pm_obj.current_palette.pages > 1:
            self.draw_page_num()

        # Current palette
        palette.pm_obj.draw_current_palette_text()

        # Draw each tile in the selection
        for tile in palette.pm_obj.get_data_current_page():
            # Draw tile selection highlight
            if tile["id"] == palette.pm_obj.selected_tile_id: 
                self.screen.blit(self.selected_tile_highlight, (tile["pos"][0] - Sidebar.TILE_HIGHLIGHT_W, tile["pos"][1] - Sidebar.TILE_HIGHLIGHT_W))
            self.screen.blit(tile["image"], tile["pos"])
    


    def update_page_arrows(self) -> None:
        """Updates page scrolling arrows according to the current palette"""
        self.buttons_dict["PageLeftButton"].disabled = False
        self.buttons_dict["PageRightButton"].disabled = False

        # self.tiles_page starts at 0, palette.pages start at 1
        # If this is the first page
        if self.tiles_page == 0:
            self.buttons_dict["PageLeftButton"].disabled = True

        # If this is the last page
        if (self.tiles_page + 1) == palette.pm_obj.current_palette.pages:
            self.buttons_dict["PageRightButton"].disabled = True


    def draw_empty_palette(self):
        col = 150
        text = data.font_30.render("PALETTE IS EMPTY", True, (col,col,col))
        text2 = data.font_30.render("PRESS TILE > ADD", True, (col,col,col))

        text_rect = text.get_rect(center=(self.size[0]//2+self.pos[0], settings.SCR_H//2-20))
        text_rect2 = text2.get_rect(center=(self.size[0]//2+self.pos[0], settings.SCR_H//2+10))
        
        self.screen.blit(text, text_rect)
        self.screen.blit(text2, text_rect2)


    def draw_page_num(self):
        text = data.font_30.render(f"{self.tiles_page + 1}", True, (150,150,150))
        text_rect = text.get_rect(center=(self.size[0]//2+self.pos[0]-8, 510))

        self.screen.blit(text, text_rect)



s_obj: Sidebar = None
def create_sidebar(screen) -> None:
    global s_obj
    s_obj = Sidebar(screen)