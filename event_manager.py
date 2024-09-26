import pygame, sys
import ui
import manager
import data

def manage_events(event_list) -> None:
    
    for event in event_list:
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:
            manager.m_obj.handle_tool_hotkeys(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.mouse.get_rel()  #reset rel pos

            if pygame.mouse.get_pressed()[0]:
                ui.ui_obj.on_mouse_click()
        
        if pygame.mouse.get_pressed()[0]:
            manager.m_obj.mouse_update(pygame.mouse.get_pos())


def update_dropdowns(screen, event_list) -> None:
    for x in data.dropdowns:  #update dropdown dropdowns
        x.draw(screen)
        selected_option = x.update(event_list)

        if selected_option >= 0:
            selected = x.functions[selected_option]

            if not isinstance(selected, tuple): # no tuple = no args
                selected()
                continue
            
            # has args
            selected[0](*selected[1])