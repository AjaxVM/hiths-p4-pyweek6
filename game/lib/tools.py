import pygame, random
from pygame.locals import *
from world import Territory


class ShipRangeRender(object):
    def __init__(self, ship, player, world):
        self.ship = ship
        self.player = player
        self.world = world

        #create the speed image
        self.move_circle = pygame.Surface([self.ship.speed*2, self.ship.speed*2]).convert()
        pygame.draw.circle(self.move_circle, [0, 255, 0], [self.ship.speed, self.ship.speed], self.ship.speed)

        m2 = self.move_circle.copy()
        m2.fill((0,0,0))
        p1 = self.ship.territory.capitol.pos
        p2 = self.ship.rect.center
        p2dif = p2[0] - self.ship.speed, p2[1] - self.ship.speed
        x = p1[0] - p2dif[0]
        y = p1[1] - p2dif[1]
        if self.ship.string:
            pygame.draw.circle(m2, [0, 255, 0], (x, y), self.ship.string)
        m2.set_colorkey((0, 255, 0), RLEACCEL)
        self.move_circle.blit(m2, (0,0))


        m3 = self.move_circle.copy()
        m3.fill((0,0,0))
        p = self.ship.rect.center
        np = []
        for i in self.ship.territory.points:
            x, y = i
            x -= p[0] - self.ship.speed
            y -= p[1] - self.ship.speed
            np.append((x, y))

        pygame.draw.polygon(m3, [0, 255, 0], np)
        m4 = m3.copy()
        m4.fill((0,0,0))
        pygame.draw.circle(m4, [0, 255, 0], [self.ship.speed, self.ship.speed], self.ship.speed)
        m4.set_colorkey((0, 255, 0), RLEACCEL)
        m3.blit(m4, (0,0))
        m3.set_colorkey((0,0,0), RLEACCEL)

        self.move_circle.blit(m3, (0,0))

        self.move_circle.set_colorkey((0,0,0), RLEACCEL)
        self.move_circle.set_alpha(175)

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

    def render(self, screen):
        ox, oy = self.world.camera.get_offset()
        x, y = self.ship.pos
        x -= ox
        y -= oy

        pos1 = (self.ship.rect.centerx - ox, self.ship.rect.centery - oy)
        pos2 = (self.ship.territory.capitol.pos[0] - ox, self.ship.territory.capitol.pos[1] - oy)
        if self.ship.can_move:
            screen.blit(self.move_circle, [x - self.ship.speed, y - self.ship.speed])
        if self.ship.can_attack:
            screen.blit(self.range_circle, [x - self.ship.long_range, y - self.ship.long_range])

        if not self.ship.rect.center in self.ship.territory.pixels:
            pygame.draw.line(screen, [random.randrange(255), random.randrange(255), random.randrange(255)], pos1, pos2, 3)

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
                            self.t = Territory(self.player)
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
