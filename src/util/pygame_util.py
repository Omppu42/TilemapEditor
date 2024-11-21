import pygame
from typing import Literal
from dataclasses import dataclass


@dataclass
class __TextRenderingStruct():
    text: str
    font: "pygame.font.Font"
    color:  tuple
    

def render_different_color_text(font: "pygame.font.Font", texts: "list[str]", colors: "list[tuple]") -> "pygame.Surface":
    """Adds different color texts together. Each list index of texts list corresponds with list index colors list."""
    _size = font.size("".join(texts))
    surf = pygame.Surface(_size).convert_alpha()
    surf.fill((255,255,255, 0))

    filled_to_x = 0

    for _text, _col in zip(texts, colors):
        _render = font.render(_text, True, _col)
        surf.blit(_render, (filled_to_x, 0))

        filled_to_x += _render.get_rect().w

    return surf



def __get_align_rect(parent_surface: "pygame.Surface", child_surface: "pygame.Surface", align:Literal['center', 'left', 'right'], next_render_height: int):
    """Helper function for render_multiline_text()"""
    child_size = child_surface.get_size()
    
    match align:
        case "center":
            pos = child_surface.get_rect(center=(parent_surface.get_size()[0] // 2,
                                        next_render_height + child_size[1] // 2))
        case "left":
            pos = child_surface.get_rect(midleft=(0,
                                        next_render_height + child_size[1] // 2))
        case "right":
            pos = child_surface.get_rect(midright=(parent_surface.get_size()[0],
                                        next_render_height + child_size[1] // 2))

    return pos


def render_multiline_text(text: str, 
                          font: "pygame.font.Font", 
                          color=(0,0,0), 
                          text_vertical_spacing=1, 
                          align:Literal['center', 'left', 'right']="center", 
                          linenum_to_font:dict={}, 
                          linenum_to_color:dict={},
                          insert_surface_after_line:dict={}) -> "pygame.Surface":
    """Split lines by using the \\n sign
    
       Linenum_to_font and linenum_to_color should {1 : font} where 1st line will be affected. This will override the default given"""
    text_vertical_spacing = text_vertical_spacing if text_vertical_spacing != 0 else 0.001
    VERTICAL_SPACE = font.size("Tg")[1] // (4 / text_vertical_spacing)
    splitted_strings = text.split("\n")

    # VALIDATE VALUES
    assert all([k >= 0 and k<=len(splitted_strings) for k in linenum_to_font]),  f"Invalid line num found in linenum_to_font. Negative or greater than linecount? (line count: {len(splitted_strings)})"
    assert all([k >= 0 and k<=len(splitted_strings) for k in linenum_to_color]), f"Invalid line num found in linenum_to_color. Negative or greater than linecount? (line count: {len(splitted_strings)})"

    insert_keys = list(insert_surface_after_line.keys())
    insert_keys.sort()

    for _i, _key in enumerate(insert_keys):
        assert _key >= 0 and _key <= len(splitted_strings) + _i, f"Invalid key {_key}. This position does not exist"

    # Create structs
    strings_with_properties_list: "list[__TextRenderingStruct]" = []

    for _i, _text in enumerate(splitted_strings):
        _font = font  if not _i + 1 in linenum_to_font  else linenum_to_font [_i + 1]
        _col  = color if not _i + 1 in linenum_to_color else linenum_to_color[_i + 1]

        strings_with_properties_list.append(__TextRenderingStruct(_text, _font, _col))


    # Get the height of the surface that needs to be
    height = 0
    # All different fonts
    for _font in linenum_to_font.values():
        height += _font.size("Tg")[1]

    for _surface in insert_surface_after_line.values():
        height += _surface.get_size()[1]

    # Default fonts
    height += font.size("Tg")[1] * (len(splitted_strings) - len(linenum_to_font.values()))
    # Spaces between lines
    height += VERTICAL_SPACE * (len(splitted_strings) - 1)

    # WIDTH
    width = 0
    for _surface in insert_surface_after_line.values():
        _new_w = _surface.get_size()[0]
        if _new_w > width:
            width = _new_w

    for data in strings_with_properties_list:
        _new_w = data.font.size(data.text)[0]
        if _new_w > width:
            width = _new_w

    # RENDERING
    surface = pygame.Surface((width, height)).convert_alpha()
    surface.fill((255,255,255, 0))

    next_render_height = 0

    # Render texts onto the surface
    for _i, _data in enumerate(strings_with_properties_list):
        # Check if manual surface insertion should happen
        if _i in insert_surface_after_line:
            _insert_surf = insert_surface_after_line[_i]
            _rect = __get_align_rect(surface, _insert_surf, align, next_render_height)
            surface.blit(_insert_surf, _rect)
            next_render_height += _insert_surf.get_size()[1] + VERTICAL_SPACE

        # Render the text normally
        _render = _data.font.render(_data.text, True, _data.color)
        _rect = __get_align_rect(surface, _render, align, next_render_height)
                
        surface.blit(_render, _rect)
        next_render_height += _render.get_size()[1] + VERTICAL_SPACE
        
    return surface