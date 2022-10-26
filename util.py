import pygame, time
from block import Block
pygame.init()

def get_cell_from_mousepos(ui, pos: tuple) -> Block:
    cell = ((pos[0] - ui.total_mouse_change[0]) // ui.cell_size, 
            (pos[1] - ui.total_mouse_change[1]) // ui.cell_size)

    block = next((x for x in ui.blocks if x.pos_on_grid == cell), None)
    return block

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        rv = func(*args, **kwargs)
        print(f"Running the function took: {time.time() - start_time} seconds")
        return rv
    
    return wrapper