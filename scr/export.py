import pygame, os, shutil, glob, json
from datetime import datetime

from util.util import timer
import settings.settings as settings

import ui
import palette
import manager

pygame.init()

# TODO: Export GUI

def export_tilemap():
    dest_folder = manager.m_obj.ask_filedialog(initialdir="Tilemaps")
    if dest_folder == "": return #pressed cancel when selecting folder
    export_map(dest_folder)

@timer
def export_map(dest_folder):
    dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") #make unique folder for output
    dest_folder = dest_folder+"\\"+"tilemap-"+dt_string
    os.mkdir(dest_folder)

    create_tiles_folder(dest_folder)

    with open(dest_folder + "\\data.json", "w") as f:
        json_object = json.dumps(create_data_json(), indent=None) #write json object to explanations.json
        f.write(json_object)



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