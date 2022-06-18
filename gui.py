import pygame


# class GUI_object(object):
#     visible: bool = None


# class Checkbox(object):
#     state: bool = None

#     def __init__(self, state: bool=False):
#         self.state = state


class Textbox(object):
    rendered: pygame.Surface = None
    rectangle: pygame.Rect = None

    def __init__(
        self,
        text: str,
        position: tuple,
        foreground_color: tuple,
        background_color: tuple,
        font: pygame.font.Font,
    ):

        self.rendered = font.render(text, True, foreground_color, background_color)
        self.rectangle = self.rendered.get_rect()
        self.rectangle.x = position[0]
        self.rectangle.y = position[1]

    def render(self, display: pygame.Surface):
        display.blit(self.rendered, self.rectangle)


class Button(object):
    pass


class Inputbox(object):
    pass


class Frame(object):

    surface: pygame.Surface = None
    rectangle: pygame.Rect = None

    #position: tuple = None
    color: tuple = None
    gui_objects: list = None
    font: pygame.font.Font = None
    
    def __init__(
        self,
        position: tuple,
        size: tuple,
        background_color: tuple,
        font: pygame.font.Font,
    ):
        self.gui_objects = []
        self.surface = pygame.Surface(size)
        self.rectangle = pygame.Rect(position[0], position[1], size[0], size[1])
        self.color = background_color
        self.font = font

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

    def render(self, display: pygame.Surface):
        self.surface.fill(self.color)
        
        for gui_object in self.gui_objects:
            gui_object.render(self.surface)
        
        display.blit(self.surface, self.rectangle)

class Page(object):
    font: pygame.font.Font = None
    frames: list = None

    def __init__(self, font_path: str, font_size: int):
        self.frames = []
        self.font = pygame.font.Font(font_path, font_size)

    def add_frame(self, position: tuple, size: tuple, background_color: tuple):
        self.frames.append(Frame(position, size, background_color, self.font))

    def render(self, display: pygame.Surface):
        for frame in self.frames:
            frame.render(display)
