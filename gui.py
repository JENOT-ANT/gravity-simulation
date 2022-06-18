import pygame


class GUI_object(object):
    position: tuple = None
    visible: bool = None
    state: bool = None # enabled/disabled


class Checkbox(GUI_object):
    state: bool = None

    def __init__(self, state: bool=False):
        self.state = state


class Inputbox(GUI_object):
    pass


class Textbox(GUI_object):
    text: str = None

    def __init__(self, text):
        self.text = text

    def render(self):
        pass


class Button(GUI_object):
    pass


class Frame(GUI_object):
    gui_objects: list = None

    def render(self):
        for gui_object in self.gui_objects:
            gui_object.render()


class Page(object):
    
    def render(self):
        pass
