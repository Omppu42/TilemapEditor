import pygame, os, glob, filecmp, tkinter, shutil, json
from tkinter import filedialog
from tkinter.messagebox import askokcancel, WARNING

from import_export import ie_interface

from util.util_logger import logger
from util import file_utils
import settings.data as data
import settings.settings as settings

import sidebar
import manager


pygame.init()

class Palette:
    ORDER_JSON_FILENAME = "_order.json"
    def __init__(self, path: str):
        self.tile_list: list = []
        self.palette_data: list = []
        self.tiles_order: list = []
        self.pages = 1

        self.path = path
        self.name = os.path.split(self.path)[1]

        self.__init_tiles_order()

        self.load_sequence()
        logger.debug(f"Initialized palette '{self.name}'")

    # PUBLIC ----------------------------------
    def __str__(self):
        return f"'{os.path.split(self.path)[1]}' at '{self.path}'"


    def load_sequence(self):
        self.tile_list = self.__load_tiles()
        self.palette_data = self.__init_palette()

    
    def export_tiles_order(self) -> None:
        order_json_path = self.path + "\\" + Palette.ORDER_JSON_FILENAME
        with open(order_json_path, "w") as f:
            json.dump(self.tiles_order, f, indent=4)



    # PRIVATE ----------------------------------
    def __init_tiles_order(self) -> None:
        """Load the tile order that has been saved"""
        order_json_path = self.path + "\\" + Palette.ORDER_JSON_FILENAME
        last_tiles_order = []

        # If tile order already exists
        if os.path.isfile(order_json_path):
            with open(order_json_path, "r") as f:
                last_tiles_order = json.load(f)
                logger.debug(f"Palette '{self.name}': _order.json loaded from last session")
        else:
            logger.debug(f"No last session order found for palette '{self.name}'. Creating from file order")

        # PNGs present now
        present_tiles = []
        # Get all png images
        for _png in glob.glob(self.path+"\\*.png"): 
            # Get the filename only
            _tail = os.path.split(_png)[1]
            present_tiles.append(_tail)

        # Check which tiles have been deleted between sessions
        # Add tiles which are still present first
        for _tile in last_tiles_order:
            if _tile in present_tiles:
                self.tiles_order.append(_tile)

        # Check which tiles are new
        for _tile in present_tiles:
            if not _tile in last_tiles_order:
                self.tiles_order.append(_tile)

        # Old tiles first, new ones last
        self.export_tiles_order()


    def __load_tiles(self) -> list:
        output = []

        # load all images to tiles
        for image_path in self.tiles_order:    
            sprite = pygame.image.load(self.path + "\\" + image_path)
            sprite = pygame.transform.scale(sprite, (settings.CELL_SIZE, settings.CELL_SIZE))
            output.append(sprite)

        return output


    def __init_palette(self) -> list: #tiles list has dicts with id, image and xy pos
        self.pages = 1

        output = []
        sublist = []
        j = 0

        for i in range(len(self.tile_list)):
            if i % settings.TILES_PER_PAGE == 0 and not sublist == []:
                output.append(sublist)
                sublist = []
                j = 0
                self.pages += 1

            if i % settings.TILES_PER_ROW == 0:
                j += 1

            sublist.append({"id" : i, 
                            "image" : self.tile_list[i], 
                            "pos" : (sidebar.s_obj.pos[0] + 30 + (50 * (i % settings.TILES_PER_ROW)), sidebar.s_obj.pos[1] + 50 * j)})

        output.append(sublist)
        return output



class PaletteManager:
    def __init__(self):
        self.PALETTE_DIRS = [settings.PALETTES_PATH + "\\" + _dir for _dir in os.listdir(settings.PALETTES_PATH) 
                                    if os.path.isdir(settings.PALETTES_PATH + "\\" + _dir)]
        
        self.current_palette: Palette = None
        self.all_palettes: "list[Palette]" = []
        self.selected_tile_id: int = 0

        self.__init_palettes()
        self.__init_load_last_session_data()

        if self.current_palette == None:
            logger.fatal(f"Error in PaletteManager initialization: Palette loaded is 'None' for some reason. Something failed in the palette loading.")
            return

        logger.log(f"Loaded palette {self.current_palette}")
        logger.debug("Initialized PaletteManager")


    # STATIC ------------
    def get_all_palettes_paths() -> "list[str]":
        return [settings.PALETTES_PATH + "\\" + x for x in os.listdir(settings.PALETTES_PATH)]

    def is_valid_palette_path(self, path: str) -> bool:
        if (path is None 
            or not os.path.exists(path)
            or not self.__get_palette_at_path(path)): 
            return False
        
        if os.path.commonprefix([path, settings.PALETTES_PATH]) == settings.PALETTES_PATH:
            return True
        
        logger.error(f"Invalid palette ({path}). Valid path but outside '{settings.PALETTES_PATH}'")
        return False


    # GETTERS ----------------------------------------------------------------
    def get_current_tiles(self) -> list:
        """Returns current_palette.tile_list"""
        return self.current_palette.tile_list

    def get_data(self) -> list:
        """Returns current_palette.palette_data\n
        Data is of format [[ {"id":1, "image":pygame.Surf, "pos":[950, 50]}, ...]]"""
        return self.current_palette.palette_data
    
    def get_data_current_page(self) -> list:
        """Returns current_palette.palette_data[current_page]\n
        Data is of format [ {"id":1, "image":pygame.Surf, "pos":[950, 50]}, ...]"""
        return self.current_palette.palette_data[sidebar.s_obj.tiles_page]
    
    def get_total_pages(self) -> int:
        return self.current_palette.pages
    
    def get_tiles_order(self) -> list:
        return self.current_palette.tiles_order
    
    def get_tiles_count(self) -> int:
        return len(self.current_palette.tiles_order)


    # PRIVATE ----------------------------------------------------------------
    def __init_palettes(self):
        if self.PALETTE_DIRS == []:
            logger.warning("No palette in palettes folder, creating empty one")
            self.create_empty_palette(ask_confirm=False, update_palette=False)

        for path in self.PALETTE_DIRS:
            self.all_palettes.append(Palette(path))


    def __init_load_last_session_data(self) -> None:
        # Default to the first palette, change to the last session palette if found
        self.current_palette = self.all_palettes[0]

        last_session_data = file_utils.load_json_data_dict(settings.LAST_SESSION_DATA_JSON)

        if last_session_data == {}:
            logger.warning("No last session data found, returning to defaults")
            return

        #Load palette
        target_palette = self.__get_palette_at_path(last_session_data["palette"])
        if not target_palette:
            _last_palette_path, _last_palette_name = os.path.split(last_session_data["palette"])
            logger.warning(f"Trying to load the palette from last session ('{_last_palette_name}'), but it was not found in '{_last_palette_path}'. Selecting the default palette")
            return
        
        self.current_palette = target_palette


    def __get_palette_at_path(self, path: str) -> Palette:
        for palette in self.all_palettes: #check if path is valid
            if path == palette.path:
                return palette
        else:
            logger.warning(f"No palette found at path: '{path}'")
            return None


    def __create_palette(self, name: str, tiles_folder=None) -> str: 
        """WARNING: will overwrite palette's folder if folder with same name already exists\n
        Returns path to new folder."""
        new_palette_folder = str(settings.PALETTES_PATH + "\\" + name)

        if os.path.isdir(new_palette_folder): #if already exists, delete old one
            self.delete_palette(ask_confirm=False, dest_folder=new_palette_folder)
        os.mkdir(new_palette_folder)
    
        # if no tilesfolder, don't copy any tiles
        if tiles_folder is None: 
            self.all_palettes.append(Palette(new_palette_folder))
            return new_palette_folder 

        for png in glob.glob(tiles_folder+"\\*.png"): # copy tiles to tiles folder
            shutil.copy(png, new_palette_folder)
        
        if os.path.exists(tiles_folder + "\\_order.json"):
            shutil.copy(tiles_folder + "\\_order.json", new_palette_folder)
            logger.debug(f"Palette _order.json was copied from Tiles/ folder. Palette '{name}'")
        else:
            logger.warning(f"No _order.json was found in '{os.path.relpath(tiles_folder, os.getcwd())}' when creating a palette from tiles folder. Falling back to file order as the palette order")

        self.all_palettes.append(Palette(new_palette_folder))
        return new_palette_folder
    

    def __update_palette_change(self):
        self.current_palette.load_sequence()
        
        sidebar.tile_selection_rects = [pygame.Rect(x["pos"], (settings.CELL_SIZE, settings.CELL_SIZE)) for x in self.current_palette.palette_data[sidebar.s_obj.tiles_page]] #make sidebar tiles' rects
        self.selected_tile_id = sidebar.s_obj.tiles_page * settings.TILES_PER_PAGE

        sidebar.s_obj.update_page_arrows()
    


    # PUBLIC ----------------------------------------------------------------
    def export_all_palette_tile_orders(self) -> None:
        for _palette in self.all_palettes:
            _palette.export_tiles_order()
            

    def select_nth_tile_on_page(self, tile_index: int) -> None:
        """Selects the nth tile on the current page of the tile selection. Tile_index 0 is the first tile"""
        self.selected_tile_id = self.current_palette.palette_data[sidebar.s_obj.tiles_page][tile_index]["id"]        


    def change_palette(self, palette_path: str) -> bool:
        """Load a palette from a path, returns True if succeeded"""
        dest_palette = self.__get_palette_at_path(palette_path)
        if dest_palette is None: 
            logger.error(f"Trying to load a palette which is invalid from path '{palette_path}'")
            return False

        sidebar.s_obj.tiles_page = 0
        self.current_palette = dest_palette

        self.__update_palette_change()

        logger.log(f"Loaded {dest_palette}")
        return True


    def import_map_palette_change(self, directory: str):
        tiles_dir = directory+"\\Tiles"
        map_name = os.path.split(directory)[1]
        has_palette = False
        new_palette_path = None

        for x in glob.glob(tiles_dir+"\\*.png"): #check that all tiles match in current palette and imported palette
            filename = os.path.split(x)[1]
            if not os.path.exists(self.current_palette.path+"\\"+filename):
                break

            #if one of the tiles doesn't match, tilemaps are different
            if filecmp.cmp(x, self.current_palette.path+"\\"+filename) == False:
                break
        else: return # different tilemap
        
        #find matching palette from existing palettes
        for palette in self.all_palettes:
            for tile in glob.glob(tiles_dir+"\\*.png"):
                filename = os.path.split(tile)[1]
                
                if os.path.isfile(palette.path+"\\"+filename) == False:
                    break
                if filecmp.cmp(tile, palette.path+"\\"+filename) == False:
                    break
            else:
                has_palette = True
                new_palette_path = palette.path
                break

        if not has_palette:
            logger.warning(f"Didn't find a suitable palette for tilemap '{os.path.relpath(directory, os.getcwd())}' in '{settings.PALETTES_PATH}', creating a new one named 'Palette_{map_name}'")
            self.change_palette(self.__create_palette("Palette_"+map_name, tiles_folder=tiles_dir))
            return
        
        self.change_palette(new_palette_path)

    
    def add_tile(self):
        root = tkinter.Tk()
        root.withdraw()
        pngs = filedialog.askopenfilenames(filetypes=[("PNG file", ".png")])
        root.destroy()

        if pngs == "": 
            return

        for png in pngs: 
            filename = os.path.split(png)[1]
            destination = self.current_palette.path + "\\" + filename

            # Add file (1) if needed
            destination = file_utils.prevent_existing_file_overlap(destination)
            filename = os.path.split(destination)[1]
            
            shutil.copy(png, destination)
            self.current_palette.tiles_order.append(filename)
            
            logger.log(f"Added '{filename}.png' to {self.current_palette}")

                

        self.__update_palette_change()


    def remove_tile(self, index: int):
        """Run after selecting a tile to remove from the palette"""
        # Stop from deleting more tiles
        manager.m_obj.remove_palette_tiles = False

        root = tkinter.Tk()
        root.withdraw()
        if not askokcancel("Confirm", "Please backup before deleting tiles.\n\nBy deleting this tile, all it's instances will deleted.\nYou can recover the tile from deleted tiles folder.", icon=WARNING):
            # Clicked "No"
            root.destroy()
            return

        # "Yes"
        root.destroy()
        
        if not os.path.isdir(settings.DELETED_TILES_PATH):
            os.mkdir(settings.DELETED_TILES_PATH)
        
        tile_to_remove_path = self.current_palette.path + "\\" + self.current_palette.tiles_order[index]
        
        deleted_tile_path = settings.DELETED_TILES_PATH + "\\" + self.current_palette.tiles_order[index]
        deleted_tile_path = file_utils.prevent_existing_file_overlap(deleted_tile_path)


        shutil.move(tile_to_remove_path, deleted_tile_path)
        self.current_palette.tiles_order.remove(os.path.split(tile_to_remove_path)[1]) # Remove the filename

        self.__update_palette_change()
        manager.m_obj.remove_index_map(index)
        manager.m_obj.on_tile_deleted(index)

        logger.log(f"Moved '{os.path.split(tile_to_remove_path)[1]}' from '{self.current_palette.name}' to '{settings.DELETED_TILES_PATH}' folder")


    def create_empty_palette(self, ask_confirm=True, update_palette=True, num=None):
        if ask_confirm:
            root = tkinter.Tk()
            root.withdraw()
            if not askokcancel("Confirm", "When you create a new palette, your map will reset.\nMake sure to save before continuing.", icon=WARNING):
                root.destroy()
                return

            root.destroy()

        if num is None:
            num = len(self.all_palettes)
        logger.log(f"Creating new palette 'Palette_{num}'")
        new_palette = self.__create_palette("Palette_"+str(num))

        if update_palette:
            self.change_palette(new_palette)
            manager.m_obj.reset_map()


    def delete_palette(self, palette_path: str, rename_to_path:str="", move_to_deleted=True):
        if not self.is_valid_palette_path(palette_path):
            return
            
        if not os.path.isdir(settings.DELETED_PALETTES_PATH):
            os.mkdir(settings.DELETED_PALETTES_PATH)

        if not move_to_deleted:
            try:
                shutil.rmtree(palette_path)
            except Exception as e:
                logger.error("Error: %s - %s." % (e.filename, e.strerror))
            return

        try:
            shutil.move(palette_path, settings.DELETED_PALETTES_PATH)

            if rename_to_path:
                rename_to_path = file_utils.prevent_existing_file_overlap(rename_to_path)
                deleted_path = settings.DELETED_PALETTES_PATH + "\\" + os.path.basename(palette_path)
                os.rename(deleted_path, rename_to_path)
                
        except Exception as e:
            logger.error("Error: %s - %s." % (e.filename, e.strerror))

        self.current_palette = self.all_palettes[0]
        self.__update_palette_change()

        self.all_palettes.remove(self.__get_palette_at_path(palette_path))
        
        logger.log(f"Palette deleted at '{palette_path}'. Moved palette to '{settings.DELETED_TILEMAPS_PATH}\\'")


    def draw_current_palette_text(self, screen):
        text = data.font_35.render(self.current_palette.name, True, (150,150,150))
        text_rect = text.get_rect(center=(sidebar.s_obj.pos[0]+sidebar.s_obj.size[0]//2, 25))
        screen.blit(text, text_rect)




pm_obj: PaletteManager = None
def create_palette_manager() -> None:
    global pm_obj
    pm_obj = PaletteManager()