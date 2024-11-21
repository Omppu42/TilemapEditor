import pygame

from typing import Any

from settings import settings
from GUI import button

from util.util import RunnableFunc

import anchors

from . import popup_contents
from . import popup_window



def __set_default_kwarg(kwargs: dict, key: str, default_value: Any) -> dict:
    """Place a new key in to kwargs if it is not already present"""
    given_value = kwargs.get(key, None)
    if given_value == None:
        kwargs[key] = default_value

    return kwargs

def __common_popup_base_two_buttons(screen: pygame.Surface, text_surface: pygame.Surface, on_yes_func: "function|RunnableFunc", **kwargs) -> None:
    popup_size = kwargs.get("size", (400, 300))
    popup_pos = kwargs.get("pos",  (settings.SCR_W//2 - 2*popup_size[0]//3, 
                                    settings.SCR_H//2 - popup_size[1]//2))
    
    popup_bg_color          = kwargs.get("bg_color", (120, 120, 120))
    popup_border_w          = kwargs.get("border_w", 2)
    popup_backdrop_depth    = kwargs.get("backdrop_depth", 10)
    topbar_bg_color         = kwargs.get("topbar_bg_color", (255, 255, 255))
    frame_color             = kwargs.get("frame_color", (200,200,200))

    main_popup = popup_window.PopupWindow(screen, popup_pos, popup_size, popup_bg_color, topbar_bg_color, border_w=popup_border_w, backdrop_depth=popup_backdrop_depth)
    frame = popup_contents.PopupContents(main_popup, (10,10), (popup_size[0] - 20, popup_size[1] - 60), color=frame_color)    

    yes_button = button.TextButton(frame.frame_base, (0,0), (100, 35), kwargs.get("yes_button_text", "Yes"), 25, hover_col=kwargs.get("yes_button_hover_color", None))
    no_button  = button.TextButton(frame.frame_base, (0,0), (100, 35), kwargs.get("no_button_text", "No"), 25,   hover_col=kwargs.get("no_button_hover_color", None))

    frame.add_surface(text_surface, (0.0, kwargs.get("text_rel_y", -0.1)), anchor=anchors.CENTER)

    if kwargs.get("additional_on_yes_funcs", None):
        funcs = kwargs["additional_on_yes_funcs"]
        for func in funcs:
            yes_button.add_onclick_func(func)

    if kwargs.get("close_on_yes", True):
        yes_button.add_onclick_func(main_popup.close_popup)

    if kwargs.get("on_close_func", None):
        no_button.add_onclick_func(kwargs["on_close_func"])

    frame.add_button(yes_button, (-0.17, -0.05), on_yes_func, anchor=anchors.BOTTOM)
    frame.add_button(no_button,  ( 0.17, -0.05), main_popup.close_popup, anchor=anchors.BOTTOM)

    main_popup.add_contents_class(frame)


def __common_popup_base_three_buttons(screen: pygame.Surface, text_surface: pygame.Surface, on_save_func: "function|RunnableFunc", on_dont_save_func: "function|RunnableFunc", **kwargs) -> None:
    popup_size = kwargs.get("size", (400, 300))
    popup_pos = kwargs.get("pos",  (settings.SCR_W//2 - 2*popup_size[0]//3, 
                                    settings.SCR_H//2 - popup_size[1]//2))
    
    popup_bg_color          = kwargs.get("bg_color", (120, 120, 120))
    popup_border_w          = kwargs.get("border_w", 2)
    popup_backdrop_depth    = kwargs.get("backdrop_depth", 10)
    topbar_bg_color         = kwargs.get("topbar_bg_color", (255, 255, 255))
    frame_color             = kwargs.get("frame_color", (200,200,200))

    main_popup = popup_window.PopupWindow(screen, popup_pos, popup_size, popup_bg_color, topbar_bg_color, border_w=popup_border_w, backdrop_depth=popup_backdrop_depth)
    frame = popup_contents.PopupContents(main_popup, (10,10), (popup_size[0] - 20, popup_size[1] - 60), color=frame_color)    

    save_button         = button.TextButton(frame.frame_base, (0,0), (100, 35), kwargs.get("save_button_text", "Save"), 25, hover_col=kwargs.get("save_button_hover_color", None))
    dont_save_button    = button.TextButton(frame.frame_base, (0,0), (100, 35), kwargs.get("dont_save_button_text", "Don't save"), 25, hover_col=kwargs.get("dont_save_button_hover_color", (200, 0, 0)))
    cancel_button       = button.TextButton(frame.frame_base, (0,0), (100, 35), kwargs.get("cancel_button_text", "Cancel"), 25,   hover_col=kwargs.get("cancel_button_hover_color", None))

    frame.add_surface(text_surface, (0.0, kwargs.get("text_rel_y", -0.1)), anchor=anchors.CENTER)

    if kwargs.get("additional_on_save_funcs", None):
        funcs = kwargs["additional_on_save_funcs"]
        for func in funcs:
            save_button.add_onclick_func(func)

    if kwargs.get("on_cancel_func", None):
        cancel_button.add_onclick_func(kwargs["on_cancel_func"])

    if kwargs.get("on_dont_save_func", None):
        dont_save_button.add_onclick_func(kwargs["on_dont_save_func"])


    if kwargs.get("close_on_save", True):
        save_button.add_onclick_func(main_popup.close_popup)

    if kwargs.get("close_on_dont_save", True):
        dont_save_button.add_onclick_func(main_popup.close_popup)


    frame.add_button(save_button, (-0.32, -0.05),       on_save_func, anchor=anchors.BOTTOM)
    frame.add_button(dont_save_button,  ( 0.0,  -0.05), on_dont_save_func, anchor=anchors.BOTTOM)
    frame.add_button(cancel_button,  ( 0.32, -0.05),    main_popup.close_popup, anchor=anchors.BOTTOM)

    main_popup.add_contents_class(frame)



def create_yes_no_popup(screen: pygame.Surface, text_surface: pygame.Surface, on_yes_func: "function|RunnableFunc", **kwargs) -> None:
    __common_popup_base_two_buttons(screen, text_surface, on_yes_func, **kwargs)


def create_confirm_cancel_popup(screen: pygame.Surface, text_surface: pygame.Surface, on_yes_func: "function|RunnableFunc", **kwargs) -> None:
    kwargs = __set_default_kwarg(kwargs, "yes_button_text", "Confirm")
    kwargs = __set_default_kwarg(kwargs, "no_button_text", "Cancel")

    __common_popup_base_two_buttons(screen, text_surface, on_yes_func, **kwargs)


def create_save_dont_save_cancel_popup(screen: pygame.Surface, text_surface: pygame.Surface, on_save_func: "function|RunnableFunc", on_dont_save_func: "function|RunnableFunc", **kwargs) -> None:
    __common_popup_base_three_buttons(screen, text_surface, on_save_func, on_dont_save_func, **kwargs)