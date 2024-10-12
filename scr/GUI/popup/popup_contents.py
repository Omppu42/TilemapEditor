import pygame

import GUI.button as button
import GUI.input_field as input_field
import GUI.popup.popup_window as popup_window

import mouse

class PopupContents:
    """An object that holds any other pygame objects. Think of it like a canvas that things can be added to and cofigured"""
    def __init__(self, popup: "popup_window.PopupWindow", pos: tuple, size: tuple, color: tuple=(200,200,200)) -> None:
        """parent_pos being the position of the parent on the screen, pos being relative to parent surface"""
        self.parent = popup
        #self.pos = pos
        self.pos = (pos[0] + popup.border_w, 
                    pos[1] + popup.border_w + popup_window.PopupWindow.TOP_BAR_H)
        
        self.size = size
        self.frame_base = pygame.Surface(size)
        self.frame_base.fill(color)

        # Absolute position on the screen
        self.screen_pos = (self.parent.pos[0] + self.pos[0], self.parent.pos[1] + self.pos[1]) # Updated in update()
        
        self.buttons: "list[tuple[button.Button, tuple, tuple[function, list, dict]]]" = []  # [(ButtonClass, (relx, rely), (onclickfunc, args, kwargs)), (ButtonClass, (relx, rely), onclickfunc, (args, kwargs))]
        self.input_fields: "list[input_field.NumberInputField]" = []   #list of tuples containing a NumberInputField class and a rel position

    def add_surface(self, surface: pygame.Surface, center_pos_rel: tuple) -> None:
        """center_pos_rel being the relative (0 to 1) distance of the whole size in x and y, starting from top left corner"""
        rect = surface.get_rect(center=(center_pos_rel[0]*self.size[0], 
                                        center_pos_rel[1]*self.size[1]))


        self.frame_base.blit(surface, rect)

    def add_surface_non_center(self, surface: pygame.Surface, topleft_pos_rel: tuple) -> None:
        """topleft_pos_rel being the relative (0 to 1) distance of the whole size in x and y, starting from top left corner"""

        self.frame_base.blit(surface, (topleft_pos_rel[0]*self.size[0], 
                                      topleft_pos_rel[1]*self.size[1]))

    def add_button(self, button: button.Button, pos_rel: tuple, on_click_func: "function", on_click_func_args: list=[], on_click_func_kwargs:dict={}) -> None:
        """pos_rel being the relative (0 to 1) distance of the whole size in x and y, starting from top left corner"""
        self.buttons.append((button, (pos_rel[0]*self.size[0], 
                                      pos_rel[1]*self.size[1]),
                                      (on_click_func, on_click_func_args, on_click_func_kwargs)))

    def add_number_input_field(self, field: "input_field.NumberInputField", pos_rel: tuple) -> None:
        field.pos = (pos_rel[0] * self.size[0], 
                     pos_rel[1] * self.size[1])

        self.input_fields.append(field)


    def update(self) -> None:
        self.screen_pos = (self.parent.pos[0] + self.pos[0], self.parent.pos[1] + self.pos[1])

        for _button, _rel_pos, _ in self.buttons:
            _button.pos = _rel_pos
            _button.update(rect_override=pygame.rect.Rect(self.screen_pos[0] + _rel_pos[0], 
                                                          self.screen_pos[1] + _rel_pos[1],
                                                          _button.size[0], _button.size[1]),
                            boundaries   =pygame.rect.Rect(self.parent.pos, self.parent.size))

        for _field in self.input_fields:
            _field.draw(self.frame_base)

        self.parent.surface.blit(self.frame_base, self.pos)

    
    def on_mousebuttondown(self, event) -> None:
        if not self.parent.active: return
        if not mouse.get_pressed_override()[0]: return

        for _field in self.input_fields:
            _field.on_left_mouse_click(rect_override=pygame.rect.Rect(self.screen_pos[0] + _field.pos[0], 
                                                                      self.screen_pos[1] + _field.pos[1],
                                                                      _field.size[0], _field.size[1]),
                                        boundaries   =pygame.rect.Rect(self.parent.pos, self.parent.size))

        for _btn, _rel_pos, _func in self.buttons:
            if _btn.check_clicked(rect_override=pygame.rect.Rect(self.screen_pos[0] + _rel_pos[0], 
                                                                 self.screen_pos[1] + _rel_pos[1],
                                                                 _btn.size[0], _btn.size[1]),
                                    boundaries   =pygame.rect.Rect(self.parent.pos, self.parent.size)):
                _func[0](*_func[1], **_func[2])


    def on_keydown(self, event) -> None:
        for _field in self.input_fields:
            _field.on_keydown(event)