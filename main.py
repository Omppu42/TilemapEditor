import pygame, sys
from ui import UI
import export
pygame.init()

#TODO: in tile selection, make it possible to drag tiles around
#TODO: change mouse to hand when hovering over tile in tile selection and over buttons
#TODO: save tileset and create empty one 
#TODO: in paint mode, preview of where tile will be placed
#TODO: more pages for tiles to prevent overflow

def main():
    SCR_W = 1200
    SCR_H = 600
    CELL_SIZE = 32

    screen = pygame.display.set_mode((SCR_W,SCR_H))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)

    ui = UI((SCR_W, SCR_H), screen, CELL_SIZE)
    bg_color = 100

    while True:
        screen.fill((bg_color, bg_color, bg_color))
        for event in pygame.event.get():
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
        pygame.display.update()
        clock.tick(500)

if __name__ == "__main__":
    main()