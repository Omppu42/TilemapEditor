import pygame

import time, os, math
from functools import wraps
import traceback

from util.util_logger import logger

from settings import settings


def timer(text="default", log_function=logger.debug):
    """Custon text can be set as 'Time took: %.2f' to insert the time while rounding to 2 digits"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            rv = func(*args, **kwargs)

            caller_path = os.path.abspath(func.__globals__["__file__"])
            caller_path = os.path.relpath(caller_path, os.getcwd()) #get path relative to cwd
            
            total_time = round(time.time() - start_time, 4)
            if text == "default":
                log_function(f"Running function '{func.__name__}' at '{caller_path}' in {total_time} seconds")
            else:
                log_function(text % total_time)
            return rv
        
        return wrapper
    return decorator


def get_cell_pos_from_mousepos(pos: tuple, total_mouse_movement: tuple) -> tuple:
    """Returns tuple of x and y block coordinates"""
    cell = ((pos[0] - total_mouse_movement[0]) // settings.CELL_SIZE, 
            (pos[1] - total_mouse_movement[1]) // settings.CELL_SIZE)

    return cell

def get_clicked_block(pos: tuple, total_mouse_movement: tuple, blocks_list: list) -> tuple:
    """Returns a block which was clicked on"""
    cell = ((pos[0] - total_mouse_movement[0]) // settings.CELL_SIZE, 
            (pos[1] - total_mouse_movement[1]) // settings.CELL_SIZE)

    block = next((x for x in blocks_list if x.pos_on_grid == cell), None)
    return block


def get_tile_page_from_index(index: int) -> int:
    """Get the page that the tile index is on"""
    return math.floor(index / settings.TILES_PER_PAGE)


def get_tile_index_on_page(index: int) -> int:
    """Get the index of the tile on it's page"""
    return index % settings.TILES_PER_PAGE

def get_tile_column_from_index(index: int) -> int:
    """From 0 to TILES_PER_ROW-1"""
    return index % settings.TILES_PER_ROW

def get_tile_row_from_index(index: int) -> int:
    """From 0 to TILES_PER_COL-1"""
    return math.floor((index % settings.TILES_PER_PAGE) / settings.TILES_PER_ROW)


def pygame_different_color_text(font: "pygame.font.Font", texts: "list[str]", colors: "list[tuple]") -> "pygame.Surface":
    """Adds different color texts together. Each list index of texts list corresponds with list index colors list."""
    _size = font.size("".join(texts))
    surf = pygame.Surface(_size).convert_alpha()
    surf.fill((255,255,255, 0))

    filled_to_x = 0

    for _text, _col in zip(texts, colors):
        _render = font.render(_text, True, _col)
        surf.blit(_render, (filled_to_x, 0))

        filled_to_x += _render.get_rect().w

    return surf


class RunnableFunc():
    def __init__(self, function: "function", args:list=[], kwargs:dict={}):
        self.function = function
        self.args = args
        self.kwargs = kwargs

        self.traceback = traceback.extract_stack()[-2]

    def run_function(self, start_args_override:list=None) -> None:
        args = start_args_override + self.args if start_args_override != None else self.args

        try:
            return self.function(*args, **self.kwargs)
        except Exception as e:
            logger.fatal(f"Error in running RunnableFunction created in {os.path.basename(self.traceback[0])} line {self.traceback[1]}: {repr(e)}")