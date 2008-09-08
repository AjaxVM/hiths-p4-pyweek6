import pygame
from pygame.locals import *


from collisions import Polygon, Vector, line_intersect
import math
import random
from objects import *
import data


class MapObject(object):
    def __init__(self, size, world):
        self.world = world
        self.size = size
        self.territories = []

    def add(self, terr):
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

        islands = []
        for i in self.world.islands:
            if terr.rect.colliderect(i.rect) and terr.poly.colliderect(i.rect):
                islands.append(i)
        if not islands:
            return False

        terr.islands = islands
        terr.calculate_ship_support_cap()
        return True


class Territory(object):
    def __init__(self, player):
        self.points = []
        self.pixels = []
        self.rect = pygame.Rect(0,0,1,1)
        self.midpoint = [0,0]
        self.poly = None

        self.player = player

        self.islands = []

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
        area_amount = int(len(self.pixels) / 2500) #so for every 50 pixels we have we can support a new ship
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

        self.mo = MapObject(self.wsize, self)
        self.tile_image = data.image("water.png")
        self.cur_timer = 0
        self.cur_cycle = 0

        self.camera = Camera(self.ssize, self.wsize)

        self.islands = []
        self.units = []

        self.make_islands()

        self.font = pygame.font.Font(None, 30)

    def render(self, screen):
        self.cur_timer += 1
        if self.cur_timer >= 10:
            self.cur_timer = 0
            self.cur_cycle += 1
            if self.cur_cycle >= 25:
                self.cur_cycle = 0
        x, y = self.camera.get_offset()
        if x:
            tox = x % 25
        else:
            tox = 0
        if y:
            toy = y % 25
        else:
            toy = 0

        yy = xrange(-1,self.ssize[1]/25+2)

        for ix in xrange(-1,self.ssize[0]/25+2):
            for iy in yy:
                screen.blit(self.tile_image, (ix*25+tox+self.cur_cycle,
                                              iy*25+toy+self.cur_cycle))

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

        for i in self.mo.territories:
            px, py = i.pixels[int(len(i.pixels)/2)]
            
            px -= x
            py -= y
            screen.blit(self.font.render(str(i.pop_cap), 1, [0,0,0]),
                        (px, py))

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
            i = Island((x*125+offx, y*125+offy))
            i.get_random_resources()
            self.islands.append(i)
