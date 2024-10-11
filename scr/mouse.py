import pygame

__mouse_clicked = [False, False, False]
__mouse_pos     = (0, 0)


def frame_start_update() -> None:
    """Run at the start of the frame"""
    global __mouse_clicked, __mouse_pos

    __mouse_clicked = pygame.mouse.get_pressed()
    __mouse_pos = pygame.mouse.get_pos()



def clear_pressed_override() -> None:
    """Set pygame.mouse.get_pressed() to all False for this frame"""
    global __mouse_clicked
    __mouse_clicked = [False, False, False]


def get_pressed_override() -> list:
    """This function returns pygame.mouse.get_pressed(), but the values are modified for layer-like functionality for clicking"""
    global __mouse_clicked
    return __mouse_clicked


def clear_pos_override() -> None:
    """Set mouse pos to a value outside the screen for this frame"""
    global __mouse_pos
    __mouse_pos = (-1000, -1000)

def get_pos_override() -> tuple:
    """This function returns pygame.mouse.get_pos(), but the values are modified for layer-like functionality for clicking"""
    global __mouse_pos
    return __mouse_pos