import pygame, os

from util.util import timer
from util.util_logger import logger
from util.util import RunnableFunc
from util import util

from . import tilemap_util
from . import ie_interface

import GUI.button as button
from GUI import popup

import settings.data as data
import settings.settings as settings
import ui
import palette
import manager
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
        self.confirm_popup = None

        logger.debug("Initialized Palette Loader")


    def start_palette_import(self) -> None:
        """Call to start the palette loader popup sequence"""
        self.make_import_popup()


    def make_import_popup(self):
        if self.confirm_popup:
            self.confirm_popup.close_popup()

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
            self.create_frame(_p)


    def create_frame(self, path) -> None:
        frame = popup.FramePiece(self.scrollable, (10,10), (480, 50))

        mapname = os.path.basename(path)
        name_text = data.font_25.render(mapname, True, (0,0,0))

        frame.add_surface(name_text, (0.05, 0), anchor=anchors.CENTER)

        load_button = button.TextButton(frame.frame_base, (0,0), (80, 35), "Load", 25)
        trash_button = button.ImageButton(frame.frame_base, (0,0), (35,35), "Assets\\trash.png")
        
        frame.add_button(load_button, (-0.4, 0), RunnableFunc(self.on_load_click, args=[path]), anchor=anchors.CENTER)
        frame.add_button(trash_button, (-0.015, 0), RunnableFunc(self.confirm_delete_frame, args=[frame, path]), anchor=anchors.RIGHT)

        self.scrollable.add_frame(frame)


    def confirm_delete_frame(self, frame_to_delete: "popup.FramePiece", palette_path: str) -> None:
        popup_size = (400, 340)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 
                     settings.SCR_H//2 - popup_size[1]//2)

        self.confirm_popup = popup.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)

        frame = popup.PopupContents(self.confirm_popup, (10,10), (popup_size[0] - 20, popup_size[1] - 60))

        palette_name = os.path.basename(palette_path)
        confirm_text_1 = util.pygame_different_color_text(data.font_30, ["Are you sure you want to ", "DELETE"], [(0,0,0), (200,00,00)])
        confirm_text_2 = data.font_30.render(f"'{palette_name}'?", True, (0,0,0))
        confirm_text_3 = data.font_25.render(f"The palette can be recovered from", True, (0,0,0))
        confirm_text_4 = data.font_25.render(f"'{settings.DELETED_PALETTES_PATH}'.", True, (0,0,0))

        yes_button =    button.TextButton(frame.frame_base, (0,0), (100, 35), "DELETE", 25, hover_col=(200,0,0))
        cancel_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Cancel", 25)

        frame.add_surface(confirm_text_1, (0.0,0.2), anchor=anchors.UP)
        frame.add_surface(confirm_text_2, (0.0,0.3), anchor=anchors.UP)

        frame.add_surface(confirm_text_3, (0.0,0.5), anchor=anchors.UP)
        frame.add_surface(confirm_text_4, (0.0,0.6), anchor=anchors.UP)

        frame.add_button(yes_button,    (-0.17, -0.05), RunnableFunc(self.delete_palette_confirmed, args=[frame_to_delete, palette_path]), anchor=anchors.BOTTOM)
        frame.add_button(cancel_button, ( 0.17, -0.05), RunnableFunc(self.confirm_popup.close_popup), anchor=anchors.BOTTOM)

        self.confirm_popup.add_contents_class(frame)


    def delete_palette_confirmed(self, frame_to_delete: "popup.FramePiece", palette_path: str) -> None:
        deleted_active_palette = (palette.pm_obj.current_palette == palette_path)

        self.scrollable.delete_frame(frame_to_delete)
        palette.pm_obj.delete_palette(palette_path)
        
        if deleted_active_palette:
            self.import_tools.import_empty_map()

        self.confirm_popup.close_popup()


    def on_load_click(self, palette_path: str) -> None:
        popup.popup_window.popup_m_obj.close_popup(self.popup)
        self.scrollable.disable_clicking()
        
        if palette_path == palette.pm_obj.current_palette.path:
            return
        
        ie_interface.Iie_obj.save_tilemap_quiet()

        result = palette.pm_obj.change_palette(palette_path)
        if result == 0:
            logger.error(f"Error while loading palette at path '{palette_path}'")

        ie_interface.Iie_obj.import_empty_map()


pl_obj: PaletteLoader = None

def create_palette_loader(screen):
    global pl_obj
    pl_obj = PaletteLoader(screen)