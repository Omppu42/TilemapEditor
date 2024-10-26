import pygame, os, shutil, glob
from datetime import datetime

from settings import data
from settings import settings

from util.util import RunnableFunc
from util.util_logger import logger
from util import file_utils
from util import util

import GUI.button as button
from GUI import input_field
from GUI import popup

import ui
import palette
import constants

pygame.init()

# TODO: Export GUI

def export_tilemap():
    # dest_folder = manager.m_obj.ask_filedialog(initialdir="Tilemaps")
    # if dest_folder == "": return #pressed cancel when selecting folder
    exporter.start_export_tilemap()

# @timer
# def export_map(dest_folder):
#     dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") #make unique folder for output
#     dest_folder = dest_folder+"\\"+"tilemap-"+dt_string
#     os.mkdir(dest_folder)

#     create_tiles_folder(dest_folder)

#     with open(dest_folder + "\\data.json", "w") as f:
#         json_object = json.dumps(create_data_json(), indent=None) #write json object to explanations.json
#         f.write(json_object)



def create_tiles_folder(dest_folder: str):
    TILE_FOLDER = dest_folder + "\\Tiles"
    PALETTE_PATH = palette.pm_obj.current_palette.path


    if not os.path.isdir(TILE_FOLDER): #create tiles folder
        os.mkdir(TILE_FOLDER)
    
    for png in glob.glob(PALETTE_PATH+"\\*.png"): #copy tiles to tiles folder
        shutil.copy(png, TILE_FOLDER)

    shutil.copy(PALETTE_PATH+"\\_order.json", TILE_FOLDER)


def create_data_json() -> dict:
    output = {}

    output["last_loaded"] = datetime.now().strftime(settings.EXPORT_TIME_FORMAT)
    output["grid_size"] = ui.ui_obj.grid_size_rows_cols
    output["tile_ids"] = create_tiles_list()

    return output


def create_tiles_list() -> list:
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


class Exporter():
    SELECTION_W = 500
    SELECTION_H = 160

    BTN_UNSELECTED_COLOR = "gray75"
    BTN_SELECTED_COLOR = "gray80"
    FRAME_BG = "gray60"
    FRAME_BG_2 = "gray70"
    
    def __init__(self, screen: "pygame.Surface") -> None:
        self.popup = None
        self.scrollable = None
        self.screen = screen

        logger.debug("Initialized Exporter")

    def start_export_tilemap(self) -> None:
        logger.debug("Opening tilemap export popup")
        popup_size = (600, 510)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 50)

        self.popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)
        self.scrollable = popup.ScrollableFrame(self.popup.surface, popup_pos, (50, 50), (500,340), frames_gap=4)

        contents_canvas = popup.PopupContents(self.popup, (10, 10), (580, 455), (120,120,120))
        name = input_field.TextInputField((0,0), (320, 40), 30, empty="Tilemap name", bg_color=(180,180,180), border_width=1, font=data.font_30)
        # TODO: Add a button to confirm export
        contents_canvas.add_input_field(name, (0, -0.1), anchor=constants.BOTTOM)


        self.popup.add_contents_draw_func( RunnableFunc(contents_canvas.update) )
        self.popup.add_contents_draw_func( RunnableFunc(self.scrollable.update) )

        self.popup.add_contents_onmousebuttondown_func( RunnableFunc(self.scrollable.on_mousebuttondown) )
        self.popup.add_contents_onmousebuttondown_func( RunnableFunc(contents_canvas.on_mousebuttondown) )

        self.popup.add_destroy_func( RunnableFunc(self.scrollable.deactivate) )

        self.popup.add_contents_onkeydown_func( RunnableFunc(contents_canvas.on_keydown) )

        popup.popup_window.popup_m_obj.track_popup(self.popup)

        tilemap_paths = file_utils.get_tilemap_paths_alphabetically()
        for _p in tilemap_paths:
            self.create_frame(_p)


        logger.debug("Tilemap export popup initialized successfully")



    def create_frame(self, path) -> None:
        frame = popup.FramePiece(self.scrollable, (10,10), (480, 30))

        mapname = os.path.basename(path)
        name_text = data.font_25.render(mapname, True, (0,0,0))

        frame.add_surface(name_text, (0.1, 0), anchor=constants.LEFT)

        self.scrollable.add_frame(frame)


    def confirm_delete_frame(self, frame_to_delete: "popup.FramePiece", map_path: str) -> None:
        print("Confirm")
        logger.debug(f"Opening tilemap delete confirmation popup to delete tilemap at '{map_path}'")
        popup_size = (400, 340)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 
                     settings.SCR_H//2 - popup_size[1]//2)

        self.confirm_popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)

        frame = popup.PopupContents(self.confirm_popup, (10,10), (popup_size[0] - 20, popup_size[1] - 60))

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
        popup.popup_window.popup_m_obj.track_popup(self.confirm_popup)

        logger.debug("Tilemap delete confirmation popup initialized successfully")


    def delete_tilemap_confirmed(self, frame_to_delete: "popup.FramePiece", map_path: str) -> None:
        logger.debug(f"Confirmed tilemap deletion. Deleting tilemap at '{map_path}'...")
        self.scrollable.delete_frame(frame_to_delete)
        delete_tilemap(map_path)

        self.confirm_popup.close_popup()


    def on_load_click(self, path_to_tilemap: str) -> None:
        import_tilemap_from_path(path_to_tilemap)
        popup.popup_window.popup_m_obj.close_popup(self.popup)
        self.scrollable.disable_clicking()
        

exporter: Exporter = None
def create_exporter(screen) -> None:
    global exporter
    exporter = Exporter(screen)