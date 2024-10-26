import pygame, time, math
import inspect

from settings import settings
from util import util

from .. import button
from . import settings_popup

import input_overrides

class RunnableFuncList:
    def __init__(self):
        self.runnable_funcs: "list[util.RunnableFunc]" = []

    def add_func(self, runnable_func: "util.RunnableFunc") -> None:
        self.runnable_funcs.append(runnable_func)

    def has_funcs(self) -> bool:
        return len(self.runnable_funcs) >= 1

    def run_funcs(self, start_args_override=None) -> None:
        for func in self.runnable_funcs:
            if start_args_override:
                func.run_function(start_args_override=start_args_override)
            else:
                func.run_function()


class PopupWindow:
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
                                               (self.pos[0] + self.size[0] + border_w - settings_popup.POPUP_TOPBAR_H, self.pos[1] + border_w),
                                               (settings_popup.POPUP_TOPBAR_H, settings_popup.POPUP_TOPBAR_H),
                                               "Assets\\close.png", hover_col_on=(255, 50, 50), img_color_on_hover=(255, 255, 255), border_w=0, col_on=(255,255,255))

        self.active = False # Set to true after the starting animation
        self.creation_time = time.time()

        self.start_animation_playing = True
        self.close_animation_playing = False
        self.close_anim_start_time = 0


        self.visible_pos = self.pos
        self.hidden_pos = (self.pos[0], -self.size[1] - (2 * self.border_w + self.backdrop_depth))

        self.c_draw_obj:        "RunnableFuncList" = RunnableFuncList()
        self.c_onmousedown_obj: "RunnableFuncList" = RunnableFuncList()
        self.c_onkeydown_obj:   "RunnableFuncList" = RunnableFuncList()
        self.on_destroy_func:   "RunnableFuncList" = RunnableFuncList()

        self.contents_list: list = []

        self.key_bound_funcs: "dict[int, util.RunnableFunc]" = {}

        self.__start_animation()
        self.__redraw_surface()

        popup_m_obj.track_popup(self)
        

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
        pygame.draw.rect(self.surface, self.bar_bg, (self.border_w, self.border_w, self.size[0], settings_popup.POPUP_TOPBAR_H))

        # Keep the close button in it's correct place during animations
        self.close_button.pos = (self.pos[0] + self.size[0] + self.border_w - settings_popup.POPUP_TOPBAR_H, self.pos[1] + self.border_w)
        self.close_button.update()


    def __anim_ease_pos(self, x) -> float:
        ease = 2 * x * x if x < 0.5 else 1 - math.pow(-2 * x + 2, 2) / 2

        self.screen_shade_surf.set_alpha(ease * settings_popup.POPUP_BACKSHADOW_OPACITY)

        # At progress=1    self.hidden_pos[1]  cancel each other out 
        return (self.visible_pos[0], self.hidden_pos[1] + (self.visible_pos[1] - self.hidden_pos[1]) * ease)


    def __start_animation(self) -> None:
        alive_time = time.time() - self.creation_time      

        progress = alive_time / settings_popup.POPUP_ANIM_TIME_S

        if progress > 1:
            self.start_animation_playing = False
            self.active = True
            progress = 1

        self.pos = self.__anim_ease_pos(progress)



    def __close_animation(self) -> None:
        elapsed_time = time.time() - self.close_anim_start_time

        progress = 1 - (elapsed_time / settings_popup.POPUP_ANIM_TIME_S)

        if progress < 0:
            progress = 0
            if self.contents_list:
                [c.on_destroy() for c in self.contents_list]

            if self.on_destroy_func.has_funcs():
                self.on_destroy_func.run_funcs()

            self.close_animation_playing = False
            self.active = False
            popup_m_obj.remove_popup(self)
            pygame.mouse.get_rel() # Reset mouse movement

        self.pos = self.__anim_ease_pos(progress)


    def __get_runnable_func(self, func: "util.RunnableFunc | function") -> util.RunnableFunc:
        if callable(func):
            return util.RunnableFunc(func)
        elif isinstance(func, util.RunnableFunc):
            return func
        else:
            raise TypeError(f"Invalid function passed: {func}")
        
    def __get_positional_args(self, func: "function") -> "list[inspect.Parameter]":
        return [
                param.name for param in inspect.signature(func).parameters.values()
                if param.default == inspect.Parameter.empty and
                param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ]


    # PUBLIC --------------------------------
    def update(self) -> None:
        """contents_update_func being a function that draws the contents of the popup window"""
        if self.start_animation_playing: self.__start_animation()
        if self.close_animation_playing: self.__close_animation()

        self.__redraw_surface()

        # Drawing Funcs
        if self.contents_list:
            [c.update() for c in self.contents_list]

        if self.c_draw_obj.has_funcs():
            self.c_draw_obj.run_funcs()


    def draw(self) -> None:
        self.screen.blit(self.screen_shade_surf, (0, 0))

        self.screen.blit(self.backdrop_surface, (self.pos[0] + self.backdrop_depth,
                                                 self.pos[1] + self.backdrop_depth))
        self.screen.blit(self.surface, self.pos)

        self.close_button.draw()


    def add_contents_draw_func(self, runnable_obj: "util.RunnableFunc | function") -> None:
        """Function that draws the contents of the contents of the popup"""
        self.c_draw_obj.add_func(
            self.__get_runnable_func(runnable_obj)
        )

    def add_destroy_func(self, runnable_obj: "util.RunnableFunc | function") -> None:
        """Called when the popup is off the screen and deleted"""
        self.on_destroy_func.add_func(
            self.__get_runnable_func(runnable_obj)
        )

    def add_contents_onmousebuttondown_func(self, runnable_obj: "util.RunnableFunc | function") -> None:
        """Function has to have 1st arg: event (pygame.Event). It is given automatically to the function when running it"""
        runnable_obj = self.__get_runnable_func(runnable_obj)
        req_args = inspect.getfullargspec(runnable_obj.function).args

        assert (len(req_args) >= 2), f"{runnable_obj.function.__self__.__class__.__name__}.{runnable_obj.function.__name__}() must have at least 2 args: 'self' and 'event'. Current args: {req_args}"

        self.c_onmousedown_obj.add_func(runnable_obj)

    def add_contents_onkeydown_func(self, runnable_obj: "util.RunnableFunc | function") -> None:
        """Function has to have 1st arg: event (pygame.Event). It is given automatically to the function when running it"""
        runnable_obj = self.__get_runnable_func(runnable_obj)
        req_args = inspect.getfullargspec(runnable_obj.function).args

        assert (len(req_args) >= 2), f"{runnable_obj.function.__self__.__class__.__name__}.{runnable_obj.function.__name__}() must have at least 2 args: 'self' and 'event'. Current args: {req_args}"

        self.c_onkeydown_obj.add_func(runnable_obj)



    def bind_func_to_key(self, pygame_keycode: int, runnable_obj: "util.RunnableFunc | function") -> None:
        runnable_obj = self.__get_runnable_func(runnable_obj)

        self.key_bound_funcs[pygame_keycode] = runnable_obj


    def add_contents_class(self, contents_class) -> None:
        """Adds a contents class to update automatically.\n
        Class has to have update(), on_mousebuttondown(), on_keydown(), on_delete() functions.\n
        No args or kwargs can be passed. To pass args and kwargs, make the func called here empty and assign with add_funcname() the function desired with args"""
        f1 = getattr(contents_class, "update")
        f2 = getattr(contents_class, "on_mousebuttondown")
        f3 = getattr(contents_class, "on_keydown")
        f4 = getattr(contents_class, "on_destroy")

        assert callable(f1),                f"update is not a function: {type(f1)}"
        assert callable(f2),    f"on_mousebuttondown is not a function: {type(f2)}"
        assert callable(f3),            f"on_keydown is not a function: {type(f3)}"
        assert callable(f4),            f"on_destroy is not a function: {type(f4)}"

        f1args = self.__get_positional_args(f1)
        f2args = self.__get_positional_args(f2)
        f3args = self.__get_positional_args(f3)
        f4args = self.__get_positional_args(f4)

        assert( len(f1args) == 0),             f"{type(contents_class).__name__}.update() function must take in no args. Currently there are {len(f1args)} arguments: {f1args}"
        assert( len(f2args) == 1), f"{type(contents_class).__name__}.on_mousebuttondown() function must take in only 'event' as an arg. Currently there are {len(f2args)} arguments: {f2args}"
        assert( len(f3args) == 1),         f"{type(contents_class).__name__}.on_keydown() function must take in only 'event' as an arg. Currently there are {len(f3args)} arguments: {f3args}"
        assert( len(f4args) == 0),         f"{type(contents_class).__name__}.on_destroy() function must take in no args. Currently there are {len(f4args)} arguments: {f4args}"


        self.contents_list.append(contents_class)


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


    def track_popup(self, popup_obj: PopupWindow) -> None:
        """Add a popup to track"""
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


    def draw_popups(self) -> None:
        for _popup in self.popups:
            _popup.draw()

    
    def handle_events(self, events: "list[pygame.event.Event]") -> None:
        if not self.popups_exist(): return

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.on_mousebuttondown(event)

            if event.type == pygame.KEYDOWN:
                self.on_keydown(event)

                input_overrides.remove_event(event)

        # Mouse buttons and pos is cleared here after top popup has updated
        for _popup in self.popups[::-1]:
            _popup.update()

            # If popups are present, remove the button clicked status and mousepos to not allow clicking on other buttons
            input_overrides.clear_mouse_pos()
            input_overrides.clear_mouse_pressed()


    def on_mousebuttondown(self, event: "pygame.event.Event") -> None:  
        # Update only the top popup, which is the last popup in the list
        if len(self.popups) == 0: return     
        
        if input_overrides.get_mouse_pressed()[0]:
            self.popups[-1].on_left_mouse_click() # Update top popup leftclick
        
        top_popup_contents = self.popups[-1].contents_list
        if top_popup_contents:
            [c.on_mousebuttondown(event) for c in top_popup_contents]

        top_popup_onmd_obj = self.popups[-1].c_onmousedown_obj
        if top_popup_onmd_obj.has_funcs():
            top_popup_onmd_obj.run_funcs(start_args_override=[event]) # Update contents_on_mousebuttondown function


    def on_keydown(self, event: "pygame.event.Event") -> None:        
        # Update only the top popup, which is the last popup in the list
        if len(self.popups) == 0: return

        top_popup_contents = self.popups[-1].contents_list
        if top_popup_contents:
            [c.on_keydown(event) for c in top_popup_contents]

        top_popup_onkd_obj = self.popups[-1].c_onkeydown_obj
        if top_popup_onkd_obj.has_funcs():
            top_popup_onkd_obj.run_funcs(start_args_override=[event]) # Update contents_on_mousebuttondown function

        for _keycode, _func in self.popups[-1].key_bound_funcs.items():
            if event.key == _keycode:
                _func.run_function()


    def popups_exist(self) -> bool:
        if len(self.popups) > 0:
            return True

        return False
    

popup_m_obj: PopupManager = PopupManager()