import pygame, json, os

from datetime import datetime

from util.util import timer
from util.util_logger import logger
from util.util import RunnableFunc
from util import file_utils
from util import util

from . import tilemap_util

import GUI.button as button
from GUI import popup

import settings.data as data
import settings.settings as settings
import ui
import palette
import sidebar
import manager
import anchors

pygame.init()


class Importer():
    SELECTION_W = 500
    SELECTION_H = 160

    BTN_UNSELECTED_COLOR = "gray75"
    BTN_SELECTED_COLOR = "gray80"
    FRAME_BG = "gray60"
    FRAME_BG_2 = "gray70"
    
    def __init__(self, screen: "pygame.Surface", ie_interface) -> None:
        self.screen = screen
        self.ie_interface = ie_interface
        self.import_tools = ImportTools()
        self.popup = None
        self.scrollable = None
        self.confirm_popup = None

        logger.debug("Initialized Importer")

    def import_tilemap(self) -> None:
        edited = tilemap_util.tilemap_has_changes(manager.m_obj.loaded_tilemap, ui.ui_obj.blocks, ui.ui_obj.grid_size_rows_cols, palette.pm_obj.current_palette.tiles_order)
        if edited:
            self.ask_save_first_popup()
            return

        self.make_import_popup()


    def make_import_popup(self):
        if self.confirm_popup:
            self.confirm_popup.close_popup()

        popup_size = (600, 510)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 50)

        self.popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)
        self.scrollable = popup.ScrollableFrame(self.popup.surface, popup_pos, (50, 50), (500,440))
        
        self.popup.add_contents_class(self.scrollable)


        paths = file_utils.get_tilemap_paths_sort_date()
        for _p in paths:
            self.create_frame(_p)


    def create_frame(self, path) -> None:
        frame = popup.FramePiece(self.scrollable, (10,10), (480, 50))

        mapname = os.path.basename(path)
        name_text = data.font_25.render(mapname, True, (0,0,0))

        frame.add_surface(name_text, (0.05, 0), anchor=anchors.CENTER)

        load_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Load", 25)
        trash_button = button.ImageButton(frame.frame_base, (0,0), (35,35), "Assets\\trash.png")
        
        frame.add_button(load_button, (-0.38, 0), RunnableFunc(self.on_load_click, args=[path]), anchor=anchors.CENTER)
        frame.add_button(trash_button, (0.4, 0), RunnableFunc(self.confirm_delete_frame, args=[frame, path]), anchor=anchors.CENTER)

        self.scrollable.add_frame(frame)


    def confirm_delete_frame(self, frame_to_delete: "popup.FramePiece", map_path: str) -> None:
        logger.debug(f"Opening tilemap delete confirmation popup to delete tilemap at '{map_path}'")
        popup_size = (400, 340)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 
                     settings.SCR_H//2 - popup_size[1]//2)

        self.confirm_popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)

        frame = popup.PopupContents(self.confirm_popup, (10,10), (popup_size[0] - 20, popup_size[1] - 60))

        mapname = os.path.basename(map_path)
        confirm_text_1 = util.pygame_different_color_text(data.font_30, ["Are you sure you want to ", "DELETE"], [(0,0,0), (200,00,00)])
        confirm_text_2 = data.font_30.render(f"'{mapname}'?", True, (0,0,0))
        confirm_text_3 = data.font_25.render(f"The tilemap can be recovered from", True, (0,0,0))
        confirm_text_4 = data.font_25.render(f"'{settings.DELETED_TILEMAPS_PATH}'.", True, (0,0,0))

        yes_button =    button.TextButton(frame.frame_base, (0,0), (100, 35), "DELETE", 25, hover_col=(200,0,0))
        cancel_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Cancel", 25)

        frame.add_surface(confirm_text_1, (0.0,0.2), anchor=anchors.UP)
        frame.add_surface(confirm_text_2, (0.0,0.3), anchor=anchors.UP)

        frame.add_surface(confirm_text_3, (0.0,0.5), anchor=anchors.UP)
        frame.add_surface(confirm_text_4, (0.0,0.6), anchor=anchors.UP)

        frame.add_button(yes_button,    (-0.17, -0.05), RunnableFunc(self.delete_tilemap_confirmed, args=[frame_to_delete, map_path]), anchor=anchors.BOTTOM)
        frame.add_button(cancel_button, ( 0.17, -0.05), RunnableFunc(self.confirm_popup.close_popup), anchor=anchors.BOTTOM)

        self.confirm_popup.add_contents_class(frame)


    def delete_tilemap_confirmed(self, frame_to_delete: "popup.FramePiece", map_path: str) -> None:
        logger.debug(f"Confirmed tilemap deletion. Deleting tilemap at '{map_path}'...")
        self.scrollable.delete_frame(frame_to_delete)
        tilemap_util.delete_tilemap(map_path)
        
        if map_path == manager.m_obj.loaded_tilemap:
            self.import_tools.import_empty_map()

        self.confirm_popup.close_popup()


    def ask_save_first_popup(self) -> None:
        popup_size = (400, 240)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 
                     settings.SCR_H//2 - popup_size[1]//2)

        self.confirm_popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)

        frame = popup.PopupContents(self.confirm_popup, (10,10), (popup_size[0] - 20, popup_size[1] - 60))

        confirm_text_1 = data.font_30.render(f"Unsaved changes.", True, (0,0,0))
        confirm_text_2 = data.font_25.render(f"Save before loading a different tilemap?", True, (0,0,0))

        ignore_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Don't save", 25, hover_col=(200,0,0))
        yes_button =    button.TextButton(frame.frame_base, (0,0), (100, 35), "Save", 25)
        cancel_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Cancel", 25)

        frame.add_surface(confirm_text_1, (0.0,0.25), anchor=anchors.UP)
        frame.add_surface(confirm_text_2, (0.0,0.45), anchor=anchors.UP)

        frame.add_button(yes_button,    (-0.32, -0.05), RunnableFunc(self.save_first_confirmed), anchor=anchors.BOTTOM)
        frame.add_button(ignore_button, (-0.0, -0.05),  RunnableFunc(self.make_import_popup), anchor=anchors.BOTTOM)
        frame.add_button(cancel_button, ( 0.32, -0.05), RunnableFunc(self.confirm_popup.close_popup), anchor=anchors.BOTTOM)

        self.confirm_popup.add_contents_class(frame)
        
        
    def ask_save_first_empty_tilemap(self) -> None:
        """Ask if wanting to save before loading an empty tilemap"""
        popup_size = (400, 240)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 
                     settings.SCR_H//2 - popup_size[1]//2)

        self.confirm_popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)

        frame = popup.PopupContents(self.confirm_popup, (10,10), (popup_size[0] - 20, popup_size[1] - 60))

        confirm_text_1 = data.font_30.render(f"Unsaved changes.", True, (0,0,0))
        confirm_text_2 = data.font_25.render(f"Save before creating an empty tilemap?", True, (0,0,0))

        ignore_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Don't save", 25, hover_col=(200,0,0))
        yes_button =    button.TextButton(frame.frame_base, (0,0), (100, 35), "Save", 25)
        cancel_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Cancel", 25)

        frame.add_surface(confirm_text_1, (0.0,0.25), anchor=anchors.UP)
        frame.add_surface(confirm_text_2, (0.0,0.45), anchor=anchors.UP)

        frame.add_button(yes_button,    (-0.32, -0.05), RunnableFunc(self.save_first_empty_confirmed), anchor=anchors.BOTTOM)
        frame.add_button(ignore_button, (-0.0, -0.05),  RunnableFunc(self.import_empty_nosave_confirmed), anchor=anchors.BOTTOM)
        frame.add_button(cancel_button, ( 0.32, -0.05), RunnableFunc(self.confirm_popup.close_popup), anchor=anchors.BOTTOM)

        self.confirm_popup.add_contents_class(frame)


    def on_load_click(self, path_to_tilemap: str) -> None:
        self.import_tools.import_tilemap_from_path(path_to_tilemap)
        popup.popup_window.popup_m_obj.close_popup(self.popup)
        self.scrollable.disable_clicking()


    def save_first_confirmed(self) -> None:
        if manager.m_obj.loaded_tilemap is None:
            self.ie_interface.export_tilemap()
            self.confirm_popup.close_popup()
            return
        
        self.ie_interface.save_tilemap()

        self.make_import_popup()
        self.confirm_popup.close_popup()


    def save_first_empty_confirmed(self) -> None:
        if manager.m_obj.loaded_tilemap is None:
            self.ie_interface.export_tilemap()
            self.confirm_popup.close_popup()
            return
        
        self.ie_interface.save_tilemap()

        self.import_tools.import_empty_map()
        self.confirm_popup.close_popup()


    def import_empty_nosave_confirmed(self) -> None:
        self.confirm_popup.close_popup()
        self.import_tools.import_empty_map()


class ImportTools:
    def __init__(self):
        pass

    def import_tilemap_from_path(self, path: str, recenter_camera=True) -> None:
        # Check that path isn't None and it points to a valid folder
        if not tilemap_util.is_valid_tilemap(path): return

        logger.log(f"Importing tilemap '{os.path.split(path)[1]}'")

        # Load the data
        grid_size   = tilemap_util.get_data_gridsize(path)
        tile_ids_lst = tilemap_util.get_data_tileids(path)

        self.update_last_loaded(path)

        ui.ui_obj.set_gridsize(grid_size, recenter_camera=recenter_camera)
        
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

        if os.path.isfile(path+"\\data.json"):
            json_path = path+"\\data.json"
        elif os.path.isfile(path+"\\explanations.json"):
            json_path = path+"\\explanations.json"
        else:
            logger.error("This shouldn't happen")
            return

        json_data = None
        with open(json_path, "r") as f:
            json_data = json.load(f)

        json_data["last_loaded"] = datetime.now().strftime(settings.EXPORT_TIME_FORMAT)

        with open(json_path, "w") as f:
            json.dump(json_data, f)


