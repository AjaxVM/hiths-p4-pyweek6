import pygame
from pygame.locals import *
from world import Territory


class ShipRangeRender(object):
    def __init__(self, ship, player, world):
        self.ship = ship
        self.player = player
        self.world = world
        self.move_circle = pygame.Surface([self.ship.speed*2, self.ship.speed*2]).convert()
        pygame.draw.circle(self.move_circle, [0, 255, 0], [self.ship.speed, self.ship.speed], self.ship.speed)
        self.move_circle.set_colorkey(self.move_circle.get_at((0,0)), RLEACCEL)
        self.move_circle.set_alpha(125)

        self.range_circle = pygame.Surface([self.ship.long_range*2, self.ship.long_range*2]).convert()
        pygame.draw.circle(self.range_circle, [255, 255, 0],
                           [self.ship.long_range, self.ship.long_range],
                            self.ship.long_range, 3)
        pygame.draw.circle(self.range_circle, [255, 165, 0],
                           [self.ship.long_range, self.ship.long_range],
                            self.ship.medium_range, 3)
        pygame.draw.circle(self.range_circle, [255, 0, 0],
                           [self.ship.long_range, self.ship.long_range],
                            self.ship.short_range, 3)
        self.range_circle.set_colorkey(self.range_circle.get_at((0,0)), RLEACCEL)
        self.range_circle.set_alpha(100)

    def render(self, screen):
        ox, oy = self.world.camera.get_offset()
        x, y = self.ship.pos
        x -= ox
        y -= oy

        if self.ship.can_move:
            screen.blit(self.move_circle, [x - self.ship.speed, y - self.ship.speed])
##            pygame.draw.circle(screen, [0, 255, 0], (x, y), self.ship.speed, 3)
        if self.ship.can_attack:
##            pygame.draw.circle(screen, [255, 255, 0], (x, y), self.ship.long_range, 3)
##            pygame.draw.circle(screen, [255, 165, 0], (x, y), self.ship.medium_range, 3)
##            pygame.draw.circle(screen, [255, 0, 0], (x, y), self.ship.short_range, 3)
            screen.blit(self.range_circle, [x - self.ship.long_range, y - self.ship.long_range])


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
                                    self.player.territories.append(self.t)
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
