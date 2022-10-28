import pygame, tkinter
from tkinter import filedialog
from util import timer
pygame.init()

def import_tilemap(ui):
    tkinter.Tk().withdraw()
    dest_folder = filedialog.askdirectory()
    if dest_folder == "": return #pressed cancel when selecting 
    
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
            
    update_tiles(ui, tile_ids_lst)

@timer
def update_tiles(ui, tile_ids):
    total = 0
    for i in range(ui.cells_r_c[0]):
        for j in range(ui.cells_r_c[1]):
            # block = next((x for x in ui.blocks if x.pos_on_grid == (j, i)), None)
            
            # if block is None:
            #     print("couldn't find block at pos: ", (j, i))
            #     continue

            ui.blocks[total].tile_id = tile_ids[j][i]
            ui.blocks[total].update_surf(ui.sidebar.buttons["GridButton"].is_clicked())

            total += 1
                