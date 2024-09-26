import pygame
import export, import_map, grid_resize
from tkinter_opener import tk_util

import ui
import palette

pygame.init()

class DropDown():
    def __init__(self, color_menu, color_option, x, y, w, h, font, main, options, functions):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.main = main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.functions = functions
        self.mouse_on = False #cursor on dropdown menu
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, True, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
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
    # (tk_util.queue_func, [import_map.import_tilemap, ui])             --- 1 arg to the import_map.import_tilemap function: ui
    # (tk_util.queue_func, [import_map.import_tilemap, (ui, example)])  --- 2 arg to the import_map.import_tilemap function: (ui, example)
    
    #TODO: Set some values as defaluts to avoid repeated code

    dropdowns = []

    dropdowns.append( DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    5, 0, 140, 30, 
    pygame.font.Font(None, 25), 
    "Tilemap", 
    ["Load", "Export"],
    [(tk_util.queue_func, [import_map.import_tilemap]), 
     (tk_util.queue_func, [export.export_tilemap])]))  #funcs, args

    dropdowns.append( DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    150, 0, 125, 30, 
    pygame.font.Font(None, 25), 
    "Palette", 
    ["Load", "New", "Delete"],
    [(tk_util.queue_func, [palette.pm_obj.change_palette_ask]), 
     (tk_util.queue_func, [palette.pm_obj.create_empty_palette]), 
     (tk_util.queue_func, [palette.pm_obj.delete_palette])]))

    dropdowns.append( DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    280, 0, 125, 30, 
    pygame.font.Font(None, 25), 
    "Tiles", 
    ["New Tile", "Remove"],
    [(tk_util.queue_func, [palette.pm_obj.add_tile]), 
     (ui.ui_obj.toggle_delete)]))

    dropdowns.append( DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    410, 0, 125, 30, 
    pygame.font.Font(None, 25), 
    "Grid", 
    ["Resize"],
    [ (tk_util.queue_func, [grid_resize.set_gridsize_ask]) ]))
    
    return dropdowns