import pygame, threading, time
pygame.init()

import main
import input_overrides
import palette

from import_export import ie_interface
from settings import settings

from tests._constants import *
from tests import _utils as utils
from tests._utils import inject_click_at_pos_events, inject_keydown


def main_tests():
    settings.FPS_CAP = 1000 # Boost fps cap for faster tests
    utils.window = main.Window()

    while utils.running:
        if utils.tests_process_cycles > 0:
            main.main_loop(utils.window)
            
            if input_overrides.get_mouse_pressed()[0]:
                pygame.draw.circle(utils.window.screen, (255,0,0), input_overrides.get_mouse_pos(), 5)
            pygame.draw.circle(utils.window.screen, (255,255,0), input_overrides.get_mouse_pos(), 3)
            
            utils.window.update_screen()

            utils.tests_process_cycles -= 1
            
            time.sleep(SLEEP_BETWEEN_PROCESS_LOOPS_SEC)


class TestsInitialize():
    def test_initialization(self):
        game_thread = threading.Thread(target=main_tests)
        game_thread.start()

        time.sleep(0.5)
        utils.run_game_for_cycles(1)

        assert utils.window != None, "Window failed to initialize"

        successful = palette.pm_obj.change_palette(settings.TESTS_PALETTE_PATH)
        assert successful, "Palette loading failed"

        utils.run_game_for_cycles(1)
        
        try:
            ie_interface.Iie_obj.import_tilemap_from_path(settings.TESTS_TILEMAP_PATH, check_palette_change=False)
        except Exception as e:
            assert False, "Error loading tilemap: %s - %s." % (e.filename, e.strerror)

        utils.run_game_for_cycles(2)
