import pygame
import export, import_map
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

def create_lists(ui) -> list:
    lists = []

    lists.append( DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    5, 0, 140, 30, 
    pygame.font.Font(None, 25), 
    "Tilemap", 
    ["Load", "Export"],
    [(import_map.import_tilemap, [ui]), (export.export_tilemap, [ui])]))  #funcs, args, kwargs

    lists.append( DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    150, 0, 125, 30, 
    pygame.font.Font(None, 25), 
    "Palette", 
    ["Load", "New", "Delete"],
    [(ui.manager.palette_manager.change_palette_ask), (ui.manager.palette_manager.create_empty_palette), (ui.manager.palette_manager.delete_palette)]))  #funcs, args, kwargs

    lists.append( DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    280, 0, 125, 30, 
    pygame.font.Font(None, 25), 
    "Tiles", 
    ["Add", "Remove"],
    [(ui.manager.palette_manager.add_tile), (ui.toggle_delete)]))  #funcs, args, kwargs
    
    return lists