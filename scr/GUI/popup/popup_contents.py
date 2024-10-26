import pygame

import GUI.button as button
from . import settings_popup
from . import popup_window
from GUI import input_field

import util.util as util
from util.util import RunnableFunc

import input_overrides
import constants

class ButtonStruct:
    def __init__(self, button: "button.Button", frame_pos: tuple, on_click_class: "RunnableFunc"):
        """Button being the button instance, frame_pos the position on the frame, on_click being the function to run when clicked"""
        self.btn = button
        self.frame_pos = frame_pos
        self.on_click_class = on_click_class

    

class PopupContents:
    """An object that holds any other pygame objects. Think of it like a canvas that things can be added to and cofigured"""
    def __init__(self, popup: "popup_window.PopupWindow", pos: tuple, size: tuple, color: tuple=(200,200,200)) -> None:
        """parent_pos being the position of the parent on the screen, pos being relative to parent surface"""
        self.parent = popup
        #self.pos = pos
        self.pos = (pos[0] + popup.border_w, 
                    pos[1] + popup.border_w + settings_popup.POPUP_TOPBAR_H)
        
        self.size = size
        self.frame_base = pygame.Surface(size)
        self.frame_base.fill(color)

        # Absolute position on the screen
        self.screen_pos = (self.parent.pos[0] + self.pos[0], self.parent.pos[1] + self.pos[1]) # Updated in update()
        
        self.buttons: "list[ButtonStruct]" = []  # [(ButtonClass, (relx, rely), (onclickfunc, args, kwargs)), (ButtonClass, (relx, rely), onclickfunc, (args, kwargs))]
        self.input_fields: "list[input_field.NumberInputField]" = []   #list of tuples containing a NumberInputField class and a rel position

    # PRIVATE -----------------
    def __get_anchor_position(self, surface: pygame.Surface, pos_rel: tuple, anchor: int) -> "pygame.Rect":
        
        size_w, size_h = surface.get_size()

        frame_anchor_xy = util.get_anchor_pos_from_rect(self.frame_base.get_rect(), anchor)

        surface_anchor_rect = util.get_rect_anchor(surface, 
                                                   (pos_rel[0]*self.size[0], 
                                                    pos_rel[1]*self.size[1]),
                                                   anchor)

        return pygame.Rect(frame_anchor_xy[0] + surface_anchor_rect.x,
                           frame_anchor_xy[1] + surface_anchor_rect.y,
                           size_w,
                           size_h)


    def __get_rect_override(self, pos_on_frame: tuple, rect_size: tuple) -> "pygame.Rect":
        return pygame.rect.Rect(self.screen_pos[0] + pos_on_frame[0], 
                                self.screen_pos[1] + pos_on_frame[1],
                                rect_size[0], rect_size[1])


    # PUBLIC ---------------
    def add_surface(self, surface: pygame.Surface, pos_rel: tuple, anchor=constants.UL) -> None:
        """center_pos_rel being the relative (0 to 1) distance of the whole size in x and y, starting from top left corner"""

        anchor_pos = self.__get_anchor_position(surface, pos_rel, anchor)

        self.frame_base.blit(surface, anchor_pos)


    def add_button(self, button: button.Button, pos_rel: tuple, on_click_func: "RunnableFunc", anchor=constants.UL) -> None:
        """pos_rel being the relative (0 to 1) distance of the whole size in x and y, starting from top left corner"""
        anchor_pos = self.__get_anchor_position(button.btn_surf, pos_rel, anchor)

        self.buttons.append(
            ButtonStruct(button, (anchor_pos.x, anchor_pos.y), on_click_func)
        )
        

    def add_input_field(self, field: "input_field.NumberInputField | input_field.TextInputField", pos_rel: tuple, anchor=constants.UL) -> None:
        anchor_pos = self.__get_anchor_position(field.surface, pos_rel, anchor)

        field.pos = anchor_pos

        self.input_fields.append(field)


    def update(self, screen_pos_override:tuple=None, parent_pos_override:tuple=None) -> None:
        """Screen_pos_override is for ScrollableFramePiece class"""
        parent_pos = self.parent.pos if parent_pos_override == None else parent_pos_override
        self.screen_pos = (parent_pos[0] + self.pos[0], parent_pos[1] + self.pos[1]) if screen_pos_override == None else screen_pos_override

        for _btn_struct in self.buttons:
            _btn_struct.btn.pos = _btn_struct.frame_pos

            _rect_override = self.__get_rect_override(_btn_struct.frame_pos, _btn_struct.btn.size)
            _boundaries = pygame.rect.Rect(parent_pos, self.parent.size)

            _btn_struct.btn.update(rect_override=_rect_override, 
                                   boundaries=_boundaries)


        for _field in self.input_fields:
            _field.draw(self.frame_base)

        self.parent.surface.blit(self.frame_base, self.pos)

    
    def on_mousebuttondown(self, event, parent_pos_override:tuple=None) -> None:
        if not self.parent.active: return
        if not input_overrides.get_mouse_pressed()[0]: return

        parent_pos = self.parent.pos if parent_pos_override == None else parent_pos_override

        for _field in self.input_fields:
            _rect_override = self.__get_rect_override(_field.pos, _field.size)
            _boundaries = pygame.rect.Rect(parent_pos, self.parent.size)

            _field.on_left_mouse_click(rect_override=_rect_override,
                                       boundaries=_boundaries)

        for _btn_struct in self.buttons:
            _rect_override = self.__get_rect_override(_btn_struct.frame_pos, _btn_struct.btn.size)
            _boundaries = pygame.rect.Rect(parent_pos, self.parent.size)

            if _btn_struct.btn.check_clicked(rect_override=_rect_override,
                                             boundaries=_boundaries):
                _btn_struct.on_click_class.run_function()


    def on_keydown(self, event) -> None:
        for _field in self.input_fields:
            _field.on_keydown(event)