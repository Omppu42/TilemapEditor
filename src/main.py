import pygame, os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

pygame.init()

from window import Window


# TODO: Create popups for loading and exporting palettes
# TODO: Rename Tilemaps and palettes

# TODO: Zooming
# TODO: Layers
# TODO: Automated testing

# TODO: Support screen resizes
# TODO: Rearrange tiles selection by dragging 

# TODO: Autosave

# TODO: Ask to save if closing tilemap without saving first

# TODO: Undoing with a stack

# FIXME: Make sure when loading a tilemap that the order of the tilemaps has not changed


def main():
    # DISPLAY
    window = Window()

    while True:
        main_loop(window)
        

def main_loop(window: Window) -> None:
    window.early_update()

    window.manage_events()
    window.update()

    window.update_screen()


if __name__ == "__main__":
    main()