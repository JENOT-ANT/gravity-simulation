'''
Basic library defining 2D vector object and some basic operations on vectors.

Author: JENOT
'''

from math import sqrt


class Vector(object):
    '''2D vector object'''

    x: float
    y: float

    def __init__(self, coordinate_x: float, coordinate_y: float):
        self.x = coordinate_x
        self.y = coordinate_y

    def to_tuple(self):
        return (self.x, self.y)

    def get_value(self):
        return sqrt(pow(self.x, 2) + pow(self.y, 2))  # _/x^2 + y^2`


def add_vectors(v1: Vector, v2: Vector):
    return Vector(v1.x + v2.x, v1.y + v2.y)


def subtract_vectors(v1: Vector, v2: Vector):
    return Vector(v1.x - v2.x, v1.y - v2.y)
