import pygame

from util.util import round_to_significant_digits
from settings import data


class FrameTimeGraph:
    KEEP_POINTS = 200
    POINT_DISTANCE_X = 1

    def __init__(self, screen: "pygame.Surface", pos: tuple, height: int):
        self.screen = screen
        self.pos = pos
        self.height = height

        self.frametimes: "list[int]"   = []
        self.framerates: "list[float]" = []
        

    def add_frametime(self, ms: int) -> None:
        self.frametimes.append(ms)

        if len(self.frametimes) > FrameTimeGraph.KEEP_POINTS:
            self.frametimes.pop(0)

    def add_framerate(self, fps: float) -> None:
        if fps == 0:
            fps = 1

        self.framerates.append(round_to_significant_digits(fps, 2))

        if len(self.framerates) > FrameTimeGraph.KEEP_POINTS:
            self.framerates.pop(0)

    
    def draw_graph(self) -> None:
        if len(self.frametimes) < 2: return
    
        frametimes_xy = [(self.pos[0] + i * FrameTimeGraph.POINT_DISTANCE_X,
                      self.pos[1] - p) for i, p in enumerate(self.frametimes)]


        pygame.draw.line(self.screen, (0,0,0), (self.pos[0] - 5, self.pos[1]), 
                                                (self.pos[0] - 5, self.pos[1] - self.height), 
                                                 width=2)
       
        pygame.draw.line(self.screen, (0,0,0), (self.pos[0], self.pos[1] + 5), 
                                                (self.pos[0] + FrameTimeGraph.KEEP_POINTS * FrameTimeGraph.POINT_DISTANCE_X, self.pos[1] + 5), 
                                                 width=2)


        pygame.draw.lines(self.screen, (0,0,0), False, frametimes_xy)

         

        ms_now =        data.font_20.render(f"Now: {self.frametimes[-1]}ms", True, (0,0,0))
        ms_average =    data.font_20.render(f"Avg: {round(sum(self.frametimes) / len(self.frametimes), 1)}ms", True, (0,0,0))
        ms_peak =       data.font_20.render(f"Max: {max(self.frametimes)}ms", True, (0,0,0))

        fps_now =       data.font_20.render(f"/  {self.framerates[-1]}fps", True, (0,0,0))
        fps_average =   data.font_20.render(f"/  {round_to_significant_digits(sum(self.framerates) / len(self.framerates), 2)}fps", True, (0,0,0))
        fps_peak =      data.font_20.render(f"/  {min(self.framerates)}fps", True, (0,0,0))

        self.screen.blit(ms_now, (self.pos[0], self.pos[1] + 10))
        self.screen.blit(fps_now, (self.pos[0] + 80, self.pos[1] + 10))

        self.screen.blit(ms_average, (self.pos[0], self.pos[1] + 25))
        self.screen.blit(fps_average, (self.pos[0] + 80, self.pos[1] + 25))

        self.screen.blit(ms_peak, (self.pos[0], self.pos[1] + 40))
        self.screen.blit(fps_peak, (self.pos[0] + 80, self.pos[1] + 40))