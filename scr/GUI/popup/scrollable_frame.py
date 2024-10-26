import pygame

from .. import button
from . import scrollable_frame_piece
from util.util import RunnableFunc

import constants

class ScrollableFrame:
    # TODO: Add scroll bar dragging with mouse

    SCROLL_SPEED = 17
    def __init__(self, surface: pygame.Surface, parent_pos: tuple, pos: int, size: int, frames_gap=10) -> None:
        """parent_pos being the position of the parent on the screen, pos being relative to parent surface"""
        self.parent_surf = surface
        self.pos = pos
        self.size = size
        self.active = True
        self.clickable = True

        # Absolute position on the screen
        self.__parent_screen_pos = parent_pos
        self.screen_pos = (parent_pos[0] + self.pos[0], parent_pos[1] + self.pos[1])

        # Scroll
        self.can_scroll = False
        self.total_scroll_amout = 0

        # Frames
        self.frames: "list[scrollable_frame_piece.FramePiece]" = []
        self.frames_gap = frames_gap
        self.first_frame_h = 0

        # Surfaces
        self.surface = self.__redraw_surface()
        self.scroll_bar_surf = self.__redraw_scrollbar_surface()

        # This doesn't actually work, it's just needed for PopupContents to work
        self.border_w = 0



    def __redraw_surface(self) -> pygame.surface.Surface:
        surface = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
        surface.fill((255,0,0,0))
        return surface
    
    def __redraw_scrollbar_surface(self) -> pygame.surface.Surface:
        if not self.can_scroll:
            alpha = 0
            scrollbar_h = self.size[1]
        else:
            alpha = 100
            scrollbar_h = self.size[1] * self.size[1] / self.__get_scrollables_height()


        surface = pygame.Surface((10, scrollbar_h), pygame.SRCALPHA, 32).convert_alpha()
        surface.fill((0,0,0,alpha))

        return surface


    def __update_frames_scroll_pos(self, scroll_change) -> None:
        for _frame in self.frames:
            _frame.pos = (_frame.pos[0], _frame.pos[1] + scroll_change)


    def __set_frames_scroll_pos(self, scroll) -> None:
        for _i, _frame in enumerate(self.frames):
            _frame.pos = (_frame.pos[0], 
                          self.first_frame_h + _i * (_frame.size[1] + self.frames_gap) + scroll)  
            

    def __update_can_scroll(self) -> None:
        height = self.__get_scrollables_height()
        self.can_scroll = True if height > self.size[1] else False


    def __get_scrollables_height(self) -> int:
        if not self.frames: return 0
        
        return (len(self.frames) * (self.frames[0].size[1] + self.frames_gap))


    def __fix_scroll_outofbounds(self) -> None:
        if not self.can_scroll: 
            self.total_scroll_amout = 0
            self.__set_frames_scroll_pos(self.total_scroll_amout)
            return

        bottom_bound = -(self.__get_scrollables_height() - self.size[1] + 10)

        if self.total_scroll_amout > 0:
            self.total_scroll_amout = 0
            self.__set_frames_scroll_pos(self.total_scroll_amout)
        if self.total_scroll_amout < bottom_bound:
            self.total_scroll_amout = bottom_bound
            self.__set_frames_scroll_pos(self.total_scroll_amout)



    def __scroll(self, direction) -> None:
        """Direction being -1 (up) or 1 (down) """
        scroll = direction * ScrollableFrame.SCROLL_SPEED

        bottom_bound = -(self.__get_scrollables_height() - self.size[1] + 10)

        # Baundaries

        if not self.can_scroll: return
        self.__fix_scroll_outofbounds()

        if self.total_scroll_amout + scroll > 0: 
            # If full scroll is too much, scroll what only what is needed
            scroll = -self.total_scroll_amout  
        if self.total_scroll_amout + scroll < bottom_bound: 
            # If full scroll is too much, scroll what only what is needed
            scroll = -self.total_scroll_amout + bottom_bound

        self.__update_frames_scroll_pos(scroll)

        self.total_scroll_amout += scroll

    # PUBLIC ----------------------------------------------------
    def delete_frame(self, frame: scrollable_frame_piece.FramePiece):
        self.frames.remove(frame)

        # Shift all remaining frames to start from the top
        for _i, _frame in enumerate(self.frames):
            _frame.pos = (_frame.pos[0], 
                          self.first_frame_h + _i * (frame.size[1] + self.frames_gap) + self.total_scroll_amout)
        
        self.__update_can_scroll()
        self.__fix_scroll_outofbounds()


    def set_scroll(self, amount: int) -> None:
        if not self.can_scroll: return

        self.total_scroll_amout = amount
        self.__fix_scroll_outofbounds()
        self.__set_frames_scroll_pos(self.total_scroll_amout)

    def add_scroll(self, amount: int) -> None:
        if not self.can_scroll: return

        self.total_scroll_amout += amount
        self.__fix_scroll_outofbounds()
        self.__set_frames_scroll_pos(self.total_scroll_amout)


    def disable_clicking(self) -> None:
        self.clickable = False


    def reactivate(self, new_surf: "pygame.Surface") -> None:
        self.__init__(new_surf, self.pos, self.size, self.__parent_screen_pos)


    def add_frame(self, frame: scrollable_frame_piece.FramePiece) -> None:
        index = len(self.frames)
        if index == 0:
            self.first_frame_h = frame.pos[1]
        frame.pos = (frame.pos[0], 
                     frame.pos[1] + index * (frame.size[1] + self.frames_gap) + self.total_scroll_amout)
        
        self.frames.append(frame)
        self.__update_can_scroll()


    def create_frame(self) -> None:
        font = pygame.font.Font(None, 35)
        frame = scrollable_frame_piece.FramePiece(self, (10,10), (480, 50))

        mapname = f"Tilemap {len(self.frames) + 1}"
        test_text = font.render(mapname, True, (0,0,0))

        frame.add_surface(test_text, (0,0), anchor=constants.CENTER)

        load_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Load", 25)
        trash_button = button.ImageButton(frame.frame_base, (0,0), (35,35), "Assets\\trash.png")
        frame.add_button(load_button, (0.05, 0.0), RunnableFunc(ScrollableFrame.load_btn_onclick_test, args=[f"Tilemaps\\{mapname}"]), anchor=constants.LEFT)
        frame.add_button(trash_button, (-0.05, 0.0), RunnableFunc(self.delete_frame, args=[frame]), anchor=constants.RIGHT)

        self.add_frame(frame)


    def load_btn_onclick_test(map_path: str) -> None:
        print("Load", map_path)


    def update(self) -> None:
        self.surface = self.__redraw_surface()
        self.scroll_bar_surf = self.__redraw_scrollbar_surface()

        for _frame in self.frames:
            _frame.update()

        self.__fix_scroll_outofbounds()

        self.parent_surf.blit(self.surface, self.pos)

        scrollbar_y = self.pos[1] + (-self.total_scroll_amout * self.size[1]) / self.__get_scrollables_height() if self.can_scroll else self.pos[1]
        self.parent_surf.blit(self.scroll_bar_surf, (self.pos[0] + self.size[0], scrollbar_y))


    def on_mousebuttondown(self, event: pygame.event.Event) -> None:
        if not self.clickable: return

        for _frame in self.frames:
            _frame.on_mousebuttondown(event)

        if event.button == 4:
            self.__scroll(1)
        elif event.button == 5:
            self.__scroll(-1)
    
    def on_keydown(self, event: pygame.event.Event) -> None:
        pass # Used for popup add_class

    def on_destroy(self) -> None:
        pass

    def on_deactivate(self, int1, int2=3) -> None:
        print("Frame ondestroy:", int1, int2)
        self.active = False