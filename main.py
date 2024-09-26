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

def on_exit(palette_manager_obj):
    json_obj = {"palette" : palette_manager_obj.current_palette.path,
                "GridSize" : ui.ui_obj.cells_r_c}

    for palette in palette_manager_obj.all_palettes:
        json_obj[palette.path+"_added_tiles"] = palette.added_tiles

    with open("last_session_data.json", "w") as f:
        f.write(json.dumps(json_obj, indent=4))
    
    logger.log("Exited")


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

    data.init_data()

    atexit.register(on_exit, palette.pm_obj)
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