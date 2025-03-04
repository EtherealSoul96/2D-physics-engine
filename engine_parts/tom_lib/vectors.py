
from math import sqrt, sin, cos, asin, acos, tau
from .angle import Angle
import numpy as np


class Vec2():

    __slots__ = "x", "y"

    def __init__(self, x, y):

        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y


    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        raise IndexError("vector index out of range")

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        raise IndexError("vector index out of range")

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vec2(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        try:
            return Vec2(self.x / other, self.y / other)
        except ZeroDivisionError as err:
            print("MOD ZEROOOOOOOO!!!!")
            print(err)

    def __floordiv__(self, other):
        try:
            return Vec2(self.x // other, self.y // other)
        except ZeroDivisionError as err:
            print("MOD ZEROOOOOOOO!!!!")
            print(err)

    def __neg__(self):
        return -1 * self

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def normalize(self):

        mod = (self.x ** 2 + self.y ** 2) ** (0.5)

        try:
            # print(self, mod, "hi")

            self.x /= mod
            self.y /= mod

            return self
        except ZeroDivisionError as err:
            print("MOD ZEROOOOOOOO!!!!")
            raise err

    def normalized(self):
        return Vec2(*self).normalize()

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def angle(self):

        # if abs(self) == 0:
        if self.abs_2() == 0:
            return Angle(0)

        v = self/abs(self)

        if asin(v.y) >= 0:
            # return acos(v.x)
            return Angle(acos(v.x))
        else:
            # return tau-acos(v.x)
            return Angle(-acos(v.x))


    def rotated(self, angle):
        c = cos(angle)
        s = sin(angle)
        return Vec2(c * self.x - s * self.y,
                    s * self.x + c * self.y)

    def rotate(self, angle):
        old_x = self.x
        self.x = cos(angle) * old_x - sin(angle) * self.y
        self.y = sin(angle) * old_x + cos(angle) * self.y

    def rotated_90(self):
        return Vec2(-self.y, self.x)

    def rotated_270(self):
        return Vec2(self.y, -self.x)

    def round(self):
        return Vec2(round(self.x), round(self.y))

    def __abs__(self):
        return sqrt(self.abs_2())
        # return (self.x ** 2 + self.y ** 2) ** (1 / 2)

    def abs_2(self):
        return self.x * self.x + self.y * self.y
        # return self.x ** 2 + self.y ** 2

    def __str__(self):
        return str((self.x, self.y))

    def __repr__(self):
        return str((self.x, self.y))

    def __hash__(self):
        return hash((self.x, self.y))

    def __bool__(self):
        return bool(self.x) or bool(self.y)

    @staticmethod
    def versor(a):
        return Vec2(cos(a), sin(a))

    def project(self, v):
        return v * self.dot(v)/abs(v)**2

def vector_list_to_normal_list(l):
    return [val for vec in l for val in vec]
