import pygame

class GUI_object(object):
    position: tuple = None

    def render(self, display: pygame.Surface):
        pass

class Textbox(GUI_object):
    pass


class Button(GUI_object):
    pass


class Frame(GUI_object):
    pass


class Page(object):
    pass
