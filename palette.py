import pygame, os, glob, filecmp, tkinter, shutil
from tkinter import filedialog
from util_logger import logger
pygame.init()

class Palette:
    def __init__(self, ui, path: str):
        self.ui = ui
        self.path = path
        self.tile_size = ui.cell_size
        self.tile_list = self.load_tiles()
        self.palette_data = self.init_palette(ui.sidebar_pos)


    def __str__(self):
        return f"palette '{os.path.split(self.path)[1]}' at '{self.path}'"


    def load_tiles(self) -> list:
        output = []
        png_images = []

        for f in glob.glob(self.path+"\\*.png"): #get all png images
            png_images.append(f)

        for image_path in png_images:                               #load all images to tiles
            sprite = pygame.image.load(image_path)
            sprite = pygame.transform.scale(sprite, (self.tile_size, self.tile_size))
            output.append(sprite)

        return output


    def init_palette(self, pos: tuple) -> list: #tiles list has dicts with image and xy pos
        output = []
        img_per_row = 5
        j = 0
        for i in range(len(self.tile_list)):
            if i % img_per_row == 0:
                j += 1

            output.append({"image" : self.tile_list[i], "pos" : (pos[0] + 30 + (50 * (i % img_per_row)), pos[1] + 50 * j)})
        return output



class PaletteManager:
    def __init__(self, ui):
        self.ui = ui
        self.palettes_path = "Assets\\Palettes\\"
        self.palette_directories = [self.palettes_path+x for x in os.listdir(self.palettes_path) if os.path.isdir(self.palettes_path+x)]
        #TODO: if no palettes in directory
        self.palettes = []

        for path in self.palette_directories:
            self.palettes.append(Palette(ui, path))

        #TODO: Use same palette as last time when closing as first palette
        self.current_palette = self.palettes[0]
        logger.log(f"Loaded {self.current_palette}")


    def create_palette(self, name: str, tiles_folder=None) -> str: 
        """WARNING: will overwrite palette's folder if folder with same name already exists\n
        Returns path to new folder."""
        new_palette_folder = str(self.palettes_path+"Palette_"+name)

        if os.path.isdir(new_palette_folder): #if already exists, delete old one
            shutil.rmtree(new_palette_folder)
        os.mkdir(new_palette_folder) #create tiles folder
    
        if tiles_folder is None: return #if no tilesfolder, don't copy any tiles

        for png in glob.glob(tiles_folder+"\\*.png"): #copy tiles to tiles folder
            shutil.copy(png, new_palette_folder)

        self.palettes.append(Palette(self.ui, new_palette_folder))
        return new_palette_folder


    def change_palette(self, palette_path: str) -> bool:
        """Returns True if changed palette succesfully, False if invalid path"""
        for palette in self.palettes: #check if path is valid
            if palette_path == palette.path:
                dest_palette = palette
                break
        else:
            logger.error(f"No palette found at path: '{palette_path}', keeping old palette")
            return False

        self.current_palette = dest_palette
        logger.log(f"Loaded {dest_palette}")
        self.update_palette_change()
        return True


    def update_palette_change(self):
        self.ui.current_palette = self.current_palette
        self.ui.tile_selection_rects = [pygame.Rect(x["pos"], (self.ui.cell_size, self.ui.cell_size)) for x in self.current_palette.palette_data] #make sidebar tiles' rects
        self.ui.tile_to_place_id = 0

        for x in self.ui.blocks:
            x.update_palette()

    
    def change_palette_ask(self):
        root = tkinter.Tk()
        root.withdraw()
        dest_folder = filedialog.askdirectory(title="Select folder with palette to load.", initialdir="Assets\\Palettes")
        root.destroy()
        if dest_folder == "": return #pressed cancel when selecting 
        #TODO: Finish this, not called anywhere
        dest_folder = os.path.relpath(dest_folder, os.getcwd())

        #check if dest path is current palette
        if dest_folder == self.current_palette.path:
            logger.log("While changing palette, selected current palette. Didn't changed palette or reset map")
            return
        if not self.change_palette(dest_folder): return

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
            logger.warn(f"Didn't find a suitable palette in '{self.palettes_path}', creating a new one named 'Palette_{map_name}'")
            self.change_palette(self.create_palette(map_name, tiles_folder=tiles_dir))
            return
        
        self.change_palette(new_palette_path)