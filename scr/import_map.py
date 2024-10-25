import pygame, json, os, shutil
import tkinter as tk

from tkinter.messagebox import askyesno, WARNING
from datetime import datetime

from util.util import timer
from util.util_logger import logger
from util.util import RunnableFunc
import util.util as util

import GUI.button as button
import GUI.popup.popup_window as popup_window
import GUI.popup.popup_contents as popup_contents
import GUI.popup.scrollable_frame as scrollable_frame
import GUI.popup.scrollable_frame_piece as scrollable_frame_piece

import settings.data as data
import settings.settings as settings
import ui
import palette
import sidebar
import manager
import constants

pygame.init()


def import_tilemap_from_path(path: str) -> None:
    # Check that path isn't None and it points to a valid folder
    if not path or not os.path.exists(path): return

    # If has explanations.json, will run deprecated data retrieving functions
    has_explanations_json = False

    if not os.path.isfile(path+"\\data.json"):
        if os.path.isfile(path+"\\explanations.json"):
            has_explanations_json = True
            logger.debug(f"Old tilemap export system detected. Using the old map import function")
        else:
            logger.error("Invalid tilemap. Doesn't have data.json or deprecated explanations.json file")
            return
    

    logger.log(f"Importing tilemap '{os.path.split(path)[1]}'")

    # Load the grid size 
    if has_explanations_json:
        grid_size   = get_data_gridsize_deprecated(path)
        tile_ids_lst = get_data_tileids_deprecated(path)
        update_last_loaded(path+"\\explanations.json")
    else:
        grid_size   = get_data_gridsize(path)
        tile_ids_lst = get_data_tileids(path)
        update_last_loaded(path+"\\data.json")


    ui.ui_obj.set_gridsize(grid_size)
    
    palette.pm_obj.import_map_palette_change(path)   
    
    update_tiles(tile_ids_lst)

    manager.m_obj.loaded_tilemap = path


def delete_tilemap(tilemap_path: str) -> None:
    if not os.path.isdir(settings.DELETED_TILEMAPS_PATH):
        os.mkdir(settings.DELETED_TILEMAPS_PATH)

    shutil.move(tilemap_path, settings.DELETED_TILEMAPS_PATH)
    # TODO: Check if this tilemap was loaded and deload it if it was
    logger.log(f"Tilemap deleted at '{tilemap_path}'. Moved tilemap to '{settings.DELETED_TILEMAPS_PATH}\\'")


def import_empty_map() -> None:
    manager.m_obj.loaded_tilemap = None
    ui.ui_obj.set_gridsize(settings.DEFAULT_GRID_SIZE)
    
    logger.log("Opened empty tilemap")


@timer
def update_tiles(tile_ids):
    total = -1
    for i in range(ui.ui_obj.grid_size_rows_cols[1]):
        for j in range(ui.ui_obj.grid_size_rows_cols[0]):
            total += 1
            if i >= len(tile_ids) or j >= len(tile_ids[0]):
                continue
            ui.ui_obj.blocks[total].tile_id = tile_ids[i][j]
            ui.ui_obj.blocks[total].update_surf(sidebar.s_obj.buttons_dict["GridButton"].is_clicked())


def update_last_loaded(json_path: str) -> None:
    json_data = None
    with open(json_path, "r") as f:
        json_data = json.load(f)

    json_data["last_loaded"] = datetime.now().strftime(settings.EXPORT_TIME_FORMAT)

    with open(json_path, "w") as f:
        json.dump(json_data, f)


# NEW DATA RETREAVAL --------------
def get_data_gridsize(tilemap_root_path) -> list:
    """Method for getting grid_size. Returns a list with 2 items"""
    with open(tilemap_root_path+"\\data.json", "r") as f:
        json_obj = json.load(f)
        return json_obj["grid_size"]

def get_data_tileids(tilemap_root_path) -> list:
    """Method for getting tile_ids. Returns 2D list of ids"""
    with open(tilemap_root_path+"\\data.json", "r") as f:
        json_obj = json.load(f)
        return json_obj["tile_ids"]
    

# DEPRICATED DATA RETREAVAL ------------
def get_data_gridsize_deprecated(tilemap_root_path) -> list:
    """Depricated method of getting grid_size. Returns a list with 2 items"""
    with open(tilemap_root_path+"\\explanations.json", "r") as f:
        json_obj = json.load(f)
        return json_obj["grid_size"]

def get_data_tileids_deprecated(tilemap_root_path) -> list:
    """Depricated method of getting tile_ids. Returns 2D list of ids"""
    output = []

    with open(tilemap_root_path+"\\tile_ids.txt", "r") as f:
        line_count = len(f.readlines())

    # Open twice because f.readlines() goes to the end of the file, so if ran twice the second one will not give any output
    with open(tilemap_root_path+"\\tile_ids.txt", "r") as f:
        for _ in range(line_count):
            sublist = f.readline().replace(" ", "").split(",")
            sublist_int = []

            for x in sublist:
                sublist_int.append(int(x))
            
            output.append(sublist_int)

    return output



def get_data_data_or_explanations(tilemap_path: str) -> dict:
    if os.path.isfile(tilemap_path + "\\data.json"):
        with open(tilemap_path + "\\data.json", "r") as f:
            return json.load(f)
    elif os.path.isfile(tilemap_path + "\\explanations.json"):
        with open(tilemap_path + "\\explanations.json", "r") as f:
            return json.load(f)
    else:
        logger.warning(f"Retrieving tilemap data: Trying to get tilemap data, but no \\data.json or \\explanations.json was found")
    
    return {}




class Importer():
    SELECTION_W = 500
    SELECTION_H = 160

    BTN_UNSELECTED_COLOR = "gray75"
    BTN_SELECTED_COLOR = "gray80"
    FRAME_BG = "gray60"
    FRAME_BG_2 = "gray70"
    
    def __init__(self, screen: "pygame.Surface") -> None:
        self.popup = None
        self.scrollable = None
        self.confirm_popup = None
        self.screen = screen

        logger.debug("Initialized importer")

    def import_tilemap(self) -> None:
        logger.debug("Opening tilemap import popup")
        popup_size = (600, 510)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 50)

        self.popup = popup_window.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)
        self.scrollable = scrollable_frame.ScrollableFrame(self.popup.surface, popup_pos, (50, 50), (500,440))
        

        self.popup.add_contents_draw_func( RunnableFunc(self.scrollable.update) )
        self.popup.add_contents_onmousebuttondown_func( RunnableFunc(self.scrollable.on_mousebuttondown) )
        self.popup.add_destroy_func( RunnableFunc(self.scrollable.deactivate) )

        popup_window.popup_m_obj.track_popup(self.popup)

        paths = self.__get_folders_to_selection()
        for _p in paths:
            self.create_frame(_p)

        logger.debug("Tilemap import popup initialized successfully")



    def create_frame(self, path) -> None:
        frame = scrollable_frame_piece.FramePiece(self.scrollable, (10,10), (480, 50))

        mapname = os.path.basename(path)
        name_text = data.font_25.render(mapname, True, (0,0,0))

        frame.add_surface(name_text, (0, 0), anchor=constants.CENTER)

        load_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Load", 25)
        trash_button = button.ImageButton(frame.frame_base, (0,0), (35,35), "Assets\\trash.png")
        
        frame.add_button(load_button, (-0.38, 0), RunnableFunc(self.on_load_click, args=[path]), anchor=constants.CENTER)
        frame.add_button(trash_button, (0.4, 0), RunnableFunc(self.confirm_delete_frame, args=[frame, path]), anchor=constants.CENTER)

        self.scrollable.add_frame(frame)


    def confirm_delete_frame(self, frame_to_delete: "scrollable_frame_piece.FramePiece", map_path: str) -> None:
        print("Confirm")
        logger.debug(f"Opening tilemap delete confirmation popup to delete tilemap at '{map_path}'")
        popup_size = (400, 340)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 
                     settings.SCR_H//2 - popup_size[1]//2)

        self.confirm_popup = popup_window.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)

        frame = popup_contents.PopupContents(self.confirm_popup, (10,10), (popup_size[0] - 20, popup_size[1] - 60))

        mapname = os.path.basename(map_path)
        confirm_text_1 = util.pygame_different_color_text(data.font_25, ["Are you sure you want to ", "DELETE"], [(0,0,0), (200,00,00)])
        confirm_text_2 = data.font_25.render(f"'{mapname}'?", True, (0,0,0))
        confirm_text_3 = data.font_25.render(f"The tilemap can be recovered from", True, (0,0,0))
        confirm_text_4 = data.font_25.render(f"'{settings.DELETED_TILEMAPS_PATH}'.", True, (0,0,0))

        yes_button =    button.TextButton(frame.frame_base, (0,0), (100, 35), "DELETE", 25, hover_col=(200,0,0))
        cancel_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Cancel", 25)

        frame.add_surface(confirm_text_1, (0.0,0.2), anchor=constants.UP)
        frame.add_surface(confirm_text_2, (0.0,0.3), anchor=constants.UP)

        frame.add_surface(confirm_text_3, (0.0,0.5), anchor=constants.UP)
        frame.add_surface(confirm_text_4, (0.0,0.6), anchor=constants.UP)

        frame.add_button(yes_button,    (-0.17, -0.05), RunnableFunc(self.delete_tilemap_confirmed, args=[frame_to_delete, map_path]), anchor=constants.BOTTOM)
        frame.add_button(cancel_button, ( 0.17, -0.05), RunnableFunc(self.confirm_popup.close_popup), anchor=constants.BOTTOM)

        self.confirm_popup.add_contents_draw_func( RunnableFunc(frame.update) )
        self.confirm_popup.add_contents_onmousebuttondown_func( RunnableFunc(frame.on_mousebuttondown) )
        popup_window.popup_m_obj.track_popup(self.confirm_popup)

        logger.debug("Tilemap delete confirmation popup initialized successfully")


    def delete_tilemap_confirmed(self, frame_to_delete: "scrollable_frame_piece.FramePiece", map_path: str) -> None:
        logger.debug(f"Confirmed tilemap deletion. Deleting tilemap at '{map_path}'...")
        self.scrollable.delete_frame(frame_to_delete)
        delete_tilemap(map_path)

        self.confirm_popup.close_popup()


    def on_load_click(self, path_to_tilemap: str) -> None:
        import_tilemap_from_path(path_to_tilemap)
        popup_window.popup_m_obj.close_popup(self.popup)
        self.scrollable.disable_clicking()


    def __get_folders_to_selection(self) -> list:
        # Get all directories in Tilemap export folder
        dirs = os.listdir(settings.TILEMAPS_EXPORT)
        
        # Add tilemaps export folder to the path to make it relative to cwd
        dirs = [settings.TILEMAPS_EXPORT + "\\" + _dir for _dir in dirs]

        # Remove any folders that are not tilemap exports
        dirs_clean = [_dir for _dir in dirs if (os.path.isfile(_dir + "\\data.json") or 
                                                os.path.isfile(_dir + "\\explanations.json"))]
        
        if dirs != dirs_clean:
            # Find the directories that are not tilemaps and put them into bad_paths
            bad_paths = []
            for _d in dirs:
                if _d not in dirs_clean:
                    bad_paths.append(_d)

            logger.warning(f"One or more of folder under {settings.TILEMAPS_EXPORT}\\ is not a tilemap. Invalid tilemaps ({len(bad_paths)}) are {bad_paths}")

        dirs = dirs_clean

        # If no tilemaps exist
        if dirs == []:
            return []

        sorted_dirs = []
        dirs_no_time = []

        # Sort by time saved
        for _dir in dirs:
            # Load each tilemap's data
            data = get_data_data_or_explanations(_dir)

            # if not saved_time in data
            if not "last_loaded" in data.keys():
                dirs_no_time.append( (_dir, -1) )
                continue

            last_loaded_time = data["last_loaded"]
            diff = datetime.now() - datetime.strptime(last_loaded_time, settings.EXPORT_TIME_FORMAT)
            loaded_minutes_ago = diff.total_seconds() / 60
            
            sorted_dirs.append( (_dir, loaded_minutes_ago) )


        # sort by the difference to current time: Most recently exported will be on top
        sorted_dirs.sort(key=lambda x: x[1])

        # Append the ones that didn't have last_loaded to the back
        for d in dirs_no_time:
            sorted_dirs.append(d)

        output = [_dir for _dir, _ in sorted_dirs]

        return output
        

i_obj: Importer = None
def create_importer(screen) -> None:
    global i_obj
    i_obj = Importer(screen)