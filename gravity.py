import math
import vector as v

G = 6.6743015 * pow(10, -17)  # using kilometer^3


class Object(object):
    """material object class"""

    mass: float = None
    position: v.Vector = None
    force: v.Vector = None
    acceleration: v.Vector = None
    velocity: v.Vector = None

    radius: float = None
    color: tuple = None

    def __init__(
        self, object_mass: float, object_position: v.Vector, radius: float, color: tuple
    ):
        self.mass = object_mass
        self.position = object_position
        self.radius = radius
        self.color = color

    def _calculate_gravity_one_object_(self, influancing_object):
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
        gravity_value: float = None

        for influanceing_object in influacing_objects:
            pass
