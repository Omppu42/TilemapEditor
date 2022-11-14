import time, os
from util_logger import logger
from block import Block
from functools import wraps

def get_cell_from_mousepos(ui, pos: tuple) -> Block:
    cell = ((pos[0] - ui.total_mouse_change[0]) // ui.cell_size, 
            (pos[1] - ui.total_mouse_change[1]) // ui.cell_size)

    block = next((x for x in ui.blocks if x.pos_on_grid == cell), None)
    return block


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        rv = func(*args, **kwargs)

        caller_path = os.path.abspath(func.__globals__["__file__"])
        caller_path = os.path.relpath(caller_path, os.getcwd()) #get path relative to cwd
        
        total_time = round(time.time() - start_time, 4)
        logger.log(f"Running function '{func.__name__}' at '{caller_path}' in {total_time} seconds")
        return rv
    
    return wrapper
