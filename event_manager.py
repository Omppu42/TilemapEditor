import pygame, sys, json, time

from util_logger import logger

import ui
import manager
import data
import sidebar

ARROW_KEYS = [pygame.K_LEFT, 
              pygame.K_RIGHT, 
              pygame.K_UP, 
              pygame.K_DOWN]

def on_exit(palette_manager_obj):
    palette_manager_obj.export_all_palette_tile_orders()

    json_obj = {"palette" : palette_manager_obj.current_palette.path,
                "grid_size" : ui.ui_obj.cells_r_c}

    with open("last_session_data.json", "w") as f:
        f.write(json.dumps(json_obj, indent=4))
    
    logger.log("Exited")



def manage_events(event_list) -> None:
    for event in event_list:
        if event.type == pygame.QUIT:
            sys.exit()

        # KEYDOWN -------------
        if event.type == pygame.KEYDOWN:
            match (event.key):
                case pygame.K_p:
                    manager.m_obj.equip_brush()
                case pygame.K_e:
                    manager.m_obj.equip_eraser()
                case pygame.K_o:
                    manager.m_obj.equip_color_picker()
                case pygame.K_g:
                    manager.m_obj.toggle_grid()

                # If any of the arrow keys were pressed
                case _key if _key in ARROW_KEYS:
                    sidebar.s_obj.arrowkeys_tile_selection_move(event)
            
        
        # ANY MOUSE BUTTON -----------
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.mouse.get_rel()  #reset rel pos

            # CLICK LEFT CLICK ----------
            if pygame.mouse.get_pressed()[0]:
                sidebar.s_obj.on_left_mouse_click()
        
        # HOLD LEFT CLICK ---------
        if pygame.mouse.get_pressed()[0]: 
            manager.m_obj.mouse_update(pygame.mouse.get_pos())


def update_dropdowns(screen, event_list) -> None:
    for x in data.dropdowns:  #update dropdown dropdowns
        x.draw(screen)
        selected_option = x.update(event_list)

        if selected_option >= 0:
            # convert the values of a dict to list so we can access the nth value
            selected = list(x.options.values())[selected_option]  

            if not isinstance(selected, tuple): # no tuple = no args
                selected()
                continue
            
            # has args
            selected[0](*selected[1])