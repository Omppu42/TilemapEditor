import pygame
import export, import_map, grid_resize
from tkinter_opener import tk_util

import ui
import palette
import data

pygame.init()

class DropDown():
    def __init__(self, color_menu, color_option, pos_size, font, main, options):
        """pos_size being a vector4 x y w h"""
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(pos_size)
        self.font = font
        self.main = main
        self.options = options
        #self.options = list(options.keys())
        # self.functions = list(options.values())


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
        msg = self.font.render(self.main, True, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options.keys()):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, True, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center = rect.center))

    def update(self, event_list):
        self.drawing = self.menu_active or self.draw_menu
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1
    


COLOR_INACTIVE = (200, 200, 200)
COLOR_ACTIVE = (240, 240, 240)
COLOR_LIST_INACTIVE = (180, 180, 180)
COLOR_LIST_ACTIVE = (220, 220, 220)

def create_dropdowns() -> list:
    # for multiple args into function, wrap them into ()
    # options={"Load"   : (tk_util.queue_func, [import_map.import_tilemap]),                    ---No args. Invoke function import_map.import_tilemap() using tk_util.queue_func [timer]
    #          "Export" : (tk_util.queue_func, [export.export_tilemap, (1, 3)])} ))             ---2 args.  Invoke function export.export_tilemap(1, 3) using tk_util.queue_func [timer]
    

    defaults = {"color_menu" : [COLOR_INACTIVE, COLOR_ACTIVE],
                "color_option" : [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
                "font" : data.font_25,}


    dropdowns = []

    dropdowns.append( DropDown.from_defaults(
        defaults,
        pos_size=(5, 0, 140, 30), 
        main="Tilemap", 
        options={"Load"   : (tk_util.queue_func, [import_map.import_tilemap]), 
                 "Export" : (tk_util.queue_func, [export.export_tilemap])} ))  #funcs, args

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
        options={"Resize" : (tk_util.queue_func, [grid_resize.set_gridsize_ask])} ))
    
    return dropdowns