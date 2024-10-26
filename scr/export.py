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

        self.popup.add_contents_class(contents_canvas)
        self.popup.add_contents_class(self.scrollable)

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
        

exporter: Exporter = None
def create_exporter(screen) -> None:
    global exporter
    exporter = Exporter(screen)