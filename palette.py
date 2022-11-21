import pygame, os, glob, filecmp, tkinter, shutil, json
from tkinter import filedialog
from tkinter.messagebox import askokcancel, WARNING
from util_logger import logger
pygame.init()

class Palette:
    def __init__(self, ui, path: str):
        self.ui = ui
        self.path = path
        self.name = os.path.split(self.path)[1]
        self.tile_size = ui.cell_size
        self.page_size = 45
        self.added_tiles = {}
        print(self.added_tiles)
        self.load_sequence()

    def __str__(self):
        return f"palette '{os.path.split(self.path)[1]}' at '{self.path}'"


    def load_sequence(self):
        self.tile_list = self.load_tiles()
        self.palette_data = self.init_palette()


    def load_tiles(self) -> list:
        output = []
        self.img_paths = []

        for f in glob.glob(self.path+"\\*.png"): #get all png images
            self.img_paths.append(f)

        for image_path in self.img_paths:                               #load all images to tiles
            sprite = pygame.image.load(image_path)
            sprite = pygame.transform.scale(sprite, (self.tile_size, self.tile_size))
            output.append(sprite)

        return output


    def init_palette(self) -> list: #tiles list has dicts with image and xy pos
        output = []
        sublist = []
        img_per_row = 5
        j = 0
        self.pages = 1

        for i in range(len(self.tile_list)):
            if i % self.page_size == 0 and not sublist == []:
                output.append(sublist)
                sublist = []
                j = 0
                self.pages += 1

            if i % img_per_row == 0:
                j += 1

            sublist.append({"id" : i, "image" : self.tile_list[i], "pos" : (self.ui.sidebar_pos[0] + 30 + (50 * (i % img_per_row)), self.ui.sidebar_pos[1] + 50 * j)})

        output.append(sublist)
        return output



class PaletteManager:
    def __init__(self, ui):
        self.ui = ui
        self.palettes_path = "Assets\\Palettes\\"

        self.init_palettes()

        json_data = {}
        if os.path.isfile("last_session_data.json"):
            with open("last_session_data.json", "r") as f:
                data = f.readlines()
                if not data == []:
                    json_data = json.loads("".join(data))

        for palette in self.palettes:
            key = palette.path+"_added_tiles"
            if key in json_data:
                palette.added_tiles = json_data[key]


        #Load palette
        if not "palette" in json_data:
            logger.warning("Last used palette invalid, falling back to first palette")
            self.current_palette = self.palettes[0]

        else:
            target_palette = self.get_palette_at_path(json_data["palette"])
            if target_palette is None:
                self.current_palette = self.palettes[0]
            else:
                self.current_palette = target_palette

        print(self.current_palette.added_tiles)
        logger.log(f"Loaded {self.current_palette}")

    
    def init_palettes(self):
        self.palette_directories = [self.palettes_path+x for x in os.listdir(self.palettes_path) if os.path.isdir(self.palettes_path+x)]

        if self.palette_directories == []:
            logger.warning("No palette in palettes folder, creating empty one")
            self.create_empty_palette(ask_confirm=False, update_palette=False)

        self.palettes = []
        for path in self.palette_directories:
            self.palettes.append(Palette(self.ui, path))



    def get_palette_at_path(self, path: str) -> Palette:
        for palette in self.palettes: #check if path is valid
            if path == palette.path:
                return palette
        else:
            logger.warning(f"No palette found at path: '{path}', keeping old palette")
            return None


    def create_palette(self, name: str, tiles_folder=None) -> str: 
        """WARNING: will overwrite palette's folder if folder with same name already exists\n
        Returns path to new folder."""
        new_palette_folder = str(self.palettes_path+name)

        if os.path.isdir(new_palette_folder): #if already exists, delete old one
            self.delete_palette(ask_confirm=False, dest_folder=new_palette_folder)
        os.mkdir(new_palette_folder)
    
        self.palettes.append(Palette(self.ui, new_palette_folder))
        if tiles_folder is None: return new_palette_folder#if no tilesfolder, don't copy any tiles

        for png in glob.glob(tiles_folder+"\\*.png"): #copy tiles to tiles folder
            shutil.copy(png, new_palette_folder)

        return new_palette_folder


    def change_palette(self, palette_path: str) -> bool:
        """Returns True if changed palette succesfully, False if invalid path"""
        dest_palette = self.get_palette_at_path(palette_path)
        if dest_palette is None: return False

        self.ui.sidebar.tiles_page = 0
        self.current_palette = dest_palette
        logger.log(f"Loaded {dest_palette}")
        self.update_palette_change()
        return True


    def update_palette_change(self):
        self.ui.current_palette = self.current_palette
        self.ui.tile_selection_rects = [pygame.Rect(x["pos"], (self.ui.cell_size, self.ui.cell_size)) for x in self.current_palette.palette_data[self.ui.sidebar.tiles_page]] #make sidebar tiles' rects
        self.ui.tile_to_place_id = 0

        for x in self.ui.blocks:
            x.update_palette()

    
    def change_palette_ask(self):
        dest_folder = self.ui.manager.ask_filedialog(initialdir="Assets\\Palettes")
        if dest_folder == "": return #pressed cancel when selecting 
        dest_folder = os.path.relpath(dest_folder, os.getcwd())

        #check if dest path is current palette
        if dest_folder == self.current_palette.path:
            logger.log("While changing palette, selected current palette. Didn't changed palette or reset map")
            return
        if not self.change_palette(dest_folder): 
            self.change_palette_ask()
            return

        self.ui.manager.reset_map()


    def import_map_palette_change(self, directory: str):
        tiles_dir = directory+"\\Tiles"
        map_name = os.path.split(directory)[1]
        has_palette = False
        new_palette_path = None

        for x in glob.glob(tiles_dir+"\\*.png"): #check that all tiles match in current palette and imported palette
            filename = os.path.split(x)[1]

            #if one of the tiles doesn't match, tilemaps are different
            if filecmp.cmp(x, self.current_palette.path+"\\"+filename) == False:
                break
        else: return # different tilemap
        
        #find matching palette from existing palettes
        for palette in self.palettes:
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
            logger.warning(f"Didn't find a suitable palette in '{self.palettes_path}', creating a new one named 'Palette_{map_name}'")
            self.change_palette(self.create_palette("Palette_"+map_name, tiles_folder=tiles_dir))
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
            number = 0
            if self.current_palette.added_tiles:
                number = list(self.current_palette.added_tiles.values())[-1] + 1
            number = str(number).zfill(3)
            filename = os.path.split(png)[1]
            filename = f"_{number}-"+os.path.splitext(filename)[0]
            
            new_filename = self.current_palette.path + "\\" + filename + ".png"

            shutil.copy(png, new_filename)
            self.current_palette.added_tiles[filename] = int(number)
            
            logger.log(f"Added '{filename}.png' to {self.current_palette}")
        
        self.current_palette.load_sequence()
        self.update_palette_change()


    def remove_tile(self, index: int):
        root = tkinter.Tk()
        root.withdraw()
        if not askokcancel("Confirm", "Please backup before deleting tiles.\n This action can mess up your tile ids.\n\nBy deleting this tile, all it's instances will deleted.\nYou can recover the tile from deleted tiles folder.", icon=WARNING):
            root.destroy()
            self.ui.detele_tiles = -1
            return

        root.destroy()
        self.ui.detele_tiles = -1
        remove_path = self.current_palette.img_paths[index]
        
        org_name = os.path.split(remove_path)[1]
        org_name = os.path.splitext(org_name)[0]
        name = org_name+"(%s).png"

        full_path = "Deleted_tiles\\"+name

        i = 1
        while os.path.exists(full_path % i):
            i += 1

        deleted_tiles_path = "Deleted_tiles"
        if not os.path.isdir(deleted_tiles_path):
            os.mkdir(deleted_tiles_path)

        if org_name in self.current_palette.added_tiles:
            self.current_palette.added_tiles.pop(org_name, None)
        
        print(self.current_palette.added_tiles)

        shutil.move(remove_path, deleted_tiles_path+"\\"+name % i)

        self.current_palette.load_sequence()
        self.update_palette_change()
        self.ui.manager.remove_index_map(index)

        logger.log(f"Moved '{os.path.split(remove_path)[1]}' from '{self.current_palette.name}' to 'Deleted_tiles' folder")


    def create_empty_palette(self, ask_confirm=True, update_palette=True, num=None):
        if ask_confirm:
            root = tkinter.Tk()
            root.withdraw()
            if not askokcancel("Confirm", "When you create a new palette, your map will reset.\nMake sure to save before continuing.", icon=WARNING):
                root.destroy()
                return

            root.destroy()

        if num is None:
            num = len(self.palettes)
        logger.log(f"Creating new palette 'Palette_{num}'")
        new_palette = self.create_palette("Palette_"+str(num))

        if update_palette:
            self.change_palette(new_palette)
            self.ui.manager.reset_map()


    def delete_palette(self, ask_confirm=True, dest_folder=None):
        if dest_folder is None:
            dest_folder = self.ui.manager.ask_filedialog(initialdir="Assets\\Palettes")
            if dest_folder == "":return

        allowed_path = os.path.abspath("Assets\\Palettes")  #reformat paths
        allowed_path = os.path.normpath(allowed_path)
        
        dest_folder = os.path.abspath(dest_folder)
        dest_folder = os.path.normpath(dest_folder)

        if not os.path.commonprefix([dest_folder, allowed_path]) == allowed_path: #check if in palettes folder
            logger.error(f"Deleting palette: Tried deleting a non-palette folder. You can olny delete palettes folder inside 'Assets\\Palettes'")
            return

        if dest_folder == allowed_path:
            logger.error("Deleting palette: You cant select 'Assets\\Palettes' folder. You have to select one of it's child folders")
            return

        palette = self.get_palette_at_path(os.path.relpath(dest_folder, os.getcwd()))
        if palette is None:
            logger.error("Deleting palette: No palette found.")
            return

        if ask_confirm:
            root = tkinter.Tk()
            root.withdraw()
            if not askokcancel("Confirm", f"Are you sure you want to delete {palette.name}?\nThis action cannot be undone.", icon=WARNING):
                root.destroy()
                return

            root.destroy()

        for file in os.listdir(dest_folder):
            if not file.endswith(".png"):
                logger.warning("Deleting palette: Not all file were '.png' files. Can't delete such folder")
                return
        
        logger.log("Deleting palette: Deleting pngs..")
        for f in glob.glob(dest_folder+"\\*.png"):
            os.remove(f)
    
        if not os.listdir(dest_folder) == []:
            logger.error("Deleting palette: Directory isn't empty. This should never happen")
            return

        logger.log("Deleting palette: Deleting folder")
        os.rmdir(dest_folder)

        if os.listdir("Assets\\Palettes") == []:
            self.create_empty_palette(ask_confirm=False, num=0)
        
        self.init_palettes()
        self.current_palette = self.palettes[0]
        self.update_palette_change()
        logger.log(f"Deleting palette: Deleted '{palette.name}'")


    def current_palette_text(self):
        font = pygame.font.Font(None, 35)
        text = font.render(self.current_palette.name, True, (150,150,150))
        text_rect = text.get_rect(center=(self.ui.sidebar.pos[0]+self.ui.sidebar.size[0]//2, 25))
        self.ui.screen.blit(text, text_rect)