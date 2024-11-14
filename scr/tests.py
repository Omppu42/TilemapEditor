import time, os
import pytest
import threading
import pygame

pygame.init()

import main

from util.util_logger import logger
from util.util import timer

from GUI import popup

from settings import settings
from settings import data

from import_export import ie_interface

import palette
import ui
import manager
import sidebar
import input_overrides
import grid_resize


# In terminal, run: pytest -q scr/tests.py
# Add -s for printing

LEFT_CLICK = [1, 0, 0]
SLEEP_BETWEEN_TESTS_SEC = 0.2


running = True
tests_process_cycles = 2
window = None

# TODO: Implement can_run variable to continue straight after process_cycles have finished

def main_tests():
    global running, window, tests_process_cycles
    window = main.Window()

    while running:
        if tests_process_cycles > 0:
            main.main_loop(window)
            
            if input_overrides.get_mouse_pressed()[0]:
                pygame.draw.circle(window.screen, (255,0,0), input_overrides.get_mouse_pos(), 5)
            pygame.draw.circle(window.screen, (255,255,0), input_overrides.get_mouse_pos(), 3)
            
            window.update_screen()

            tests_process_cycles -= 1


@pytest.fixture(autouse=True)
def before_and_after_tests(request):
    
    def finalize():
        time.sleep(SLEEP_BETWEEN_TESTS_SEC)

    request.addfinalizer(finalize)

def run_game_for_cycles(cycles: int, sleeptime_s:float=0.05) -> None: 
    global tests_process_cycles
    tests_process_cycles = cycles

    time.sleep(sleeptime_s)


def inject_click_at_pos_events(buttons: "list", pos: tuple, run_cycles:int=1) -> None:
    assert len(buttons) == 3, "Injected buttons list must be of length 3 (non-test error)"
    down = pygame.event.Event(1025, {'pos': pos, 'button': 1, 'touch': False, 'window': None})
    up =   pygame.event.Event(1026, {'pos': pos, 'button': 1, 'touch': False, 'window': None})

    input_overrides.inject_mousepos(pos)
    input_overrides.inject_mousepressed(buttons)
    input_overrides.inject_event(down)
    input_overrides.inject_next_frame_event(up)

    run_game_for_cycles(run_cycles)

def inject_keydown(pygame_keycode: int, pygame_scancode: int, run_cycles=2) -> None:
    down = pygame.event.Event(768, {'unicode': pygame.key.name(pygame_keycode), 'key': pygame_keycode, 'mod': 4096, 'scancode': pygame_scancode, 'window': None})
    up =   pygame.event.Event(769, {'unicode': pygame.key.name(pygame_keycode), 'key': pygame_keycode, 'mod': 4096, 'scancode': pygame_scancode, 'window': None})

    input_overrides.inject_event(down)
    input_overrides.inject_next_frame_event(up)

    run_game_for_cycles(run_cycles)



class TestsInitialize():
    def test_initialization(self):
        global window

        game_thread = threading.Thread(target=main_tests)
        game_thread.start()

        time.sleep(0.5)
        run_game_for_cycles(1)

        assert window != None, "Window failed to initialize"

        successful = palette.pm_obj.change_palette(settings.TESTS_PALETTE_PATH)
        assert successful, "Palette loading failed"

        run_game_for_cycles(1)
        
        try:
            ie_interface.Iie_obj.import_tilemap_from_path(settings.TESTS_TILEMAP_PATH, check_palette_change=False)
        except Exception as e:
            assert False, "Error loading tilemap: %s - %s." % (e.filename, e.strerror)

        run_game_for_cycles(2)


class TestsButtons():
    def test_grid_toggle_key(self):
        grid_btn_state = sidebar.s_obj.buttons_dict["GridButton"].is_clicked()
        grid_on_state = manager.m_obj.grid_on

        inject_keydown(pygame.K_g, pygame.KSCAN_G)

        assert grid_btn_state != sidebar.s_obj.buttons_dict["GridButton"].is_clicked(), "Grid button state didn't change"
        assert grid_on_state  != manager.m_obj.grid_on, "Grid on state didn't change"

    def test_grid_toggle_mouse(self):
        btn_pos = sidebar.s_obj.buttons_dict["GridButton"].pos

        grid_btn_state = sidebar.s_obj.buttons_dict["GridButton"].is_clicked()
        grid_on_state = manager.m_obj.grid_on

        inject_click_at_pos_events(LEFT_CLICK, (btn_pos[0] + 10, btn_pos[1] + 10))

        assert grid_btn_state != sidebar.s_obj.buttons_dict["GridButton"].is_clicked(), "Grid button state didn't change"
        assert grid_on_state  != manager.m_obj.grid_on, "Grid on state didn't change"

    def test_tool_buttons(self):
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "100", "Only the brush should be equipped"
        
        inject_keydown(pygame.K_e, pygame.KSCAN_E)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "010", "Only the eraser should be equipped"

        inject_keydown(pygame.K_o, pygame.KSCAN_O)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "001", "Only the Color Picker should be equipped"

        inject_keydown(pygame.K_p, pygame.KSCAN_P)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "100", "Only the brush should be equipped"

    def test_tool_mouse(self):
        brush_pos = sidebar.s_obj.buttons_dict["BrushButton"].pos
        eraser_pos = sidebar.s_obj.buttons_dict["EraserButton"].pos
        colorpick_pos = sidebar.s_obj.buttons_dict["ColorPickButton"].pos

        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "100", "Only the brush should be equipped"
        
        inject_click_at_pos_events(LEFT_CLICK, (eraser_pos[0]+10, eraser_pos[1]+10))
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "010", "Only the eraser should be equipped"

        inject_click_at_pos_events(LEFT_CLICK, (colorpick_pos[0]+10, colorpick_pos[1]+10))
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "001", "Only the Color Picker should be equipped"

        inject_click_at_pos_events(LEFT_CLICK, (brush_pos[0]+10, brush_pos[1]+10))
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "100", "Only the brush should be equipped"

    def test_page_turn(self):
        left_pos = sidebar.s_obj.buttons_dict["PageLeftButton"].pos
        right_pos = sidebar.s_obj.buttons_dict["PageRightButton"].pos

        pages = palette.pm_obj.get_total_pages()
        first_page_first_data = palette.pm_obj.get_data_current_page()[0]

        assert pages == 2, "For testing purposes, palette at 'Data\\Palettes\\Palette_tests' must have 2 pages of tiles"
        assert sidebar.s_obj.tiles_page == 0, "In the beginning tiles page should be 0"
        assert first_page_first_data["id"] == 0, "The first tile should be ID 0"

        inject_click_at_pos_events(LEFT_CLICK, (right_pos[0]+10, right_pos[1]+10))

        assert sidebar.s_obj.tiles_page == 1, "After turning page should be one"
        assert palette.pm_obj.get_data_current_page()[0]["id"] != first_page_first_data["id"], "ID Should be different than 0"

        inject_click_at_pos_events(LEFT_CLICK, (left_pos[0]+10, left_pos[1]+10))

        assert sidebar.s_obj.tiles_page == 0, "After turning the page back, the page should be 0"
        assert first_page_first_data["id"] == 0, "After turning back the first tile should be ID 0"


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


class TestsBrushes():
    def test_paint(self):
        inject_keydown(pygame.K_p, pygame.KSCAN_P)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "100", "Only the brush should be equipped"
        
        print(1/2*settings.CELL_SIZE+settings.DEFAULT_GIRD_OFFSET[0], 3/2*settings.CELL_SIZE+settings.DEFAULT_GIRD_OFFSET[1])
        

class TestsEnd():
    def test_end(self):
        global running
        running = False


if __name__ == "__main__":
    #os.system("pytest -q scr/tests.py")
    os.system("C:\\Users\\RomanLesnyak\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python311\\Scripts\\pytest.exe -q -s scr/tests.py")
    #os.system("pytest -q -s scr/tests.py")
