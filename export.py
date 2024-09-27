import pygame, tkinter, os, shutil, glob, json
from datetime import datetime
from tkinter import filedialog
from util import timer

import ui
import palette
import manager

pygame.init()

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

    with open(dest_folder + "\\explanations.json", "w") as f:
        json_object = json.dumps(create_explanations_dict(), indent=4) #write json object to explanations.json
        f.write(json_object)

    with open(dest_folder + "\\tile_ids.txt", "w") as f:
        for i in create_tiles_list():
            out = str(i).replace("[", "")
            out = out.replace("]", "")
            f.write(out + "\n")


def create_tiles_folder(dest_folder: str):
    TILE_FOLDER = dest_folder + "\\Tiles"
    PALETTE_PATH = palette.pm_obj.current_palette.path


    if not os.path.isdir(TILE_FOLDER): #create tiles folder
        os.mkdir(TILE_FOLDER)
    
    for png in glob.glob(PALETTE_PATH+"\\*.png"): #copy tiles to tiles folder
        shutil.copy(png, TILE_FOLDER)


def create_explanations_dict() -> dict:
    PALETTE_PATH = palette.pm_obj.current_palette.path
    output = {}

    png_images = [x for x in os.listdir(PALETTE_PATH) if x.endswith(".png")]

    for i, path in enumerate(png_images):
        output[i] = path

    output["grid_size"] = ui.ui_obj.cells_r_c
    return output


def create_tiles_list() -> list:
    output = []

    #get id's of each block
    total = 0
    for _ in range(ui.ui_obj.cells_r_c[1]):
        sublist = []
        for _ in range(ui.ui_obj.cells_r_c[0]):
            sublist.append(ui.ui_obj.blocks[total].tile_id)
            total += 1

        output.append(sublist)

    return output