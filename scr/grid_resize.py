import pygame
import tkinter

import GUI.button as button
import GUI.popup.popup_window as popup_window
import GUI.popup.popup_contents as popup_contents
import GUI.popup.scrollable_frame as scrollable_frame
import GUI.popup.scrollable_frame_piece as scrollable_frame_piece
from GUI import input_field

from util.util_logger import logger
from util.util import RunnableFunc
import settings.settings as settings
import settings.data as data

import ui
import manager
import constants


class GridResizer:
    def __init__(self, screen):
        self.screen = screen
    
    def grid_resize_popup(self) -> None:
        logger.debug("Opening grid resize popup")
        popup_size = (400, 300)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 100)


        self.popup = popup_window.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)

        frame = popup_contents.PopupContents(self.popup, (10, 10), (popup_size[0] - 20, popup_size[1] - 60))

        current_w, current_h = ui.ui_obj.grid_size_rows_cols

        current_size_text = data.font_25.render(f"Current size: {current_w} x {current_h}", True, (0,0,0))
        new_size_text = data.font_35.render(f"NEW SIZE:", True, (0,0,0))

        width_text = data.font_25.render(f"WIDTH", True, (150,150,150))
        height_text = data.font_25.render(f"HEIGHT", True, (150,150,150))

        yes_button =    button.TextButton(frame.frame_base, (0,0), (100, 35), "Confirm", 25)
        cancel_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Cancel",  25)

        x_size = input_field.NumberInputField((0,0), (60, 40), 3, default_value="", int_only=True, empty=str(current_w), bg_color=(180,180,180), border_width=2, min_value=5, max_value=100, font=data.font_35)
        y_size = input_field.NumberInputField((0,0), (60, 40), 3, default_value="", int_only=True, empty=str(current_h), bg_color=(180,180,180), border_width=2, min_value=5, max_value=100, font=data.font_35)


        by_image_surf = pygame.image.load("Assets\\close.png")
        by_image_surf = pygame.transform.smoothscale(by_image_surf, (32, 32))

        # frame.add_surface(current_size_text, (0, 0.1), constants.UP)
        frame.add_surface(current_size_text, (0, 0.05), anchor=constants.UP)
        frame.add_surface(new_size_text, (0, 0.22), anchor=constants.UP)

        # Input
        frame.add_input_field(x_size, (-0.15, 0), anchor=constants.CENTER)  #-2 From image x
        frame.add_input_field(y_size, ( 0.15, 0), anchor=constants.CENTER) #+1,25 From image x

        frame.add_surface(by_image_surf, (0, 0), anchor=constants.CENTER)

        frame.add_surface(width_text,  (-0.15, -0.3), anchor=constants.BOTTOM)
        frame.add_surface(height_text, ( 0.15, -0.3), anchor=constants.BOTTOM)

        # frame.add_surface(center, (0.5,0.5))

        frame.add_button(yes_button, (-0.17, -0.05), RunnableFunc(self.confirm_button, args=[x_size.return_val, y_size.return_val]), anchor=constants.BOTTOM)
        frame.add_button(cancel_button, (0.17, -0.05), RunnableFunc(self.popup.close_popup), anchor=constants.BOTTOM)

        self.popup.add_contents_draw_func( RunnableFunc(frame.update) )
        self.popup.add_contents_onmousebuttondown_func( RunnableFunc(frame.on_mousebuttondown) )
        self.popup.add_contents_onkeydown_func( RunnableFunc(frame.on_keydown) )
        popup_window.popup_m_obj.track_popup(self.popup)

        logger.debug("Grid resize popup initialized successfully")


    def confirm_button(self, x_size_getter: "function", y_size_getter: "function") -> None:
        ui.ui_obj.set_gridsize((x_size_getter(), 
                                y_size_getter()))
        
        self.popup.close_popup()
        manager.m_obj.loaded_tilemap = None


gr_obj: "GridResizer" = None
def create_grid_resizer(screen) -> None:
    global gr_obj
    gr_obj = GridResizer(screen)