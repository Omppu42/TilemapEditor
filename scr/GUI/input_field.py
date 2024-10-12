import pygame

import settings.data as data

import mouse

pygame.init()

# TODO: Allow typing with keypad here

class NumberInputField():
    EVENT_TO_INT = {
            pygame.K_0: 0,
            pygame.K_1: 1,
            pygame.K_2: 2,
            pygame.K_3: 3,
            pygame.K_4: 4,
            pygame.K_5: 5,
            pygame.K_6: 6,
            pygame.K_7: 7,
            pygame.K_8: 8,
            pygame.K_9: 9,
        }
    
    def __init__(self, pos: tuple, size: tuple, max_chars, default_value, bg_color=(155,155,155),active_color=(200,200,200),
                border_width=0, border_color=(0,0,0), empty="0", int_only=False, min_value=-1, max_value=-1, font=data.font_25):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos, size)
        self.max_chars = max_chars
        self.bg_color = bg_color
        self.active_color = active_color
        self.text_color = (0, 0, 0)

        self.font = font
        self.placeholder_txt = empty
        self.placeholder_color = self.text_color
        self.int_only = int_only
        
        self.border_color = border_color
        self.border_width = border_width

        self.image = pygame.Surface(self.size)
        self.active = False

        self.__check_default_text_validity(str(default_value))
        self.text = str(default_value)

        self.has_preiod = False
        self.length = 0   

        self.min_value = min_value
        self.max_value = max_value

        

    def __check_default_text_validity(self, default_text: str) -> None:
        num_of_dots = len( [_index for _index, _letter in enumerate(default_text) if _letter == "."] )
        if num_of_dots > 1:
            raise ValueError(f"The NumberInputField's default text '{default_text}' must not contain more than one '.'")

        _length = len(default_text.replace(".", ""))

        if _length > self.max_chars:
            raise ValueError(f"The NumberInputField's default text '{default_text}' has a length of {_length}, when the maximum allowed is {self.max_chars}")

    def __draw_text(self, _text):
        _text_width, _text_height = _text.get_size()

        if _text_width < self.size[0] - self.border_width*2:
            # _text_width fits into the inputfield
            self.image.blit(_text, (2 + self.border_width*2, (self.size[1] - _text_height) // 2))
        else:
            # _text_width doesn't fit into the inputfield
            self.image.blit(_text, ( (self.border_width * 2) + (self.size[0] - _text_width - self.border_width * 3),
                                     (self.size[1] - _text_height) // 2) )

    def __text_info(self):
        if "." in self.text:
            self.has_preiod = True
        else:
            self.has_preiod = False

        _text = self.text.replace(".", "")

        self.length = len(_text)

    def fix_text(self):
        if len(self.text) == 0: return
        if self.text == "": return

        if self.text[-1] == ".":
            self.text = self.text[:-1]

        if not "." in self.text:
            # If placeholder isn't zero but the text is zero, empty the text
            # if self.placeholder_txt != 0 and int(self.text) == 0:
            #     self.text = ""
            
            # Remove zeros from before the int
            while int(self.text[0]) == 0 and len(self.text) > 1:
                self.text = self.text[1:]

            # Min Max values
            if self.min_value != -1 and int(self.text) < self.min_value:
                self.text = str(self.min_value)
            if self.max_value != -1 and int(self.text) > self.max_value:
                self.text = str(self.max_value)


    def draw(self, screen):
        if self.active:
            if self.border_width == 0:
                self.image.fill(self.active_color)
            else:
                self.image.fill(self.border_color)
                pygame.draw.rect(self.image, self.active_color, (self.border_width, self.border_width, 
                                                                self.size[0] - self.border_width * 2, self.size[1] - self.border_width * 2))

        elif self.border_width == 0:
            self.image.fill(self.bg_color)
        else:
            self.image.fill(self.border_color)
            pygame.draw.rect(self.image, self.bg_color, (self.border_width, self.border_width, 
                                                        self.size[0] - self.border_width * 2, self.size[1] - self.border_width * 2))

        #rendering text
        if self.text == "":
            placeholder_txt = self.font.render(self.placeholder_txt, True, self.placeholder_color)
            placeholder_txt.set_alpha(100)
            self.__draw_text(placeholder_txt)
        else:
            text = self.font.render(self.text, True, self.text_color)
            self.__draw_text(text)
        screen.blit(self.image, self.pos)
    
    
    def on_keydown(self, event: pygame.event.Event):
        if not self.active: return

        # Backspace    
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]

        # If limit reached
        self.__text_info()
        
        if self.length >= self.max_chars: return

        # Adding numbers
        if event.key in NumberInputField.EVENT_TO_INT:
            self.text += str(NumberInputField.EVENT_TO_INT[event.key])

        if self.int_only: return

        # Dot
        if event.key == pygame.K_PERIOD and self.has_preiod == False:
            self.text += "."


    def on_left_mouse_click(self, rect_override:"pygame.rect.Rect"=None, boundaries:"pygame.rect.Rect"=None):
        if rect_override == None:
            rect_override = self.rect

        mouse_pos = mouse.get_pos_override()
        self.active = rect_override.collidepoint(mouse_pos)

        if boundaries:
            if not boundaries.collidepoint(mouse_pos):
                self.active = False

        self.fix_text()


    def return_val(self):
        if self.int_only:
            return int(self.__get_val_str())
        
        return float(self.__get_val_str())
    
    def __get_val_str(self) -> str:
        if self.text == "":
            return self.placeholder_txt
        return self.text