'''
This is crude code where the whole project begins.
It's not very good piece of code, it's just a root of this project,
which, I hope, will be a little more cleaner.

INSTRUCTION:
    esc     > quite
    arrows  > camera movement
    +/-     > zoom in/out
    r       > leave/delete a trace
'''

import pygame
import math

pygame.init()

RESOLUTION = (1000, 700)
G = 6.67430 * pow(10, -3)
ANIMATION_SPEED = 200
FRAME_RATE = 30

display = pygame.display.set_mode(RESOLUTION)
clock = pygame.time.Clock()


class Vector(object):
    x = None
    y = None

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_value(self):
        return math.sqrt(pow(self.x, 2) + pow(self.y, 2))


def add_vectors(v1, v2):
    return Vector(v1.x + v2.x, v1.y + v2.y)


class Object(object):

    RECTANGLE = pygame.Rect(0, 0, 10, 10)
    position = [0, 0]
    mass = None
    force = Vector(0, 0)
    acceleration = Vector(0, 0)
    velocity = Vector(0, 0)

    radius = 0
    color = (210, 210, 200)

    def __init__(self, mass, position, radius, color):
        self.mass = mass
        self.position = position
        self.radius = radius
        self.color = color

    def set_velocity(self, velocity):
        self.velocity = velocity

    def calculate_gravity(self, objects):
        gravity = Vector(0, 0)
        r_distance = 0
        distance = Vector(0, 0)
        value = 0
        angle = 0

        for obj in objects:
            r_distance = math.dist(obj.position, self.position)

            if r_distance >= obj.radius + self.radius:
                value = (G * obj.mass * self.mass) / pow(r_distance, 2)

                distance.x = obj.position[0] - self.position[0]
                distance.y = obj.position[1] - self.position[1]

                if distance.x != 0:
                    angle = math.atan(distance.y / distance.x)
                else:
                    angle = 0

                if distance.x > 0:
                    gravity.x += math.cos(angle) * value
                    gravity.y += math.sin(angle) * value
                else:
                    gravity.x -= math.cos(angle) * value
                    gravity.y -= math.sin(angle) * value

        self.force = gravity

    def calcualte_other_forces(self, force):
        self.force = add_vectors(self.force, force)

    def calculate_acceleration(self):
        self.acceleration = Vector(
            self.force.x / self.mass, self.force.y / self.mass)

    def update_velocity(self):
        self.velocity = add_vectors(self.velocity, self.acceleration)

    def update_position(self, objects):
        update = True
        updated_position = [self.position[0] +
                            self.velocity.x, self.position[1] + self.velocity.y]

        for obj in objects:
            # (updated_position[0] > obj.position[0] - obj.radius and updated_position[0] < obj.position[0] + obj.radius) and (updated_position[1] > obj.position[1] - obj.radius and updated_position[1] < obj.position[1] + obj.radius):
            if math.dist(updated_position, obj.position) < obj.radius + self.radius and obj.mass > self.mass:
                # print(obj.color)
                update = False
                self.acceleration = obj.acceleration
                self.velocity = obj.velocity
                self.position[0] += self.velocity.x
                self.position[1] += self.velocity.y
                break

        if update == True:
            self.position = updated_position

    def update(self, objects, force=Vector(0, 0)):
        self.calculate_gravity(objects)
        self.calcualte_other_forces(force)
        self.calculate_acceleration()
        self.update_velocity()
        self.update_position(objects)

    def render(self, scale, translation):
        #pygame.draw.circle(display, (10, 10, 100), (self.position[0] * scale + translation[0] * scale, self.position[1] * scale + translation[1] * scale), self.radius * scale * 2)
        #pygame.draw.circle(display, (0, 0, 0), (self.position[0] * scale + translation[0] * scale, self.position[1] * scale + translation[1] * scale), self.radius * scale * 2 - 2)

        #pygame.draw.circle(display, (80, 100, 255), (self.position[0] * scale + translation[0] * scale, self.position[1] * scale + translation[1] * scale), 5)
        #pygame.draw.circle(display, (0, 0, 0), (self.position[0] * scale + translation[0] * scale, self.position[1] * scale + translation[1] * scale), 4)
        self.RECTANGLE.x = self.position[0] * \
            scale + translation[0] * scale - 10 / 2
        self.RECTANGLE.y = self.position[1] * \
            scale + translation[1] * scale - 10 / 2
        pygame.draw.rect(display, self.color,
                         self.RECTANGLE, 1)  # (80, 100, 255)

        pygame.draw.circle(display, self.color, (self.position[0] * scale + translation[0]
                           * scale, self.position[1] * scale + translation[1] * scale), self.radius * scale)


star = Object(10000, (0, 0), 1000, (110, 150, 255))
planet1 = Object(100, (3100, 0), 200, (100, 200, 50))
planet2 = Object(100, (-6500, 0), 300, (200, 100, 50))
planet3 = Object(100, (9000, 0), 220, (200, 150, 100))
# moon = Object(10, (-7000, 0), 100, (120, 120, 120))

def main():
    drawing = False
    follow = False
    force = Vector(0, 0)
    scale =  0.4 * pow(10, -1)
    translation = [12000, 9000]
    speed = 5
    
    planet1.set_velocity(Vector(0, 0.15))
    planet2.set_velocity(Vector(0, 0.1))
    planet3.set_velocity(Vector(0, 0.06))
    # moon.set_velocity(Vector(0 , 0.14))

    while True:
        clock.tick(FRAME_RATE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return 0

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                drawing = not(drawing)


        keyboard = pygame.key.get_pressed()

        if keyboard[pygame.K_RSHIFT]:
            speed = 10
        else:
            speed = 5

        if keyboard[pygame.K_EQUALS]:
            scale += 0.05 * scale
            print(scale)

        elif keyboard[pygame.K_MINUS]:
            scale -= 0.05 * scale
            print(scale)

        elif keyboard[pygame.K_UP]:
            translation[1] += speed / scale
        elif keyboard[pygame.K_DOWN]:
            translation[1] -= speed / scale
        elif keyboard[pygame.K_RIGHT]:
            translation[0] -= speed / scale
        elif keyboard[pygame.K_LEFT]:
            translation[0] += speed / scale

        for _ in range(0, ANIMATION_SPEED):
            star.update(tuple(), Vector(0, 0))
            planet1.update((star, planet2, planet3), Vector(0, 0))
            planet2.update((star, planet1, planet3), Vector(0, 0))
            # moon.update((star, planet1, planet2), Vector(0, 0))
            planet3.update((star, planet1, planet2), Vector(0, 0))

        if drawing == False:
            display.fill((0, 0, 0))

        star.render(scale, translation)
        planet1.render(scale, translation)
        planet2.render(scale, translation)
        planet3.render(scale, translation)
        # moon.render(scale, translation)

        pygame.display.flip()


main()
