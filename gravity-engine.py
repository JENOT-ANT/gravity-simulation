from gravity import Object
import pygame
import gui
from vector import *

pygame.init()

FRAME_RATE: int = 25
RESOLUTION: tuple[int, int] = (600, 600)
FONT_PATH: str | None = None
FONT_SIZE: int = 30
ZOOM_SPEED: float = 0.05
CAM_SPEED: int = 3

LITTLE: float = 0.0001
APP_NAME: str = 'Gravity-Engine'

EVENTS = {'QUIT': 0, 'KEY': 1, 'ZOOM': 2, 'MOUSE_LEFT_BUTTON': 3, 'BUTTON': 4}
STATES = {'OFF': 0, 'ON': 1, 'PAUSE': 2, 'MENU': 3}

COLORS = {
    'BLACK': (10, 10, 10),
    'L_BLACK': (40, 40, 40),
    'L_RED': (255, 100, 100),
    'L_GREEN': (100, 255, 100),
    'L_BLUE': (100, 100, 255),
    'WHITE': (240, 240, 240),

    'GRAY': (80, 80, 100),
}


class Event(object):
    '''Useless pygame event wrapper.'''
    
    event_id: int
    value = None

    def __init__(self, event_id: int, value=None):
        self.event_id = event_id
        self.value = value


class Window:
    '''Just another useless wrapper around pygame display and envents.'''

    resolution: tuple[int, int]
    display: pygame.Surface
    frame_color: tuple[int, int, int]


    def __init__(self, window_resolution: tuple[int, int], window_name: str, frame_color: tuple = COLORS['BLACK']):
        self.resolution = window_resolution
        self.display = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption(window_name)
        self.frame_color = frame_color

    def get_mouse_position(self):
        return pygame.mouse.get_pos()

    def get_events(self, gui_page: gui.Page) -> list[Event]:
        events: list[Event] = []
        button: tuple[str | int, str | int] | None # (frame_id, button_id)

        for pygame_event in pygame.event.get():

            if pygame_event.type == pygame.QUIT:
                events.append(Event(EVENTS['QUIT']))

            elif pygame_event.type == pygame.KEYDOWN:
                if gui_page.focus is None:
                    events.append(Event(EVENTS['KEY'], pygame_event.key))
                    continue
                
                if pygame_event.key == pygame.K_BACKSPACE:
                    gui_page.focus.text = gui_page.focus.text[:-1]
                elif pygame_event.key == pygame.K_ESCAPE:
                    gui_page.focus.update(False)
                    gui_page.focus = None
                    continue
                else:
                    gui_page.focus.text += pygame_event.unicode
                
                gui_page.focus.update()

            elif pygame_event.type == pygame.MOUSEWHEEL:
                events.append(Event(EVENTS['ZOOM'], pygame_event.y))

            elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
                if pygame_event.button == pygame.BUTTON_LEFT:
                    gui_page.update_focus_state(pygame_event.pos, True)
                    
                    button = gui_page.get_clicked_button(pygame_event.pos, True)
                    
                    if button != None:
                        events.append(Event(EVENTS['BUTTON'], button))
                    
            else:
                continue

        return events

    def render(self, gui_page: gui.Page):

        self.display.fill(self.frame_color)  # clear screen
        gui_page.render(self.display)

        pygame.display.flip()


class Cam:
    size: tuple[int, int]
    translation: Vector
    scale: int

    def __init__(self, size: tuple[int, int], translation: Vector, scale: int):
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


class Scene:

    objects: dict[str | int, Object] # {id: Object}
    connections: dict[str | int, list[Object]] # {id: [Object, ...]}
    cam: Cam

    def __init__(self, cam_size: tuple, cam_translation: Vector, cam_scale: int):
        self.objects = {}
        self.connections = {}
        self.cam = Cam(cam_size, cam_translation, cam_scale)


    def _render_object(self, object: Object, surface: pygame.Surface):
        pygame.draw.circle(
            surface,
            object.color,
            (
                object.position.x * self.cam.scale + self.cam.translation.x * self.cam.scale,
                object.position.y * self.cam.scale + self.cam.translation.y * self.cam.scale,
            ),
            object.radius * self.cam.scale,
        )

    def add_object(self, object_id: str | int, material_object: Object, connections_by_id: list[str | int], is_influancer: bool = True) -> None:
        self.objects[object_id] = material_object
        self.connections[object_id] = []

        for _object_id in connections_by_id:
            self.connections[object_id].append(self.objects[_object_id])

        if is_influancer is False:
            return
        
        for _object_id in self.connections:
            if _object_id != object_id:
                self.connections[_object_id].append(self.objects[object_id])

    def update(self):
        for object_id in self.objects:
            self.objects[object_id].update(self.connections[object_id])

    def render(self, surface: pygame.Surface):
        for material_object in self.objects.values():
            self._render_object(material_object, surface)


class Simulation:

    window: Window
    scene: Scene
    state: int
    clock: pygame.time.Clock
    frame_rate: int

    main_interface: gui.Page
    menu_interface: gui.Page

    def __init__(self, window_resolution: tuple[int, int], frame_rate: int, frame_color: tuple[int, int, int], cam_size: tuple, cam_translation: Vector, scale: int):
        self.window = Window(window_resolution, APP_NAME, frame_color)
        self.frame_rate = frame_rate
        self.scene = Scene(cam_size, cam_translation, scale)
        self.clock = pygame.time.Clock()

    def _handle_events_simulation(self):
        for event in self.window.get_events(self.main_interface):

            if event.event_id == EVENTS['QUIT']:
                pygame.quit()
                self.state = STATES['OFF']

            elif event.event_id == EVENTS['KEY']:
                if event.value == pygame.K_SPACE:
                    self.state = STATES['PAUSE'] if self.state == STATES['ON'] else STATES['ON']
                elif event.value == pygame.K_ESCAPE:
                    self.state = STATES['MENU']
            
            elif event.event_id == EVENTS['ZOOM']:
                self.scene.cam.set_scale(self.scene.cam.scale + ZOOM_SPEED * event.value)
            
            elif event.event_id == EVENTS['BUTTON']:
                if event.value[0] == 'simulation':
                    if event.value[1] == 'menu':
                        self.state = STATES['MENU']

    def _handle_events_menu(self):
        for event in self.window.get_events(self.menu_interface):

            if event.event_id == EVENTS['QUIT']:
                pygame.quit()
                self.state = STATES['OFF']

            elif event.event_id == EVENTS['KEY']:
                if event.value == pygame.K_ESCAPE:
                    self.state = STATES['ON']
            

    def _handle_keys(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] == True:
            self.scene.cam.transform(Vector(0, CAM_SPEED))
        elif keys[pygame.K_DOWN] == True:
            self.scene.cam.transform(Vector(0, -CAM_SPEED))
        if keys[pygame.K_RIGHT] == True:
            self.scene.cam.transform(Vector(-CAM_SPEED, 0))
        elif keys[pygame.K_LEFT] == True:
            self.scene.cam.transform(Vector(CAM_SPEED, 0))

    def _create_main_interface(self):
        self.main_interface = gui.Page(FONT_PATH, FONT_SIZE)
        
        self.main_interface.add_frame(
            'simulation', (10, 10), (RESOLUTION[0] - 20, RESOLUTION[1] - 20), COLORS['BLACK']
        )
        self.main_interface.frames['simulation'].add_scene_view(self.scene)
        self.main_interface.frames['simulation'].add_button('menu', '|menu|', (10, 10), COLORS['WHITE'], COLORS['L_BLUE'], COLORS['L_GREEN'])
        
        self.main_interface.add_frame(
            'panel', (RESOLUTION[0] - 110, 10), (100, RESOLUTION[1] - 20), COLORS['GRAY']
        )
        self.main_interface.frames['panel'].add_inputbox('test1', '', (5, 10), 90, COLORS['WHITE'], COLORS['L_BLACK'])
        self.main_interface.frames['panel'].add_inputbox('test2', '', (5, 40), 90, COLORS['WHITE'], COLORS['L_BLACK'])

    def _create_menu_interface(self):
        self.menu_interface = gui.Page(FONT_PATH, FONT_SIZE)
        
        self.menu_interface.add_frame('main', (RESOLUTION[0] // 2 - 150, 100), (300, 400), COLORS['L_BLUE'])

        self.menu_interface.frames['main'].add_textbox(
            '- Pause -', (100, 10), COLORS['L_GREEN'], COLORS['L_RED']
        )

    def start(self):
        self._create_main_interface()
        self._create_menu_interface()

        self.state = STATES['ON']

        while self.state != STATES['OFF']:
            self.clock.tick(self.frame_rate)

            if self.state == STATES['ON']:
                self.scene.update()

                self.window.render(self.main_interface)

                self._handle_keys()
                self._handle_events_simulation()
                

            elif self.state == STATES['PAUSE']:
                self.window.render(self.main_interface)
                self._handle_keys()
                self._handle_events_simulation()

            elif self.state == STATES['MENU']:
                self.window.render(self.menu_interface)

                self._handle_events_menu()


def main():
    app = Simulation(RESOLUTION, FRAME_RATE, COLORS['L_BLACK'], RESOLUTION, Vector(200, 200), 1)

    app.scene.add_object(
        'asteroid', Object(pow(10, 18), Vector(0, 0), 20, COLORS['L_RED']), [],
    )
    app.scene.add_object(
        'satellite', Object(10000, Vector(200, 20), 5, COLORS['L_GREEN']), ['asteroid',],
    )
    app.scene.objects['satellite'].set_velocity(Vector(0, 0.5))

    print(app.scene.connections)
    print(app.scene.objects)

    app.start()


if __name__ == '__main__':
    main()
