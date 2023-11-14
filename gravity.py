from math import atan, cos, sin
from vector import *

G: float = 6.6743015 * pow(10, -17)  # for [km and 1000 kg]
BOUNCING_FACTOR: float = 0.8
EARTH_MASS: float = 5.9722 * pow(10, 21) # [1000 kg]


class Object:
    '''material object class'''

    mass: float             # [1000 kg]
    radius: float           # [km]

    position: Vector        # [km]
    force: Vector           # [N]
    acceleration: Vector    # [km / t^2]
    velocity: Vector        # [km / t]

    color: tuple            # (Red, Green, Blue)
    
    
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


    def _one_object_gravity(self, influancing_object):
        angle: float
        gravity: Vector = Vector(0, 0)

        distance: Vector = subtract_vectors(influancing_object.position, self.position)
        value: float = (G * influancing_object.mass * self.mass) / pow(distance.get_value(), 2)  # (G * M * m) / r^2

        if distance.x != 0:
            angle = atan(distance.y / distance.x)
        else:
            angle = 0

        if distance.x > 0:
            gravity.x = cos(angle) * value
            gravity.y = sin(angle) * value
        else:
            gravity.x = -(cos(angle) * value)
            gravity.y = -(sin(angle) * value)

        return gravity

    def _calculate_gravity(self, influacing_objects: list):
        gravity: Vector = Vector(0, 0)

        for influanceing_object in influacing_objects:
            gravity = add_vectors(gravity, self._one_object_gravity(influanceing_object))

        return gravity

    def _calculate_acceleration(self):
        self.acceleration: Vector = Vector(
            self.force.x / self.mass, self.force.y / self.mass
        )  # a = F / m

    def _update_velocity(self):
        self.velocity = add_vectors(self.velocity, self.acceleration)

    def _handle_collsion(self, influacing_objects: list):
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

    def _update_position(self):
        self.position = add_vectors(self.position, self.velocity)


    def update(self, influancing_objects: list, force: Vector=Vector(0, 0)):
        
        self.force = add_vectors(force, self._calculate_gravity(influancing_objects))
        self._calculate_acceleration()
        
        self._update_velocity()
        self._handle_collsion(influancing_objects)
        
        self._update_position()

    def set_velocity(self, velocity: Vector):
        self.velocity = velocity
        