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


SLEEP_BETWEEN_TESTS_SEC = 0.2


running = True
tests_process_cycles = 2
window = None

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


def run_game_for_cycles(cycles: int, sleeptime_s:float=0.1) -> None: 
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





class TestsButton():
    def test_initialization(self):
        global window

        game_thread = threading.Thread(target=main_tests)
        game_thread.start()

        time.sleep(0.1)
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

        inject_click_at_pos_events([1,0,0], (btn_pos[0] + 10, btn_pos[1] + 10))

        assert grid_btn_state != sidebar.s_obj.buttons_dict["GridButton"].is_clicked(), "Grid button state didn't change"
        assert grid_on_state  != manager.m_obj.grid_on, "Grid on state didn't change"


    def test_tool_buttons(self):
        buttons = sidebar.s_obj.brushes_group.get_pressed_all()
        assert buttons[0] and not buttons[1] and not buttons[2], "Only the brush should be equipped"
        
        inject_keydown(pygame.K_e, pygame.KSCAN_E)
        buttons = sidebar.s_obj.brushes_group.get_pressed_all()
        assert not buttons[0] and buttons[1] and not buttons[2], "Only the eraser should be equipped"

        inject_keydown(pygame.K_o, pygame.KSCAN_O)
        buttons = sidebar.s_obj.brushes_group.get_pressed_all()
        assert not buttons[0] and not buttons[1] and buttons[2], "Only the Color Picker should be equipped"

        inject_keydown(pygame.K_p, pygame.KSCAN_P)
        buttons =  sidebar.s_obj.brushes_group.get_pressed_all()
        assert buttons[0] and not buttons[1] and not buttons[2], "Only the brush should be equipped"


    def test_tool_mouse(self):
        brush_pos = sidebar.s_obj.buttons_dict["BrushButton"].pos
        eraser_pos = sidebar.s_obj.buttons_dict["EraserButton"].pos
        colorpick_pos = sidebar.s_obj.buttons_dict["ColorPickButton"].pos

        buttons = sidebar.s_obj.brushes_group.get_pressed_all()
        assert buttons[0] and not buttons[1] and not buttons[2], "Only the brush should be equipped"
        
        inject_click_at_pos_events([1,0,0], (eraser_pos[0]+10, eraser_pos[1]+10))
        buttons = sidebar.s_obj.brushes_group.get_pressed_all()
        assert not buttons[0] and buttons[1] and not buttons[2], "Only the eraser should be equipped"

        inject_click_at_pos_events([1,0,0], (colorpick_pos[0]+10, colorpick_pos[1]+10))
        buttons = sidebar.s_obj.brushes_group.get_pressed_all()
        assert not buttons[0] and not buttons[1] and buttons[2], "Only the Color Picker should be equipped"

        inject_click_at_pos_events([1,0,0], (brush_pos[0]+10, brush_pos[1]+10))
        buttons = sidebar.s_obj.brushes_group.get_pressed_all()
        assert buttons[0] and not buttons[1] and not buttons[2], "Only the brush should be equipped"


    def test_page_turn(self):
        left_pos = sidebar.s_obj.buttons_dict["PageLeftButton"].pos
        right_pos = sidebar.s_obj.buttons_dict["PageRightButton"].pos

        pages = palette.pm_obj.get_total_pages()

        first_page_first_data = palette.pm_obj.get_data_current_page()[0]

        assert pages == 2, "For testing purposes, palette at 'Data\\Palettes\\Palette_tests' must have 2 pages of tiles"
        assert sidebar.s_obj.tiles_page == 0, "In the beginning tiles page should be 0"
        assert first_page_first_data["id"] == 0, "The first tile should be ID 0"

        inject_click_at_pos_events([1,0,0], (right_pos[0]+10, right_pos[1]+10))

        assert sidebar.s_obj.tiles_page == 1, "After turning page should be one"
        assert palette.pm_obj.get_data_current_page()[0]["id"] != first_page_first_data["id"], "ID Should be different than 0"

        inject_click_at_pos_events([1,0,0], (left_pos[0]+10, left_pos[1]+10))

        assert sidebar.s_obj.tiles_page == 0, "After turning the page back, the page should be 0"
        assert first_page_first_data["id"] == 0, "After turning back the first tile should be ID 0"


    def test_end(self):
        global running
        running = False


if __name__ == "__main__":
    os.system("pytest -q scr/tests.py")
    #os.system("pytest -q -s scr/tests.py")
