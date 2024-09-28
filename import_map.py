import pygame, tkinter, json, os
from tkinter.messagebox import askyesno, WARNING

from util import timer
from util_logger import logger

import ui
import palette
import sidebar
import manager

pygame.init()


def import_tilemap():
    dest_folder = manager.m_obj.ask_filedialog(initialdir="Tilemaps", title="Select a tilemap folder to load")
    if dest_folder == "": return #pressed cancel when selecting 

    # If has explanations.json, will run depricated data retrieving functions
    has_explanations_json = False

    if not os.path.isfile(dest_folder+"\\data.json"):
        if os.path.isfile(dest_folder+"\\explanations.json"):
            has_explanations_json = True
            logger.debug(f"Old tilemap export system detected. Using the old map import function.")
        else:
            logger.error("Invalid tilemap. Doesn't have data.json (depricated explanations.json) file.")
            import_tilemap()
            return

    logger.log(f"Importing tilemap '{os.path.split(dest_folder)[1]}'")

    # Load the grid size 
    if has_explanations_json:
        grid_size   = get_data_gridsize_depricated(dest_folder)
        tile_ids_lst = get_data_tileids_depricated(dest_folder)
    else:
        grid_size   = get_data_gridsize(dest_folder)
        tile_ids_lst = get_data_tileids(dest_folder)


    msg = "Your grid is bigger than the tilemap.\nDo you want to scale your grid to fit the tilemap?"
    if ui.ui_obj.cells_r_c[0] < grid_size[0] or ui.ui_obj.cells_r_c[1] < grid_size[1]:
        msg = "Selected tilemap doesn't fit current grid size.\nDo you want to change it to fit?"

    if not ui.ui_obj.cells_r_c == grid_size:
        root = tkinter.Tk()
        root.withdraw()
        if askyesno("Change Grid Size", msg, icon=WARNING):
            ui.ui_obj.set_gridsize(grid_size)
        root.destroy()
    
    palette.pm_obj.import_map_palette_change(dest_folder)   
    
    update_tiles(tile_ids_lst)


@timer
def update_tiles(tile_ids):
    total = -1
    for i in range(ui.ui_obj.cells_r_c[1]):
        for j in range(ui.ui_obj.cells_r_c[0]):
            total += 1
            if i >= len(tile_ids) or j >= len(tile_ids[0]):
                continue
            ui.ui_obj.blocks[total].tile_id = tile_ids[i][j]
            ui.ui_obj.blocks[total].update_surf(sidebar.s_obj.buttons_dict["GridButton"].is_clicked())


# NEW DATA RETREAVAL --------------
def get_data_gridsize(tilemap_root_path) -> list:
    """Method for getting grid_size. Returns a list with 2 items"""
    with open(tilemap_root_path+"\\data.json", "r") as f:
        data = f.readlines()
        json_obj = json.loads("".join(data))
        return json_obj["grid_size"]

def get_data_tileids(tilemap_root_path) -> list:
    """Method for getting tile_ids. Returns 2D list of ids"""
    with open(tilemap_root_path+"\\data.json", "r") as f:
        data = f.readlines()
        json_obj = json.loads("".join(data))
        return json_obj["tile_ids"]
    

# DEPRICATED DATA RETREAVAL ------------
def get_data_gridsize_depricated(tilemap_root_path) -> list:
    """Depricated method of getting grid_size. Returns a list with 2 items"""
    with open(tilemap_root_path+"\\explanations.json", "r") as f:
        data = f.readlines()
        json_obj = json.loads("".join(data))
        return json_obj["grid_size"]

def get_data_tileids_depricated(tilemap_root_path) -> list:
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

