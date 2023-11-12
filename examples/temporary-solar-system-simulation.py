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
G = 6.67430 * pow(10, -17)
ANIMATION_SPEED = 100
FRAME_RATE = 25

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

    def update(self, objects, force):
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


sun = Object(2 * pow(10, 27), [0, 0], 696342, (255, 250, 50))

earth = Object(6 * pow(10, 21), [1.47 * pow(10, 8), 0], 6378, (10, 150, 50))

moon = Object(7.348 * pow(10, 19),
              [1.47 * pow(10, 8) - 363104, 0], 1737, (50, 50, 50))

mercury = Object(3.3011 * pow(10, 20), [46000000, 0], 2440, (80, 80, 80))

wenus = Object(4.867 * pow(10, 21), [107476002, 0], 6051, (190, 120, 50))

mars = Object(6.417 * pow(10, 20), [2.07*pow(10, 8), 0], 3390, (140, 70, 0))

jupiter = Object(1.898 * pow(10, 24),
                 [7.4052 * pow(10, 8), 0], 70000, (200, 60, 0))

saturn = Object(5.6834 * pow(10, 23),
                [1.35255 * pow(10, 9), 0], 58232, (215, 160, 100))

space_craft = Object(4000, [1.47 * pow(10, 8), -6380], 2, (150, 150, 150))


def main():
    drawing = False
    follow = False
    force = Vector(0, 0)
    scale = pow(10, -6)
    translation = [0, 100000000]
    speed = 5

    earth.set_velocity(Vector(0, 30.290))
    moon.set_velocity(Vector(0, 30.290 + 1.082))
    mercury.set_velocity(Vector(0, 58.980))
    wenus.set_velocity(Vector(0, 35.260))
    mars.set_velocity(Vector(0, 26.500))
    jupiter.set_velocity(Vector(0, 13.720))
    saturn.set_velocity(Vector(0, 10.18))

    space_craft.set_velocity(Vector(0, 30.290))

    while True:
        clock.tick(FRAME_RATE)
        force.x = 0
        force.y = 0


        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return 0

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                drawing = not(drawing)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                follow = not(follow)

        if follow == True:
            translation = [-space_craft.position[0] + RESOLUTION[0] / 2 /
                           scale, -space_craft.position[1] + RESOLUTION[1] / 2 / scale]

        keyboard = pygame.key.get_pressed()

        if keyboard[pygame.K_RSHIFT]:
            speed = 10
        else:
            speed = 5

        if keyboard[pygame.K_w]:
            force.y = -5*pow(10, 1)

        elif keyboard[pygame.K_s]:
            force.y = 5*pow(10, 1)

        elif keyboard[pygame.K_d]:
            force.x = 5*pow(10, 1)

        elif keyboard[pygame.K_a]:
            force.x = -5*pow(10, 1)

        elif keyboard[pygame.K_f]:
            force.x = 0
            force.y = 0

        elif keyboard[pygame.K_EQUALS]:
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

        for i in range(0, ANIMATION_SPEED):

            sun.update((mercury, wenus, earth, mars,
                       jupiter, saturn), Vector(0, 0))

            mercury.update((sun, wenus), Vector(0, 0))
            wenus.update((sun, mercury, earth), Vector(0, 0))

            earth.update((sun, ), Vector(0, 0))
            moon.update((sun, earth), Vector(0, 0))

            mars.update((sun, earth, jupiter), Vector(0, 0))
            jupiter.update((sun, mars, saturn), Vector(0, 0))
            saturn.update((sun, jupiter), Vector(0, 0))

            space_craft.update((sun, mercury, earth, moon, mars), force)

        if drawing == False:
            display.fill((0, 0, 0))

        sun.render(scale, translation)
        mercury.render(scale, translation)
        wenus.render(scale, translation)

        earth.render(scale, translation)
        moon.render(scale, translation)

        mars.render(scale, translation)
        jupiter.render(scale, translation)
        saturn.render(scale, translation)

        space_craft.render(scale, translation)

        pygame.display.flip()


main()
