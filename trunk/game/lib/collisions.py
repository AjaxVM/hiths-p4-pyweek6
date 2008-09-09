"""Vector, Projection and Polygon classes from:
http://gpwiki.org/index.php/Physics:2D_Physics_Engine:Intersection_Detection
And then modified."""


import pygame
import math

class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def dot(self, other):
        return self.x*other.x + self.y*other.y
    def __add__(self, other):
        return Vector(self.x+other.x, self.y+other.y)
    def __neg__(self):
        return Vector(-self.x, -self.y)
    def __sub__(self, other):
        return -other + self
    def __mul__(self, scalar):
        return Vector(self.x*scalar, self.y*scalar)
    __rmul__ = __mul__
    def __div__(self, scalar):
        return 1.0/scalar * self
    def magnitude(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    def normalize(self):
        inverse_magnitude = 1.0/self.magnitude()
        return Vector(self.x*inverse_magnitude, self.y*inverse_magnitude)
    def perpendicular(self):
        return Vector(-self.y, self.x)

class Projection:
    def __init__(self, min, max):
        self.min, self.max = min, max
    def intersects(self, other):
        return self.max > other.min and other.max > self.min

class Polygon:
    def __init__(self, points):
        self.points = points
        
        self.edges = []
        for i in range(len(points)):
            point = points[i]
            next_point = points[(i+1)%len(points)]
            self.edges.append(next_point - point)
    def project_to_axis(self, axis):
        projected_points = []
        for point in self.points:
            projected_points.append(point.dot(axis))
        return Projection(min(projected_points), max(projected_points))

    def collidepoly(self, other):
        try:
            edges = []
            edges.extend(self.edges)
            edges.extend(other.edges)
            
            for edge in edges:
                axis = edge.normalize().perpendicular()
                
                self_projection = self.project_to_axis(axis)
                other_projection = other.project_to_axis(axis)
                
                if not self_projection.intersects(other_projection):
                    return False

            return True
        except:
            return True

    def colliderect(self, other):
        other = Polygon([Vector(*other.topleft), Vector(*other.topright),
                         Vector(*other.bottomright), Vector(*other.bottomleft),
                         Vector(*other.topleft)])
        return self.collidepoly(other)
def line_intersect(a, b):
    denom = ((b[1][1] - b[0][1]) * (a[1][0] - a[0][0])) -\
            ((b[1][0] - b[0][0]) * (a[1][1] - a[0][1]))
    nume_a = ((b[1][0] - b[0][0]) * (a[0][1] - b[0][1])) -\
             ((b[1][1] - b[0][1]) * (a[0][0] - b[0][0]))
    nume_b = ((a[1][0] - a[0][0]) * (a[0][1] - b[0][1])) - \
             ((a[1][1] - a[0][1]) * (a[0][0] - b[0][0]))

    if denom == 0:
        if nume_a == 0 and nume_b == 0:
            return False
        return False

    ua = nume_a / denom
    ub = nume_b / denom

    if (ua >= 0 and ua <= 1) and (ub >= 0 and ub <= 1):
        x = a[0][0] + ua * (a[1][0] - a[0][0])
        y = a[0][1] + ua * (a[1][1] - a[0][1])
        return int(x), int(y)
    return False
