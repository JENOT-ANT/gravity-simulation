import gravity
import pygame
from vector import *

pygame.init()
OFF = 0
ON = 1
PAUSE = 2

BLACK = (40, 40, 40)
L_RED = (255, 100, 100)
L_GREEN = (100, 255, 100)
L_BLUE = (100, 100, 255)
WHITE = (240, 240, 240)


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

    def __init__(self, window_resolution: tuple, frame_color: tuple):
        self.resolution = window_resolution
        self.display = pygame.display.set_mode(self.resolution)
        self.frame_color = frame_color

    def update(self):
        self.display.blits()
        self.display.fill((0, 0, 0))


class Scene(object):
    objects: list = None
    connections: list = None  # 2D list: for each object there is a separate list with True on indexes, where object is influenced by object of this index.

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
        self.translation = translation
        self.scale = scale

    def transform(self, transformation: Vector):
        self.translation = add_vectors(self.translate, transformation)

    def set_scale(self, new_scale: int):
        self.scale = new_scale


class Simulation(object):

    window: Window = None
    cam: Cam = None
    scene: Scene = None
    state: int = None

    def __init__(
        self,
        window_resolution: tuple,
        frame_color: tuple,
        cam_translation: Vector,
        scale: int,
    ):
        self.window = Window(window_resolution, frame_color)
        self.cam = Cam(cam_translation, scale)
        self.scene = Scene()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quite()

    def main_loop(self):
        self.state = ON
        while self.state != OFF:
            pygame.clock.tick(self.frame_rate)

            self.handle_events()

            self.window.update()
