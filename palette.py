import pygame, os, glob, filecmp, tkinter
from tkinter import filedialog
pygame.init()

class Palette:
    def __init__(self, tile_size: int, path: str, ui):
        self.tile_size = tile_size
        self.path = path
        self.ui = ui
        self.tile_list = self.load_tiles()
        self.palette_data = self.init_palette(ui.sidebar_pos)


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
            self.palettes.append(Palette(ui.cell_size, path, ui))

        self.current_palette = self.palettes[0]


    def create_palette(self):
        pass


    def change_palette(self, palette_path: str):
        for palette in self.palettes: #check if path is valid
            if palette_path == palette.path:
                dest_palette = palette
                break
        else:
            print(f"ERROR: No palette found at path: {palette_path}")
            return

        self.current_palette = dest_palette
        self.update_palette_change()
        #TODO: Finish palette changing


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


    def import_map_palette_change(self, directory: str):
        same_tilemap = True
        for x in glob.glob(directory+"\\Tiles\\*.png"): #check that all tiles match in current palette and imported palette
            filename = os.path.split(x)[1]

            #if one of the tiles doesn't match, tilemaps are different
            if filecmp.cmp(x, self.current_palette.path+"\\"+filename) == False:
                same_tilemap = False
                break
        
        print(same_tilemap)
        if same_tilemap: return
        #TODO: check if palette exists or should create new one, hardcoded path is for testing
        self.change_palette("Assets\\Palettes\\Palette_1")