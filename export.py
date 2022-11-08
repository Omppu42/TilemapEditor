import pygame, tkinter, os, shutil, glob, json
from datetime import datetime
from tkinter import filedialog
from util import timer
pygame.init()

def export_tilemap(ui):
    root = tkinter.Tk()
    root.withdraw()
    dest_folder = filedialog.askdirectory()
    root.destroy()
    if dest_folder == "": return #pressed cancel when selecting folder
    export_map(ui, dest_folder)

@timer
def export_map(ui, dest_folder):
    dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") #make unique folder for output
    dest_folder = dest_folder+"\\"+"tilemap-"+dt_string
    os.mkdir(dest_folder)

    create_tiles_folder(dest_folder)

    with open(dest_folder + "\\explanations.json", "w") as f:
        json_object = json.dumps(create_explanations_dict(), indent=4) #write json object to explanations.json
        f.write(json_object)

    with open(dest_folder + "\\tile_ids.txt", "w") as f:
        for i in create_tiles_list(ui):
            out = str(i).replace("[", "")
            out = out.replace("]", "")
            f.write(out + "\n")


def create_tiles_folder(dest_folder: str):
    tile_folder = dest_folder + "\\Tiles"

    if not os.path.isdir(tile_folder): #create tiles folder
        os.mkdir(tile_folder)

    for png in glob.glob("Assets\\Tiles\\*.png"): #copy tiles to tiles folder
        shutil.copy(png, tile_folder)


def create_explanations_dict() -> dict:
    output = {}
    png_images = [x for x in os.listdir("Assets\\Tiles") if x.endswith(".png")]
    for i, path in enumerate(png_images):
        output[i] = path

    return output


def create_tiles_list(ui) -> list:
    output = []

    #get id's of each block
    total = 0
    for i in range(ui.cells_r_c[1]):
        sublist = []
        for j in range(ui.cells_r_c[0]):
            sublist.append(ui.blocks[total].tile_id)
            total += 1

        output.append(sublist)

    return output