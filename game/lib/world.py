import pygame, math
from pygame.locals import *


from collisions import Polygon, Vector, line_intersect
import math
import random
from objects import *
import data
import constants


class MapObject(object):
    def __init__(self, size, world):
        self.world = world
        self.size = size
        self.territories = []
        self.territories_by_player = []

    def add(self, terr):
        self.territories.append(terr)
        while terr.player.pnum >= len(self.territories_by_player):
            self.territories_by_player.append([])
        self.territories_by_player[terr.player.pnum].append(terr)

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
            r = pygame.Rect(0,0,7,7)
            r.center = i.rect.center
            if terr.rect.colliderect(r) and terr.poly.colliderect(r):
                islands.append(i)
        if not islands:
            return False

        terr.islands = islands
        terr.calculate_ship_support_cap()
        terr.get_capitol()
        return True

    def get_territories(self, pnum):
        while pnum >= len(self.territories_by_player):
            self.territories_by_player.append([])
        return self.territories_by_player[pnum]


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
        self.capitol = None
        self.resources = (0,0,0)
        
        self.name = None

    def create_name(self, first_name, second_name):
        self.name = first_name[random.randint(0,len(first_name)-1)] + second_name[random.randint(0,len(second_name)-1)]

    def add_point(self, point):
        self.points.append(point)

    def finish(self):
        self.points.append(self.points[0])
        self.get_pixels()
        self.calculate_ship_support_cap()

    def get_capitol(self):
        if self.islands:
            x = list(self.islands)
            empty = []
            for i in x:
                if i.capitol:
                    x.remove(i)
                    continue
                if not i.resources:
                    empty.append(i)
            if empty:
                self.capitol = random.choice(empty)
            else:
                self.capitol = random.choice(self.islands)
            self.capitol.capitol = True
            self.capitol.resources = []

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

        self.pixels = set(self.pixels)


    def within_range(self, pos):
        r = pygame.Rect(self.points[0][0]-10, self.points[0][1]-10, 20, 20)
        return r.collidepoint(pos)

    def calculate_ship_support_cap(self):
        area_amount = int(len(self.pixels) / 5000) #so for every 5000 pixels we have we can support a new ship
        island_amount = len(self.islands) * 3 #so for each island we get 3 new ships we can support
        default_amount = 1 #this is what you automatically will get

        self.pop_cap = area_amount + island_amount + default_amount


class Camera(object):
    def __init__(self, view, world, screen_rect):
        self.view = view
        self.world = world
        self.screen_rect = screen_rect

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

    def center_at(self, pos):
        self.rect.center = pos
        self.move(0,0)


class World(object):
    def __init__(self, screen_size=(640, 480),
                 world_size = (5000, 5000),
                 screen_rect=(640, 480),
                 screen=None):
        self.ssize = screen_size
        self.wsize = world_size

        self.mo = MapObject(self.wsize, self)
        self.tile_image = data.image("water.png")
        self.rock = data.image("rock.png")
        self.cur_timer = 0
        self.cur_cycle = 0

        self.camera = Camera(self.ssize, self.wsize, screen_rect)

        self.islands = []

        self.make_islands()

        self.font = data.font(None, 30)
        self.font2 = data.font("Pieces-of-Eight.ttf", 25)
        
        self.screen = screen

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

        yy = xrange(-2,self.ssize[1]/25+4)

        for ix in xrange(-2,self.ssize[0]/25+4):
            for iy in yy:
                screen.blit(self.tile_image, (ix*25+tox+self.cur_cycle,
                                              iy*25+toy+self.cur_cycle))

        for i in self.mo.territories:
            if i.poly.colliderect(self.camera.rect.inflate(45, 45)):
                np = []
                for p in i.points:
                    px, py = p
                    px -= x
                    py -= y
                    np.append((px, py))
                pygame.draw.polygon(screen, constants.player_colors[i.player.pnum], np, 3)
                
                for j in np:
                    self.screen.blit(self.rock,(j[0]-16,j[1]+8))
          
        for i in self.islands:
            if i.rect.colliderect(self.camera.rect.inflate(45, 45)):
                i.render(screen, (x, y))

        for i in self.mo.territories:
            ox, oy = self.camera.get_offset()
            ren = self.font2.render(i.name, 1, (0, 0, 0))
            self.screen.blit(ren, (i.capitol.pos[0]-ren.get_width()/2 - ox + 1, i.capitol.pos[1] + 50 - oy + 1))
            ren = self.font2.render(i.name, 1, (255, 255, 0))
            self.screen.blit(ren, (i.capitol.pos[0]-ren.get_width()/2 - ox, i.capitol.pos[1] + 50 - oy))

    def make_islands(self):
        grid = []
        for x in xrange(1,int(self.wsize[0]/125)):
            for y in xrange(1,int(self.wsize[1]/125)):
                grid.append((x, y))
        self.islands = []
        for x in xrange(int(len(grid)/3)):
            x, y = random.choice(grid)
            grid.remove((x, y))
            offx = random.randint(-25,50)
            offy = random.randint(-25,50)
            i = Island((x*125+offx, y*125+offy))
            i.get_random_resources()
            self.islands.append(i)

