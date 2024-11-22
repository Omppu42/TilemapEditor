import pygame

from settings import data


class FrameTimeGraph:
    KEEP_POINTS = 200
    POINT_DISTANCE_X = 1

    def __init__(self, screen: "pygame.Surface", pos: tuple, height: int):
        self.screen = screen
        self.pos = pos
        self.height = height

        self.points: "list[float]" = []
        

    def add_point(self, point: float) -> None:
        self.points.append(point)

        if len(self.points) > FrameTimeGraph.KEEP_POINTS:
            self.points.pop(0)

    
    def draw_graph(self) -> None:
        if len(self.points) < 2: return
    
        points_xy = [(self.pos[0] + i * FrameTimeGraph.POINT_DISTANCE_X,
                      self.pos[1] - p) for i, p in enumerate(self.points)]


        pygame.draw.line(self.screen, (0,0,0), (self.pos[0] - 5, self.pos[1]), 
                                                (self.pos[0] - 5, self.pos[1] - self.height), 
                                                 width=2)
       
        pygame.draw.line(self.screen, (0,0,0), (self.pos[0], self.pos[1] + 5), 
                                                (self.pos[0] + FrameTimeGraph.KEEP_POINTS * FrameTimeGraph.POINT_DISTANCE_X, self.pos[1] + 5), 
                                                 width=2)


        pygame.draw.lines(self.screen, (0,0,0), False, points_xy)

        ms_now =        data.font_20.render(f"Now: {self.points[-1]}ms", True, (0,0,0))
        ms_average =    data.font_20.render(f"Avg: {sum(self.points) // len(self.points)}ms", True, (0,0,0))
        ms_peak =       data.font_20.render(f"Max: {max(self.points)}ms", True, (0,0,0))

        self.screen.blit(ms_now, (self.pos[0], self.pos[1] + 10))
        self.screen.blit(ms_average, (self.pos[0], self.pos[1] + 25))
        self.screen.blit(ms_peak, (self.pos[0], self.pos[1] + 40))