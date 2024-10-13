import pygame
import tkinter

import GUI.button as button
import GUI.input_field as input_field
import GUI.popup.popup_window as popup_window
import GUI.popup.popup_contents as popup_contents
import GUI.popup.scrollable_frame as scrollable_frame
import GUI.popup.scrollable_frame_piece as scrollable_frame_piece

from util.util_logger import logger
from util.util import RunnableFunc
import settings.settings as settings
import settings.data as data

import ui
import manager


def set_gridsize_ask():
    window = tkinter.Tk(className="grid settings")
    window.geometry("300x200")
    window.resizable(False, False)
    window.attributes('-topmost', True)
    window.eval('tk::PlaceWindow . center')

    text = tkinter.Label(text="RESIZE GRID", font=(None, 18))
    text.pack(pady=20,side=tkinter.TOP)

    def validate(P):
        if len(P) == 0:
            return True
        elif (len(P) == 1 or len(P) == 2) and P.isdigit():
            return True
        else:
            return False

    def get_gridsize():
        w = width.get()
        h = height.get()
        if w == "" or h == "":
            window.destroy()
            set_gridsize_ask()
            return

        ui.ui_obj.set_gridsize((int(w), int(h)))
        window.destroy()

    vcmd = (window.register(validate), '%P')

    width = tkinter.Entry(width=5, font=(None, 14), validate="key", validatecommand=vcmd)
    width.place(x=50, y=90)
    width.focus()

    width_text = tkinter.Label(text="WIDTH", font=(None, 11))
    width_text.place(x=53, y=120)

    height = tkinter.Entry(width=5, font=(None, 14), validate="key", validatecommand=vcmd)
    height.place(x=190, y=90)
    
    height_text = tkinter.Label(text="HEIGHT", font=(None, 11))
    height_text.place(x=193, y=120)

    xtext = tkinter.Label(text="x", font=(None, 18))
    xtext.place(x=140, y=85)

    button = tkinter.Button(text="CONFIRM", width=10, height=1, bg="Gainsboro", command=get_gridsize)
    button.pack(side=tkinter.BOTTOM, pady=10)

    window.mainloop()


class GridResizer:
    def __init__(self, screen):
        self.screen = screen
    
    def grid_resize_popup(self) -> None:
        logger.debug("Opening grid resize popup")
        popup_size = (400, 300)
        popup_pos = (settings.SCR_W//2 - 2*popup_size[0]//3, 100)

        self.popup = popup_window.PopupWindow(self.screen, popup_pos, popup_size, (120, 120, 120), (255, 255, 255), border_w=2, backdrop_depth=10)

        frame = popup_contents.PopupContents(self.popup, (10, 10), (popup_size[0] - 20, popup_size[1] - 60))


        current_size_text = data.font_25.render(f"Current size: {ui.ui_obj.grid_size_rows_cols[0]} x {ui.ui_obj.grid_size_rows_cols[1]}", True, (0,0,0))
        new_size_text = data.font_35.render(f"NEW SIZE:", True, (0,0,0))

        width_text = data.font_25.render(f"WIDTH", True, (150,150,150))
        height_text = data.font_25.render(f"HEIGHT", True, (150,150,150))

        yes_button =    button.TextButton(frame.frame_base, (0,0), (100, 35), "Confirm", 25)
        cancel_button = button.TextButton(frame.frame_base, (0,0), (100, 35), "Cancel", 25)

        x_size = input_field.NumberInputField((0,0), (60, 40), 3, "", int_only=True, empty="30", bg_color=(180,180,180), border_width=2, min_value=5, max_value=100, font=data.font_35)
        y_size = input_field.NumberInputField((0,0), (60, 40), 3, "", int_only=True, empty="20", bg_color=(180,180,180), border_width=2, min_value=5, max_value=100, font=data.font_35)


        by_image_surf = pygame.image.load("Assets\\close.png")
        by_image_surf = pygame.transform.smoothscale(by_image_surf, (32, 32))

        frame.add_surface(current_size_text, (0.5,0.1))
        frame.add_surface(new_size_text, (0.5,0.3))

        # Input
        frame.add_number_input_field(x_size, (0.26, 0.45))  #-2 From image x
        frame.add_number_input_field(y_size, (0.585, 0.45)) #+1,25 From image x
        frame.add_surface_non_center(by_image_surf, (0.46,0.46))

        frame.add_surface(width_text,  (0.33,0.67))
        frame.add_surface(height_text, (0.665,0.67))

        # frame.add_surface(center, (0.5,0.5))

        frame.add_button(yes_button, (0.65, 0.8), self.confirm_button, on_click_func_args=[x_size.return_val, y_size.return_val])
        frame.add_button(cancel_button, (0.1, 0.8), self.popup.close_popup)

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