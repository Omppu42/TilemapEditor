import os, json
from datetime import datetime

from settings import settings
from util.util_logger import logger


def get_tilemap_paths_alphabetically() -> list:
    """Returns all valid tilemap paths in settings.TILEMAPS_EXPORT sorted alphabetically"""
    # Get all directories in Tilemap export folder
    dirs = os.listdir(settings.TILEMAPS_EXPORT)
    
    # Add tilemaps export folder to the path to make it relative to cwd
    dirs = [settings.TILEMAPS_EXPORT + "\\" + _dir for _dir in dirs]

    # Remove any folders that are not tilemap exports
    dirs.remove(settings.TILEMAP_LOAD_DATES_JSON)
    dirs_clean = [_dir for _dir in dirs if (os.path.isfile(_dir + "\\data.json") or 
                                            os.path.isfile(_dir + "\\explanations.json"))]

    if dirs != dirs_clean:
        # Find the directories that are not tilemaps and put them into bad_paths
        bad_paths = []
        for _d in dirs:
            if _d not in dirs_clean:
                bad_paths.append(_d)

        logger.warning(f"One or more of folder under {settings.TILEMAPS_EXPORT}\\ is not a tilemap. Invalid tilemaps ({len(bad_paths)}) are {bad_paths}")

    return dirs_clean


def get_tilemap_paths_sort_date() -> list:
    """Returns all valid tilemap paths in settings.TILEMAPS_EXPORT sorted by the date opened"""
    dirs = get_tilemap_paths_alphabetically()
    load_dates = {}

    if os.path.isfile(settings.TILEMAP_LOAD_DATES_JSON):
        with open(settings.TILEMAP_LOAD_DATES_JSON, "r") as f:
            load_dates = json.load(f)

    # If no tilemaps exist
    if dirs == []: return []

    sorted_dirs = []
    dirs_no_time = []

    # Sort by time saved
    for _dir in dirs:        
        if not _dir in load_dates:
            logger.error(f"'{_dir}' not found in load_dates: {load_dates}")

        last_loaded_time = load_dates[_dir]
        if last_loaded_time == 0:
            epoch_start = datetime(1970, 1, 1, 0, 0, 0)
            last_loaded_time = epoch_start.strftime(settings.EXPORT_TIME_FORMAT)

        diff = datetime.now() - datetime.strptime(last_loaded_time, settings.EXPORT_TIME_FORMAT)
        loaded_minutes_ago = diff.total_seconds() / 60
        
        sorted_dirs.append( (_dir, loaded_minutes_ago) )
    
    # sort by the difference to current time: Most recently exported will be on top
    sorted_dirs.sort(key=lambda x: x[1])

    # Append the ones that didn't have last_loaded to the back
    for d in dirs_no_time:
        sorted_dirs.append(d)

    output = [_dir for _dir, _ in sorted_dirs]

    return output


def __get_tilemap_data(tilemap_path: str) -> dict:
    if os.path.isfile(tilemap_path + "\\data.json"):
        with open(tilemap_path + "\\data.json", "r") as f:
            return json.load(f)
    elif os.path.isfile(tilemap_path + "\\explanations.json"):
        with open(tilemap_path + "\\explanations.json", "r") as f:
            return json.load(f)
    else:
        logger.warning(f"Retrieving tilemap data: Trying to get tilemap data, but no \\data.json or \\explanations.json was found")
    
    return {}


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


def load_json_data_dict(path: str) -> dict:
    if not os.path.isfile(path): 
        logger.error(f"Trying to open file at path {path}, which was not found")
        return {}

    with open(path, "r") as f:        
        return json.load(f)