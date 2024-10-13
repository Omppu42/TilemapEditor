import pygame, time

import manager
import settings.data as data
import input_overrides

pygame.init()

class Button:
    def __init__(self, screen, pos: tuple, size: tuple, col_off=(100,100,100), col_on=(250,250,250), 
                 can_toggle_off=True, hover_text="", border_w=1, hover_col=None, hover_col_on=None, hover_col_off=None, hover_change=20, tooltip_delay=0):
        self.pos = pos
        self.size = size
        self.col_off = col_off
        self.col_on = col_on
        self.screen = screen
        self.rect = pygame.Rect(pos, size)
        self.btn_surf = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
        self.border_width = border_w
        self.border_surf = pygame.Surface((self.size[0] + self.border_width * 2, self.size[1] + self.border_width * 2), pygame.SRCALPHA, 32).convert_alpha()

        if len(col_off) == 4:
            self.border_surf.fill((0, 0, 0, col_off[3]))
        elif len(col_on) == 4:
            self.border_surf.fill((0, 0, 0, col_on[3]))
        else:
            self.border_surf.fill((0, 0, 0, 255))


        self.has_border = True
        self.clicked = -1 #defalut starting value is "off"
        self.just_clicked = False #is true one cycle after being clicked
        self.can_toggle_off = can_toggle_off

        # HOVER
        self.hover_start_time = 0
        self.hovering = False

        self.hover_col_off = None
        self.hover_col_on = None

        self.__init_hover_color(hover_col, hover_col_off, hover_col_on, hover_change)

        # TOOLTIP
        # Show tooltip after seconds
        self.tooltip_delay = tooltip_delay
        self.tooltip_text_surf = data.font_25.render(str(hover_text), True, (150,150,150))
        self.tooltip_text_rect = self.tooltip_text_surf.get_rect(center=(self.pos[0]+self.size[0]//2, 
                                                                       self.pos[1]+self.size[1]//2 - size[1]))

        # Disabling removes the ability to click and to render
        self.disabled = False
        
        self.set_color()

    def __init_hover_color(self, hover_both, hover_off, hover_on, hover_change) -> None:
        self.hover_col_off = hover_off
        self.hover_col_on = hover_on

        if self.hover_col_off is None:
            self.hover_col_off = hover_both if hover_both != None else (min(self.col_off[0] + hover_change, 255),  # min function finds the smaller on: 
                                                                        min(self.col_off[1] + hover_change, 255),  # if the hover change causes it to go over 255, 255 will be chosen
                                                                        min(self.col_off[2] + hover_change, 255))

        if self.hover_col_on is None:
            self.hover_col_on = hover_both if hover_both != None else (abs(self.col_on[0] - hover_change), 
                                                                       abs(self.col_on[1] - hover_change), 
                                                                       abs(self.col_on[2] - hover_change))


    def update(self, rect_override:"pygame.rect.Rect"=None, boundaries:"pygame.rect.Rect"=None):
        """Should be called every frame"""
        if self.disabled: return

        self.update_hover(rect_override, boundaries)
        self.update_color()

        self.rect = pygame.Rect(self.pos, self.size)

        self.draw()

        self.just_clicked = False
    

    def draw(self):
        if self.disabled: return

        if self.has_border:
            self.screen.blit(self.border_surf, (self.pos[0] - self.border_width, self.pos[1] - self.border_width))

        self.screen.blit(self.btn_surf, self.rect)


    def check_clicked(self, rect_override:"pygame.rect.Rect"=None, boundaries:"pygame.rect.Rect"=None) -> bool:
        """Should be called on mouse click event"""
        if self.disabled: return
        if not input_overrides.get_mouse_pressed()[0]: return False
        if rect_override != None:
            self.rect = rect_override

        mouse_pos = input_overrides.get_mouse_pos()

        # Check if mouse overlaps the button's rect
        if self.rect.collidepoint(mouse_pos):
            if boundaries:
                if not boundaries.collidepoint(mouse_pos):
                    return False
                
            if self.can_toggle_off:
                self.clicked *= -1
            else: #if can't toggle off, keep on when clicked
                self.clicked = 1
            
            self.set_state(self.clicked)
            self.just_clicked = True
            return True
        return False
            
    def set_color(self):
        if self.disabled: return

        if self.clicked == 1:
            if self.hovering:
                self.btn_surf.fill(self.hover_col_on)
                return
            
            self.btn_surf.fill(self.col_on)

        elif self.clicked == -1:
            if self.hovering:
                self.btn_surf.fill(self.hover_col_off)
                return
            self.btn_surf.fill(self.col_off)

        else:
            assert False, f"Invalid self.clicked state of {self.clicked}"

    def update_color(self):
        if self.disabled: return

        self.set_color()

    def update_hover(self, rect_override:"pygame.rect.Rect"=None, boundaries:"pygame.rect.Rect"=None):
        if self.disabled: return

        if rect_override != None:
            self.rect = rect_override

        mouse_pos = input_overrides.get_mouse_pos()

        if not self.rect.collidepoint(mouse_pos): # Not hovering
            self.hovering = False  
            self.hover_start_time = 0 
            return
        
        if boundaries:
            if not boundaries.collidepoint(mouse_pos): # Outside boundaries
                self.hovering = False  
                self.hover_start_time = 0 
                return

        self.hovering = True
        if self.hover_start_time == 0:
            self.hover_start_time = time.time() # Set hovering start time
        
        # Tooltip
        if time.time() - self.hover_start_time >= self.tooltip_delay: 
            self.screen.blit(self.tooltip_text_surf, self.tooltip_text_rect)


    def set_state(self, state: int): #-1 = off, 1 = on
        assert state == -1 or state == 1, "Button state can only be -1 or 1"
        if self.disabled: return

        self.clicked = state
        self.set_color()

    def is_clicked(self) -> bool:
        if self.disabled: return

        if self.clicked == 1:
            return True
        return False



class ButtonGroup:  #only one button in the button group can be on at a time
    def __init__(self, buttons: list): 
        self.buttons = buttons
        self.button_to_leave_on = None

    def update(self):
        for x in self.buttons:
            if x.just_clicked:
                self.button_to_leave_on = x
        
        if self.button_to_leave_on is None: return

        for x in self.buttons:
            if x is self.button_to_leave_on:
                x.set_state(1)
                continue
            x.set_state(-1)
        
        self.button_to_leave_on = None


class ToolButton(Button):
    def __init__(self, screen, pos: tuple, size: tuple, image, state_when_clicked=None, hover_text=None, init_state=-1, can_toggle_off=True, **kwargs):
        super().__init__(screen, pos, size, can_toggle_off=can_toggle_off, hover_text=hover_text, **kwargs)
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, size)
        self.state_when_clicked = state_when_clicked
        self.set_state(init_state)

    def update(self, **kwargs):
        if self.disabled: return

        if self.just_clicked and self.state_when_clicked is not None:
            manager.m_obj.state = self.state_when_clicked

        super().update(**kwargs)
        self.screen.blit(self.image, self.rect)


class TextButton(Button):
    def __init__(self, screen, pos: tuple, size: tuple, text: str, text_size: int, can_toggle=False, **kwargs):
        super().__init__(screen, pos, size, can_toggle_off=can_toggle, **kwargs)
        self.set_state(1)
        font = pygame.font.Font(None, text_size)
        self.text_surf = font.render(text, True, (0,0,0))
        

        self.click_time_start = 0
        self.click_color_time: float = 0.15
        self.click_color = (self.col_on[0] - 50, self.col_on[1] - 50, self.col_on[2] - 50)

    def update(self, **kwargs):
        if self.disabled: return

        super().update(**kwargs)
        rect = self.text_surf.get_rect(center=(self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2))


        if time.time() - self.click_time_start < self.click_color_time:
            self.btn_surf.fill(self.click_color)
            self.screen.blit(self.btn_surf, self.rect)

        self.screen.blit(self.text_surf, rect)

    def check_clicked(self, **kwargs) -> bool:
        if self.disabled: return
        
        clicked = super().check_clicked(**kwargs)
        if not clicked: return False

        self.click_time_start = time.time()
        return True
    


class ImageButton(Button):
    def __init__(self, screen, pos: tuple, size: tuple, image_cwd_path: str, img_color_on_hover=None, image_rel_size=0.8, can_toggle=False, **kwargs):
        super().__init__(screen, pos, size, can_toggle_off=can_toggle,**kwargs)
        self.set_state(1)

        self.image_surf = pygame.image.load(image_cwd_path)
        self.image_surf = pygame.transform.smoothscale(self.image_surf, (size[0] * image_rel_size, size[1] * image_rel_size))

        self.image_hover_col = img_color_on_hover
        if self.image_hover_col:
            self.hovering_image = self.__set_image_color_to(self.image_surf)

        self.use_white_image = False

        self.click_time_start = 0
        self.click_color_time: float = 0.15
        self.click_color = (abs(self.hover_col_on[0] - 20), abs(self.hover_col_on[1] - 20), abs(self.hover_col_on[2] - 20))
    

    def __set_image_color_to(self, original_image: pygame.Surface,) -> pygame.Surface:
        assert len(self.image_hover_col) == 3, "Image hover color can only be (r, g, b) format"
        white_shape_surface = pygame.Surface(original_image.get_rect().size, pygame.SRCALPHA)

        # Lock the surfaces for pixel manipulation (improves performance)
        original_image.lock()
        white_shape_surface.lock()

        # Get the pixel array of the image and alpha array
        alpha_array = pygame.surfarray.pixels_alpha(original_image)

        # Set the RGB values of the white-shape surface to (255, 255, 255) (white)
        white_shape_surface.fill(self.image_hover_col)

        # Set the alpha values to match the original image's alpha (transparency)
        pygame.surfarray.pixels_alpha(white_shape_surface)[:] = alpha_array[:]

        # Unlock the surfaces
        original_image.unlock()
        white_shape_surface.unlock()

        return white_shape_surface


    def update(self, **kwargs):
        if self.disabled: return

        super().update(**kwargs)

        self.draw()
        

    def draw(self) -> None:
        super().draw()
        if self.disabled: return

        rect = self.image_surf.get_rect(center=(self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2))

        if time.time() - self.click_time_start < self.click_color_time:
            self.btn_surf.fill(self.click_color)
            self.screen.blit(self.btn_surf, self.rect)

        if (self.hovering and self.image_hover_col) or self.use_white_image:
            self.screen.blit(self.hovering_image, rect)
            return

        self.screen.blit(self.image_surf, rect)


    def check_clicked(self, **kwargs) -> bool:
        if self.disabled: return
        
        clicked = super().check_clicked(**kwargs)
        if not clicked: return False

        self.click_time_start = time.time()
        return True