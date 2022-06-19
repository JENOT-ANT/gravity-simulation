import math
from vector import *

G = 6.6743015 * pow(10, -17)  # for [km]
BOUNCING_FACTOR = 0.8

class Object(object):
    """material object class"""

    mass: float = None  # [kg]
    radius: float = None  # [km]

    position: Vector = None  # [km]
    force: Vector = None  # [N]
    acceleration: Vector = None  # [km / t^2]
    velocity: Vector = None  # [km / t]

    color: tuple = None # (Red, Green, Blue)
    
    
    def __init__(
        self,
        object_mass: float,
        object_position: Vector,
        object_radius: float,
        object_color: tuple,
    ):
        self.mass = object_mass
        self.position = object_position
        self.radius = object_radius
        self.color = object_color

        self.force = Vector(0, 0)
        self.velocity = Vector(0, 0)
        self.acceleration = Vector(0, 0)


    def __one_object_gravity__(self, influancing_object):
        angle: float = None
        gravity: Vector = Vector(0, 0)

        distance: Vector = subtract_vectors(influancing_object.position, self.position)
        value: float = (G * influancing_object.mass * self.mass) / pow(distance.get_value(), 2)  # (G * M * m) / r^2

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
                gravity, self.__one_object_gravity__(influanceing_object)
            )

        return gravity

    def calculate_acceleration(self):
        self.acceleration: Vector = Vector(
            self.force.x / self.mass, self.force.y / self.mass
        )  # a = F / m

    def update_velocity(self):
        self.velocity = add_vectors(self.velocity, self.acceleration)

    def handle_collsion(self, influacing_objects: tuple):
        for influancing_object in influacing_objects:
            
            distance: Vector = subtract_vectors(
                influancing_object.position, self.position
            )

            if distance.get_value() <= (self.radius + influancing_object.radius):
                if self.velocity.get_value() > 1:
                    self.velocity.x = (
                        BOUNCING_FACTOR * self.velocity.x * (self.mass - influancing_object.mass)
                        + (2 * influancing_object.mass * influancing_object.velocity.x)
                    ) / (self.mass + influancing_object.mass)
                        
                    self.velocity.y = (
                        BOUNCING_FACTOR * self.velocity.y * (self.mass - influancing_object.mass)
                        + (2 * influancing_object.mass * influancing_object.velocity.y)
                    ) / (self.mass + influancing_object.mass)
            
                elif self.mass < influancing_object.mass:
                    self.velocity = influancing_object.velocity

    def update_position(self):
        self.position = add_vectors(self.position, self.velocity)


    def update(self, influancing_objects, force: Vector=Vector(0, 0)):
        
        self.force = add_vectors(force, self.calculate_gravity(influancing_objects))
        self.calculate_acceleration()
        
        self.update_velocity()
        self.handle_collsion(influancing_objects)
        
        self.update_position()

    def set_velocity(self, velocity: Vector):
        self.velocity = velocity