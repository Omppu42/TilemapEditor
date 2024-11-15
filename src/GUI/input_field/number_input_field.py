import pygame

from . import input_field_base

pygame.init()

class NumberInputField(input_field_base.InputField):
    EVENT_TO_INT = {
        (pygame.K_0, pygame.K_KP_0): 0,
        (pygame.K_1, pygame.K_KP_1): 1,
        (pygame.K_2, pygame.K_KP_2): 2,
        (pygame.K_3, pygame.K_KP_3): 3,
        (pygame.K_4, pygame.K_KP_4): 4,
        (pygame.K_5, pygame.K_KP_5): 5,
        (pygame.K_6, pygame.K_KP_6): 6,
        (pygame.K_7, pygame.K_KP_7): 7,
        (pygame.K_8, pygame.K_KP_8): 8,
        (pygame.K_9, pygame.K_KP_9): 9,
    }
    
    def __init__(self, pos: tuple, size: tuple, max_chars, start_value="",
                placeholder="0", int_only=False, min_value=-1, max_value=-1, forbidden_chars=[pygame.K_COMMA], **kwargs):
        super().__init__(pos, size, max_chars, start_value=start_value, placeholder=placeholder, forbidden_chars=forbidden_chars, **kwargs)

        self.int_only = int_only
        self.min_value = min_value
        self.max_value = max_value

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
            # Remove zeros from before the int
            while int(self.text[0]) == 0 and len(self.text) > 1:
                self.text = self.text[1:]

            # Min Max values
            if self.min_value != -1 and int(self.text) < self.min_value:
                self.text = str(self.min_value)
            if self.max_value != -1 and int(self.text) > self.max_value:
                self.text = str(self.max_value)
    

    def on_keydown(self, event: pygame.event.Event):
        if not self.active: return
        super().on_keydown(event)

        # If limit reached
        self.__text_info()        
        if self.length >= self.max_chars: return

        # Adding numbers
        for keys, result in NumberInputField.EVENT_TO_INT.items():
            if event.key in keys:
                self.add_character_at_cursor(str(result))

        if self.int_only: return

        # Dot
        if event.key == pygame.K_PERIOD and self.has_preiod == False:
            self.add_character_at_cursor(".")


    def on_left_mouse_click(self, rect_override:"pygame.rect.Rect"=None, boundaries:"pygame.rect.Rect"=None):
        super().on_left_mouse_click(rect_override=rect_override, boundaries=boundaries)

        self.fix_text()


    def get_value(self):
        if self.int_only:
            return int(super().get_value())
        
        return float(super().get_value())















