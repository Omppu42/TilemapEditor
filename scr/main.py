import pygame
pygame.init()

from util.tkinter_opener import tk_util

from window import Window
import input_overrides

import ui


# TODO: Create popups for exporting, loading and exporting palettes


# TODO: Zooming
# TODO: Automated testing
# TODO: Support screen resizes
# TODO: Layers
# TODO: Rearrange tiles selection by dragging 

# TODO: Autosave

# TODO: Ask to save if closing tilemap without saving first

# TODO: Rename tilemaps

# FIXME: Make sure when loading a tilemap that the order of the tilemaps has not changed


running = True
tests_process_cycles = 2
window = None

def main_tests():
    global running, window, tests_process_cycles
    window = Window()

    while running:
        if tests_process_cycles > 0:
            main_loop(window)
            
            if input_overrides.get_mouse_pressed()[0]:
                pygame.draw.circle(window.screen, (255,0,0), input_overrides.get_mouse_pos(), 5)
            pygame.draw.circle(window.screen, (255,255,0), input_overrides.get_mouse_pos(), 3)
            
            window.update_screen()

            tests_process_cycles -= 1


def main():
    global running, window
    # DISPLAY
    window = Window()

    while running:
        main_loop(window)
        

def main_loop(window: Window) -> None:
    window.early_update()

    window.manage_events()
            
    tk_util.update()
    ui.ui_obj.update()

    window.draw()
    window.update_screen()


if __name__ == "__main__":
    main()