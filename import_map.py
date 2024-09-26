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

    if not os.path.isfile(dest_folder+"\\explanations.json"):
        logger.error("Invalid tilemap. Doesn't have explanations.json file.")
        import_tilemap()
        return

    with open(dest_folder+"\\explanations.json", "r") as f:
        data = f.readlines()
        json_obj = json.loads("".join(data))
        grid_size = json_obj["GridSize"]

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

    tile_ids_lst = []
    with open(dest_folder+"\\tile_ids.txt", "r") as f:
        line_count = len(f.readlines())
    
    with open(dest_folder+"\\tile_ids.txt", "r") as f:
        for i in range(line_count):
            sublist = f.readline().replace(" ", "").split(",")
            sublist_int = []

            for x in sublist:
                sublist_int.append(int(x))
            
            tile_ids_lst.append(sublist_int)
            
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
            ui.ui_obj.blocks[total].update_surf(sidebar.s_obj.buttons["GridButton"].is_clicked())