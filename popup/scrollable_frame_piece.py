import pygame

import button
import popup.scrollable_frame as scrollable_frame

class FramePiece:
    """An object that holds any other pygame objects. Think of it like a canvas that things can be added to and cofigured"""
    def __init__(self, scrollable_frame_obj: "scrollable_frame.ScrollableFrame", pos: tuple, size: tuple) -> None:
        """parent_pos being the position of the parent on the screen, pos being relative to parent surface"""
        self.parent = scrollable_frame_obj
        self.pos = pos
        self.size = size
        self.frame_base = pygame.Surface(size)
        self.frame_base.fill((200,200,200))

        # Absolute position on the screen
        self.screen_pos = (self.parent.screen_pos[0] + self.pos[0], self.parent.screen_pos[1] + self.pos[1]) # Updated in update()
        
        self.buttons: "list[tuple[button.Button, tuple, tuple[function, list, dict]]]" = []  # [(ButtonClass, (relx, rely), (onclickfunc, args, kwargs)), (ButtonClass, (relx, rely), onclickfunc, (args, kwargs))]

    def add_surface(self, surface: pygame.Surface, center_pos_rel: tuple) -> None:
        """center_pos_rel being the relative (0 to 1) distance of the whole size in x and y, starting from top left corner"""
        rect = surface.get_rect(center=(center_pos_rel[0]*self.size[0], 
                                        center_pos_rel[1]*self.size[1]))

        self.frame_base.blit(surface, rect)

    def add_button(self, button: button.Button, pos_rel: tuple, on_click_func: "function", on_click_func_args: list=[], on_click_func_kwargs:dict={}) -> None:
        """pos_rel being the relative (0 to 1) distance of the whole size in x and y, starting from top left corner"""
        self.buttons.append((button, (pos_rel[0]*self.size[0], 
                                      pos_rel[1]*self.size[1]),
                                      (on_click_func, on_click_func_args, on_click_func_kwargs)))

    def update(self) -> None:
        if not self.parent.active: return

        self.screen_pos = (self.parent.screen_pos[0] + self.pos[0], self.parent.screen_pos[1] + self.pos[1])

        for _button, _rel_pos, _ in self.buttons:
            _button.pos = _rel_pos
            _button.update(rect_override=pygame.rect.Rect(self.screen_pos[0] + _rel_pos[0], 
                                                                self.screen_pos[1] + _rel_pos[1],
                                                                _button.size[0], _button.size[1]),
                            boundaries   =pygame.rect.Rect(self.parent.screen_pos, self.parent.size))

        self.parent.surface.blit(self.frame_base, self.pos)

    
    def on_left_mouse_click(self) -> None:
        if not self.parent.active: return

        for _btn, _rel_pos, _func in self.buttons:
            if _btn.check_clicked(rect_override=pygame.rect.Rect(self.screen_pos[0] + _rel_pos[0], 
                                                                self.screen_pos[1] + _rel_pos[1],
                                                                _btn.size[0], _btn.size[1]),
                                    boundaries   =pygame.rect.Rect(self.parent.screen_pos, self.parent.size)):
                _func[0](*_func[1], **_func[2])
