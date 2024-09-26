import pygame, sys, json, time

from util_logger import logger

import ui
import manager
import data
import sidebar

def on_exit(palette_manager_obj):
    json_obj = {"palette" : palette_manager_obj.current_palette.path,
                "GridSize" : ui.ui_obj.cells_r_c}

    for palette in palette_manager_obj.all_palettes:
        json_obj[palette.path+"_added_tiles"] = palette.added_tiles

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

        
        # ANY MOUSE BUTTON -----------
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.mouse.get_rel()  #reset rel pos

            # CLICK LEFT CLICK ----------
            if pygame.mouse.get_pressed()[0]:
                ui.ui_obj.on_mouse_click()
                sidebar.s_obj.on_mouse_click()
        
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