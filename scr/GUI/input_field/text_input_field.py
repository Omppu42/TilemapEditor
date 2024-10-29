import pygame

from . import input_field_base

class TextInputField(input_field_base.InputField):
    def __init__(self, pos: tuple, size: tuple, max_chars, bg_color=(155,155,155), active_color=(200,200,200),
                start_value="", placeholder="", **kwargs):
        super().__init__(pos, size, max_chars, bg_color=bg_color, active_color=active_color, start_value=start_value, placeholder=placeholder, **kwargs)
    
    # PRIVATE -------------
    def __process_key(self, event: "pygame.event.Event") -> None:
        key = pygame.key.name(event.key)
        key = key.replace("[", "")
        key = key.replace("]", "")

        # SPECIALS
        if event.key == pygame.K_SPACE:
            if self.cursor_pos > 0 and self.text[self.cursor_pos - 1] == " ": return
            self.add_character_at_cursor(" ")

        # TYPING
        if len(key) > 1: return
        
        shift = event.mod & pygame.KMOD_SHIFT
        control = event.mod & pygame.KMOD_CTRL

        if control: return

        if key == "-" and shift:
            self.add_character_at_cursor("_")
            return

        self.add_character_at_cursor(key if not shift else key.upper())


    # PUBLIC ---------------    
    def set_cursor_active(self) -> None:
        super().set_cursor_active()


    def on_keydown(self, event: pygame.event.Event):
        """Handles OnKeydown events, call under 'if event.type == pygame.KEYDOWN:'"""
        if not self.active: return
        super().on_keydown(event)

        if event.key in self.forbidden_chars: return                    # Key is allowed to be typed
        if len(self.text) >= self.max_chars: return                     # Text lenght does not exceed the max length
        if self.font.size(self.text)[0] >= self.size[0] - 40: return    # Another char will not exceed the size of the input field

        self.__process_key(event)