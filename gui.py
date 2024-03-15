import pygame


def _mouse_over(gui_object, mouse_position: tuple):
    object_rectangle: pygame.Rect = gui_object.rectangle

    if (
        mouse_position[0] >= object_rectangle.x and mouse_position[1] >= object_rectangle.y
        and mouse_position[0] <= object_rectangle.x + object_rectangle.width
        and mouse_position[1] <= object_rectangle.y + object_rectangle.height
    ):
        return True
    else:
        return False

def _clicked(gui_object, mouse_position: tuple[int, int], mouse_button_state: bool):
    if _mouse_over(gui_object, mouse_position) and mouse_button_state == True:
        return True
    else:
        return False


class Textbox:
    rendered: pygame.Surface
    rectangle: pygame.Rect

    def __init__(self, text: str, position: tuple[int, int], foreground_color: tuple, background_color: tuple, font: pygame.font.Font):
        self.rendered = font.render(text, True, foreground_color, background_color)
        self.rectangle = pygame.Rect(
            position[0],
            position[1],
            self.rendered.get_width(),
            self.rendered.get_height(),
        )

    def render(self, display: pygame.Surface):
        display.blit(self.rendered, self.rectangle)

class Inputbox:
    text: str
    rendered: pygame.Surface
    rectangle: pygame.Rect
    
    _position: tuple[int, int]
    _foreground: tuple[int, int, int]
    _background: tuple[int, int, int]
    _font: pygame.font.Font

    def update(self, active: bool=True):
        self.rendered = self._font.render(self.text + ('|' if active else ''), True, self._foreground)
        
    def __init__(self, text: str, position: tuple[int, int], width: int, foreground: tuple[int, int, int], background: tuple[int, int, int], font: pygame.font.Font):
        self.text = text

        self._position = position
        self._foreground = foreground
        self._background = background
        self._font = font

        self.update(False)
        self.rectangle = pygame.Rect(
            self._position[0],
            self._position[1],
            width,
            self.rendered.get_height(),
        )
        

    def render(self, display: pygame.Surface):
        pygame.draw.rect(display, self._background, self.rectangle, border_radius=5)
        display.blit(self.rendered, self.rectangle)

    def is_clicked(self, mouse_position, mouse_button_state):
        return _clicked(self, mouse_position, mouse_button_state)

class Button:
    rendered: pygame.Surface
    rectangle: pygame.Rect
    rendered_clicked: pygame.Surface

    def __init__(
        self,
        text: str,
        position: tuple,
        foreground_color: tuple,
        background_color: tuple,
        click_color: tuple,
        font: pygame.font.Font,
    ):

        self.rendered = font.render(text, True, foreground_color, background_color)
        self.rendered_clicked = font.render(text, True, foreground_color, click_color)
        self.rectangle = pygame.Rect(
            position[0],
            position[1],
            self.rendered.get_width(),
            self.rendered.get_height(),
        )

    def render(self, display: pygame.Surface):
        display.blit(self.rendered, self.rectangle)
    
    def is_clicked(self, mouse_position, mouse_button_state):
        return _clicked(self, mouse_position, mouse_button_state)


class Frame:
    surface: pygame.Surface
    rectangle: pygame.Rect

    enable: bool
    color: tuple
    gui_objects: list
    buttons: dict[str | int, Button]
    iboxes: dict[str | int, Inputbox]
    
    font: pygame.font.Font


    def __init__(self, position: tuple, size: tuple, background_color: tuple, font: pygame.font.Font):
        self.gui_objects = []
        self.buttons = {}
        self.iboxes = {}

        self.surface = pygame.Surface(size)
        self.rectangle = pygame.Rect(position[0], position[1], size[0], size[1])

        self.enable = True
        self.color = background_color
        self.font = font

    def get_clicked_buttons(self, mouse_position: tuple[int, int], mouse_button_state: bool):
        output: list = []

        for key in self.buttons.keys():
            if _clicked(self.buttons[key], mouse_position, mouse_button_state) == True:
                output.append(key)

        return output

    def add_textbox(
        self,
        text: str,
        local_position: tuple,
        foreground_color: tuple,
        background_color: tuple,
    ):
        self.gui_objects.append(
            Textbox(text, local_position, foreground_color, background_color, self.font)
        )

    def add_inputbox(
        self,
        ibox_id: str | int,
        text: str,
        local_position: tuple,
        width: int,
        foreground_color: tuple,
        background_color: tuple,
    ):
        self.iboxes[ibox_id] = Inputbox(text, local_position, width, foreground_color, background_color, self.font)
    
    def add_button(
        self,
        button_id: str | int,
        text: str,
        position: tuple,
        foreground_color: tuple,
        background_color: tuple,
        click_color: tuple,
    ):

        self.buttons[button_id] = Button(
            text, position, foreground_color, background_color, click_color, self.font
        )

    def add_scene_view(self, scene):
        self.gui_objects.append(scene)

    def render(self, display: pygame.Surface):
        
        if self.enable is False:
            return

        self.surface.fill(self.color)

        for gui_object in self.gui_objects:
            gui_object.render(self.surface)

        for button in self.buttons.values():
            button.render(self.surface)
        
        for ibox in self.iboxes.values():
            ibox.render(self.surface)

        display.blit(self.surface, self.rectangle)

    def get_clicked_button(self, mouse_position: tuple[int, int], mouse_button_state: bool):
        
        if self.enable is False:
            return None
        
        # convert mouse position to local
        _mouse_position: tuple[int, int] = (
            mouse_position[0] - self.rectangle.left,
            mouse_position[1] - self.rectangle.top,
        )

        for button_id in self.buttons:
            if self.buttons[button_id].is_clicked(_mouse_position, mouse_button_state):
                return button_id
        
        return None

    def get_clicked_inputbox(self, mouse_position: tuple[int, int], mouse_button_state: bool):
        
        if self.enable is False:
            return None
        
        # convert mouse position to local
        _mouse_position: tuple[int, int] = (
            mouse_position[0] - self.rectangle.left,
            mouse_position[1] - self.rectangle.top,
        )

        for ibox_id in self.iboxes:
            if self.iboxes[ibox_id].is_clicked(_mouse_position, mouse_button_state):
                return self.iboxes[ibox_id]
        
        return None

    def update_iboxes(self):
        for ibox in self.iboxes.values():
            ibox.update(False)
        
    def resurface(self):
        self.surface = pygame.Surface(self.rectangle.size)


class Page:
    font: pygame.font.Font
    frames: dict[str | int, Frame]
    focus: Inputbox | None

    def __init__(self, font_path: str | None, font_size: int):
        self.frames = {}
        self.focus = None
        self.font = pygame.font.Font(font_path, font_size)

    def add_frame(self, frame_id: str | int, position: tuple[int, int], size: tuple[int, int], background_color: tuple[int, int, int]):
        self.frames[frame_id] = Frame(position, size, background_color, self.font)

    def render(self, display: pygame.Surface):
        for frame in self.frames.values():
            frame.render(display)

    def local_mouse_position(self, mouse_position: tuple[int, int]):
        for frame in self.frames.keys():
            if _mouse_over(self.frames[frame], mouse_position):
                return frame, (mouse_position[0] - self.frames[frame].rectangle.x, mouse_position[1] - self.frames[frame].rectangle.y)

    def get_clicked_button(self, mouse_position: tuple[int, int], mouse_button_state: bool):
        button_id = None

        for frame_id in self.frames:
            button_id = self.frames[frame_id].get_clicked_button(mouse_position, mouse_button_state)
            
            if button_id is None:
                continue

            return (frame_id, button_id)

        return None
    
    def update_focus_state(self, mouse_position: tuple[int, int], mouse_button_state: bool) -> None:
        new_focus: Inputbox | None

        for frame_id in self.frames:
            new_focus = self.frames[frame_id].get_clicked_inputbox(mouse_position, mouse_button_state)
            
            if new_focus is not None:
                if self.focus is not None:
                    self.focus.update(False)
                
                self.focus = new_focus
                self.focus.update()
                return
        
        if mouse_button_state is True:
            if self.focus is not None:
                self.focus.update(False)
            
            self.focus = None
            
        