import atexit
import pygame, sys, json, time

from util.util_logger import logger

import GUI.dropdown as dropdown
import GUI.popup.popup_window as popup_window
import settings.settings as settings

import palette
import ui
import manager
import sidebar
import import_map
import mouse



class Window:
    ARROW_KEYS = [pygame.K_LEFT, 
                pygame.K_RIGHT, 
                pygame.K_UP, 
                pygame.K_DOWN]
    
    def __init__(self):
        logger.log("Starting...")
        self.event_list = None

        self.screen = pygame.display.set_mode((settings.SCR_W, settings.SCR_H))
        pygame.display.set_caption("Tilemap Editor")

        self.clock = pygame.time.Clock()

        # NOT DEPENDENT ON ANYTHING ELSE
        popup_window.create_popup_manager()
        import_map.create_importer(self.screen)

        # ORDER OF CREATION IS IMPORTANT!
        manager.create_manager()
        sidebar.create_sidebar(self.screen)
        palette.create_palette_manager()
        ui.create_ui(self.screen)

        # POST_INIT UPDATES
        sidebar.s_obj.post_init()
        dropdown.init_dropdowns()
        atexit.register(Window.__on_exit, palette.pm_obj)

        logger.log("Initialized successfully")
    

    def __on_exit(palette_manager_obj):
        palette_manager_obj.export_all_palette_tile_orders()

        json_obj = {"palette" : palette_manager_obj.current_palette.path,
                    "grid_size" : ui.ui_obj.cells_r_c}

        with open("Data\\last_session_data.json", "w") as f:
            f.write(json.dumps(json_obj, indent=4))
        
        logger.log("Exited")



    def early_update(self) -> None:
        self.screen.fill((settings.BG_COLOR, settings.BG_COLOR, settings.BG_COLOR))

        self.event_list = pygame.event.get()
        mouse.frame_start_update()

    def update_screen(self) -> None:
        pygame.display.update()
        self.clock.tick(60)


    # PUT IN ORDER, SOME EVENTS PREVENT EVENTS FURTHER DOWN LIKE POPUPS
    def manage_events(self) -> None:
        for event in self.event_list:
            if event.type == pygame.QUIT:
                sys.exit()

        # POPUPS ----------
        if popup_window.popup_m_obj.popups_exist():
            self.manage_popups()

            # If popups are present, remove the button clicked status and mousepos to not allow clicking on other buttons
            mouse.clear_pos_override()
            mouse.clear_pressed_override()


        # DROPDOWNS -----------
        for _dd in dropdown.dropdowns:  #update dropdown dropdowns
            _dd.update(self.event_list)

            if _dd.drawing:
                mouse.clear_pos_override()
                mouse.clear_pressed_override()
            

        # REST ---------
        for event in self.event_list:
            # KEYDOWN -------------
            if event.type == pygame.KEYDOWN:
                self.manage_keydown(event)
                
            
            # ANY MOUSE BUTTON -----------
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mouse.get_rel()  #reset rel pos

                # CLICK LEFT CLICK ----------
                if mouse.get_pressed_override()[0]:
                    sidebar.s_obj.on_left_mouse_click()
            
            # HOLD LEFT CLICK ---------
            if mouse.get_pressed_override()[0]: 
                manager.m_obj.mouse_update()


    def manage_popups(self):
        for event in self.event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                import_map.i_obj.scrollable.on_mouse_buttondown(event)

                if mouse.get_pressed_override()[0]:
                    popup_window.popup_m_obj.on_left_mouse_click()

        popup_window.popup_m_obj.update_popups()


    def manage_keydown(self, event) -> None:
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
            case _key if _key in Window.ARROW_KEYS:
                sidebar.s_obj.arrowkeys_tile_selection_move(event)


    def draw_dropdowns(self) -> None:
        for _dd in dropdown.dropdowns:
            _dd.draw(self.screen)

    def draw_popups(self) -> None:
        popup_window.popup_m_obj.draw_popups()