import pygame, os, glob
pygame.init()

class Tiles:
    def __init__(self, tile_size: int):
        self.tile_size = tile_size
        self.tile_list = self.load_tiles()


    def load_tiles(self) -> list:
        output = []
        png_images = []

        for f in glob.glob("Assets\\Tiles\\*.png"): #get all png images
            png_images.append(f)

        for image_path in png_images:                               #load all images to tiles
            sprite = pygame.image.load(image_path)
            sprite = pygame.transform.scale(sprite, (self.tile_size, self.tile_size))
            output.append(sprite)

        return output


    def init_tiles(self, pos: tuple) -> list: #tiles list has dicts with image and xy pos
        output = []
        img_per_row = 5
        j = 0
        for i in range(len(self.tile_list)):
            if i % img_per_row == 0:
                j += 1

            output.append({"image" : self.tile_list[i], "pos" : (pos[0] + 30 + (50 * (i % img_per_row)), pos[1] + 50 * j)})
        
        return output