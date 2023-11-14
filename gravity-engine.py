from gravity import Object, EARTH_MASS
import pygame
import gui
from vector import *
from math import dist

pygame.init()

FRAME_RATE: int = 60
ENGINE_RATE: int = 5
RESOLUTION: tuple[int, int] = (800, 600)
CAM_SIZE: tuple[int, int] = (RESOLUTION[0] - 130, RESOLUTION[1] - 20)
FONT_PATH: str | None = None
FONT_SIZE: int = 30
ZOOM_SPEED: float = 0.0002
CAM_SPEED: int = 4

LITTLE: float = pow(10, -6)
APP_NAME: str = 'Gravity-Engine'

EVENTS = {'QUIT': 0, 'KEY': 1, 'ZOOM': 2, 'MOUSE_LEFT_BUTTON': 3, 'MOUSE_RIGHT_BUTTON': 4, 'BUTTON': 5}
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


    def __init__(self, window_resolution: tuple[int, int], window_name: str, frame_color: tuple[int, int, int] = COLORS['BLACK']):
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
                        events.append(Event(EVENTS['MOUSE_LEFT_BUTTON'], gui_page.local_mouse_position(pygame_event.pos)))
                elif pygame_event.button == pygame.BUTTON_RIGHT:
                    events.append(Event(EVENTS['MOUSE_RIGHT_BUTTON'], gui_page.local_mouse_position(pygame_event.pos)))
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
    scale: float

    def __init__(self, size: tuple[int, int], translation: Vector, scale: float):
        self.size = size
        self.translation = translation
        self.scale = scale

    def translate(self, translation: Vector):
        self.translation = add_vectors(
            self.translation,
            Vector(
                translation.x / (self.scale + LITTLE),
                translation.y / (self.scale + LITTLE),
            ),
        )

    def set_scale(self, new_scale: float):
        self.scale = new_scale


class Scene:

    objects: dict[str | int, Object] # {id: Object}
    connections: dict[str | int, list[Object]] # {id: [Object, ...]}
    cam: Cam

    def __init__(self, cam_size: tuple[int, int], cam_translation: Vector, cam_scale: float):
        self.objects = {}
        self.connections = {}
        self.cam = Cam(cam_size, cam_translation, cam_scale)


    def _render_object(self, object: Object, surface: pygame.Surface):
        pygame.draw.circle(
            surface,
            object.color,
            (
                (object.position.x + self.cam.translation.x) * self.cam.scale + self.cam.size[0] / 2,
                (object.position.y + self.cam.translation.y) * self.cam.scale + self.cam.size[1] / 2,
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
        
        # pygame.draw.circle(surface, (200, 50, 50), (0, 0), 5)
        # pygame.draw.circle(surface, (200, 50, 50), (self.cam.size[0] / 2, self.cam.size[1] / 2), 5)
        # pygame.draw.circle(surface, (200, 50, 50), (self.cam.size[0], self.cam.size[1]), 5)


class App:

    window: Window
    scene: Scene
    state: int
    clock: pygame.time.Clock
    frame_rate: int

    main_interface: gui.Page
    menu_interface: gui.Page

    click_waiter: bool

    def __init__(self, window_resolution: tuple[int, int], frame_rate: int, frame_color: tuple[int, int, int], cam_size: tuple[int, int], cam_translation: Vector, scale: int):
        self.window = Window(window_resolution, APP_NAME, frame_color)
        self.frame_rate = frame_rate
        self.scene = Scene(cam_size, cam_translation, scale)
        self.clock = pygame.time.Clock()
        self.click_waiter = False

    def _handle_create_button(self):
        name: str = self.main_interface.frames['panel'].iboxes['name'].text
        mass: float = float(self.main_interface.frames['panel'].iboxes['mass'].text) * EARTH_MASS
        position: Vector = Vector(
            float(self.main_interface.frames['panel'].iboxes['x'].text),
            float(self.main_interface.frames['panel'].iboxes['y'].text)
        )
        radius: float = float(self.main_interface.frames['panel'].iboxes['radius'].text)
        velocity: Vector = Vector(
            float(self.main_interface.frames['panel'].iboxes['v_x'].text),
            float(self.main_interface.frames['panel'].iboxes['v_y'].text)
        )

        if name in self.scene.objects.keys():
            self.scene.objects[name] = Object(mass, position, radius, (50, 200, 100))
        else:
            self.scene.add_object(name, Object(mass, position, radius, (50, 200, 100)), [key for key in self.scene.objects.keys()])

        self.scene.objects[name].set_velocity(velocity)

        self.main_interface.frames['panel'].iboxes['name'].text = ''
        self.main_interface.frames['panel'].iboxes['mass'].text = ''
        self.main_interface.frames['panel'].iboxes['radius'].text = ''
        self.main_interface.frames['panel'].iboxes['v_x'].text = ''
        self.main_interface.frames['panel'].iboxes['v_y'].text = ''
        self.main_interface.frames['panel'].iboxes['x'].text = ''
        self.main_interface.frames['panel'].iboxes['y'].text = ''
        
        self.main_interface.frames['panel'].update_iboxes()

    def _handle_scene_click(self, mouse_local_position: tuple):
        material_object: Object
        world_mouse_position: tuple[float, float] = (
            (mouse_local_position[0] - self.scene.cam.size[0] / 2) / self.scene.cam.scale - self.scene.cam.translation.x,
            (mouse_local_position[1] - self.scene.cam.size[1] / 2) / self.scene.cam.scale - self.scene.cam.translation.y
        )

        for object_id in self.scene.objects.keys():
            material_object = self.scene.objects[object_id]
            
            if dist(material_object.position.to_tuple(), world_mouse_position) <= material_object.radius:
                self.main_interface.frames['panel'].iboxes['name'].text = str(object_id)
                self.main_interface.frames['panel'].iboxes['mass'].text = str(round(material_object.mass / EARTH_MASS, 6))
                self.main_interface.frames['panel'].iboxes['radius'].text = str(round(material_object.radius))
                self.main_interface.frames['panel'].iboxes['v_x'].text = str(round(material_object.velocity.x, 4))
                self.main_interface.frames['panel'].iboxes['v_y'].text = str(round(material_object.velocity.y, 4))
                self.main_interface.frames['panel'].iboxes['x'].text = str(round(material_object.position.x))
                self.main_interface.frames['panel'].iboxes['y'].text = str(round(material_object.position.y))
                
                self.main_interface.frames['panel'].update_iboxes()
                print(object_id)

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
                elif event.value[0] == 'panel':
                    if event.value[1] == 'create':
                        try:
                            self._handle_create_button()
                        except:
                            print('Incorrect values.')
                    elif event.value[1] == 'set':
                        if self.click_waiter is True:
                            self.click_waiter = False
                            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                        else:
                            self.click_waiter = True
                            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

            elif event.event_id == EVENTS['MOUSE_LEFT_BUTTON']:
                if self.click_waiter is True and event.value[0] == 'simulation':
                    self.main_interface.frames['panel'].iboxes['x'].text = str((event.value[1][0] - self.scene.cam.size[0] / 2) / self.scene.cam.scale - self.scene.cam.translation.x)
                    # self.main_interface.frames['panel'].iboxes['x'].text = str((event.value[1][0]) / self.scene.cam.scale - self.scene.cam.translation.x)
                    self.main_interface.frames['panel'].iboxes['x'].update(False)
                    self.main_interface.frames['panel'].iboxes['y'].text = str((event.value[1][1] - self.scene.cam.size[1] / 2) / self.scene.cam.scale - self.scene.cam.translation.y)
                    # self.main_interface.frames['panel'].iboxes['y'].text = str((event.value[1][1]) / self.scene.cam.scale - self.scene.cam.translation.y)
                    self.main_interface.frames['panel'].iboxes['y'].update(False)

                    self.click_waiter = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                elif self.state == STATES['PAUSE'] and event.value[0] == 'simulation':
                    self._handle_scene_click(event.value[1])

            elif event.event_id == EVENTS['MOUSE_RIGHT_BUTTON']:
                if self.click_waiter is True:
                    self.click_waiter = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


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

        if keys[pygame.K_UP] is True or (keys[pygame.K_w] is True and self.main_interface.focus == None):
            self.scene.cam.translate(Vector(0, CAM_SPEED))
        elif keys[pygame.K_DOWN] is True or (keys[pygame.K_s] is True and self.main_interface.focus == None):
            self.scene.cam.translate(Vector(0, -CAM_SPEED))
        
        if keys[pygame.K_RIGHT] is True or (keys[pygame.K_d] is True and self.main_interface.focus == None):
            self.scene.cam.translate(Vector(-CAM_SPEED, 0))
        elif keys[pygame.K_LEFT] is True or (keys[pygame.K_a] is True and self.main_interface.focus == None):
            self.scene.cam.translate(Vector(CAM_SPEED, 0))
        
        if keys[pygame.K_PAGEUP] is True or (keys[pygame.K_q] is True and self.main_interface.focus == None):
            self.scene.cam.set_scale(self.scene.cam.scale + ZOOM_SPEED)
        elif keys[pygame.K_PAGEDOWN] is True or (keys[pygame.K_e] is True and self.main_interface.focus == None):
            self.scene.cam.set_scale(self.scene.cam.scale - ZOOM_SPEED)

    def _create_main_interface(self):
        self.main_interface = gui.Page(FONT_PATH, FONT_SIZE)
        
        self.main_interface.add_frame(
            'simulation', (10, 10), CAM_SIZE, COLORS['BLACK']
        )
        self.main_interface.frames['simulation'].add_scene_view(self.scene)
        self.main_interface.frames['simulation'].add_button('menu', '|menu|', (10, 10), COLORS['WHITE'], COLORS['L_BLUE'], COLORS['L_GREEN'])
        
        self.main_interface.add_frame(
            'panel', (RESOLUTION[0] - 110, 10), (100, RESOLUTION[1] - 20), COLORS['GRAY']
        )
        
        self.main_interface.frames['panel'].add_textbox('name:', (5, 10), COLORS['WHITE'], COLORS['GRAY'])
        self.main_interface.frames['panel'].add_inputbox('name', '', (5, 35), 90, COLORS['WHITE'], COLORS['L_BLACK'])
        
        self.main_interface.frames['panel'].add_textbox('m [M+]:', (5, 65), COLORS['WHITE'], COLORS['GRAY'])
        self.main_interface.frames['panel'].add_inputbox('mass', '', (5, 90), 90, COLORS['WHITE'], COLORS['L_BLACK'])
        
        self.main_interface.frames['panel'].add_textbox('r [km]:', (5, 120), COLORS['WHITE'], COLORS['GRAY'])
        self.main_interface.frames['panel'].add_inputbox('radius', '', (5, 145), 90, COLORS['WHITE'], COLORS['L_BLACK'])

        self.main_interface.frames['panel'].add_textbox('v(x):', (5, 175), COLORS['WHITE'], COLORS['GRAY'])
        self.main_interface.frames['panel'].add_inputbox('v_x', '', (5, 200), 90, COLORS['WHITE'], COLORS['L_BLACK'])

        self.main_interface.frames['panel'].add_textbox('v(y):', (5, 230), COLORS['WHITE'], COLORS['GRAY'])
        self.main_interface.frames['panel'].add_inputbox('v_y', '', (5, 255), 90, COLORS['WHITE'], COLORS['L_BLACK'])


        self.main_interface.frames['panel'].add_textbox('x:', (5, 310), COLORS['WHITE'], COLORS['GRAY'])
        self.main_interface.frames['panel'].add_inputbox('x', '', (5, 335), 90, COLORS['WHITE'], COLORS['L_BLACK'])
        
        self.main_interface.frames['panel'].add_textbox('y:', (5, 365), COLORS['WHITE'], COLORS['GRAY'])
        self.main_interface.frames['panel'].add_inputbox('y', '', (5, 390), 90, COLORS['WHITE'], COLORS['L_BLACK'])
        
        self.main_interface.frames['panel'].add_button('set', '|set|', (25, 415), COLORS['WHITE'], COLORS['L_BLUE'], COLORS['WHITE'])

        self.main_interface.frames['panel'].add_button('create', '|create|', (15, 500), COLORS['GRAY'], COLORS['L_GREEN'], COLORS['WHITE'])


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
                for _ in range(ENGINE_RATE):
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
    app = App(RESOLUTION, FRAME_RATE, COLORS['L_BLACK'], CAM_SIZE, Vector(0, 0), pow(10, -2))

    app.scene.add_object(
        'earth', Object(EARTH_MASS, Vector(0, 0), 6378, COLORS['L_RED']), [],
    )
    app.scene.add_object(
        'satellite', Object(EARTH_MASS * 0.000001, Vector(10000, 20), 200, COLORS['L_GREEN']), ['earth',],
    )
    app.scene.objects['satellite'].set_velocity(Vector(0, 6.5))

    print(app.scene.connections)
    print(app.scene.objects)

    app.start()


if __name__ == '__main__':
    main()
