import pygame, os, shutil, glob, json, time
from datetime import datetime

from settings import data
from settings import settings

from util.util import RunnableFunc
from util.util_logger import logger
from util import file_utils
from util import util

from . import tilemap_util

from GUI import button
from GUI import input_field
from GUI import popup

import ui
import palette
import anchors
import manager

pygame.init()




class Exporter():
    SELECTION_W = 500
    SELECTION_H = 160

    BTN_UNSELECTED_COLOR = "gray75"
    BTN_SELECTED_COLOR = "gray80"
    FRAME_BG = "gray60"
    FRAME_BG_2 = "gray70"
    
    def __init__(self, screen: "pygame.Surface", ie_interface) -> None:
        self.screen = screen
        self.ie_interface = ie_interface
        self.export_tools = ExportTools(self)

        self.popup = None
        self.confirm_popup = None
        self.scrollable = None

        logger.debug("Initialized Exporter")

    def start_export_tilemap(self) -> None:
        logger.debug("Opening tilemap export popup")
        popup_size = (600, 510)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 50)

        self.popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)
        self.scrollable = popup.ScrollableFrame(self.popup.surface, popup_pos, (50, 50), (500,340), frames_gap=4)

        contents_canvas = popup.PopupContents(self.popup, (10, 10), (580, 455), (120,120,120))

        name = input_field.TextInputField((0,0), (320, 40), 30, placeholder="Enter tilemap name", empty_return_val="", bg_color=(180,180,180), border_width=1, font=data.font_30)
        export_btn = button.TextButton(contents_canvas.frame_base, (0,0), (100,40), "Export", 30)

        contents_canvas.add_input_field(name, (0.1, 0.35), anchor=anchors.LEFT)
        contents_canvas.add_button(export_btn, (0.7, 0.35), RunnableFunc(self.export, args=[name.get_value]), anchor=anchors.LEFT)

        self.popup.add_contents_class(contents_canvas)
        self.popup.add_contents_class(self.scrollable)

        self.tilemap_paths = file_utils.get_tilemap_paths_alphabetically()
        if settings.TESTS_TILEMAP_PATH:
            self.tilemap_paths.remove(settings.TESTS_TILEMAP_PATH)

        for _p in self.tilemap_paths:
            self.create_frame(_p)

        logger.debug("Tilemap export popup initialized successfully")
        

    def create_frame(self, path) -> None:
        frame = popup.FramePiece(self.scrollable, (10,10), (480, 30))

        mapname = os.path.basename(path)
        name_text = data.font_25.render(mapname, True, (0,0,0))

        frame.add_surface(name_text, (0.1, 0), anchor=anchors.LEFT)

        self.scrollable.add_frame(frame)


    def confirm_default_export(self, default_map_name: str) -> None:
        popup_size = (400, 300)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 
                     settings.SCR_H//2 - popup_size[1]//2)

        self.confirm_popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)

        frame = popup.PopupContents(self.confirm_popup, (10,10), (popup_size[0] - 20, popup_size[1] - 60))

        confirm_text_1 = data.font_30.render(f"Empty tilemap name detected.", True, (0,0,0))
        confirm_text_2 = data.font_25.render(f"Export as", True, (0,0,0))
        confirm_text_3 = data.font_25.render(f"'{default_map_name}'?", True, (0,0,0))

        yes_button =    button.TextButton(frame.frame_base, (0,0), (100, 35), "Export", 25)
        cancel_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Cancel", 25)

        frame.add_surface(confirm_text_1, (0.0,0.2), anchor=anchors.UP)
        frame.add_surface(confirm_text_2, (0.0,0.4), anchor=anchors.UP)
        frame.add_surface(confirm_text_3, (0.0,0.5), anchor=anchors.UP)

        frame.add_button(yes_button,    (-0.17, -0.05), RunnableFunc(self.confirmed_default_export, args=[default_map_name]), anchor=anchors.BOTTOM)
        frame.add_button(cancel_button, ( 0.17, -0.05), RunnableFunc(self.confirm_popup.close_popup), anchor=anchors.BOTTOM)

        self.confirm_popup.add_contents_class(frame)


    def conflict_popup(self, map_name: str) -> None:
        popup_size = (400, 300)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 
                     settings.SCR_H//2 - popup_size[1]//2)

        self.confirm_popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)

        frame = popup.PopupContents(self.confirm_popup, (10,10), (popup_size[0] - 20, popup_size[1] - 60))

        confirm_text_1 = data.font_25.render(f"Tilemap '{map_name}'", True, (0,0,0))
        confirm_text_2 = data.font_30.render(f"ALREADY EXISTS", True, (200,0,0))
        confirm_text_3 = util.pygame_different_color_text(data.font_30, ["Do you want to ", "OVERRIDE IT?"], [(0,0,0), (200,0,0)])
        confirm_text_4 = data.font_25.render(f"You can recover the old tilemap from", True, (0,0,0))
        confirm_text_5 = data.font_25.render(f"'{settings.DELETED_TILEMAPS_PATH}'", True, (0,0,0))

        yes_button =    button.TextButton(frame.frame_base, (0,0), (100, 35), "OVERRIDE", 25, hover_col=(200,0,0))
        cancel_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Cancel", 25)

        frame.add_surface(confirm_text_1, (0.0,0.05), anchor=anchors.UP)
        frame.add_surface(confirm_text_2, (0.0,0.15), anchor=anchors.UP)
        frame.add_surface(confirm_text_3, (0.0,0.3), anchor=anchors.UP)
        frame.add_surface(confirm_text_4, (0.0,0.5), anchor=anchors.UP)
        frame.add_surface(confirm_text_5, (0.0,0.6), anchor=anchors.UP)

        frame.add_button(yes_button,    (-0.17, -0.05), RunnableFunc(self.confirm_override, args=[map_name]), anchor=anchors.BOTTOM)
        frame.add_button(cancel_button, ( 0.17, -0.05), RunnableFunc(self.confirm_popup.close_popup), anchor=anchors.BOTTOM)

        self.confirm_popup.add_contents_class(frame)


    def export(self, map_name_getter: "function") -> None:
        map_name = map_name_getter()
        
        if map_name.replace(" ", "") == "":
            default_name = "tilemap-"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.confirm_default_export(default_name)
            return
        
        if map_name == manager.m_obj.loaded_tilemap:
            self.export_tools.save_tilemap()
            return
        
        if settings.TILEMAPS_EXPORT + "\\" + map_name in self.tilemap_paths:
            self.conflict_popup(map_name)
            return
        
        self.export_tools.export_tilemap(map_name)
        self.popup.close_popup()
        

    def confirmed_default_export(self, tilemap_name: str) -> None:
        self.confirm_popup.close_popup()
        self.popup.close_popup()

        self.export_tools.export_tilemap(tilemap_name)

    def confirm_override(self, tilemap_name: str) -> None:
        self.confirm_popup.close_popup()
        self.popup.close_popup()

        tilemap_util.delete_tilemap(settings.TILEMAPS_EXPORT + "\\" + tilemap_name, rename_to_path=settings.DELETED_TILEMAPS_PATH + "\\overridden-" + tilemap_name)
        self.export_tools.export_tilemap(tilemap_name)
        
    def save_tilemap(self) -> None:
        map_name = manager.m_obj.loaded_tilemap
        if map_name is None:
            # Map not saved yet
            self.start_export_tilemap()
            return

        tilemap_util.delete_tilemap(map_name, move_to_deleted=False)
        self.export_tools.export_tilemap(os.path.basename(map_name), load_map=False)
        data.saved_last_time = time.time()

    def save_tilemap_quiet(self) -> None:
        """Save without save text and don't ask to save with name"""
        map_name = manager.m_obj.loaded_tilemap
        if map_name is None:
            return

        tilemap_util.delete_tilemap(map_name, move_to_deleted=False)
        self.export_tools.export_tilemap(os.path.basename(map_name), load_map=False)




class ExportTools:
    def __init__(self, exporter):
        self.exporter: "Exporter" = exporter
    
    def export_tilemap(self, tilemap_name: str, load_map=True):
        dest_folder = settings.TILEMAPS_EXPORT + "\\" + tilemap_name
        os.mkdir(dest_folder)

        self.create_tiles_folder(dest_folder)
        data_json = self.create_data_json()
        print(f"Exporting {tilemap_name} data:", data_json)

        with open(dest_folder + "\\data.json", "w") as f:
            json_object = json.dumps(data_json, indent=None) #write json object to explanations.json
            f.write(json_object)

        if load_map:
            self.exporter.ie_interface.import_tilemap_from_path(dest_folder, recenter_camera=False)


    def create_tiles_folder(self, dest_folder: str):
        TILE_FOLDER = dest_folder + "\\Tiles"
        PALETTE_PATH = palette.pm_obj.current_palette.path

        if not os.path.isdir(TILE_FOLDER): #create tiles folder
            os.mkdir(TILE_FOLDER)
        
        for png in glob.glob(PALETTE_PATH+"\\*.png"): #copy tiles to tiles folder
            shutil.copy(png, TILE_FOLDER)

        shutil.copy(PALETTE_PATH+"\\_order.json", TILE_FOLDER)


    def create_data_json(self) -> dict:
        output = {}

        output["grid_size"] = ui.ui_obj.grid_size_rows_cols
        output["tile_ids"] = self.create_tiles_list()

        return output


    def create_tiles_list(self, ) -> list:
        output = []

        #get id's of each block
        total = 0
        for _ in range(ui.ui_obj.grid_size_rows_cols[1]):
            sublist = []
            for _ in range(ui.ui_obj.grid_size_rows_cols[0]):
                sublist.append(ui.ui_obj.blocks[total].tile_id)
                total += 1

            output.append(sublist)

        return output