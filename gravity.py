import math
import vector as v

G = 6.6743015 * pow(10, -17)  # for [km]


class Object(object):
    """material object class"""

    mass: float = None # [kg]
    position: v.Vector = None # [km]
    force: v.Vector = None # [N]
    acceleration: v.Vector = None # [km / t^2]
    velocity: v.Vector = None # [km / t]

    radius: float = None # [km]

    def __init__(
        self, object_mass: float, object_position: v.Vector, object_radius: float
    ):
        self.mass = object_mass
        self.position = object_position
        self.radius = object_radius

    def _one_object_gravity_(self, influancing_object):
        angle: float = None
        gravity: v.Vector = v.Vector(0, 0)

        distance: v.Vector = v.subtract(influancing_object.position, self.position)
        value: float = (G * influancing_object.mass * self.mass) / pow(distance.get_value(), 2)

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
        gravity: v.Vector = v.Vector(0, 0)

        for influanceing_object in influacing_objects:
            gravity = v.add(gravity, self._one_object_gravity_(influanceing_object))

        return gravity

    def calculate_acceleration(self):
        acceleration: v.Vector = v.Vector(
            self.force.x / self.mass, self.force.y / self.mass
        )

        return acceleration

    def update_velocity(self, velocity: v.Vector):
        velocity = v.add(velocity, self.acceleration)

        return velocity

    def update_position(self, position: v.Vector):
        position = v.add(position, self.velocity)

        return position

    def update(self, influencing_objects: tuple):
        self.force = self.calculate_gravity(influencing_objects)
        self.acceleration = self.calculate_acceleration()
        self.velocity = self.update_velocity(self.velocity)
        self.position = self.update_position(self.position)
