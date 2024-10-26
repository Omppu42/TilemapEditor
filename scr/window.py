import pygame, sys, json, atexit, os

from util.util_logger import logger
from util.util import timer

from GUI import popup
import GUI.dropdown as dropdown
import settings.settings as settings
import settings.data as data

import palette
import ui
import manager
import sidebar
import import_map
import input_overrides
import grid_resize
import export




class Window:
    ARROW_KEYS = [pygame.K_LEFT, 
                pygame.K_RIGHT, 
                pygame.K_UP, 
                pygame.K_DOWN]
    @timer
    def __init__(self):
        logger.log("Starting...")

        self.screen = pygame.display.set_mode((settings.SCR_W, settings.SCR_H))
        pygame.display.set_caption("Tilemap Editor")

        self.clock = pygame.time.Clock()

        # NOT DEPENDENT ON ANYTHING ELSE
        grid_resize.create_grid_resizer(self.screen)
        popup.popup_window.create_popup_manager()
        export.create_exporter(self.screen)
        import_map.create_importer(self.screen)

        # ORDER OF CREATION IS IMPORTANT!
        manager.create_manager()
        sidebar.create_sidebar(self.screen)
        palette.create_palette_manager()
        ui.create_ui(self.screen)

        # POST_INIT UPDATES
        sidebar.s_obj.post_init()
        dropdown.init_dropdowns()
        atexit.register(Window.__on_exit, palette.pm_obj, manager.m_obj)

        # Import map
        import_map.import_tilemap_from_path(manager.m_obj.loaded_tilemap)

        logger.log("Initialized successfully")
    

    def early_update(self) -> None:
        self.screen.fill((settings.BG_COLOR, settings.BG_COLOR, settings.BG_COLOR))

        # Get events
        event_list = pygame.event.get()
        input_overrides.frame_start_update(event_list)


    def update_screen(self) -> None:
        pygame.display.update()
        self.clock.tick(60)


    # PUT IN ORDER, SOME EVENTS PREVENT EVENTS FURTHER DOWN LIKE POPUPS
    def manage_events(self) -> None:
        for event in input_overrides.get_event_list():
            if event.type == pygame.QUIT:
                sys.exit()

        # POPUPS ----------
        if popup.popup_window.popup_m_obj.popups_exist():
            self.manage_popups()
            # RESETS MOUSE CLICKED AND POS


        # DROPDOWNS -----------
        for _dd in dropdown.dropdowns:  #update dropdown dropdowns
            _dd.update()

            if _dd.drawing:
                input_overrides.clear_mouse_pos()
                input_overrides.clear_mouse_pressed()
            

        # REST ---------
        for event in input_overrides.get_event_list():
            # KEYDOWN -------------
            if event.type == pygame.KEYDOWN:
                self.manage_keydown(event)
                
            
            # ANY MOUSE BUTTON -----------
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mouse.get_rel()  #reset rel pos

                # CLICK LEFT CLICK ----------
                if input_overrides.get_mouse_pressed()[0]:
                    sidebar.s_obj.on_left_mouse_click()
            
            # HOLD LEFT CLICK ---------
            if input_overrides.get_mouse_pressed()[0]: 
                manager.m_obj.mouse_update()


    def manage_popups(self):
        for event in input_overrides.get_event_list():
            if event.type == pygame.MOUSEBUTTONDOWN:
                popup.popup_window.popup_m_obj.on_mousebuttondown(event)

            if event.type == pygame.KEYDOWN:
                popup.popup_window.popup_m_obj.on_keydown(event)

                #Clear this event to not allow interacting with other stuff during a popup
                input_overrides.remove_event(event)

        # Mouse buttons and pos is cleared here after top popup has updated
        popup.popup_window.popup_m_obj.update_popups()


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

    # DRAW FUNCS ----------
    def draw_dropdowns(self) -> None:
        for _dd in dropdown.dropdowns:
            _dd.draw(self.screen)

    def draw_popups(self) -> None:
        popup.popup_window.popup_m_obj.draw_popups()

    def draw_info(self) -> None:
        loaded_map = manager.m_obj.loaded_tilemap
        if loaded_map:
            loaded_map = os.path.basename(loaded_map)
        else:
            loaded_map = "Not Saved"

        fps_render = data.font_20.render(f"FPS: {round(self.clock.get_fps(), 0)}", True, (0,0,0))
        fps_rect = fps_render.get_rect(topright=(settings.VIEWPORT_W-10, 10))

        loaded_map_render = data.font_20.render(f"Tilemap: {loaded_map}", True, (0,0,0))
        loaded_map_rect = loaded_map_render.get_rect(topright=(settings.VIEWPORT_W-10, 25))

        grid_size_render = data.font_20.render(f"Grid Size: {ui.ui_obj.grid_size_rows_cols[0]}x{ui.ui_obj.grid_size_rows_cols[1]}", True, (0,0,0))
        grid_size_rect = grid_size_render.get_rect(topright=(settings.VIEWPORT_W-10, 40))

        self.screen.blit(fps_render, fps_rect)
        self.screen.blit(loaded_map_render, loaded_map_rect)
        self.screen.blit(grid_size_render, grid_size_rect)


    def __on_exit(palette_manager_obj, manager_obj):
        palette_manager_obj.export_all_palette_tile_orders()

        json_obj = {"palette" : palette_manager_obj.current_palette.path,
                    "grid_size" : ui.ui_obj.grid_size_rows_cols,
                    "loaded_tilemap" : manager_obj.loaded_tilemap}

        with open(settings.LAST_SESSION_DATA_JSON, "w") as f:
            f.write(json.dumps(json_obj, indent=4))
        
        logger.log("Exited")