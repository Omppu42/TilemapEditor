import pygame, sys, json, atexit, os, time

from util.util_logger import logger
from util.util import timer
from util import file_utils

from util.tkinter_opener import tk_util

from GUI import popup

from settings import settings
from settings import data

from import_export import ie_interface
from import_export import import_palette

from frametime_graph import FrameTimeGraph

import palette
import ui
import manager
import sidebar
import input_overrides
import grid_resize




class Window:
    ARROW_KEYS = [
        pygame.K_LEFT, 
        pygame.K_RIGHT, 
        pygame.K_UP, 
        pygame.K_DOWN
    ]
    
    @timer(text="Initialization completed in %.2f seconds", log_function=logger.log)
    def __init__(self):
        logger.log("Creating window...")

        self.screen = pygame.display.set_mode((settings.SCR_W, settings.SCR_H))
        pygame.display.set_caption("Tilemap Editor")

        self.clock = pygame.time.Clock()

        self.frametime_graph = FrameTimeGraph(self.screen, (10, settings.SCR_H - 60), 100)

        # NOT DEPENDENT ON ANYTHING ELSE
        grid_resize.create_grid_resizer(self.screen)
        ie_interface.create_Iie(self.screen)
        import_palette.create_palette_loader(self.screen)

        # ORDER OF CREATION IS IMPORTANT!
        sidebar.create_sidebar(self.screen)
        palette.create_palette_manager()
        ui.create_ui(self.screen)

        # POST_INIT UPDATES
        sidebar.s_obj.post_init()
        
        # Import map
        ie_interface.Iie_obj.importer.import_tools.import_tilemap_from_path(manager.m_obj.loaded_tilemap)
        
        atexit.register(Window.__on_exit, palette.pm_obj, manager.m_obj, file_utils.load_json_data_dict(settings.LAST_SESSION_DATA_JSON))
    

    def __manage_keydown(self, event) -> None:
        shift_pressed   = event.mod & pygame.KMOD_SHIFT
        control_pressed = event.mod & pygame.KMOD_CTRL

        if control_pressed:
            match (event.key):
                case pygame.K_s:
                    ie_interface.Iie_obj.save_tilemap()
            return
        
        
        match (event.key):
            case pygame.K_p:
                manager.m_obj.equip_brush()
            case pygame.K_e:
                manager.m_obj.equip_eraser()
            case pygame.K_o:
                manager.m_obj.equip_color_picker()
            case pygame.K_g:
                manager.m_obj.toggle_grid()
            case pygame.K_F3:
                settings.DEBUG_INFO = not settings.DEBUG_INFO
                [block.update_surf(manager.m_obj.grid_on) for block in ui.ui_obj.blocks] # Update blocks

            # If any of the arrow keys were pressed
            case _key if _key in Window.ARROW_KEYS:
                sidebar.s_obj.arrowkeys_tile_selection_move(event)
                

    def early_update(self) -> None:
        self.screen.fill((settings.BG_COLOR, settings.BG_COLOR, settings.BG_COLOR))

        # Get events
        event_list = pygame.event.get()
        input_overrides.frame_start_update(event_list)

    # PUT IN ORDER, SOME EVENTS PREVENT EVENTS FURTHER DOWN LIKE POPUPS
    def manage_events(self) -> None:
        for event in input_overrides.get_event_list():
            if event.type == pygame.QUIT:
                sys.exit()

        # POPUPS ----------
        popup.popup_window.popup_m_obj.handle_events(
            input_overrides.get_event_list()
        )
        # RESETS MOUSE CLICKED AND POS

        # DROPDOWNS -----------
        for _dd in ui.dropdowns:  #update dropdown dropdowns
            _dd.update()

            if _dd.drawing:
                input_overrides.clear_mouse_pos()
                input_overrides.clear_mouse_pressed()
            

        # REST ---------
        for event in input_overrides.get_event_list():
            # KEYDOWN -------------
            if event.type == pygame.KEYDOWN:
                self.__manage_keydown(event)
                
            
            # ANY MOUSE BUTTON -----------
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mouse.get_rel()  #reset rel pos

                # CLICK LEFT CLICK ----------
                if input_overrides.get_mouse_pressed()[0]:
                    sidebar.s_obj.on_left_mouse_click()
            
            # HOLD LEFT CLICK ---------
            if input_overrides.get_mouse_pressed()[0]: 
                manager.m_obj.mouse_update()


    def update(self) -> None:
        tk_util.update()
        ui.ui_obj.update()
        
        # Dropdowns
        for _dd in ui.dropdowns:
            _dd.draw(self.screen)

        # Popups
        popup.popup_window.popup_m_obj.draw_popups()

        # Info
        loaded_map = manager.m_obj.loaded_tilemap
        if loaded_map:
            loaded_map = os.path.basename(loaded_map)
        else:
            loaded_map = "Not Saved"

        # Frametime Graph
        if settings.DEBUG_INFO: 
            self.frametime_graph.draw_graph()
        

        fps_render = data.font_20.render(f"FPS: {round(self.clock.get_fps(), 0)}", True, (0,0,0))
        fps_rect = fps_render.get_rect(topright=(settings.VIEWPORT_W-10, 10))

        loaded_map_render = data.font_20.render(f"Tilemap: {loaded_map}", True, (0,0,0))
        loaded_map_rect = loaded_map_render.get_rect(topright=(settings.VIEWPORT_W-10, 25))

        grid_size_render = data.font_20.render(f"Grid Size: {ui.ui_obj.grid_size_rows_cols[0]}x{ui.ui_obj.grid_size_rows_cols[1]}", True, (0,0,0))
        grid_size_rect = grid_size_render.get_rect(topright=(settings.VIEWPORT_W-10, 40))

        saved_text_render = data.font_25.render(f"Saved", True, (0,0,0))
        saved_text_rect = saved_text_render.get_rect(topright=(settings.VIEWPORT_W-10, settings.SCR_H-20))

        self.screen.blit(fps_render, fps_rect)
        self.screen.blit(loaded_map_render, loaded_map_rect)
        self.screen.blit(grid_size_render, grid_size_rect)

        if time.time() - data.saved_last_time < settings.SAVE_TEXT_TIME_S:
            self.screen.blit(saved_text_render, saved_text_rect)

        self.frametime_graph.add_point(self.clock.get_time())


    def update_screen(self) -> None:
        pygame.display.update()
        self.clock.tick(settings.FPS_CAP)


    def __on_exit(palette_manager_obj, manager_obj, old_data):
        palette_manager_obj.export_all_palette_tile_orders()

        palette = palette_manager_obj.current_palette.path
        tilemap = manager_obj.loaded_tilemap

        if "palette" in old_data and os.path.normpath(palette) == os.path.normpath(settings.TESTS_PALETTE_PATH):
            palette = old_data["palette"]

        if (tilemap != None 
            and "loaded_tilemap" in old_data 
            and os.path.normpath(tilemap) == os.path.normpath(settings.TESTS_TILEMAP_PATH)):

            tilemap = old_data["loaded_tilemap"]


        json_obj = {"palette" : palette,
                    "loaded_tilemap" : tilemap,
                    "grid_size" : ui.ui_obj.grid_size_rows_cols,
                    "grid_draw" : manager_obj.grid_on}

        with open(settings.LAST_SESSION_DATA_JSON, "w") as f:
            f.write(json.dumps(json_obj, indent=4))
        
        logger.log("Exited")