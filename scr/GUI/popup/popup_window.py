import pygame, time, math

import settings.settings as settings
import GUI.button as button

import mouse

class PopupWindow:
    TOP_BAR_H = 40
    POPUP_TIME_S = 0.5
    BACKSHADOW_OPACITY = 100
    def __init__(self, screen: pygame.Surface, pos: tuple, size: tuple, bg: tuple, bar_bg: tuple, border_w: int=0, backdrop_depth: int=0) -> None:
        self.screen = screen
        self.pos = pos
        self.size = size
        self.bg = bg
        self.bar_bg = bar_bg
        self.border_w = border_w
        self.backdrop_depth = backdrop_depth

        self.__init_validate_values()

        self.screen_shade_surf = self.__init_screen_shade_surf()

        self.backdrop_surface = self.__init_backdrop_surf()
        self.surface = self.__init_surface()

        self.close_button = button.ImageButton(screen,
                                               (self.pos[0] + self.size[0] + border_w - PopupWindow.TOP_BAR_H, self.pos[1] + border_w),
                                               (PopupWindow.TOP_BAR_H, PopupWindow.TOP_BAR_H),
                                               "Assets\\close.png", hover_col_on=(255, 50, 50), img_color_on_hover=(255, 255, 255), border_w=0, col_on=(255,255,255))

        self.active = False # Set to true after the starting animation
        self.creation_time = time.time()

        self.start_animation_playing = True
        self.close_animation_playing = False
        self.close_anim_start_time = 0

        self.on_destroy_func: list[tuple[function, list, dict]] = None  #Function, args, kwargs

        self.visible_pos = self.pos
        self.hidden_pos = (self.pos[0], -self.size[1] - (2 * self.border_w + self.backdrop_depth))

        self.contents_draw_func: "function"            = None # Given in PopupManager track_popup()
        self.contents_onmousebuttondown_func: "function" = None # Given in PopupManager track_popup()
        self.contents_onkeydown_func: "function"         = None # Given in PopupManager track_popup()

        self.__start_animation()
        self.__redraw_surface()
        

    # PRIVATE -------------------------------
    def __init_validate_values(self) -> None:
        assert len(self.pos)    == 2, "Position must be a (x, y) tuple"
        assert len(self.size)   == 2, "Size must be a (x, y) tuple"
        assert len(self.bg)     == 3, "Background must be a (r, g, b) tuple"
        assert len(self.bar_bg) == 3, "Bar BG must be a (r, g, b) tuple"

        assert self.border_w    >= 0, "Border width must be positive"

    def __init_screen_shade_surf(self) -> "pygame.Surface":
        surf = pygame.Surface((settings.SCR_W, settings.SCR_H))
        surf.fill((0, 0, 0))
        surf.set_alpha(0)

        return surf

    def __init_backdrop_surf(self) -> "pygame.Surface":
        backdrop = pygame.Surface((self.size[0] + self.border_w * 2, self.size[1] + self.border_w * 2))
        backdrop.fill((0, 0, 0))
        backdrop.set_alpha(50)

        return backdrop


    def __init_surface(self) -> "pygame.Surface":
        # Create a surface that can hold the border and the backdrop
        surface = pygame.Surface(((self.size[0] + self.border_w * 2),
                                  (self.size[1] + self.border_w * 2)))

        return surface

    def __redraw_surface(self) -> None:
        # Draw the base for everything that includes the borders
        pygame.draw.rect(self.surface, (0, 0, 0), (0, 0, self.size[0] + self.border_w * 2, self.size[1] + self.border_w * 2))

        # Draw the background
        pygame.draw.rect(self.surface, self.bg, ((self.border_w, self.border_w), self.size))

        # Draw the top bar
        pygame.draw.rect(self.surface, self.bar_bg, (self.border_w, self.border_w, self.size[0], PopupWindow.TOP_BAR_H))

        # Keep the close button in it's correct place during animations
        self.close_button.pos = (self.pos[0] + self.size[0] + self.border_w - PopupWindow.TOP_BAR_H, self.pos[1] + self.border_w)
        self.close_button.update()


    def __anim_ease_pos(self, x) -> float:
        ease = 2 * x * x if x < 0.5 else 1 - math.pow(-2 * x + 2, 2) / 2

        self.screen_shade_surf.set_alpha(ease * PopupWindow.BACKSHADOW_OPACITY)

        # At progress=1    self.hidden_pos[1]  cancel each other out 
        return (self.visible_pos[0], self.hidden_pos[1] + (self.visible_pos[1] - self.hidden_pos[1]) * ease)


    def __start_animation(self) -> None:
        alive_time = time.time() - self.creation_time      

        progress = alive_time / PopupWindow.POPUP_TIME_S

        if progress > 1:
            self.start_animation_playing = False
            self.active = True
            progress = 1

        self.pos = self.__anim_ease_pos(progress)



    def __close_animation(self) -> None:
        elapsed_time = time.time() - self.close_anim_start_time

        progress = 1 - (elapsed_time / PopupWindow.POPUP_TIME_S)

        if progress < 0:
            progress = 0
            if self.on_destroy_func != None:
                # Function, args, kwargs
                self.on_destroy_func[0](*self.on_destroy_func[1], **self.on_destroy_func[2])

            self.close_animation_playing = False
            self.active = False
            popup_m_obj.remove_popup(self)
            pygame.mouse.get_rel() # Reset mouse movement

        self.pos = self.__anim_ease_pos(progress)



    # PUBLIC --------------------------------
    def update(self) -> None:
        """contents_update_func being a function that draws the contents of the popup window"""
        if self.start_animation_playing: self.__start_animation()
        if self.close_animation_playing: self.__close_animation()

        self.__redraw_surface()
        self.contents_draw_func()

        # Allow next code only after animations are finished
        if not self.active: return


    def draw(self) -> None:
        self.screen.blit(self.screen_shade_surf, (0, 0))

        self.screen.blit(self.backdrop_surface, (self.pos[0] + self.backdrop_depth,
                                                 self.pos[1] + self.backdrop_depth))
        self.screen.blit(self.surface, self.pos)

        self.close_button.draw()


    def add_destroy_func(self, func: "function", args=[], kwargs={}) -> None:
        self.on_destroy_func = (func, args, kwargs)


    def on_left_mouse_click(self) -> None:
        if not self.active: return

        # If close button clicked, disable interactions and start the closing animation
        if self.close_button.check_clicked():
            self.close_popup()
            self.close_button.use_white_image = True


    def close_popup(self):
        self.active = False
        self.close_anim_start_time = time.time()
        self.close_animation_playing = True



class PopupManager:
    def __init__(self) -> None:
        self.popups: "list[PopupWindow]" = []

    def track_popup(self, popup_obj: PopupWindow, contents_draw_func: "function", contents_on_mousebuttondown_func: "function", contents_onkeydown_func: "function"=None) -> None:
        """Add a popup to track. \n
        Contents_draw_func being a function that draws the contents of the popup window. \n
        Contents_on_mousebuttondown_func being the function that handles events in pygame.MOUSEBUTTONDOWN. \n
        IMPORTANT: Contents_on_mousebuttondown_func has to take in event (pygame.event.Event)"""

        popup_obj.contents_draw_func = contents_draw_func
        popup_obj.contents_onmousebuttondown_func = contents_on_mousebuttondown_func
        popup_obj.contents_onkeydown_func = contents_onkeydown_func

        self.popups.append(popup_obj)

    def remove_popup(self, popup_obj: PopupWindow) -> None:
        for _obj in self.popups:
            if _obj == popup_obj:
                self.popups.remove(_obj)
                break

        
    def close_popup(self, popup_obj: PopupWindow):
        for _obj in self.popups:
            if _obj == popup_obj:
                _obj.close_popup()
                break

    def update_popups(self) -> None:
        for _popup in self.popups[::-1]:
            _popup.update()

            # If popups are present, remove the button clicked status and mousepos to not allow clicking on other buttons
            mouse.clear_pos_override()
            mouse.clear_pressed_override()


    def draw_popups(self) -> None:
        for _popup in self.popups:
            _popup.draw()


    def on_mousebuttondown(self, event: "pygame.event.Event") -> None:        
        # Update only the top popup, which is the last popup in the list
        if len(self.popups) == 0: return
        
        if mouse.get_pressed_override()[0]:
            self.popups[-1].on_left_mouse_click() # Update top popup leftclick
        
        self.popups[-1].contents_onmousebuttondown_func(event) # Update contents_on_mousebuttondown function


    def on_keydown(self, event: "pygame.event.Event") -> None:        
        # Update only the top popup, which is the last popup in the list
        if len(self.popups) == 0: return
                
        self.popups[-1].contents_onkeydown_func(event) # Update contents_on_mousebuttondown function



    def popups_exist(self) -> bool:
        if len(self.popups) > 0:
            return True

        return False
    


popup_m_obj: PopupManager = None

def create_popup_manager() -> None:
    global popup_m_obj
    popup_m_obj = PopupManager()