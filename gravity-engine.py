import gravity
import pygame
import gui
from vector import *

pygame.init()

FRAME_RATE: int = 25
RESOLUTION: tuple = (600, 600)
FONT_PATH: str = None
FONT_SIZE: int = 30
ZOOM_SPEED: float = 0.05
CAM_SPEED: int = 3

LITTLE: float = 0.0001
APP_NAME: str = "Gravity-Engine"

EVENTS = {"QUITE": 0, "PAUSE": 1, "ZOOM": 2}
STATES = {"OFF": 0, "ON": 1, "PAUSE": 2}

COLORS = {
    "BLACK": (10, 10, 10),
    "L_BLACK": (40, 40, 40),
    "L_RED": (255, 100, 100),
    "L_GREEN": (100, 255, 100),
    "L_BLUE": (100, 100, 255),
    "WHITE": (240, 240, 240),
}


class Event(object):
    id: int = None
    value = None

    def __init__(self, id: int, value=None):
        self.id = id
        self.value = value


class Window(object):
    resolution = None
    display: pygame.Surface = None
    frame_color: tuple = None

    def __init__(
        self,
        window_resolution: tuple,
        window_name: str,
        frame_color: tuple = COLORS["BLACK"],
    ):
        self.resolution = window_resolution
        self.display = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption(window_name)
        self.frame_color = frame_color

    def get_events(self):
        events: list = []
        event: int = None

        for pygame_event in pygame.event.get():

            if pygame_event.type == pygame.QUIT:
                event = Event(EVENTS["QUITE"])

            elif pygame_event.type == pygame.KEYDOWN:

                if pygame_event.key == pygame.K_ESCAPE:
                    event = Event(EVENTS["PAUSE"])
                else:
                    continue

            elif pygame_event.type == pygame.MOUSEWHEEL:
                event = Event(EVENTS["ZOOM"], pygame_event.y)

            else:
                continue

            events.append(event)

        return events

    def render(self, gui_page: gui.Page):

        self.display.fill(self.frame_color)  # clear screen
        gui_page.render(self.display)  # render current gui page

        pygame.display.flip()  # flip buffer


class Cam(object):
    size: tuple = None
    translation: Vector = None
    scale: int = None

    def __init__(self, size: tuple, translation: Vector, scale: int):
        self.size = size
        self.translation = translation
        self.scale = scale

    def transform(self, transformation: Vector):
        self.translation = add_vectors(
            self.translation,
            Vector(
                transformation.x / (self.scale + LITTLE),
                transformation.y / (self.scale + LITTLE),
            ),
        )

    def set_scale(self, new_scale: int):
        self.scale = new_scale


class Scene(object):

    objects: dict = None
    connections: list = None  # 2D list: for each object there is a separate list with True on indexes, where object is influenced by object of this index.
    cam: Cam = None

    def __init__(
        self,
        cam_size: tuple,
        cam_translation: Vector,
        cam_scale: int,
        objects: dict = {},
        objects_connections: list = list(),
    ):
        self.objects = objects
        self.connections = objects_connections
        self.cam = Cam(cam_size, cam_translation, cam_scale)

    def __render_object__(self, object: gravity.Object, surface: pygame.Surface):
        pygame.draw.circle(
            surface,
            object.color,
            (
                object.position.x * self.cam.scale
                + self.cam.translation.x * self.cam.scale,
                object.position.y * self.cam.scale
                + self.cam.translation.y * self.cam.scale,
            ),
            object.radius * self.cam.scale,
        )

    def __generate_inluancing_objects__(self, connections_index):
        object_index: int = 0
        influancing_objects: list = []
        objects = tuple(self.objects.values())

        for connection in self.connections[connections_index]:
            if connection == True:
                influancing_objects.append(objects[object_index])

            object_index += 1

        return influancing_objects

    def add_object(
        self,
        id,
        material_object: gravity.Object,
        object_connections: list,
        is_influancer: bool = True,
    ):

        for i in range(len(self.connections)):
            self.connections[i].append(is_influancer)

        self.objects[id] = material_object
        self.connections.append(object_connections)

    def update(self):
        object_index: int = 0

        for material_object in self.objects.values():
            material_object.update(self.__generate_inluancing_objects__(object_index))
            object_index += 1

    def render(self, surface: pygame.Surface):
        for material_object in self.objects.values():
            self.__render_object__(material_object, surface)


class Simulation(object):

    window: Window = None
    scene: Scene = None
    state: int = None
    clock: pygame.time.Clock = None
    frame_rate: int = None

    main_interface: gui.Page = None
    menu_interface: gui.Page = None

    def __init__(
        self,
        window_resolution: tuple,
        frame_rate: int,
        frame_color: tuple,
        cam_size: tuple,
        cam_translation: Vector,
        scale: int,
    ):
        self.window = Window(window_resolution, APP_NAME, frame_color)
        self.frame_rate = frame_rate
        self.scene = Scene(cam_size, cam_translation, scale)
        self.clock = pygame.time.Clock()

    def handle_events_simulation(self):
        for event in self.window.get_events():
            if event.id == EVENTS["QUITE"]:
                pygame.quit()
                self.state = STATES["OFF"]

            elif event.id == EVENTS["PAUSE"]:
                self.state = STATES["PAUSE"]

            elif event.id == EVENTS["ZOOM"]:
                self.scene.cam.set_scale(
                    self.scene.cam.scale
                    + ZOOM_SPEED * event.value# * (abs(event.value) / 2)
                )
                #self.scene.cam.translation = Vector(self.scene.cam.translation.x * self.scene.cam.scale, self.scene.cam.translation.y * self.scene.cam.scale)
                #self.scene.cam.transform(Vector(-ZOOM_SPEED * 290 * event.value * self.scene.cam.scale, -ZOOM_SPEED * 290 * event.value * self.scene.cam.scale))

    def handle_events_menu(self):
        for event in self.window.get_events():
            if event.id == EVENTS["QUITE"]:
                pygame.quit()
                self.state = STATES["OFF"]

            elif event.id == EVENTS["PAUSE"]:
                self.state = STATES["ON"]

    def handle_keys(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] == True:
            self.scene.cam.transform(Vector(0, CAM_SPEED))
        elif keys[pygame.K_DOWN] == True:
            self.scene.cam.transform(Vector(0, -CAM_SPEED))
        if keys[pygame.K_RIGHT] == True:
            self.scene.cam.transform(Vector(-CAM_SPEED, 0))
        elif keys[pygame.K_LEFT] == True:
            self.scene.cam.transform(Vector(CAM_SPEED, 0))

    def create_main_interface(self):
        self.main_interface = gui.Page(FONT_PATH, FONT_SIZE)
        self.main_interface.add_frame(
            "simulation", (10, 10), (580, 580), COLORS["BLACK"]
        )
        self.main_interface.frames["simulation"].add_scene_view(self.scene)

    def create_menu_interface(self):
        self.menu_interface = gui.Page(FONT_PATH, FONT_SIZE)
        self.menu_interface.add_frame("main", (150, 100), (300, 400), COLORS["L_BLUE"])

        self.menu_interface.frames["main"].add_textbox(
            "- Pause -", (100, 10), COLORS["L_GREEN"], COLORS["L_RED"]
        )

    def main_loop(self):
        self.create_menu_interface()
        self.create_main_interface()

        self.state = STATES["ON"]

        while self.state != STATES["OFF"]:
            self.clock.tick(self.frame_rate)

            if self.state == STATES["ON"]:
                self.scene.update()

                self.window.render(self.main_interface)

                self.handle_keys()
                self.handle_events_simulation()

            else:
                self.window.render(self.menu_interface)

                self.handle_events_menu()


app = Simulation(RESOLUTION, FRAME_RATE, COLORS["L_BLACK"], RESOLUTION, Vector(200, 200), 1)

app.scene.add_object(
    "asteroid", gravity.Object(pow(10, 18), Vector(0, 0), 20, COLORS["L_RED"]), [False]
)
app.scene.add_object(
    "satellite",
    gravity.Object(10000, Vector(200, 20), 5, COLORS["L_GREEN"]),
    [True, False],
)
app.scene.objects["satellite"].set_velocity(Vector(0, 0.07))

print(app.scene.connections)
print(app.scene.objects)

app.main_loop()
