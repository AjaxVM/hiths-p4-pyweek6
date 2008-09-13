import pygame
import random
import math

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

class BrainShip(object):
    def __init__(self, ship):
        self.ship = ship
        self.assigned = False

        self.state = None
        self.target_pos = None #ship gather code handles this, movement won't.
        self.pstates = ["gather", "defend"]#, "invade", "retreat"] #everything it can do!

    def need_work(self):
        if not self.state in self.pstates:
            if not self.ship.am_gathering:
                return True

    def set_state(self, state=None, xtra=None):
        self.state = state
        self.target_pos = None
        if state == "gather":
            self.ship.am_gathering = True
        if state == "defend":
            self.target_pos = xtra
            self.ship.stop_gather()
##        if state == "invade":
##            self.target_pos = xtra
##            self.ship.stop_gather()

    def update(self):
        if self.ship.can_move:
            if self.target_pos:
                if self.target_pos.capitol.rect.collidepoint(self.ship.rect.center):
                    return None
                x = self.ship.move_to(self.target_pos.capitol.pos)
                if not x:
                    self.ship.move_to(self.ship.get_goto_spot(self.target_pos.capitol.pos))

class DefenseGroup(object):
    def __init__(self, terr, myships):
        self.terr = terr
        self.ships = myships

##class ConquestPrepClass(object):
##    def __init__(self, ai, ship, target_lock, dis):
##        self.ai = ai
##        self.ship = ship
##        self.target_lock = target_lock
##        self.dis = dis - self.ship.ship.string
##
##    def update(self):
##        self.ship.set_state("gather") # do something while we are waiting
##        if self.target_lock.player == self.ai.player:
##            self.ai.waiting_for_string.remove(self)
##        else:
##            if self.ai.player.resources.string >= self.dis:
##                self.ai.player.resources.string -= self.dis
##                self.ship.ship.string += self.dis
##                self.ship.set_state("invade", self.target_lock.territory)
##                self.ai.waiting_for_string.remove(self)

class AI(object):
    def __init__(self, state, player):
        self.state = state
        self.player = player
        self.build_up = 0

        self.bships = []
        self.finished = False
        self.have_defended = False
        self.defense_groups = []
        self.conquesting = False
##        self.waiting_for_string = []

    def gbtt_r(self, r, islands):
        agg = []
        r.inflate_ip(10, 10)
        while 1:
            r.inflate_ip(-10, -10)
            if r.width <= 40:
                return False
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
                        if x.rect.colliderect(r.inflate(-10, -10)):
                            if not x in agg[-1]:
                                agg[-1].append(x)
                if not agg[-1]:
                    agg.pop()

            if not agg:
                continue

            cur_largest = agg[0]
            for i in agg:
                if len(i) > len(cur_largest):
                    cur_largest = i

            r.topleft = cur_largest[0].rect.topleft
            for i in cur_largest:
                if i.rect.top < r.top:
                    r.top = i.rect.top
                if i.rect.left < r.left:
                    r.left = i.rect.left
            return r, (r.width+r.height)*2

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

        return self.gbtt_r(r, islands)
        

    def make_territory(self):
        self.build_up = 0
        x = self.get_best_territory()
        if not x:
            return False
        pt, m_size = x
        t = Territory(self.player)
        
        for i in [pt.topleft, pt.topright,
                  pt.bottomright, pt.bottomleft]:
            t.add_point(i)

        t.finish()
        if self.state.world.mo.test_territory(t):
            self.state.world.mo.add(t)
            t.create_name(constants.territory_first_name, constants.territory_second_name)
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

            if self.conquesting:
                return False

            if not self.build_up:
                self.build_up = random.randint(250, 500)
            if self.player.resources.string >= 500 + self.build_up:
                return True

    def need_defend(self):
        good = False
        for i in self.bships:
            if i.ship.can_move:
                good = True
                break
        if not good:
            return False
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

        return t

    def need_ships(self):
        nd = self.need_defend()
        terr = {}
        for i in self.player.territories:
            terr[i] = TerritoryShips(i)

        for i in self.player.ships:
            if i.territory.poly.colliderect(i.rect):
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

        return least

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
            if not self.player.build_ship(terr, t):
                return False
            self.bships.append(BrainShip(self.player.ships[-1]))
            return True
        return False

    def move_units_default(self):
        for i in self.bships:
            if i.need_work():
                i.set_state("gather")

    def end_turn(self):
        self.player.end_turn()

    def ready_attack(self):
        return False

    def get_closest(self, dif, terr, ignore):
        x1, y1 = terr.rect.center
        cur = {}
        for i in self.bships:
            if not (i in ignore) or (i.state == "defend"):
                x2, y2 = i.ship.rect.center
                dis = math.sqrt(abs(x2-x1)**2 + abs(y2-y1)**2)
                if cur:
                    n = max(cur)
                    if dis < n:
                        del cur[n]
                        cur[dis] = i
                else:
                    cur[dis] = i

        new = []
        for i in xrange(dif):
            if cur:
                s = min(cur)
                new.append(cur[s])
                del cur[s]
            else:
                break

        return new

    def force_defend(self, a):
        for t in a:
            dif = len(t.ships) - len(t.pships)

            s = self.get_closest(dif, t.terr, t.pships) + t.pships
            n = []

            for i in s:
                for x in self.bships:
                    if i == x.ship:
                        n.append(x)

            for i in n:
                i.set_state("defend", t.terr)
            self.defense_groups.append(DefenseGroup(t.terr, n))

    def check_def_groups(self):
        for i in self.defense_groups:
            good = True
            for x in self.state.players:
                if not x == self.player:
                    for s in x.ships:
                        if i.terr.rect.colliderect(s.rect) and i.terr.poly.colliderect(s.rect):
                            good = False
                            break
                if not good:
                    break

            if good:
                for s in i.ships:
                    s.set_state()
                self.defense_groups.remove(i)

##    def ready_to_war(self):
##        if not self.need_territory():
##            for i in self.player.territories:
##                n = []
##                for s in self.bships:
##                    if not s.state == "defend":
##                        if s.ship.territory == i:
##                            n.append(s)
##
##                if len(n) >= i.pop_cap - 1:
##                    self.conquesting = True
##                    t = []
##                    for x in self.state.world.mo.territories:
##                        if not x.player == self.player:
##                            t.append(x)
##
##                    cur = {}
##                    for x in t:
##                        x1, y1 = x.capitol.rect.center
##                        x2, y2 = i.capitol.rect.center
##                        dis = int(math.sqrt(abs((x1-x2))**2 + abs(y1-y2)**2))
##                        cur[dis] = x
##                    if not cur:
##                        continue
##                    pick = cur[min(cur)]
##                    for i in n:
####                        i.set_state()
##                        self.waiting_for_string.append(ConquestPrepClass(self, i, pick, min(cur)))

    def think(self):
        for i in self.bships:
            i.update()
##        for i in self.waiting_for_string:
##            i.update()
        if not self.have_defended:
            x = self.need_defend()
            if x:
                self.force_defend(x)
                self.have_defended = True
                return None

        self.check_def_groups()

        # this goes first for these little stinkers!
        self.move_units_default()

        if self.need_territory() and self.make_territory():
            return None

        x = self.need_ships()
        if x and self.make_ship(x):
            return None

##        self.ready_to_war()

        if self.player.have_lost():
            print "Died!"

        self.player.end_turn()
        self.have_defended = False
