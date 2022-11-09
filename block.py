import pygame, random, operator
pygame.init()

class Block:
    def __init__(self, pos: tuple, size: int, screen, grid_on: bool, palette_manager):
        self.tile_id = -1 # if id -1, no image
        self.palette_manager = palette_manager
        self.palette_data = self.palette_manager.current_palette.palette_data
        self.org_pos = (pos[0]*size, pos[1]*size)
        self.pos = self.org_pos
        self.size = size
        self.pos_on_grid = pos
        self.screen = screen
        self.screen_size = self.screen.get_size()
        self.surf = pygame.Surface((self.size, self.size))
        self.update_surf(grid_on)

    def update_palette(self):
        self.palette_data = self.palette_manager.current_palette.palette_data


    def update_surf(self, grid: bool):
        self.surf.fill((120,120,120))
        if self.tile_id != -1:
            self.surf.blit(self.palette_data[self.tile_id]["image"], (0, 0))
        if grid:
            pygame.draw.lines(self.surf, (0,0,0), False, ((0, self.size), (0, 0), (self.size, 0)))


    def update(self, movement_vec: tuple):
        self.pos = list(map(operator.add, self.org_pos, movement_vec))
        self.screen.blit(self.surf, self.pos)