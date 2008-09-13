import pygame
import random

from world import Territory

class AI(object):
    def __init__(self, state, player):
        self.state = state
        self.player = player

    def gbtt_r(self, r, islands):
        agg = []
        for i in islands:
            r.topleft = i.rect.topleft
            p = True

            for c in self.state.players:
                if not p:
                    break
                for t in c.territories:
                    if t.poly.colliderect(r):
                        p = False
                        break
            if not p:
                continue

            agg.append([])
            for x in islands:
                if not i == x: #this might get slowish...
                    if x.rect.colliderect(r):
                        if not x in agg[-1]:
                            agg[-1].append(x)

        cur_largest = agg[0]
        for i in agg[1::]:
            if len(i) > len(cur_largest):
                cur_largest = i


        for i in cur_largest:
            if i.rect.top < r.top:
                r.top = i.rect.top
            if i.rect.left < r.left:
                r.left = i.rect.left

        return r

    def get_best_territory(self):
        islands = list(self.state.world.islands)
        for i in self.state.players:
            for x in i.territories:
                for c in x.islands:
                    islands.remove(c)

        s = self.player.resources.string
        m = 1
        if s == 0:
            m_size = 0
        else:
            m_size = int(s / 4)

        r = pygame.Rect(0,0,m_size, m_size)

        return self.gbtt_r(r, islands), m_size*4
        

    def make_territory(self, pt, m_size):
        t = Territory(self.player)
        for i in [pt.topleft, pt.topright,
                  pt.bottomright, pt.bottomleft]:
            t.add_point(i)

        t.finish()
        if self.state.world.mo.test_territory(t):
            self.state.world.mo.add(t)
            self.player.resources.string -= m_size

    def think(self):
        if not self.player.territories: #first, find a good starting territory!
            self.make_territory(*self.get_best_territory())
