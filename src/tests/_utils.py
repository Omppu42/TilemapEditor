import pygame, time
import pytest

from settings import settings
import input_overrides

from tests._constants import *


running = True
tests_process_cycles = 2
window = None



@pytest.fixture(autouse=True)
def before_and_after_tests(request):
    
    def finalize():
        time.sleep(SLEEP_BETWEEN_TESTS_SEC)

    request.addfinalizer(finalize)


def run_game_for_cycles(cycles: int) -> None: 
    global tests_process_cycles
    tests_process_cycles = cycles

    while tests_process_cycles > 0:
        pass


def inject_click_at_pos_events(buttons: "list", pos: tuple, run_cycles:int=1) -> None:
    assert len(buttons) == 3, "Injected buttons list must be of length 3 (non-test error)"
    down = pygame.event.Event(1025, {'pos': pos, 'button': 1, 'touch': False, 'window': None})
    up =   pygame.event.Event(1026, {'pos': pos, 'button': 1, 'touch': False, 'window': None})

    input_overrides.inject_mousepos(pos)
    input_overrides.inject_mousepressed(buttons)
    input_overrides.inject_event(down)
    input_overrides.inject_next_frame_event(up)

    run_game_for_cycles(run_cycles)

def inject_keydown(pygame_keycode: int, pygame_scancode: int, run_cycles=1) -> None:
    down = pygame.event.Event(768, {'unicode': pygame.key.name(pygame_keycode), 'key': pygame_keycode, 'mod': 4096, 'scancode': pygame_scancode, 'window': None})
    up =   pygame.event.Event(769, {'unicode': pygame.key.name(pygame_keycode), 'key': pygame_keycode, 'mod': 4096, 'scancode': pygame_scancode, 'window': None})

    input_overrides.inject_event(down)
    input_overrides.inject_next_frame_event(up)

    run_game_for_cycles(run_cycles)



def get_tile_default_pos(x: int, y: int) -> tuple:
    return (2*x+1)/2*settings.CELL_SIZE+settings.DEFAULT_GIRD_OFFSET[0], (2*y+1)/2*settings.CELL_SIZE+settings.DEFAULT_GIRD_OFFSET[1]
