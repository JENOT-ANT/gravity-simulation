from vector import *

G = 6.6743015 * pow(10, -17) # using kilometer^3

class Object(object):
    '''material object class'''

    mass:           float = None
    position:       Vector = None
    force:          Vector = None
    acceleration:   Vector = None
    velocity:       Vector = None

    radius:         float = None
    color:          tuple = None

    def __init__(self, object_mass: float, object_position: Vector, radius: float, color: tuple):
        self.mass = object_mass
        self.position = object_position
        self.radius = radius
        self.color = color
    
    def _calculate_gravity_one_object_(self, influancing_object):
        distance: Vector = math.dist(self.position._2_tuple(), influancing_object.position._2_tuple())
        value = (G * influancing_object.mass * self.mass) / pow(distance, 2)
        

    def calculate_gravity(self, influacing_objects: tuple):
        gravity_value: float = None

        for influanceing_object in influacing_objects:
            pass

