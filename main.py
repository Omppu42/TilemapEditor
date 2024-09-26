import pygame, atexit, json

from tkinter_opener import tk_util
from util_logger import logger

import ui
import event_manager
import data
import settings
import sidebar
import palette
import manager

pygame.init()


# TODO: Move between tiles selection using arrow keys
# TODO: Put window initializations somewhere else
# TODO: Zooming
# TODO: Move Buttons to data.py 
# TODO: Automated testing
# TODO: Support screen resizes
# TODO: Layers

def main():
    logger.log("Starting...")

    screen = pygame.display.set_mode((settings.SCR_W, settings.SCR_H))
    pygame.display.set_caption("Tilemap Editor")
    clock = pygame.time.Clock()

    # ORDER OF CREATION IS IMPORTANT!
    manager.create_manager()
    sidebar.create_sidebar(screen)
    palette.create_palette_manager()
    ui.create_ui(screen)

    # POST_INIT UPDATES
    sidebar.s_obj.update_page_arrows()
    data.init_data()
    atexit.register(event_manager.on_exit, palette.pm_obj)

    logger.log("Finished initializing")

    while True:
        screen.fill((settings.BG_COLOR, settings.BG_COLOR, settings.BG_COLOR))
        event_list = pygame.event.get()

        event_manager.manage_events(event_list)
                
        tk_util.update()
        ui.ui_obj.update()

        event_manager.update_dropdowns(screen, event_list)

        pygame.display.update()
        clock.tick(60)
    

if __name__ == "__main__":
    main()