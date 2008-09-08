import pygame
from pygame.locals import *


from collisions import Polygon, Vector, line_intersect
import math
import random
from objects import *
import data


##class Segment(object):
##    def __init__(self, start, end):
##        self.start = start
##        self.end = end
##
##        self.intersects = []
##
##    def inter(self, other):
##        x = line_intersection((self.start, self.end), (other.start, other.end))
##        if x:
##            self.intersects.append(other)
##
##    def poi(self, other):
##        return line_intersection((self.start, self.end), (other.start, other.end))


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
        if len(terr.pixels) < 50:
            return False
        for i in self.territories:
            if i.poly.collidepoly(terr.poly):
                return False
##                if i.player != terr.player:
##                    return False
##                else:
####                    return True
##                    self.merge_territories(i, terr)
##                    return True
        return True


##    def merge_territories(self, t1, t2):
##        t1segs = []
##        for i in xrange(len(t1.points)):
##            if i < len(t1.points)-1:
##                t1segs.append(Segment(t1.points[i], t1.points[i+1]))
##            else:
##                t1segs.append(Segment(t1.points[i], t1.points[0]))
##        t2segs = []
##        for i in xrange(len(t2.points)):
##            if i < len(t2.points)-1:
##                t2segs.append(Segment(t2.points[i], t2.points[i+1]))
##            else:
##                t2segs.append(Segment(t2.points[i], t2.points[0]))
##
##
##        for i in t1segs:
##            for x in t2segs:
##                i.inter(x)
##                x.inter(i)
##
##
##        new = []
##        cur = t1segs[0]
##        while 1:
##            if cur.intersects:
##                if len(cur.intersects) > 1:
##                    n = cur.intersects[0]
##                    for i in cur.intersects:
##                        if (cur.start+cur.end)*(i.start+i.end) <\
##                           (cur.start+cur.end)*(n.start+n.end):
##                            n = i
##                else:
##                    n = cur.intersects[0]
##
##                p = n.intersects[0]
##
##                if len(n.intersects)>1:
##                    for i in n.intersects:
##                        if t1segs.index(i) < t1segs.index(p):
##                            p = i
##                new.append((cur.start, cur.poi(p)))
##            else:
##                new.append((cur.start, cur.end))


##        use = t1segs


##        new = []
##        for seg in t1segs:
##            for s in t2segs:
##                x = line_intersect((seg.start, seg.end),
##                                   (s.start, s.end))
##                if x:
##                    new.append(Segment(seg.start, x))
##                    i = t2segs.index(s)+1
##                    nx = line_intersect((x, s.end), (ns.start, ns.end))
##                    if nx:
##                        new.append(Segment(x, nx))
##                        new.append(Segment(nx, seg.end))
##                        break
##                    while 1:
##                        for ns in t1segs:
##                            if not ns == seg:
##                                nx = line_intersect((x, s.end), (ns.start, ns.end))
##                                if nx:
##                                    new.append(Segment(x, nx))
##                                    new.append(Segment(nx, seg.end))
##                                    break
##                        new.append(Segment(x, s.end))
##                        i += 1
##                        if i == len(t2segs):
##                            i = 0
##                            print 1
##                        s = t2segs[i]
##                else:
##                    new.append(seg)

        t1.points = new
        t1.pixels.extend(t2.pixels)
            
##        inside = []
##        other = []
##        x = 0
##        for i in t2.points:
##            if i in t1.pixels:
##                inside.append([i, t2.points[x-1], t2.points[x+1]])
##                other.append([i, t2.points[x-1]])
##            else:
##                other.append([i, t2.points[x-1]])
##            x += 1
##
##        x = 0
##        for i in t1.points:
##            if i in t2.pixels:
##                inside.append([i, t1.points[x-1], t1.points[x+1]])
##                other.append([i, t1.points[x-1]])
##            else:
##                other.append([i, t1.points[x-1]])
##            x += 1
##
##        new = []
##        for i in other:
##            new.append(i[0])
##        for i in inside:
##            for x in other:
##                if not x == [i[0], i[1]]:
##                    a = line_intersect([i[0], i[1]], x)
##                    if a:
##                        new.append(a)
##                    a = line_intersect([i[0], i[2]], x)
##                    if a:
##                        new.append(a)
##            new.remove(i[0])
##        t1.pixels.extend(t2.pixels)
##
##        t1.points = new
##        return t1


class Territory(object):
    def __init__(self, player):
        self.points = []
        self.pixels = []
        self.rect = pygame.Rect(0,0,1,1)
        self.midpoint = [0,0]
        self.poly = None

        self.player = player

        self.pop_cap = 0

    def add_point(self, point):
        self.points.append(point)

    def finish(self):
        self.points.append(self.points[0])
        self.get_pixels()
        self.calculate_ship_support_cap()

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
        r = pygame.Rect(self.points[0][0]-10, self.points[0][1]-10, 20, 20)
        return r.collidepoint(pos)

    def calculate_ship_support_cap(self):
        area_amount = int(len(self.pixels) / 50) #so for every 50 pixels we have we can support a new ship
        island_amount = len(self.islands) * 3 #so for each island we get 3 new ships we can support
        default_amount = 1 #this is what you automatically will get

        self.pop_cap = area_amount + island_amount + default_amount


class Camera(object):
    def __init__(self, view, world):
        self.view = view
        self.world = world

        self.rect = pygame.Rect(0,0,*view)
        self.brect = pygame.Rect(0,0,*world)

    def move(self, x, y):
        self.rect.move_ip((x, y))

        if self.rect.right > self.brect.right:
            self.rect.right = self.brect.right
        if self.rect.left < self.brect.left:
            self.rect.left = self.brect.left

        if self.rect.bottom > self.brect.bottom:
            self.rect.bottom = self.brect.bottom
        if self.rect.top < self.brect.top:
            self.rect.top = self.brect.top

    def get_offset(self):
        return self.rect.topleft


class World(object):
    def __init__(self, screen_size=(640, 480),
                 world_size = (5000, 5000)):
        self.ssize = screen_size
        self.wsize = world_size

        self.mo = MapObject(self.wsize)
        self.tile_images = [data.image("water.png"),
                            data.image("water2.png"),
                            data.image("water3.png")]
        self.cur_ti = self.tile_images[0]
        self.cur_i = 0
        self.cur_timer = 0

        self.camera = Camera(self.ssize, self.wsize)

        self.islands = []
        self.units = []

        self.make_islands()

    def render(self, screen):
        self.cur_timer += 1
        if self.cur_timer >= 25:
            self.cur_timer = 0
            self.cur_i += 1
            if self.cur_i == 3:
                self.cur_i = 0
            self.cur_ti = self.tile_images[self.cur_i]
        x, y = self.camera.get_offset()
        if x:
            tox = x % 25
        else:
            tox = 0
        if y:
            toy = y % 25
        else:
            toy = 0

        yy = xrange(-1,480/25+2)

        for ix in xrange(-1,640/25+2):
            for iy in yy:
                screen.blit(self.cur_ti, (ix*25+tox, iy*25+toy))

        for i in self.mo.territories:
            np = []
            for p in i.points:
                px, py = p
                px -= x
                py -= y
                np.append((px, py))
            colors = [[[255,0,0], [0,255,0]],
                      [[125,125,125],[0,0,0]]]
            pygame.draw.polygon(screen, colors[i.player][0], np, 3)

        for i in self.islands:
            i.render(screen, (x, y))

        for i in self.units:
            i.render(screen, (x, y))

    def make_islands(self):
        grid = []
        for x in xrange(self.wsize[0]/125):
            for y in xrange(self.wsize[1]/125):
                grid.append((x, y))
        self.islands = []
        for x in xrange(len(grid)/random.randint(3,5)):
            x, y = random.choice(grid)
            grid.remove((x, y))
            offx = random.randint(0,50)
            offy = random.randint(0,50)
            i = Island((x*125+offx, y*125+offy), 10)
            i.get_random_resources()
            self.islands.append(i)
