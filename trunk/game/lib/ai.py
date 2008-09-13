import pygame
import random

from world import Territory
import constants

class TerritoryInvaders(object):
    def __init__(self, terr):
        self.terr = terr
        self.ships = []
        self.pships = []

class TerritoryShips(object):
    def __init__(self, terr):
        self.terr = terr
        self.ships = []

class AI(object):
    def __init__(self, state, player):
        self.state = state
        self.player = player
        self.build_up = 0

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
        

    def make_territory(self):
        self.build_up = 0
        pt, m_size = self.get_best_territory()
        t = Territory(self.player)
        t.create_name(constants.territory_first_name, constants.territory_second_name)
        for i in [pt.topleft, pt.topright,
                  pt.bottomright, pt.bottomleft]:
            t.add_point(i)

        t.finish()
        if self.state.world.mo.test_territory(t):
            self.state.world.mo.add(t)
            self.player.resources.string -= m_size
            return True


    def need_territory(self):
        if self.player.territories == []: #first, find a good starting territory!
            return True
        if self.player.resources.string >= 250:
            for i in self.state.players:
                if i == self.player: continue
                if len(i.territories) > len(self.player.territories):
                    return True

            if not self.build_up:
                self.build_up = random.randint(250, 500)
            if self.player.resources.string >= 500 + self.build_up:
                return True

    def need_defend(self):
        t = []
        for i in self.player.territories:
            t.append(TerritoryInvaders(i))
            for x in self.state.players:
                if not x == self.player:
                    for j in x.ships:
                        if i.poly.colliderect(j.rect):
                            t[-1].ships.append(j)

        for i in t:
            if not i.ships:
                t.remove(i)

        for i in self.player.ships:
            for x in t:
                if i.territory == x.terr:
                    x.pships.append(i)

        for i in t:
            if len(i.ships) < len(i.pships)+random.randint(1, 3):
                t.remove(i)

        return t

    def need_ships(self):
        nd = self.need_defend()
        terr = {}
        for i in self.player.territories:
            terr[i] = TerritoryShips(i)

        for i in self.player.ships:
            terr[i.territory].ships.append(i)

        least = None
        for i in terr:
            if not least:
                least = i
            else:
                if i in nd and (not least in nd):
                    least = i
                    continue
                if least in nd and (not i in nd):
                    continue
                if len(terr[i].ships) + random.randint(-2, 2) < len(terr[least].ships):
                    least = i

        if nd or len(self.player.ships) < len(self.player.territories) * 3:
            return least
        return None

    def make_ship(self, terr):
        x = []
        r = self.player.resources
        if r.crew >= 30 and r.gold >= 50:
            x.extend(["junk"]*25)
        if r.crew >= 50 and r.gold >= 150:
            x.extend(["frigate"]*15)
        if r.crew >= 100 and r.gold >= 250:
            x.extend(["juggernaut"]*7)

        if x:
            t = random.choice(x)
            self.player.build_ship(terr, t)
            return True
        return False

    def move_units_default(self):
        for i in self.player.ships:
            if i.can_move: #special case defensive/aggressive or resource movement done first
                i.am_gathering = True

    def end_turn(self):
        self.player.end_turn()

    def think(self):
        # this goes first for these little stinkers!
##        self.move_units_default()
        for i in self.player.ships:
            i.am_gathering = True

        if self.need_territory() and self.make_territory():
            return None

        x = self.need_ships()
        if x and self.make_ship(x):
            return None

        self.end_turn()
