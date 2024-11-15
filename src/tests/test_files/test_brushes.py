import pygame

import palette
import sidebar
import ui

from tests._constants import *
from tests import _utils as utils
from tests._utils import inject_click_at_pos_events, inject_keydown


class TestsBrushes():
    def test_paint(self):        
        inject_keydown(pygame.K_p, pygame.KSCAN_P)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "100", "Only the brush should be equipped"
        
        assert palette.pm_obj.selected_tile_id == 0, f"Tile ID doesn't match to 0"
        
        tile_pos = utils.get_tile_default_pos(0, 1)
        inject_click_at_pos_events(LEFT_CLICK, tile_pos)
        
        block = next((x for x in ui.ui_obj.blocks if x.pos_on_grid == (0, 1)), None)
        assert block.tile_id == 0, f"Tile {block.pos_on_grid} doesn't match what it should."
        
        inject_keydown(pygame.K_RIGHT, pygame.KSCAN_RIGHT)
        assert palette.pm_obj.selected_tile_id == 1, f"Tile ID doesn't match to 1"
        
        tile_pos = utils.get_tile_default_pos(1, 1)
        inject_click_at_pos_events(LEFT_CLICK, tile_pos)
        
        block = next((x for x in ui.ui_obj.blocks if x.pos_on_grid == (1, 1)), None)
        assert block.tile_id == 1, f"Tile {block.pos_on_grid} doesn't match what it should."
        
        
    def test_color_picker(self):
        inject_keydown(pygame.K_o, pygame.KSCAN_O)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "001", "Only the color picker should be equipped"
        
        tile_pos = utils.get_tile_default_pos(1, 0)
        inject_click_at_pos_events(LEFT_CLICK, tile_pos)
        
        block = next((x for x in ui.ui_obj.blocks if x.pos_on_grid == (1, 0)), None)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        
        assert buttons_binary == "100", "After using the color picker, brush should be equipped"
        assert sidebar.s_obj.tiles_page == 1, "The tiles page should be 1"
        assert palette.pm_obj.selected_tile_id == block.tile_id, f"Selected tile doesn't match (1, 0) tile's ID"
        
        # Pick (0, 1)
        inject_keydown(pygame.K_o, pygame.KSCAN_O)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "001", "Only the color picker should be equipped"
        
        tile_pos = utils.get_tile_default_pos(0, 1)
        inject_click_at_pos_events(LEFT_CLICK, tile_pos)
        
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        
        assert buttons_binary == "100", "After using the color picker, brush should be equipped"
        assert sidebar.s_obj.tiles_page == 0, "The tiles page should be 1"
        assert palette.pm_obj.selected_tile_id == 0, f"The picked tile should be of ID 0"
        
        
    def test_eraser(self):
        inject_keydown(pygame.K_e, pygame.KSCAN_E)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "010", "Only the eraser should be equipped"
        
        # Erase (0, 1)
        tile_pos = utils.get_tile_default_pos(0, 1)
        inject_click_at_pos_events(LEFT_CLICK, tile_pos)
        
        block = next((x for x in ui.ui_obj.blocks if x.pos_on_grid == (0, 1)), None)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        
        assert buttons_binary == "010", "Eraser should still be equipped"
        assert sidebar.s_obj.tiles_page == 0, "The tiles page should be 1"
        assert palette.pm_obj.selected_tile_id == 0, f"Selected tile doesn't match (1, 0) tile's ID"
        assert block.tile_id == -1, f"Erased tile should be of ID -1"
        
        # Erase (1, 1)
        tile_pos = utils.get_tile_default_pos(1, 1)
        inject_click_at_pos_events(LEFT_CLICK, tile_pos)
        
        block = next((x for x in ui.ui_obj.blocks if x.pos_on_grid == (1, 1)), None)
        assert block.tile_id == -1, f"Erased tile should be of ID -1"
        
        # Switch back to brush
        inject_keydown(pygame.K_p, pygame.KSCAN_P)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "100", "Only the eraser should be equipped"