"""Vector, Projection and Polygon classes from:
http://gpwiki.org/index.php/Physics:2D_Physics_Engine:Intersection_Detection
And then modified."""


import pygame
import math

class Vector:
    """Basic vector implementation"""
    def __init__(self, x, y):
        self.x, self.y = x, y
    def dot(self, other):
        """Returns the dot product of self and other (Vector)"""
        return self.x*other.x + self.y*other.y
    def __add__(self, other): # overloads vec1+vec2
        return Vector(self.x+other.x, self.y+other.y)
    def __neg__(self): # overloads -vec
        return Vector(-self.x, -self.y)
    def __sub__(self, other): # overloads vec1-vec2
        return -other + self
    def __mul__(self, scalar): # overloads vec*scalar
        return Vector(self.x*scalar, self.y*scalar)
    __rmul__ = __mul__ # overloads scalar*vec
    def __div__(self, scalar): # overloads vec/scalar
        return 1.0/scalar * self
    def magnitude(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    def normalize(self):
        """Returns this vector's unit vector (vector of 
        magnitude 1 in the same direction)"""
        inverse_magnitude = 1.0/self.magnitude()
        return Vector(self.x*inverse_magnitude, self.y*inverse_magnitude)
    def perpendicular(self):
        """Returns a vector perpendicular to self"""
        return Vector(-self.y, self.x)

class Projection:
    """A projection (1d line segment)"""
    def __init__(self, min, max):
        self.min, self.max = min, max
    def intersects(self, other):
        """returns whether or not self and other intersect"""
        return self.max > other.min and other.max > self.min

class Polygon:
    def __init__(self, points):
        """points is a list of Vectors"""
        self.points = points
        
        # Build a list of the edge vectors
        self.edges = []
        for i in range(len(points)): # equal to Java's for(int i=0; i<points.length; i++)
                point = points[i]
                next_point = points[(i+1)%len(points)]
                self.edges.append(next_point - point)
    def project_to_axis(self, axis):
        """axis is the unit vector (vector of magnitude 1) to project the polygon onto"""
        projected_points = []
        for point in self.points:
                # Project point onto axis using the dot operator
                projected_points.append(point.dot(axis))
        return Projection(min(projected_points), max(projected_points))

    def collidepoly(self, other):
        """returns whether or not two polygons intersect"""
        # Create a list of both polygons' edges
        try:
            edges = []
            edges.extend(self.edges)
            edges.extend(other.edges)
            
            for edge in edges:
                axis = edge.normalize().perpendicular() # Create the separating axis (see diagrams)
                
                # Project each to the axis
                self_projection = self.project_to_axis(axis)
                other_projection = other.project_to_axis(axis)
                
                # If the projections don't intersect, the polygons don't intersect
                if not self_projection.intersects(other_projection):
                    return False
            
            # The projections intersect on all axes, so the polygons are intersecting
            return True
        except:
            return True

    def colliderect(self, other):
        other = Polygon([other.rect.topleft, other.rect.topright,
                         other.rect.bottomleft, other.rect.bottomright])
        return self.collidepoly(other)

    def collideline(self, other):
        other = Polygon([other[0], other[1], other[0]])
