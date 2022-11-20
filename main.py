import pygame, sys, atexit
from util_logger import logger
from ui import UI
from dropdown import create_lists
pygame.init()


def on_exit(ui):
    with open("Data\\palette_to_load.txt", "w") as f:
        f.write(ui.manager.palette_manager.current_palette.path)

    logger.log("Exited")


def main():
    logger.log("Starting...")
    SCR_W = 1200
    SCR_H = 600
    CELL_SIZE = 32

    screen = pygame.display.set_mode((SCR_W,SCR_H))
    pygame.display.set_caption("Tilemap Editor")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)

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

        fps = font.render(str(round(clock.get_fps())), True, (255,0,0))
        screen.blit(fps, (10,10))

        for x in lists:  #update dropdown lists
            x.draw(screen)
            selected_option = x.update(event_list)
            if selected_option >= 0:
                if not isinstance(x.functions[selected_option], tuple):
                    x.functions[selected_option]()
                    continue

                x.functions[selected_option][0](*x.functions[selected_option][1])
        pygame.display.update()
        clock.tick(500)
    

if __name__ == "__main__":
    main()