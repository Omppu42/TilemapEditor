import pygame


__mouse_clicked = [False, False, False]
__mouse_pos     = (0, 0)
__event_list    = []

__injected_events = []
__injected_next_frame_events = []
__injected_mousepos = (-1, -1)
__injected_mousepressed = [-1,-1,-1]


def frame_start_update(event_list) -> None:
    """Run at the start of the frame"""
    global __mouse_clicked, __mouse_pos, __event_list, __injected_events, __injected_mousepos, __injected_mousepressed, __injected_next_frame_events

    if __injected_mousepressed == [-1,-1,-1]:
        __mouse_clicked = pygame.mouse.get_pressed()
    else:
        __mouse_clicked = __injected_mousepressed
    
    if __injected_mousepos == (-1, -1):
        __mouse_pos = pygame.mouse.get_pos() 
    else:
        __mouse_pos = __injected_mousepos

    __event_list = event_list + __injected_events

    __injected_events = __injected_next_frame_events
    __injected_next_frame_events = []
    __injected_mousepos = (-1, -1)
    __injected_mousepressed = [-1,-1,-1]



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



def inject_event(event: "pygame.event.Event") -> None:
    global __injected_events
    __injected_events.append(event)

def inject_next_frame_event(event: "pygame.event.Event") -> None:
    global __injected_next_frame_events
    __injected_next_frame_events.append(event)

def inject_mousepos(mouse_pos: tuple) -> None:
    global __injected_mousepos
    __injected_mousepos = mouse_pos

def inject_mousepressed(pressed: "list"):
    assert len(pressed) == 3, "pressed len must be 3"

    global __injected_mousepressed
    __injected_mousepressed = pressed
