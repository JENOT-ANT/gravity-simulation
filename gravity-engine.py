import gravity
import pygame
from vector import *

pygame.init()
OFF = 0
ON = 1
PAUSE = 2


class Color(object):
    red: int = None
    green: int = None
    blue: int = None

    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __call__(self):
        return (self.red, self.green, self.blue)


class Window(object):
    resolution = None
    display: pygame.Surface = None
    frame_color: tuple = None

    def __init__(self, window_resolution: tuple):
        self.display = pygame.display.set_mode(self.resolution)

    def update(self):
        self.display.blits()
        self.display.fill((0, 0, 0))


class Scene(object):
    objects: list = None

    def __init__(self):
        pass

    def add_object(self):
        pass

    def update(self):
        pass


class Cam(object):
    translation: Vector = None
    scale: int = None

    def __init__(self, translation, scale):
        pass


class Simulation(object):

    window: Window = None
    cam: Cam = None
    scene: Scene = None
    state: int = None

    def __init__(self):
        self.window = Window()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quite()

    def main_loop(self):
        while self.state != 0:
            pygame.clock.tick(self.frame_rate)
            
            self.handle_events()

            self.window.update()
