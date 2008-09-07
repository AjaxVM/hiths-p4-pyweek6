import pygame
from pygame.locals import *

class MapObject(object):
    def __init__(self, size):
        self.size = size
        self.territories = []


class Territory(object):
    def __init__(self):
        self.points = []
        self.pixels = []

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
        np = []
        for i in self.points:
            np.append((i[0]-lx, i[1]-ly))
        pygame.draw.polygon(surf, (255,0,0,255), np, 0)

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
                    if not t:
                        t = Territory()
                        t.add_point(event.pos)
                    else:
                        if t.within_range(event.pos):
                            print "done"
                            t.finish()
                            m.territories.append(t)
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
