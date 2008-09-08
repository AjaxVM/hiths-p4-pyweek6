import pygame
from pygame.locals import *

from world import *
from objects import *

import random

class TerritoryDrawer(object):
    def __init__(self, world, player=0):
        self.world = world

        self.t = None
        self.active = False

        self.player = player
        self.button = 1

    def update_event(self, event):
        if self.active:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == self.button:
                    x, y = event.pos
                    ox, oy = self.world.camera.get_offset()
                    x += ox
                    y += oy
                    pos = x, y
                    if self.world.mo.test_point(pos):
                        if not self.t:
                            self.t = Territory(self.player)
                            self.t.add_point(pos)
                        else:
                            if self.t.within_range(pos):
                                self.t.finish()
                                if self.world.mo.test_territory(self.t):
                                    for i in self.world.islands:
                                        if self.t.poly.colliderect(i.rect):
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))

    world = World(world_size=(1500, 1500))
    tdraw = TerritoryDrawer(world)
    tdraw.active = True

    tdraw2 = TerritoryDrawer(world, 1)
    tdraw2.active = True
    tdraw2.button = 3

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return None

            tdraw.update_event(event)
            tdraw2.update_event(event)


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
        tdraw2.render(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
