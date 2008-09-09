import pygame
from pygame.locals import *
from world import Territory


class TerritoryDrawer(object):
    def __init__(self, player, world):
        self.player = player
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
                            self.t = Territory(self.player.num)
                            self.t.add_point(pos)
                        else:
                            if self.t.within_range(pos):
                                if len(self.t.points) == 1:
                                    return None
                                self.t.finish()
                                if self.world.mo.test_territory(self.t):
                                    self.world.mo.add(self.t)
                                self.t = None
                                self.active = False
                            else:
                                self.t.add_point(pos)

    def render(self, screen):
        if self.t:
            ox, oy = self.world.camera.get_offset()
            np = []
            for i in self.t.points:
                x, y = i
                x -= ox
                y -= oy
                np.append((x, y))

            if len(np) > 1:
                pygame.draw.lines(screen, self.player.color, False, np, 1)
            pygame.draw.line(screen, self.player.color, np[-1], pygame.mouse.get_pos(), 3)
            for i in np:
                pygame.draw.rect(screen, self.player.color, [i[0]-10, i[1]-10, 20, 20])
