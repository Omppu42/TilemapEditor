import pygame, random
pygame.init()

class Block:
    def __init__(self, pos: tuple, size: int, screen, grid_on: bool, tiles_dict: dict):
        self.tile_id = -1 # if id -1, no image
        self.tiles_dict = tiles_dict
        self.org_pos = (pos[0]*size, pos[1]*size)
        self.pos = self.org_pos
        self.size = size
        self.pos_on_grid = pos
        self.screen = screen
        self.screen_size = self.screen.get_size()
        self.surf = pygame.Surface((self.size, self.size))
        self.update_surf(grid_on)

    def update_surf(self, grid: bool):
        self.surf.fill((120,120,120))
        if self.tile_id != -1:
            self.surf.blit(self.tiles_dict[self.tile_id][0], (0, 0))
        if grid:
            pygame.draw.lines(self.surf, (0,0,0), False, ((0, self.size), (0, 0), (self.size, 0)))


    def update(self, movement_vec: tuple):
        self.pos = (self.org_pos[0]+movement_vec[0], self.org_pos[1]+movement_vec[1])
        self.screen.blit(self.surf, self.pos)