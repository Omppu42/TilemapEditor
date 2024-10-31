import pygame
pygame.init()

from util.tkinter_opener import tk_util

from window import Window

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

def main():
    # DISPLAY
    window = Window()

    while True:
        window.early_update()

        window.manage_events()
                
        tk_util.update()
        ui.ui_obj.update()

        window.draw()
        window.update_screen()



if __name__ == "__main__":
    main()