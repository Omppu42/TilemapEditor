import pygame
import export, import_map, grid_resize
from util.tkinter_opener import tk_util

import ui
import palette
import settings.data as data
import input_overrides

pygame.init()

class DropDown():
    def __init__(self, color_menu, color_option, pos_size, font, main, options):
        """pos_size being a vector4 x y w h"""
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(pos_size)
        self.font = font
        self.main = main

        self.options = {}

        for key, option in options.items():
            # Only function given
            if callable(option):
                self.options[key] = (option, [], {})
            # Function and args given
            elif len(option) == 2:
                self.options[key] = (option[0], option[1], {})
            # Function, args and kwargs given
            elif len(option) == 3:
                self.options[key] = (option[0], option[1], option[2])
            # Error
            else:
                assert False, f"Dropdown options dict had a value that was an invalid length ({len(option)})"



        self.draw_menu = False
        self.menu_active = False
        self.mouse_on = False #cursor on dropdown menu
        self.active_option = -1

    @classmethod
    def from_defaults(cls, defaults, **kwargs):
        # Merge provided kwargs with defaults
        merged_args = {**defaults, **kwargs}
        return cls(
            merged_args['color_menu'],
            merged_args['color_option'],
            merged_args['pos_size'],
            merged_args['font'],
            merged_args['main'],
            merged_args['options']
        )


    def draw(self, surf):
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        main_text = self.font.render(self.main, True, (0, 0, 0))
        surf.blit(main_text, main_text.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options.keys()):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect)
                main_text = self.font.render(text, True, (0, 0, 0))
                surf.blit(main_text, main_text.get_rect(center = rect.center))


    def check_clicked(self,):
        """Returns the index of which option was clicken. -1 If no option selected"""
        event_list = input_overrides.get_event_list()

        self.drawing = self.menu_active or self.draw_menu

        mouse_pos = input_overrides.get_mouse_pos()
        self.menu_active = self.rect.collidepoint(mouse_pos)
        
        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mouse_pos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and input_overrides.get_mouse_pressed()[0]:
                # If clicked on the topmost bar, open the dropdown
                if self.menu_active:
                    # Toggle draw_menu
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    # If clicken on an option
                    self.draw_menu = False
                    return self.active_option
        return -1
    

    def update(self) -> None:
        clicked_on_option = self.check_clicked()

        if clicked_on_option == -1: return

        # convert the values of a dict to list so we can access the nth value
        option_func = list(self.options.values())[clicked_on_option]

        # Run the function that was assigned to the option clicked on
        option_func[0](*option_func[1], **option_func[2])

    


COLOR_INACTIVE = (200, 200, 200)
COLOR_ACTIVE = (240, 240, 240)
COLOR_LIST_INACTIVE = (180, 180, 180)
COLOR_LIST_ACTIVE = (220, 220, 220)

def create_dropdowns() -> list:
    defaults = {"color_menu" : [COLOR_INACTIVE, COLOR_ACTIVE],
                "color_option" : [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
                "font" : data.font_25,}


    dropdowns = []

    dropdowns.append( DropDown.from_defaults(
        defaults,
        pos_size=(5, 0, 140, 30), 
        main="Tilemap", 
        options={"Load"   : (import_map.i_obj.import_tilemap), 
                 "Export" : (tk_util.queue_func, [export.export_tilemap]),
                 "New"    : (import_map.import_empty_map)} ))  #funcs, args

    dropdowns.append( DropDown.from_defaults(
        defaults,
        pos_size=(150, 0, 125, 30), 
        main="Palette", 
        options={"Load"   : (tk_util.queue_func, [palette.pm_obj.change_palette_ask]), 
                 "New"    : (tk_util.queue_func, [palette.pm_obj.create_empty_palette]), 
                 "Delete" : (tk_util.queue_func, [palette.pm_obj.delete_palette])} ))

    dropdowns.append( DropDown.from_defaults(
        defaults,
        pos_size=(280, 0, 125, 30), 
        main="Tiles", 
        options={"New Tile" : (tk_util.queue_func, [palette.pm_obj.add_tile]), 
                 "Remove"   : (ui.ui_obj.toggle_delete)} ))

    dropdowns.append( DropDown.from_defaults(
        defaults,
        pos_size=(410, 0, 125, 30), 
        main="Grid", 
        options={"Resize" : (grid_resize.gr_obj.grid_resize_popup)} ))
    
    return dropdowns


dropdowns: "list[DropDown]" = []

def init_dropdowns() -> None:
    global dropdowns
    dropdowns = create_dropdowns()