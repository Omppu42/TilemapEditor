import pygame

from GUI.popup import scrollable_frame
from GUI.popup import popup_contents


class FramePiece(popup_contents.PopupContents):
    """An object that holds any other pygame objects. Think of it like a canvas that things can be added to and cofigured"""
    def __init__(self, scrollable_frame_obj: "scrollable_frame.ScrollableFrame", pos: tuple, size: tuple, color: tuple=(200,200,200)) -> None:
        """parent_pos being the position of the parent on the screen, pos being relative to parent surface"""
        super().__init__(scrollable_frame_obj, pos, size, color=color)
        self.parent = scrollable_frame_obj
        self.pos = pos
        self.size = size

    def update(self) -> None:
        self.screen_pos = (self.parent.screen_pos[0] + self.pos[0], self.parent.screen_pos[1] + self.pos[1])

        super().update(screen_pos_override=self.screen_pos,
                       parent_pos_override=self.parent.screen_pos)
        
    def on_mousebuttondown(self, event: "pygame.event.Event") -> None:
        super().on_mousebuttondown(event, parent_pos_override=self.parent.screen_pos)