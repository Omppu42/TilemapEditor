import pygame, operator, math

import palette
import ui
import settings

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

    # STATIC ------------------------------------------
    def get_cell_from_mousepos(pos: tuple) -> "Block":
        cell = ((pos[0] - ui.ui_obj.total_mouse_change[0]) // settings.CELL_SIZE, 
                (pos[1] - ui.ui_obj.total_mouse_change[1]) // settings.CELL_SIZE)

        block = next((x for x in ui.ui_obj.blocks if x.pos_on_grid == cell), None)
        return block

    # PUBLIC ------------------------------------------
    def update_surf(self, grid: bool):
        self.surf.fill((120,120,120))
        if self.tile_id != -1:
            current_palette = palette.pm_obj.current_palette
            self.surf.blit(palette.pm_obj.get_data()[math.floor(self.tile_id/palette.Palette.TILES_PER_PAGE)][self.tile_id % palette.Palette.TILES_PER_PAGE]["image"], (0, 0))
        if grid:
            pygame.draw.lines(self.surf, (0,0,0), False, ((0, self.size), (0, 0), (self.size, 0)))


    def update(self, movement_vec: tuple):
        self.pos = list(map(operator.add, self.org_pos, movement_vec))
        self.screen.blit(self.surf, self.pos)




