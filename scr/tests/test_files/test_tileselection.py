import pygame

import sidebar
import palette

from settings import settings

from tests._constants import *
from tests import _utils as utils
from tests._utils import inject_click_at_pos_events, inject_keydown


class TestsTileSelectionArrowKeys():
    def test_selection_arrow_keys_horizontal(self):
        """Scroll horizontally through pages of tile selection and back"""
        tiles_data = palette.pm_obj.get_data() #  Data is of format [[ {"id":1, "image":pygame.Surf, "pos":[950, 50]}, ...]]

        assert sidebar.s_obj.tiles_page == 0, "The tiles page should now be 0"
        assert palette.pm_obj.selected_tile_id == tiles_data[0][0]["id"], "The first tile should be selected at the beginning of the tests"
        
        for i in range(1, settings.TILES_PER_ROW):
            inject_keydown(pygame.K_RIGHT, pygame.KSCAN_RIGHT)
            assert palette.pm_obj.selected_tile_id == tiles_data[0][i]["id"], f"Tile ID doesn't match to what it should, i:{i}"
        
        # Now should be on the most right tile of the selection
        assert sidebar.s_obj.tiles_page == 0, "The tiles page should still be 0"
        
        #Flip to next page
        inject_keydown(pygame.K_RIGHT, pygame.KSCAN_RIGHT)
        assert sidebar.s_obj.tiles_page == 1, "The tiles page should now be 1"
        assert palette.pm_obj.selected_tile_id == tiles_data[1][0]["id"], f"Tile ID doesn't match to what it should. Tile id is not 2nd page first tile"
        
        # Go to the other right end of the 2nd page
        for i in range(1, settings.TILES_PER_ROW):
            inject_keydown(pygame.K_RIGHT, pygame.KSCAN_RIGHT)
            assert palette.pm_obj.selected_tile_id == tiles_data[1][i]["id"], f"Tile ID doesn't match to what it should, 2nd page i:{i}"
        
        # Try to go to 3rd page which shouldn't exist
        inject_keydown(pygame.K_RIGHT, pygame.KSCAN_RIGHT)
        assert sidebar.s_obj.tiles_page == 1, "The tiles page should remain as 1"
        assert palette.pm_obj.selected_tile_id == tiles_data[1][4]["id"], f"Tile ID doesn't match to what it should. Tile id is not 2nd page last tile"
        
        # Scroll back to first page
        for i in range(1, 2 * settings.TILES_PER_ROW):
            inject_keydown(pygame.K_LEFT, pygame.KSCAN_LEFT)
        
        assert sidebar.s_obj.tiles_page == 0, "The tiles page now be 0"
        assert palette.pm_obj.selected_tile_id == tiles_data[0][0]["id"], f"Tile ID doesn't match to 1st page 1st tile"
        
        # Try to scroll left after reaching the first element (nothing should happen)
        inject_keydown(pygame.K_LEFT, pygame.KSCAN_LEFT)
        assert sidebar.s_obj.tiles_page == 0, "The tiles page now be 0"
        assert palette.pm_obj.selected_tile_id == tiles_data[0][0]["id"], f"Tile ID doesn't match to 1st page 1st tile"
        
    def test_selection_arrow_keys_vertical(self):
        """Scroll down the tile selection and back up"""
        tiles_data = palette.pm_obj.get_data() #  Data is of format [[ {"id":1, "image":pygame.Surf, "pos":[950, 50]}, ...]]

        assert sidebar.s_obj.tiles_page == 0, "The tiles page should now be 0"
        assert palette.pm_obj.selected_tile_id == tiles_data[0][0]["id"], "The first tile should be selected at the beginning of the tests"
        
        # Go to bottom most left tile
        for i in range(1, settings.TILES_PER_COL):
            inject_keydown(pygame.K_DOWN, pygame.KSCAN_DOWN)
            pos = settings.TILES_PER_ROW * i
            assert palette.pm_obj.selected_tile_id == tiles_data[0][pos]["id"], f"Tile ID doesn't match to what it should, pos:{pos}"
        
        # Try to go one more down (nothing should happen)
        inject_keydown(pygame.K_DOWN, pygame.KSCAN_DOWN)
        bottom_left_index = (settings.TILES_PER_COL - 1) * settings.TILES_PER_ROW
        assert palette.pm_obj.selected_tile_id == tiles_data[0][bottom_left_index]["id"], f"Tile ID doesn't match to what it should, pos:{bottom_left_index}"


        # Go back to top left
        for i in range(1, settings.TILES_PER_COL):
            inject_keydown(pygame.K_UP, pygame.KSCAN_UP)
            pos = (settings.TILES_PER_COL - i - 1) * settings.TILES_PER_ROW
            assert palette.pm_obj.selected_tile_id == tiles_data[0][pos]["id"], f"Tile ID doesn't match to what it should, pos:{pos}"
            
        assert sidebar.s_obj.tiles_page == 0, "The tiles page should be 0"
        assert palette.pm_obj.selected_tile_id == tiles_data[0][0]["id"], f"Tile ID doesn't match to 1st page 1st tile"
            
        # Try to scroll up again (nothing should happen)
        inject_keydown(pygame.K_UP, pygame.KSCAN_UP)
        assert sidebar.s_obj.tiles_page == 0, "The tiles page should be 0"
        assert palette.pm_obj.selected_tile_id == tiles_data[0][0]["id"], f"Tile ID doesn't match to 1st page 1st tile"
