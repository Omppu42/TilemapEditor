import pygame

import time, os, json, math
from functools import wraps
import inspect
import traceback

from util.util_logger import logger

import settings.settings as settings



def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        rv = func(*args, **kwargs)

        caller_path = os.path.abspath(func.__globals__["__file__"])
        caller_path = os.path.relpath(caller_path, os.getcwd()) #get path relative to cwd
        
        total_time = round(time.time() - start_time, 4)
        logger.debug(f"Running function '{func.__name__}' at '{caller_path}' in {total_time} seconds")
        return rv
    
    return wrapper


def load_json_data_dict(path: str) -> dict:
    if not os.path.isfile(path): 
        logger.warning(f"Trying to open file at path {path}, which was not found")
        return {}

    with open(path, "r") as f:        
        return json.load(f)


def prevent_existing_file_overlap(filepath: str) -> str:
    """Returns a path that is valid, fixing conflicts by adding (1) or (2) depending on many conflicts there are"""
    if not os.path.isfile(filepath):
        return filepath

    _filepath, _filename = os.path.split(filepath)
    _file, _extension = os.path.splitext(_filename)

    new_filename = _file + " (%s)" + _extension
    new_filepath = _filepath + "\\" + new_filename
    # _filename (%s).png

    i = 1
    # find a free name
    while os.path.isfile(new_filepath % i):
        i += 1

    return new_filepath % i


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

    def run_function(self, args_override:list=[], kwargs_override:dict={}) -> None:
        args = self.args
        kwargs = self.kwargs

        if args_override:
            args = args_override
        if kwargs_override:
            kwargs = kwargs_override

        try:
            return self.function(*args, **kwargs)
        except Exception as e:
            logger.fatal(f"RunnableFunc trying to run function '{self.function.__name__}' from '{self.function.__module__}' at line {inspect.findsource(self.function)[1]}, but got unexpected arguments ({self.args}) and kwargs ({self.kwargs}). Possibly other errors")
            raise Exception(f"Error in running RunnableFunction created in {os.path.basename(self.traceback[0])} line {self.traceback[1]}: {repr(e)}")