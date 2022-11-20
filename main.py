import pygame, sys, atexit, json
from util_logger import logger
from ui import UI
from dropdown import create_lists
pygame.init()


def on_exit(ui):
    json_obj = {"palette" : ui.manager.palette_manager.current_palette.path,
                "GridSize" : ui.cells_r_c}

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
                

        ui.update()

        for x in lists:  #update dropdown lists
            x.draw(screen)
            selected_option = x.update(event_list)
            if selected_option >= 0:
                if not isinstance(x.functions[selected_option], tuple):
                    x.functions[selected_option]()
                    continue

                x.functions[selected_option][0](*x.functions[selected_option][1])
        pygame.display.update()
        clock.tick(200)
    

if __name__ == "__main__":
    main()