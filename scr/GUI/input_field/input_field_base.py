
import pygame, time

import input_overrides
from . import util_text


class InputField:
    CTRL_REMOVE_STOPS = [
        " ", "_", "-", ",", "."
    ]

    def __init__(self, pos: tuple, size: tuple, max_chars, bg_color=(155,155,155),active_color=(200,200,200),
                start_value="", placeholder="", empty_return_val="placeholder", border_width=0, cursor_w=3, border_color=(0,0,0), font=pygame.font.Font(None, 25), forbidden_chars:"list[int]"=[pygame.K_PERIOD, pygame.K_COMMA], blink_rate_s=0.4):
        """Max chars is overriden if the text is about to get bigger than the box can display"""
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos, size)
        self.max_chars = max_chars
        self.bg_color = bg_color
        self.active_color = active_color
        self.text_color = (0, 0, 0)

        self.font = font
        self.placeholder_txt = placeholder
        self.placeholder_color = self.text_color
        
        self.border_color = border_color
        self.border_width = border_width

        self.surface = pygame.Surface(self.size)
        self.active = False

        self.cursor_surf = pygame.Surface((cursor_w, 5/4*self.font.size("Test")[1]))
        self.cursor_surf.fill((0,0,0))
        self.cursor_blink_rate_s = blink_rate_s
        self.cursor_blink_timer = time.time()  #flips cursor_draw when reaches rate
        self.cursor_draw = True

        self.start_value = start_value
        self.empty_return_val = empty_return_val # can be "placeholder", "start_value" or any other value

        self.__check_default_text_validity(str(self.start_value))
        self.text = str(self.start_value)
        self.forbidden_chars = forbidden_chars

        self.cursor_pos = 0

    
    # PRIVATE --------
    def __check_default_text_validity(self, default_text: str) -> None:
        num_of_dots = len( [_index for _index, _letter in enumerate(default_text) if _letter == "."] )
        if num_of_dots > 1:
            raise ValueError(f"The InputField's default text '{default_text}' must not contain more than one '.'")

        _length = len(default_text.replace(".", ""))

        if _length > self.max_chars:
            raise ValueError(f"The InputField's default text '{default_text}' has a length of {_length}, when the maximum allowed is {self.max_chars}")

    def __draw_text(self, _text):
        _text_width, _text_height = _text.get_size()

        if _text_width < self.size[0] - self.border_width*2:
            # _text_width fits into the inputfield
            self.surface.blit(_text, (2 + self.border_width*2, (self.size[1] - _text_height) // 2))
        else:
            # _text_width doesn't fit into the inputfield
            self.surface.blit(_text, ( (self.border_width * 2) + (self.size[0] - _text_width - self.border_width * 3),
                                     (self.size[1] - _text_height) // 2) )

    def process_deleting(self, event: "pygame.event.Event") -> None:
        control = event.mod & pygame.KMOD_CTRL

        # BACKSPACE -------
        if event.key == pygame.K_BACKSPACE and not control:
            self.text = util_text.remove_pos_from_str(self.text, self.cursor_pos)
            self.cursor_pos -= 1 if self.cursor_pos > 0 else 0
            self.set_cursor_active()

        # DEL -----
        elif event.key == pygame.K_DELETE and not control:
            if len(self.text) - 1 < self.cursor_pos: return
            self.text = util_text.remove_pos_from_str(self.text, self.cursor_pos + 1)
            self.set_cursor_active()

        # CTRL BACKSPACE --------
        if event.key == pygame.K_BACKSPACE and control:
            closest_index = util_text.get_next_break_index_left(self.text, self.cursor_pos, InputField.CTRL_REMOVE_STOPS)

            self.text = util_text.remove_range_from_str(self.text, closest_index, self.cursor_pos)
            self.cursor_pos = closest_index

        # CTRL DEL
        elif event.key == pygame.K_DELETE and control:
            closest_index = util_text.get_next_break_index_right(self.text, self.cursor_pos, InputField.CTRL_REMOVE_STOPS)

            self.text = util_text.remove_range_from_str(self.text, self.cursor_pos, closest_index)


    def process_cursor_move(self, event: "pygame.event.Event") -> None:
        control = event.mod & pygame.KMOD_CTRL

        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            self.set_cursor_active()

        # NORMAL -------
        if event.key == pygame.K_LEFT and not control:
            self.cursor_pos -= 1 if self.cursor_pos > 0 else 0
        
        elif event.key == pygame.K_RIGHT and not control:
            self.cursor_pos += 1 if self.cursor_pos < len(self.text) else 0

        # CONTROL --------
        if event.key == pygame.K_LEFT and  control:
            closest_index = util_text.get_next_break_index_left(self.text, self.cursor_pos, InputField.CTRL_REMOVE_STOPS)
            self.cursor_pos = closest_index

        elif event.key == pygame.K_RIGHT and control:
            closest_index = util_text.get_next_break_index_right(self.text, self.cursor_pos, InputField.CTRL_REMOVE_STOPS)
            self.cursor_pos = closest_index

        # Corrections 
        if self.cursor_pos > len(self.text): self.cursor_pos = len(self.text)
        if self.cursor_pos < 0:              self.cursor_pos = 0


    # PUBLIC ----------
    def fix_text(self) -> None:
        self.text = self.text.replace("/", "")
        self.text = self.text.replace("\\", "")
        self.text = self.text.replace("$", "")
        self.text = self.text.replace("@", "")


    def set_cursor_active(self) -> None:
        self.cursor_draw = True
        self.cursor_blink_timer = time.time()

    
    def add_character_at_cursor(self, char: str) -> None:
        self.text = util_text.insert_into_string(self.text, char, self.cursor_pos)
        self.cursor_pos += 1
        self.set_cursor_active()

    
    def draw(self, screen):
        """Draws the Input Field, call every game loop"""
        if self.active:
            # Cursor blinking
            if time.time() - self.cursor_blink_timer >= self.cursor_blink_rate_s:
                self.cursor_draw = not self.cursor_draw
                self.cursor_blink_timer = time.time()

            if self.border_width == 0:
                self.surface.fill(self.active_color)
            else:
                self.surface.fill(self.border_color)
                pygame.draw.rect(self.surface, self.active_color, (self.border_width, self.border_width, 
                                                                self.size[0] - self.border_width * 2, self.size[1] - self.border_width * 2))

        elif self.border_width == 0:
            self.surface.fill(self.bg_color)
        else:
            self.surface.fill(self.border_color)
            pygame.draw.rect(self.surface, self.bg_color, (self.border_width, self.border_width, 
                                                        self.size[0] - self.border_width * 2, self.size[1] - self.border_width * 2))

        #rendering text
        if self.text == "":
            placeholder_txt = self.font.render(self.placeholder_txt, True, self.placeholder_color)
            placeholder_txt.set_alpha(100)
            self.__draw_text(placeholder_txt)
        else:
            text = self.font.render(self.text, True, self.text_color)
            self.__draw_text(text)

        # Draw cursor
        if self.active and self.cursor_draw:
            text_w_to_cursor = self.font.size(self.text[0:self.cursor_pos])[0] + self.font.size("0")[0] // 2
            rect = self.cursor_surf.get_rect(midleft=(text_w_to_cursor, self.size[1]//2))

            self.surface.blit(self.cursor_surf, rect)

        screen.blit(self.surface, self.pos)
        

    def on_keydown(self, event: pygame.event.Event):
        """Handles OnKeydown events, call under 'if event.type == pygame.KEYDOWN:'"""
        self.process_deleting(event)
        self.process_cursor_move(event)



    def on_left_mouse_click(self, rect_override:"pygame.rect.Rect"=None, boundaries:"pygame.rect.Rect"=None):
        """Handles left mouseclicks. Call under ONMOUSEBUTTONDOWN and left click event. Rect override and boundaries are there for overriding collision detection (if pos isn't relative screen)"""
        if rect_override == None:
            rect_override = self.rect

        mouse_pos = input_overrides.get_mouse_pos()
        self.active = rect_override.collidepoint(mouse_pos)
        self.cursor_pos = len(self.text)

        if boundaries:
            if not boundaries.collidepoint(mouse_pos):
                self.active = False

        self.fix_text()


    def get_value(self):
        if self.text != "": return self.text

        match (self.empty_return_val):
            case "placeholder":
                return self.placeholder_txt
            case "start_value":
                return self.start_value
            
        return self.empty_return_val
        