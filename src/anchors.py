import pygame


# PYGAME RECT ALIGNMENT
# Converted to rect 
UL      = 100
UP      = 101
UR      = 102
RIGHT   = 103
BR      = 104
BOTTOM  = 105
BL      = 106
LEFT    = 107
CENTER  = 108

ANCHORS = [
    UL, 
    UP,    
    UR,    
    RIGHT, 
    BR,    
    BOTTOM,
    BL,    
    LEFT,  
    CENTER
]


def get_rect_anchor(surface: "pygame.Surface", pos: tuple, anchor: int) -> "pygame.Rect":
    assert anchor in ANCHORS, f"Anchor id ({anchor}) not found in ANCHORS"

    if anchor == UL:
        return surface.get_rect(topleft=(pos))
    elif anchor == UP:
        return surface.get_rect(midtop=(pos))
    elif anchor == UR:
        return surface.get_rect(topright=(pos))
    elif anchor == RIGHT:
        return surface.get_rect(midright=(pos))
    elif anchor == BR:
        return surface.get_rect(bottomright=(pos))
    elif anchor == BOTTOM:
        return surface.get_rect(midbottom=(pos))
    elif anchor == BL:
        return surface.get_rect(bottomleft=(pos))
    elif anchor == LEFT:
        return surface.get_rect(midleft=(pos))
    elif anchor == CENTER:
        return surface.get_rect(center=(pos))
        
    raise ValueError(f"Anchor was in ANCHORS but failed to match in the code aboce. Anchor id {anchor}")


def get_anchor_pos_from_rect(rect: "pygame.Rect", anchor: int) -> tuple:
    """Gets the rects anchor position, for example rects UP position. Position being relative (ie, topleft is (0, 0))"""
    assert anchor in ANCHORS, f"Anchor id ({anchor}) not found in ANCHORS"

    w, h = rect.size

    if anchor == UL:
        return (0, 0)
    elif anchor == UP:
        return (w//2, 0)
    elif anchor == UR:
        return (w, 0)
    elif anchor == RIGHT:
        return (w, h//2)
    elif anchor == BR:
        return (w, h)
    elif anchor == BOTTOM:
        return (w//2, h)
    elif anchor == BL:
        return (0, h)
    elif anchor == LEFT:
        return (0, h//2)
    elif anchor == CENTER:
        return (w//2, h//2)

    raise ValueError(f"Anchor was in ANCHORS but failed to match in the code aboce. Anchor id {anchor}")