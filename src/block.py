import pygame

from util.util_logger import logger

import util.util as util
import settings.data as data
import settings.settings as settings

import palette


pygame.init()

class Block:
    def __init__(self, pos: tuple, size: int, screen, grid_on: bool):
        self.tile_id = -1 # if id -1, no image
        self.org_pos = (pos[0]*size, pos[1]*size)
        self.pos = self.org_pos
        self.size = size
        self.pos_on_grid = pos
        self.screen = screen
        self.screen_size = self.screen.get_size()
        self.surf = pygame.Surface((self.size, self.size))
        self.update_surf(grid_on)
        

    # PUBLIC ------------------------------------------
    def update_surf(self, grid: bool):
        self.surf.fill((120,120,120))
        if self.tile_id != -1:
            
            tile_page = util.get_tile_page_from_index(self.tile_id)
            tile_pos_on_page = util.get_tile_index_on_page(self.tile_id)

            palette_data = palette.pm_obj.get_data()[tile_page]

            # Check if some error occured and the ID of the block is out of palette's range 
            if len(palette_data) <= tile_pos_on_page:
                pygame.draw.rect(self.surf, (122, 0, 0), (0, 0, settings.CELL_SIZE, settings.CELL_SIZE))
                logger.error(f"Block ID {self.tile_id} is invalid. Highlighting the error block with dark red.")
            # The ID is valid, proceed to draw the texture to the block            
            else:
                self.surf.blit(palette_data[tile_pos_on_page]["image"], (0, 0))
            
            # Debug option to draw the tile ID on the tile
            if settings.DEBUG_INFO:
                id_text = data.font_25.render(str(self.tile_id), False, (255, 0, 0))
                _w, _h = id_text.get_size()

                self.surf.blit(id_text, (settings.CELL_SIZE/2 - _w/2, settings.CELL_SIZE/2 - _h/2))

        if grid:
            pygame.draw.lines(self.surf, (0,0,0), False, ((0, self.size), (0, 0), (self.size, 0)))


    def update(self, movement_vec: tuple):
        """Movement vec being the total movement of the mouse since the beginning"""
        self.pos =  (self.org_pos[0] + movement_vec[0], self.org_pos[1] + movement_vec[1])
        self.screen.blit(self.surf, self.pos)




