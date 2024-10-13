import pygame

__mouse_clicked = [False, False, False]
__mouse_pos     = (0, 0)
__event_list    = []


def frame_start_update(event_list) -> None:
    """Run at the start of the frame"""
    global __mouse_clicked, __mouse_pos, __event_list

    __mouse_clicked = pygame.mouse.get_pressed()
    __mouse_pos = pygame.mouse.get_pos()
    __event_list = event_list



def clear_mouse_pressed() -> None:
    """Set pygame.mouse.get_pressed() to all False for this frame"""
    global __mouse_clicked
    __mouse_clicked = [False, False, False]


def get_mouse_pressed() -> list:
    """This function returns pygame.mouse.get_pressed(), but the values are modified for layer-like functionality for clicking"""
    global __mouse_clicked
    return __mouse_clicked


def clear_mouse_pos() -> None:
    """Set mouse pos to a value outside the screen for this frame"""
    global __mouse_pos
    __mouse_pos = (-1000, -1000)

def get_mouse_pos() -> tuple:
    """This function returns pygame.mouse.get_pos(), but the values are modified for layer-like functionality for clicking"""
    global __mouse_pos
    return __mouse_pos


def get_event_list() -> list:
    global __event_list
    return __event_list

def remove_event(event: "pygame.event.Event") -> None:
    global __event_list
    __event_list.remove(event)