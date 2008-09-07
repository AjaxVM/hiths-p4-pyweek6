"""Vector, Projection and Polygon classes from:
http://gpwiki.org/index.php/Physics:2D_Physics_Engine:Intersection_Detection"""


import pygame
from pygame.locals import *


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
    def intersects(self, other):
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


class MapObject(object):
    def __init__(self, size):
        self.size = size
        self.territories = []

    def add(self,terr):
        self.territories.append(terr)

    def test_point(self, point):
        for i in self.territories:
            if point in i.pixels:
                return False

        return True

    def test_territory(self, terr):
        for i in self.territories:
            if i.poly.intersects(terr.poly):
                return False
        return True


class Territory(object):
    def __init__(self):
        self.points = []
        self.pixels = []
        self.rect = pygame.Rect(0,0,1,1)
        self.midpoint = [0,0]
        self.poly = None

    def add_point(self, point):
        self.points.append(point)

    def finish(self):
        self.points.append(self.points[0])
        self.get_pixels()

    def get_pixels(self):
        lx = self.points[0][0]
        ly = self.points[0][1]
        gx = self.points[0][0]
        gy = self.points[0][1]
        for p in self.points:
            if p[0] < lx: lx = p[0]
            if p[0] > gx: gx = p[0]
            if p[1] < ly: ly = p[1]
            if p[1] > gy: gy = p[1]

        surf = pygame.Surface((gx-lx, gy-ly))
        self.rect = surf.get_rect()
        self.rect.topleft = lx, ly
        np = []
        for i in self.points:
            np.append((i[0]-lx, i[1]-ly))
        pygame.draw.polygon(surf, (255,0,0,255), np, 0)
        self.mid_point = self.rect.right - self.rect.width/2, self.rect.bottom - self.rect.height/2

        vp = []
        for i in self.points:
            vp.append(Vector(i[0], i[1]))
        self.poly = Polygon(vp)

        yy = xrange(surf.get_height())

        for x in xrange(surf.get_width()):
            for y in yy:
                if surf.get_at((x, y)) == (255,0,0,255):
                    self.pixels.append((lx+x, ly+y))


    def within_range(self, pos):
        r = pygame.Rect(self.points[0][0]-7, self.points[0][1]-7, 14, 14)
        return r.collidepoint(pos)


def test():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))

    m = MapObject((640, 480))

    t = None

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return None

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if m.test_point(event.pos):
                        if not t:
                            t = Territory()
                            t.add_point(event.pos)
                        else:
                            if t.within_range(event.pos):
                                print "done"
                                t.finish()
                                if m.test_territory(t):
                                    m.add(t)
                                t = None
                            else:
                                t.add_point(event.pos)

        screen.fill((0,0,0))

        for i in m.territories:
            for p in i.pixels:
                screen.set_at(p, (255,0,0))
            pygame.draw.polygon(screen, [0,255,0], i.points, 1)

        if t:
            if len(t.points) > 1:
                pygame.draw.lines(screen, [0, 0, 255], False, t.points, 1)
            for i in t.points:
                pygame.draw.circle(screen, [75, 75, 255], i, 10)

        pygame.display.flip()


test()
