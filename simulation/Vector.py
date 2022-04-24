
import math


class Vector:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def equals(self, v: 'Vector') -> bool:
        return v.getX() == self.x and v.getY() == self.y

    def round(self) -> 'Vector':
        return Vector(round(self.x), round(self.y))

    def truncate(self) -> 'Vector':
        return Vector(self.x,  self.y)

    def getX(self) -> float:
        return self.x

    def getY(self) -> float:
        return self.y

    def distance(self, v: 'Vector') -> float:
        return math.sqrt((self.x - v.x)**2 + (self.y - v.y)**2)

    def inRange(self, v: 'Vector', range: float) -> bool:
        return self.distance(v) <= range

    def add(self, v: 'Vector') -> 'Vector':
        return Vector(self.x + v.x, self.y + v.y)

    def mult(self, scalar: float) -> 'Vector':
        return Vector(self.x * scalar, self.y * scalar)

    def sub(self, v: 'Vector') -> 'Vector':
        return Vector(self.x - v.x, self.y - v.y)

    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def lengthSquared(self) -> float:
        return self.x**2 + self.y**2

    def normalize(self) -> 'Vector':
        length = self.length()
        if length == 0:
            return Vector(0, 0)
        return Vector(self.x / length, self.y / length)

    def dot(self, v: 'Vector') -> float:
        return self.x * v.x + self.y * v.y

    def angle(self) -> float:
        return math.atan2(self.y, self.x)

    def __str__(self) -> str:
        return f"[{self.x},{self.y}]"

    def project(self, force: 'Vector') -> 'Vector':
        normalize = self.normalize()
        return normalize.mult(normalize.dot(force))

    def cross(self, s: float) -> 'Vector':
        return Vector(self.y * -s, self.x * s)

    def hsymmetric(self, center: float) -> 'Vector':
        return Vector(2*center-self.x, self.y)

    def vsymmetric(self, center: float) -> 'Vector':
        return Vector(self.x, 2*center-self.y)

    def vsymmetric(self) -> 'Vector':
        return Vector(self.x, -self.y)

    def hsymmetric(self) -> 'Vector':
        return Vector(-self.x, self.y)

    def symmetric(self) -> 'Vector':
        return self.symmetric(Vector(0, 0))

    def symmetric(self, center: 'Vector') -> 'Vector':
        return Vector(center.x * 2 - self.x, center.y * 2 - self.y)

    def withinBounds(self, minx: float, miny: float,  maxx: float,  maxy: float):
        return self.x >= minx and self.x < maxx and self.y >= miny and self.y < maxy

    def isZero(self) -> bool:
        return self.x == 0 and self.y == 0

    def symmetricTruncate(self, origin: 'Vector') -> 'Vector':
        return self.sub(origin).truncate().add(origin)
