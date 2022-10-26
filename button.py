import pygame, time
from manager import State

pygame.init()

class Button:
    def __init__(self, pos: tuple, size: tuple, screen, col_off=(100,100,100), col_on=(250,250,250), can_toggle_off=True, hover_text="", hover_col=None):
        self.pos = pos
        self.size = size
        self.col_off = col_off
        self.col_on = col_on
        self.screen = screen
        self.rect = pygame.Rect(pos, size)
        self.btn_surf = pygame.Surface(size)
        self.border_width = 1
        self.border_surf = pygame.Surface((size[0] + self.border_width * 2, self.size[1] + self.border_width * 2))
        self.border_surf.fill((0, 0, 0))
        self.has_border = True
        self.clicked = -1 #defalut starting value is "off"
        self.just_clicked = False #is true one cycle after being clicked
        self.can_toggle_off = can_toggle_off

        self.hover_text = str(hover_text)
        self.hover_delay: float = 0.3
        self.hover_start_time = 0
        self.hovering: bool = False
        self.hover_col = hover_col

        font = pygame.font.Font(None, 25)
        self.hover_text_render = font.render(self.hover_text, True, (150,150,150))
        self.hover_text_rect = self.hover_text_render.get_rect(center=(self.pos[0]+self.size[0]//2, self.pos[1]+self.size[1]//2-35))
        
        self.set_color(self.clicked)

    def update(self):
        self.update_color()

        if self.has_border:
            self.screen.blit(self.border_surf, (self.pos[0] - self.border_width, self.pos[1] - self.border_width))

        self.screen.blit(self.btn_surf, self.rect)
        self.just_clicked = False

    def check_clicked(self, mouse_pos: tuple) -> bool:
        if not pygame.mouse.get_pressed()[0]: return False
        if self.rect.collidepoint(mouse_pos):
            if self.can_toggle_off:
                self.clicked *= -1
            else: #if can't toggle off, keep on when clicked
                self.clicked = 1
            
            self.set_state(self.clicked)
            self.just_clicked = True
            return True
        return False
            
    def set_color(self, clicked: int):
        if self.hovering and self.hover_col is not None:
            self.btn_surf.fill(self.hover_col)
            return

        if self.clicked == 1:
            self.btn_surf.fill(self.col_on)
        elif self.clicked == -1:
            self.btn_surf.fill(self.col_off)

    def update_color(self):
        self.set_color(self.clicked)

    def update_hover(self, mouse_pos):
        if not self.rect.collidepoint(mouse_pos): #not hovering
            self.hovering = False  
            self.hover_start_time = 0 
            return
            
        self.hovering = True
        if self.hover_start_time == 0:
            self.hover_start_time = time.time() #set hovering start time
        
        if time.time() - self.hover_start_time >= self.hover_delay: #hovered for hover_delay amount of time
            self.screen.blit(self.hover_text_render, self.hover_text_rect)

    def set_state(self, state: int): #1 = on, -1 = off
        self.clicked = state
        self.set_color(self.clicked)

    def is_clicked(self) -> bool:
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


class GridButton(Button):
    def __init__(self, pos: tuple, size: tuple, screen):
        super().__init__(pos, size, screen, hover_text="Grid (G)")
        self.set_state(1)
        self.image = pygame.image.load("Assets\\grid_btn_img.png")
        self.image = pygame.transform.scale(self.image, size)

    def update(self):
        super().update()
        self.screen.blit(self.image, self.rect)


class ToolButton(Button):
    def __init__(self, pos: tuple, size: tuple, screen, manager, state_when_clicked, image, hover_text=None):
        super().__init__(pos, size, screen, can_toggle_off=False, hover_text=hover_text)
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, size)
        self.manager = manager
        self.state_when_clicked = state_when_clicked

    def update(self):
        if self.just_clicked:
            self.manager.state = self.state_when_clicked

        super().update()
        self.screen.blit(self.image, self.rect)


class TextButton(Button):
    def __init__(self, pos: tuple, size: tuple, screen, text: str, text_size: int, can_toggle=False, hover_col=None):
        super().__init__(pos, size, screen, can_toggle_off=can_toggle, hover_col=hover_col)
        self.set_state(1)
        font = pygame.font.Font(None, text_size)
        self.text_surf = font.render(text, True, (0,0,0))
        

        self.click_time_start = 0
        self.click_color_time: float = 0.15
        self.click_color = (self.col_on[0] - 100, self.col_on[1] - 100, self.col_on[2] - 100)

    def update(self):
        super().update()
        rect = self.text_surf.get_rect(center=(self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2))


        if time.time() - self.click_time_start < self.click_color_time:
            self.btn_surf.fill(self.click_color)
            self.screen.blit(self.btn_surf, self.rect)

        self.screen.blit(self.text_surf, rect)

    def check_clicked(self, mouse_pos) -> bool:
        clicked = super().check_clicked(mouse_pos)
        if not clicked: return False

        self.click_time_start = time.time()
        return True