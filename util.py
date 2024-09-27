import time, os, json, math
from util_logger import logger
from functools import wraps

import settings




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


def load_json_data_dict(path: str) -> dict:
    if not os.path.isfile(path): 
        logger.warning(f"Trying to open file at path {path}, which was not found")
        return {}

    with open(path, "r") as f:
        data_str = "".join(f.readlines())
        if data_str == "": return {}
        
    return json.loads(data_str)


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