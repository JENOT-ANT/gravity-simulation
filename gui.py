import pygame


def mouse_over(gui_object, mouse_position: tuple):
    object_rectangle: pygame.Rect = gui_object.rectangle

    if (
        mouse_position[0] >= object_rectangle.top
        and mouse_position[1] >= object_rectangle.y
        and mouse_position[0] <= object_rectangle.x + object_rectangle.width
        and mouse_position[1] <= object_rectangle.y + object_rectangle.height
    ):
        return True
    else:
        return False


def clicked(gui_object, mouse_position, mouse_button_state):
    if mouse_over(gui_object, mouse_position) and mouse_button_state == True:
        return True
    else:
        return False

class GUI_object(object):
    rectangle: pygame.Rect = None

class Textbox(GUI_object):
    rendered: pygame.Surface = None
    #rectangle: pygame.Rect = None

    def __init__(
        self,
        text: str,
        position: tuple,
        foreground_color: tuple,
        background_color: tuple,
        font: pygame.font.Font,
    ):

        self.rendered = font.render(text, True, foreground_color, background_color)
        self.rectangle = pygame.Rect(
            position[0],
            position[1],
            self.rendered.get_width(),
            self.rendered.get_height(),
        )

    def render(self, display: pygame.Surface):
        display.blit(self.rendered, self.rectangle)


class Button(GUI_object):
    rendered: pygame.Surface = None
    rendered_clicked: pygame.Surface = None
    #rectangle: pygame.Rect = None

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
        return clicked(self, mouse_position, mouse_button_state)

class Inputbox(GUI_object):
    pass


class Frame(GUI_object):

    surface: pygame.Surface = None
    #rectangle: pygame.Rect = None

    color: tuple = None
    gui_objects: list = None
    buttons: dict = None
    font: pygame.font.Font = None

    def __init__(
        self,
        position: tuple,
        size: tuple,
        background_color: tuple,
        font: pygame.font.Font,
    ):
        self.gui_objects = []
        self.buttons = {}

        self.surface = pygame.Surface(size)
        self.rectangle = pygame.Rect(position[0], position[1], size[0], size[1])

        self.color = background_color
        self.font = font

    def get_clicked_buttons(self, mouse_position, mouse_button_state):
        output: list = []

        for key in self.buttons.keys():
            if clicked(self.buttons[key], mouse_position, mouse_button_state) == True:
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

    def add_button(
        self,
        id,
        text: str,
        position: tuple,
        foreground_color: tuple,
        background_color: tuple,
        click_color: tuple,
    ):

        self.buttons[id] = Button(
            text, position, foreground_color, background_color, click_color, self.font
        )

    def add_scene_view(self, scene):
        self.gui_objects.append(scene)

    def render(self, display: pygame.Surface):
        self.surface.fill(self.color)

        for gui_object in self.gui_objects:
            gui_object.render(self.surface)

        for button in self.buttons.values():
            button.render(self.surface)

        display.blit(self.surface, self.rectangle)

    def get_clicked_button(self, mouse_position, mouse_button_state):
        for id in self.buttons.keys():
            if self.buttons[id].is_clicked(mouse_position, mouse_button_state) == True:
                return id
        
        return None

class Page(object):
    font: pygame.font.Font = None
    frames: dict = None

    def __init__(self, font_path: str, font_size: int):
        self.frames = {}
        self.font = pygame.font.Font(font_path, font_size)

    def add_frame(self, id, position: tuple, size: tuple, background_color: tuple):
        self.frames[id] = Frame(position, size, background_color, self.font)

    def render(self, display: pygame.Surface):
        for frame in self.frames.values():
            frame.render(display)

    def get_clicked_button(self, mouse_position: tuple, mouse_button_state: bool):
        button_id = None

        for frame_id in self.frames.keys():
            button_id = self.frames[frame_id].get_clicked_button(mouse_position, mouse_button_state)
            
            if button_id != None:
                return (frame_id, button_id)

        return None