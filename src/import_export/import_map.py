import pygame, json, os

from datetime import datetime

from util.util import timer
from util.util_logger import logger
from util.util import RunnableFunc
from util import file_utils
from util import pygame_util

from . import tilemap_util

import GUI.button as button
from GUI import popup

import settings.data as data
import settings.settings as settings
import ui
import palette
import manager
import anchors

pygame.init()


class Importer():    
    def __init__(self, screen: "pygame.Surface", ie_interface) -> None:
        self.screen = screen
        self.ie_interface = ie_interface
        self.import_tools = ImportTools()
        self.popup = None
        self.scrollable = None

        if not os.path.isfile(settings.TILEMAP_LOAD_DATES_JSON):
            with open(settings.TILEMAP_LOAD_DATES_JSON, "w") as f:
                data = {x : 0 for x in file_utils.get_tilemap_paths_alphabetically()}
                json.dump(data, f, indent=4)


        logger.debug("Initialized Importer")

    # PRIVATE --------------------
    def __make_import_popup(self):
        popup_size = (600, 510)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 50)
        scrollable_size = (500,440)

        self.popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)
        self.scrollable = popup.ScrollableFrame(self.popup.surface, popup_pos, (40, 50), scrollable_size)
        
        top_frame = popup.PopupContents(self.popup, (40,-40), (scrollable_size[0], 40), color=(0,0,0,0))
        text = data.font_35.render(f"Load a Tilemap", True, (150,150,150))
        top_frame.add_surface(text, (0.05,0.0), anchor=anchors.CENTER)

        self.popup.add_contents_class(self.scrollable)
        self.popup.add_contents_draw_func(top_frame.update)

        paths = file_utils.get_tilemap_paths_sort_date()
        if settings.TESTS_TILEMAP_PATH:
            paths.remove(settings.TESTS_TILEMAP_PATH)

        for _p in paths:
            self.__create_frame(_p)


    def __create_frame(self, path) -> None:
        frame = popup.FramePiece(self.scrollable, (10,10), (480, 50))

        mapname = os.path.basename(path)
        name_text = data.font_25.render(mapname, True, (0,0,0))

        frame.add_surface(name_text, (0.05, 0), anchor=anchors.CENTER)

        load_button = button.TextButton(frame.frame_base, (0,0), (80, 35), "Load", 25)
        trash_button = button.ImageButton(frame.frame_base, (0,0), (35,35), "Assets\\trash.png")
        
        frame.add_button(load_button, (-0.4, 0), RunnableFunc(self.__on_load_click, args=[path]), anchor=anchors.CENTER)
        frame.add_button(trash_button, (-0.015, 0), RunnableFunc(self.__confirm_delete_frame_popup, args=[frame, path]), anchor=anchors.RIGHT)

        self.scrollable.add_frame(frame)


    def __confirm_delete_frame_popup(self, frame_to_delete: "popup.FramePiece", map_path: str) -> None:
        mapname = os.path.basename(map_path)

        multicolor_surface = pygame_util.render_different_color_text(data.font_30, ["Are you sure you want to ", "DELETE"], [(0,0,0), (200,00,00)])
        text_surface = pygame_util.render_multiline_text(f"'{mapname}'?\n\nThe tilemap can be recovered from\n'{settings.DELETED_TILEMAPS_PATH}'.", data.font_25, 
                                                         linenum_to_font={1 : data.font_30},
                                                         insert_surface_after_line={0 : multicolor_surface})

        popup.create_confirm_cancel_popup(self.screen, text_surface, RunnableFunc(self.__delete_tilemap_confirmed, args=[frame_to_delete, map_path]),
                                          yes_button_text="DELETE",
                                          yes_button_hover_color=(200,0,0))


    def __ask_save_first_popup(self) -> None:
        text = pygame_util.render_multiline_text("Unsaved changes.\n\nSave before loading a different tilemap?", data.font_25, linenum_to_font={1 : data.font_30})

        popup.create_save_dont_save_cancel_popup(self.screen, text, self.__save_first_confirmed, self.__make_import_popup, size=(400, 240))


    def __delete_tilemap_confirmed(self, frame_to_delete: "popup.FramePiece", map_path: str) -> None:
        logger.debug(f"Confirmed tilemap deletion. Deleting tilemap at '{map_path}'...")
        self.scrollable.delete_frame(frame_to_delete)
        tilemap_util.delete_tilemap(map_path)
        
        if map_path == manager.m_obj.loaded_tilemap:
            self.import_tools.import_empty_map()


    def __on_load_click(self, path_to_tilemap: str) -> None:
        self.import_tools.import_tilemap_from_path(path_to_tilemap)
        self.popup.close_popup()
        self.scrollable.disable_clicking()


    def __save_first_confirmed(self) -> None:
        if manager.m_obj.loaded_tilemap is None:
            self.ie_interface.export_tilemap()
            return
        
        self.ie_interface.save_tilemap()

        self.__make_import_popup()


    def __save_first_empty_confirmed(self) -> None:
        if manager.m_obj.loaded_tilemap is None:
            self.ie_interface.export_tilemap()
            return
        
        self.ie_interface.save_tilemap()

        self.import_tools.import_empty_map()


    # PUBLIC -------------------
    def ask_save_first_empty_tilemap(self) -> None:
        """Ask if wanting to save before loading an empty tilemap"""
        text = pygame_util.render_multiline_text("Unsaved changes.\n\nSave before creating an empty tilemap?", data.font_25, linenum_to_font={1 : data.font_30})

        popup.create_save_dont_save_cancel_popup(self.screen, text, self.__save_first_empty_confirmed, self.import_tools.import_empty_map, size=(400, 240))


    def import_tilemap(self) -> None:
        edited = tilemap_util.tilemap_has_changes(manager.m_obj.loaded_tilemap, ui.ui_obj.blocks, ui.ui_obj.grid_size_rows_cols, palette.pm_obj.current_palette.tiles_order)
        if edited:
            self.__ask_save_first_popup()
            return

        self.__make_import_popup()



class ImportTools:
    def __init__(self):
        pass
    
    def import_tilemap_from_path(self, path: str, recenter_camera=True, check_palette_change=True) -> None:
        # Check that path isn't None and it points to a valid folder
        if not tilemap_util.is_valid_tilemap(path): return
        logger.log(f"Importing tilemap '{os.path.split(path)[1]}'")

        # Load the data
        grid_size   = tilemap_util.get_data_gridsize(path)
        tile_ids_lst = tilemap_util.get_data_tileids(path)

        self.update_last_loaded(path)

        ui.ui_obj.set_gridsize(grid_size, recenter_camera=recenter_camera)
        
        if check_palette_change:
            palette.pm_obj.import_map_palette_change(path)   
        
        self.update_tiles(tile_ids_lst)

        manager.m_obj.loaded_tilemap = path


    def import_empty_map(self) -> None:
        manager.m_obj.loaded_tilemap = None
        ui.ui_obj.set_gridsize(settings.DEFAULT_GRID_SIZE)
        
        logger.log("Opened empty tilemap")


    @timer(text="Tile IDs updated in %.2f seconds")
    def update_tiles(self, tile_ids):
        total = -1
        for i in range(ui.ui_obj.grid_size_rows_cols[1]):
            for j in range(ui.ui_obj.grid_size_rows_cols[0]):
                total += 1
                if i >= len(tile_ids) or j >= len(tile_ids[0]):
                    continue
                ui.ui_obj.blocks[total].tile_id = tile_ids[i][j]
                ui.ui_obj.blocks[total].update_surf(manager.m_obj.grid_on)


    def update_last_loaded(self, path: str) -> None:
        if not tilemap_util.is_valid_tilemap(path): return

        old_data = {}
        new_data = {}

        with open(settings.TILEMAP_LOAD_DATES_JSON, "r") as f:
            old_data = json.load(f) 

        if path in old_data:
            old_data.pop(path)

        new_data[path] = datetime.now().strftime(settings.EXPORT_TIME_FORMAT)
        new_data.update(old_data)
        
        with open(settings.TILEMAP_LOAD_DATES_JSON, "w") as f:
            json.dump(new_data, f, indent=4)


