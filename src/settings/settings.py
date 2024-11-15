# SCREEN --------
SCR_W = 1200
SCR_H = 600
CELL_SIZE = 32
BG_COLOR = 100
FPS_CAP = 60

# PATHS ---------
LOGS_FOLDER             = "Data\\Logs"
PALETTES_PATH           = "Data\\Palettes\\"
TILEMAPS_EXPORT         = "Data\\Tilemaps"
DELETED_TILEMAPS_PATH   = "Data\\_Deleted_tilemaps"
DELETED_TILES_PATH      = "Data\\_Deleted_tiles"
LAST_SESSION_DATA_JSON  = "Data\\last_session_data.json"

# SIDEBAR ------------
TILES_PER_ROW = 5
TILES_PER_COL = 9
TILES_PER_PAGE = TILES_PER_ROW * TILES_PER_COL

# UI -----
VIEWPORT_W = SCR_W // 4 * 3   # 3/4 of screen width
DEFAULT_GRID_SIZE = (30, 20)
SAVE_TEXT_TIME_S = 1.5
DEFAULT_GIRD_OFFSET = (100, 50)

# CONSTANTS ---------
EXPORT_TIME_FORMAT = "%d/%m/%Y %H:%M:%S"

# DEBUG ----------
DRAW_TILE_IDS = False

# TESTS------------
TESTS_PALETTE_PATH = PALETTES_PATH   +   "tests-sVLkGQUpMQokDdScZWsr"
TESTS_TILEMAP_PATH = TILEMAPS_EXPORT + "\\tests-sVLkGQUpMQokDdScZWsr"