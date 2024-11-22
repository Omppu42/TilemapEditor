import pygame, os

from util.util_logger import logger
from util.util import RunnableFunc
from util import pygame_util

from . import ie_interface

import GUI.button as button
from GUI import popup
from GUI import input_field

import settings.data as data
import settings.settings as settings
import palette
import anchors

pygame.init()


class PaletteLoader():
    SELECTION_W = 500
    SELECTION_H = 160

    BTN_UNSELECTED_COLOR = "gray75"
    BTN_SELECTED_COLOR = "gray80"
    FRAME_BG = "gray60"
    FRAME_BG_2 = "gray70"
    
    def __init__(self, screen: "pygame.Surface") -> None:
        self.screen = screen
        self.popup = None
        self.scrollable = None

        logger.debug("Initialized Palette Loader")


    # PRIVATE ------
    def __make_import_popup(self):
        popup_size = (600, 510)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 50)
        scrollable_size = (500,440)

        self.popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)
        self.scrollable = popup.ScrollableFrame(self.popup.surface, popup_pos, (40, 50), scrollable_size)
        
        top_frame = popup.PopupContents(self.popup, (40,-40), (scrollable_size[0], 40), color=(0,0,0,0))
        text = data.font_35.render(f"Load a Palette", True, (150,150,150))
        top_frame.add_surface(text, (0.05,0.0), anchor=anchors.CENTER)

        self.popup.add_contents_class(self.scrollable)
        self.popup.add_contents_draw_func(top_frame.update)

        paths = palette.PaletteManager.get_all_palettes_paths()
        if settings.TESTS_PALETTE_PATH:
            paths.remove(settings.TESTS_PALETTE_PATH)

        for _p in paths:
            self.__create_frame(_p)


    def __create_frame(self, path) -> None:
        frame = popup.FramePiece(self.scrollable, (10,10), (480, 50))

        mapname = os.path.basename(path)
        name_text = data.font_25.render(mapname, True, (0,0,0))

        frame.add_surface(name_text, (0.05, 0), anchor=anchors.CENTER)

        load_button = button.TextButton(frame.frame_base, (0,0), (80, 35), "Load", data.font_25)
        trash_button = button.ImageButton(frame.frame_base, (0,0), (35,35), data.trash_image)
        
        frame.add_button(load_button, (-0.4, 0), RunnableFunc(self.__on_load_click, args=[path]), anchor=anchors.CENTER)
        frame.add_button(trash_button, (-0.015, 0), RunnableFunc(self.__confirm_delete_frame_popup, args=[frame, path]), anchor=anchors.RIGHT)

        self.scrollable.add_frame(frame)


    def __confirm_delete_frame_popup(self, frame_to_delete: "popup.FramePiece", palette_path: str) -> None:
        palette_name = os.path.basename(palette_path)

        multicolor_surface = pygame_util.render_different_color_text(data.font_30, ["Are you sure you want to ", "DELETE"], [(0,0,0), (200,00,00)])
        text_surface = pygame_util.render_multiline_text(f"'{palette_name}'?\n\nThe palette can be recovered from\n'{settings.DELETED_PALETTES_PATH}'.", data.font_25, 
                                                         linenum_to_font={1 : data.font_30},
                                                         insert_surface_after_line={0 : multicolor_surface})

        popup.create_confirm_cancel_popup(self.screen, text_surface, 
                                          RunnableFunc(self.__delete_palette_confirmed, args=[frame_to_delete, palette_path]),
                                          yes_button_text="DELETE",
                                          yes_button_hover_color=(200,0,0))


    def __delete_palette_confirmed(self, frame_to_delete: "popup.FramePiece", palette_path: str) -> None:
        deleted_active_palette = (palette.pm_obj.current_palette == palette_path)

        self.scrollable.delete_frame(frame_to_delete)
        palette.pm_obj.delete_palette(palette_path)
        
        if deleted_active_palette:
            self.import_tools.import_empty_map()


    def __on_load_click(self, palette_path: str) -> None:
        popup.popup_window.popup_m_obj.close_popup(self.popup)
        self.scrollable.disable_clicking()
        
        if palette_path == palette.pm_obj.current_palette.path:
            return
        
        ie_interface.Iie_obj.save_tilemap_quiet()

        result = palette.pm_obj.change_palette(palette_path)
        if result == 0:
            logger.error(f"Error while loading palette at path '{palette_path}'")

        ie_interface.Iie_obj.import_empty_map()


    def __new_palette_confirmed(self, name_getter: "function", frame: "popup.PopupContents") -> None:
        name = name_getter()
        if name == "":
            name = f"Palette_{len(palette.pm_obj.all_palettes) - 1}"

        conflict = any([n.name == name for n in palette.pm_obj.all_palettes])
        if conflict: 
            text = data.font_25.render(f"Palette name already taken", True, (0,0,0))
            frame.add_surface(text, (0.0,0.15), anchor=anchors.CENTER)
            return

        palette.pm_obj.create_empty_palette(custom_name=name, save_tilemap=True)
        self.popup.close_popup()


    # PUBLIC ----------------
    def start_palette_import(self) -> None:
        """Call to start the palette loader popup sequence"""
        self.__make_import_popup()


    def new_palette_popup(self) -> None:
        popup_size = (400, 340)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 
                     settings.SCR_H//2 - popup_size[1]//2)

        self.popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)

        frame = popup.PopupContents(self.popup, (10,10), (popup_size[0] - 20, popup_size[1] - 60))

        text = data.font_30.render(f"Create a new Palette", True, (0,0,0))
        text2 = data.font_25.render(f"Give it a name:", True, (0,0,0))

        name = input_field.TextInputField((0,0), (320, 40), 30, placeholder=f"Palette_{len(palette.pm_obj.all_palettes) - 1}", empty_return_val="placeholder", bg_color=(180,180,180), active_color=(190,190,190), border_width=1, font=data.font_30)

        yes_button =    button.TextButton(frame.frame_base, (0,0), (100, 35), "Create", data.font_25)
        cancel_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Cancel", data.font_25)

        frame.add_surface(text, (0.0,-0.3), anchor=anchors.CENTER)
        frame.add_surface(text2, (0.0,-0.2), anchor=anchors.CENTER)
        frame.add_input_field(name, (0,0), anchor=anchors.CENTER)

        frame.add_button(yes_button,    (-0.17, -0.05), RunnableFunc(self.__new_palette_confirmed, args=[name.get_value, frame]), anchor=anchors.BOTTOM)
        frame.add_button(cancel_button, ( 0.17, -0.05), RunnableFunc(self.popup.close_popup), anchor=anchors.BOTTOM)

        self.popup.add_contents_class(frame)


pl_obj: PaletteLoader = None

def create_palette_loader(screen):
    global pl_obj
    pl_obj = PaletteLoader(screen)