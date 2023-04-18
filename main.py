import pygame, sys, atexit, json
from util_logger import logger
from ui import UI
from dropdown import create_lists
from tkinter_opener import tkinter_opener_instance
pygame.init()

def on_exit(ui):
    palette_manager = ui.manager.palette_manager
    json_obj = {"palette" : palette_manager.current_palette.path,
                "GridSize" : ui.cells_r_c}

    for palette in palette_manager.palettes:
        json_obj[palette.path+"_added_tiles"] = palette.added_tiles

    with open("last_session_data.json", "w") as f:
        f.write(json.dumps(json_obj, indent=4))
    
    logger.log("Exited")


def main():
    logger.log("Starting...")
    SCR_W = 1200
    SCR_H = 600
    CELL_SIZE = 32

    screen = pygame.display.set_mode((SCR_W,SCR_H))
    pygame.display.set_caption("Tilemap Editor")
    clock = pygame.time.Clock()

    ui = UI((SCR_W, SCR_H), screen, CELL_SIZE)
    bg_color = 100

    lists = create_lists(ui)
    ui.dropdown_lists = lists

    atexit.register(on_exit, ui)
    logger.log("Finished initializing")

    while True:
        screen.fill((bg_color, bg_color, bg_color))
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                ui.manager.handle_tool_hotkeys(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mouse.get_rel()  #reset rel pos

                if pygame.mouse.get_pressed()[0]:
                    ui.on_mouse_click()
            
            if pygame.mouse.get_pressed()[0]:
                ui.manager.mouse_update(pygame.mouse.get_pos())
                
        tkinter_opener_instance.update()
        ui.update()

        for x in lists:  #update dropdown lists
            x.draw(screen)
            selected_option = x.update(event_list)

            if selected_option >= 0:
                selected = x.functions[selected_option]

                if not isinstance(selected, tuple): # no tuple = no args
                    selected()
                    continue
                
                # has args
                selected[0](*selected[1])


        pygame.display.update()
        clock.tick(60)
    

if __name__ == "__main__":
    main()