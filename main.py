import pygame
pygame.init()

from tkinter_opener import tk_util
from util_logger import logger

from window import Window

import ui




# TODO: Export GUI with asking to name the tilemap. There could also be the slection of all current tilemaps to overwrite if needed
#       Add also "Save as" and "Save" to update the tilemap that you've been working on, alternatively creating a new tilemap folder
#       Add a "tilemap: {name}" indicating which tilemap is active right now.
#       Figure out how to do ctrl+s to save

# TODO: Add delete-icon to tkinter loader. Maybe load-icon too?

# TODO: Zooming
# TODO: Move Buttons to data.py 
# TODO: Automated testing
# TODO: Support screen resizes
# TODO: Layers
# TODO: Rearrange tiles selection by dragging 

# TODO: Autosave
# TODO: Give the tilemap a name when exporting to name the folder

# TODO: In grid resize tell the current grid size

# FIXME: Make sure when loading a tilemap that the order of the tilemaps has not changed

def main():
    # DISPLAY
    window = Window()

    while True:
        window.early_update()

        window.manage_events()
                
        tk_util.update() # TODO: Remove this after got rid of all TK functionality
        ui.ui_obj.update()

        window.draw_dropdowns()
        window.draw_popups()

        window.update_screen()

    

if __name__ == "__main__":
    main()