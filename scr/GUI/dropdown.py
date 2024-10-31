import pygame

from settings import data
from util.util import RunnableFunc

import input_overrides

pygame.init()

class DropDown():
    COLOR_INACTIVE = (200, 200, 200)
    COLOR_ACTIVE = (240, 240, 240)
    COLOR_LIST_INACTIVE = (180, 180, 180)
    COLOR_LIST_ACTIVE = (220, 220, 220)

    def __init__(self, pos_size, main, options, font=data.font_25, color_menu=[COLOR_INACTIVE, COLOR_ACTIVE], color_option=[COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE]):
        """pos_size being a vector4 x y w h"""
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(pos_size)
        self.font = font
        self.main = main

        self.options: "dict[str, RunnableFunc]" = {}
        self.options_texts: "list[str]" = []

        for key, option in options.items():
            if not isinstance(option, RunnableFunc) and callable(option):
                self.options[key] = RunnableFunc(option)
            elif isinstance(option, RunnableFunc):
                self.options[key] = option
            else:
                assert False, f"Dropdown options dict had a value that was invalid. Must be a function or RunnableFunc class instance ({key}: {option})"

        for text in self.options.keys():
            self.options_texts.append(text)


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
            for i, text in enumerate(self.options_texts):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                main_text = self.font.render(text, True, (0, 0, 0))
                
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect)
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

        if clicked_on_option != -1: 
            key = self.options_texts[clicked_on_option]
            self.options[key].run_function()