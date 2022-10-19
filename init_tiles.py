import pygame
from util import load_sprites
pygame.init()

class Tiles:
    def __init__(self, tile_size: int):
        self.tile_list = []
        self.tile_size = tile_size
        self.tile_list = load_sprites("Assets\\Tiles\\", "tile00", 10, ".png", (tile_size, tile_size))
        self.tile_list = self.tile_list + load_sprites("Assets\\Tiles\\", "tile0", 36, ".png", (tile_size, tile_size), 10)
        #self.tile_path_dict = #TODO: dict with tile id and path to tile image (for exporting tilemap) 

    def init_tiles(self, pos: tuple) -> dict: #tiles dict has key id: int, value tuple of image and xy pos
        output = {}
        img_per_row = 5
        j = 0
        for i in range(len(self.tile_list)):
            if i % img_per_row == 0:
                j += 1

            output[i] = {"image" : self.tile_list[i], "pos" : (pos[0] + 30 + (50 * (i % img_per_row)), pos[1] + 50 * j)}
        
        return output