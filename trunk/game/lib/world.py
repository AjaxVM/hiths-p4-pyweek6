import pygame
from pygame.locals import *

##from territory_draw import MapObject, Territory
from collisions import Polygon, Vector


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
            if i.poly.collidepoly(terr.poly):
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
        r = pygame.Rect(self.points[0][0]-10, self.points[0][1]-10, 20, 20)
        return r.collidepoint(pos)


class TerritoryDrawer(object):
    def __init__(self, world):
        self.world = world

        self.t = None
        self.active = False

    def update_event(self, event):
        if self.active:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    ox, oy = self.world.camera.get_offset()
                    x += ox
                    y += oy
                    pos = x, y
                    if self.world.mo.test_point(pos):
                        if not self.t:
                            self.t = Territory()
                            self.t.add_point(pos)
                        else:
                            if self.t.within_range(pos):
                                print "done"
                                self.t.finish()
                                if self.world.mo.test_territory(self.t):
                                    self.world.mo.add(self.t)
                                self.t = None
                            else:
                                self.t.add_point(pos)

    def render(self, screen):
        if self.active:
            ox, oy = self.world.camera.get_offset()
            if self.t:
                np = []
                for i in self.t.points:
                    x, y = i
                    x -= ox
                    y -= oy
                    np.append((x, y))

                if len(np) > 1:
                    pygame.draw.lines(screen, [255, 0, 0], False, np, 1)
                pygame.draw.line(screen, [255,0,0], np[-1], pygame.mouse.get_pos(), 3)
                for i in np:
                    pygame.draw.rect(screen, [255, 75, 75], [i[0]-10, i[1]-10, 20, 20])
                


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

        self.tile_image = pygame.Surface((25, 25))
        self.tile_image.fill((75, 75, 255)) #only till we have a good image


        self.camera = Camera(self.ssize, self.wsize)

        self.islands = []
        self.units = []

    def render(self, screen):
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
                screen.blit(self.tile_image, (ix*25+tox, iy*25+toy))
        for i in self.islands:
            i.render(screen, (x, y))

        for i in self.units:
            i.render(screen, (x, y))

        for i in self.mo.territories:
            np = []
            for p in i.points:
                px, py = p
                px -= x
                py -= y
                np.append((px, py))
            pygame.draw.polygon(screen, [255,0,0], np)
            pygame.draw.polygon(screen, [0,255,0], np, 3)



def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))

    world = World()
    tdraw = TerritoryDrawer(world)
    tdraw.active = True

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return None

            tdraw.update_event(event)


        x, y = pygame.mouse.get_pos()
        if x <= 5:
            world.camera.move(-5, 0)
        if x >= 635:
            world.camera.move(5, 0)
        if y <= 5:
            world.camera.move(0, -5)
        if y >= 475:
            world.camera.move(0, 5)

        world.render(screen)
        tdraw.render(screen)
        pygame.display.flip()

main()
