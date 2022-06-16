import math
from vector import *

G = 6.6743015 * pow(10, -17)  # for [km]


class Object(object):
    """material object class"""

    mass: float = None  # [kg]
    radius: float = None  # [km]

    position: Vector = None  # [km]
    force: Vector = None  # [N]
    acceleration: Vector = None  # [km / t^2]
    velocity: Vector = None  # [km / t]

    #influancing_objects: list = None

    def __init__(
        self,
        object_mass: float,
        object_position: Vector,
        object_radius: float,
        #influancing_objects: list,
    ):
        self.mass = object_mass
        self.position = object_position
        self.radius = object_radius
        #self.influancing_objects = influancing_objects

    def _one_object_gravity_(self, influancing_object):
        angle: float = None
        gravity: Vector = Vector(0, 0)

        distance: Vector = subtract_vectors(influancing_object.position, self.position)
        value: float = (G * influancing_object.mass * self.mass) / pow(
            distance.get_value(), 2
        )  # (G * M * m) / r^2

        if distance.x != 0:
            angle = math.atan(distance.y / distance.x)
        else:
            angle = 0

        if distance.x > 0:
            gravity.x = math.cos(angle) * value
            gravity.y = math.sin(angle) * value
        else:
            gravity.x = -(math.cos(angle) * value)
            gravity.y = -(math.sin(angle) * value)

        return gravity

    def calculate_gravity(self, influacing_objects: tuple):
        gravity: Vector = Vector(0, 0)

        for influanceing_object in influacing_objects:
            gravity = add_vectors(
                gravity, self._one_object_gravity_(influanceing_object)
            )

        return gravity

    def calculate_acceleration(self):
        acceleration: Vector = Vector(
            self.force.x / self.mass, self.force.y / self.mass
        )  # a = F / m

        return acceleration

    def update_velocity(self, velocity: Vector):
        velocity = add_vectors(velocity, self.acceleration)

        return velocity

    def calculate_collsion(self, velocity: Vector, influacing_objects: tuple):
        for influanceing_object in influacing_objects:
            distance: Vector = subtract_vectors(
                influanceing_object.position, self.position
            )

            if distance.get_value() <= (self.radius + influanceing_object.radius):
                velocity.x = (
                    velocity.x * (self.mass - influanceing_object.mass)
                    + (2 * influanceing_object.mass * influanceing_object.velocity.x)
                ) / (self.mass + influanceing_object.mass)
                
                velocity.y = (
                    velocity.y * (self.mass - influanceing_object.mass)
                    + (2 * influanceing_object.mass * influanceing_object.velocity.y)
                ) / (self.mass + influanceing_object.mass)

            return velocity

    def update_position(self, position: Vector):
        position = add_vectors(position, self.velocity)

        return position

    def update(self, influancing_objects):
        self.velocity = self.calculate_collsion(self.velocity, influancing_objects)
        
        self.force = self.calculate_gravity(influancing_objects)
        self.acceleration = self.calculate_acceleration()
        self.velocity = self.update_velocity(self.velocity)
        self.position = self.update_position(self.position)
