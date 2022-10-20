import pygame, tkinter, os, shutil, glob, json
from datetime import datetime
from tkinter import filedialog
pygame.init()

def export_tilemap(ui):
    tkinter.Tk().withdraw()
    dest_folder = filedialog.askdirectory()
    if dest_folder == "": return #pressed cancel when selecting folder

    dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") #make unique folder for output
    dest_folder = dest_folder+"\\"+"tilemap-"+dt_string
    os.mkdir(dest_folder)

    create_tiles_folder(dest_folder)

    with open(dest_folder + "\\explanations.json", "w") as f:
        json_object = json.dumps(create_explanations_dict(ui), indent=4) #write json object to explanations.json
        f.write(json_object)

    with open(dest_folder + "\\tile_ids.txt", "w") as f:
        for i in create_tiles_list(ui):
            #print(str(i))
            out = str(i).replace("[", "")
            out = out.replace("]", "")
            f.write(out + "\n")
    

def create_tiles_folder(dest_folder: str):
    tile_folder = dest_folder + "\\Tiles"

    if not os.path.isdir(tile_folder): #create tiles folder
        os.mkdir(tile_folder)

    for png in glob.glob("Assets\\Tiles\\*.png"): #copy tiles to tiles folder
        shutil.copy(png, tile_folder)


def create_explanations_dict(ui) -> dict:
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
            block = next((x for x in ui.blocks if x.pos_on_grid == (j, i)), None)
            if block is None:
                print("couldn't find block at pos: ", (j, i))
                continue

            sublist.append(block.tile_id)
            total += 1

        output.append(sublist)

    return output