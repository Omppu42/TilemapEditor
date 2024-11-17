import os, shutil, json
from itertools import chain

from util.util_logger import logger
from util import file_utils
from settings import settings


def is_valid_tilemap(path: str) -> bool:
    if path is None: return False

    if not os.path.exists(path):
        return False
    
    if not os.path.commonprefix([path, settings.TILEMAPS_EXPORT]) == settings.TILEMAPS_EXPORT:
        return False

    if os.path.isfile(path+"\\data.json"):
        return True
    
    if os.path.isfile(path+"\\explanations.json"):
        return True
    
    logger.error(f"Invalid tilemap ({path}). Doesn't have data.json or deprecated explanations.json file")
    return False
    

def delete_tilemap(tilemap_path: str, rename_to_path:str="", move_to_deleted=True) -> None:
    if not is_valid_tilemap(tilemap_path):
        return
        
    if not os.path.isdir(settings.DELETED_TILEMAPS_PATH):
        os.mkdir(settings.DELETED_TILEMAPS_PATH)

    if not move_to_deleted:
        try:
            shutil.rmtree(tilemap_path)
        except Exception as e:
            logger.error("Error: %s - %s." % (e.filename, e.strerror))
        return
    
    try:
        shutil.move(tilemap_path, settings.DELETED_TILEMAPS_PATH)

        if rename_to_path:
            rename_to_path = file_utils.prevent_existing_file_overlap(rename_to_path)
            deleted_path = settings.DELETED_TILEMAPS_PATH + "\\" + os.path.basename(tilemap_path)
            os.rename(deleted_path, rename_to_path)
            
    except Exception as e:
        logger.error("Error: %s - %s." % (e.filename, e.strerror))
        
    logger.log(f"Tilemap deleted at '{tilemap_path}'. Moved tilemap to '{settings.DELETED_TILEMAPS_PATH}\\'")


# NEW DATA RETREAVAL --------------
def get_data_gridsize(tilemap_root_path) -> list:
    """Method for getting grid_size. Returns a list with 2 items"""
    if os.path.isfile(tilemap_root_path+"\\data.json"):
        with open(tilemap_root_path+"\\data.json", "r") as f:
            json_obj = json.load(f)
            return json_obj["grid_size"]
        
    if os.path.isfile(tilemap_root_path+"\\explanations.json"):
        with open(tilemap_root_path+"\\explanations.json", "r") as f:
            json_obj = json.load(f)
            return json_obj["grid_size"]

def get_data_tileids(tilemap_root_path) -> list:
    """Method for getting tile_ids. Returns 2D list of ids"""
    if os.path.isfile(tilemap_root_path+"\\data.json"):
        with open(tilemap_root_path+"\\data.json", "r") as f:
            json_obj = json.load(f)
            return json_obj["tile_ids"]
        
    if os.path.isfile(tilemap_root_path+"\\explanations.json"):
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



def tilemap_has_changes(path: str, current_tiles_list: list, current_grid_size: tuple, current_tiles_order: list) -> bool:
    """Checks whether the tilemap was edited or not"""
    current_tiles_list = [x.tile_id for x in current_tiles_list]

    if path is None:
        if all(x == -1 for x in current_tiles_list):
            return False
        
        return True
    
    if not is_valid_tilemap(path): 
        return False
    
    grid_size = get_data_gridsize(path)

    if (not current_grid_size[0] == grid_size[0] 
        and not current_grid_size[1] == grid_size[1]):
        return True


    tile_ids = get_data_tileids(path)
    # Reduce the list to 1d list to compare
    tile_ids = list(chain.from_iterable(tile_ids))

    if not tile_ids == current_tiles_list:
        return True

    if not os.path.isfile(path+"\\Tiles\\_order.json"):
        return False
    
    with open(path+"\\Tiles\\_order.json", "r") as f:
        order = json.load(f)

    if not current_tiles_order == order:
        return True
    
    return False