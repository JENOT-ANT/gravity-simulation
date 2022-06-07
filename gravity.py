from vector import *


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
    
