import math, pygame, random
import data

def safe_div(x, y):
    if x and y:
        return x / y
    return 0

ship_types = {
    'junk' : \
        { 'hull' : 70, 'crew' : 30, 'speed' : 200, \
        'hold_capacity' : 40, 'damage_multiplier' : 1.2, 'cost' : 50 },
    'frigate' : \
        { 'hull' : 120, 'crew' : 50, 'speed' : 120, \
        'hold_capacity' : 100, 'damage_multiplier' : 1, 'cost' : 150 },
    'juggernaut' : \
        { 'hull' : 180, 'crew' : 100, 'speed' : 80, \
        'hold_capacity' : 80, 'damage_multiplier' : 2.5, 'cost' : 250 },
    'merchant' : \
        { 'hull' : 100, 'crew' : 20, 'speed' : 140, \
        'hold_capacity' : 150, 'damage_multiplier' : 0.5, 'cost' : 40 },
    'dutchman' : \
        { 'hull' : 400, 'crew' : 80, 'speed' : 100, \
        'hold_capacity' : 0, 'damage_multiplier' : 3, 'cost' : 350 }
    # TODO: add capitol/city here or subclass it from ship, or just make it
    # have the same attributes?
}

class Ship(object):
    long_range = 200
    medium_range = 150
    close_range = 60

    def __init__(self, territory, owner, type='frigate', oldship=None, test=False):
        self._alive = True
        self.owner = owner
        self.type = type

        td = ship_types[type]
        self.hull_max = td['hull']
        self.crew_max = td['crew']
        self.speed_max = td['speed']

        if oldship:
            self.hull = oldship.hull
            self.crew = oldship.crew
            self.speed = oldship.speed
        else:
            self.hull = self.hull_max
            self.crew = self.crew_max
            self.speed = self.speed_max

        self.damage_multiplier = td['damage_multiplier']

        # Keep compatibility with battle_test, all new variables need to go
        # below here.
        if test:
            return

        self.territory = territory
        self.image = data.image(self.type+".png")
        self.shadow = data.image(self.type+"_shadow.png")
        self.anchor = data.image("anchor.png")
        
        self.pos = self._get_spawn_pos()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.aoff = self.rect.width - self.anchor.get_width(), self.rect.height - self.anchor.get_height()

        # Total resources can only equal hold capacity
        self.hold_capacity = td['hold_capacity']

        if oldship:
            self.resources = oldship.resources
        else:
            self.resources = Resources(0, 0, 0) # Start empty

        self.string = 300#0
        self.distance_from_capitol = 0
        self.am_gathering = False
        self.gather_target = "gold"
        self.gather_island = None
        self.gather_moveto = None

        self.can_move = True
        self.can_attack = True
        self.goto = None
        self.camera = self.owner.state.world.camera
        self.vertical_offset = 0
        self.hopping = False
        self.anchored_to = territory.capitol

    def moving(self):
        return not (self.gather_moveto == None and self.goto == None)

    def is_alive(self):
        """Returns the status of the ship, but checks that status first, so the
        ship can be 'sunk' (pruned from list of living ships) if need be."""
        if self.hull <= 0:
            self._alive = False
            return False
        else:
            return True

    def end_turn(self):
        self.can_move = True
        self.can_attack = True

    def get_goto_spot(self, final):
        mx, my = final
        x, y = self.pos
        x -= mx
        y -= my

        angle = math.atan2(y, x)
        if angle:
            mangle = int(270.0 - (angle * 180) / math.pi)
        else:
            mangle = 0

        x, y = self.pos
        x += int(math.sin(math.radians(mangle))*self.speed)
        y += int(math.cos(math.radians(mangle))*self.speed)

        return x, y

    def get_gather_island(self):
        islands = self.territory.islands
        tot = self.owner.resources.get_total()
        have_percents = [int(safe_div(tot*1.0, self.owner.resources.gold*10)),
                         int(safe_div(tot*1.0, self.owner.resources.string*10)),
                         int(safe_div(tot*1.0, self.owner.resources.crew*10))]
        difs = [self.owner.gather_targets[0] - have_percents[0],
                self.owner.gather_targets[1] - have_percents[1],
                self.owner.gather_targets[2] - have_percents[2]]

        ptarget = min(difs)
        gtarget = ["gold", "string", "crew"][difs.index(ptarget)]

        cur = None

        for i in islands:
            if gtarget in i.resources:
                if not cur:
                    cur = i
                    continue
                if self.get_range(i) < self.get_range(cur):
                    cur = i
                    continue

        while not cur:
            if not difs:
                break
            difs.remove(ptarget)
            if not difs:
                break
            ptarget = min(difs)
            ntarget = ["gold", "string", "crew"]
            ntarget.remove(gtarget)
            gtarget = ntarget[difs.index(ptarget)]

            for i in islands:
                if gtarget in i.resources:
                    if not cur:
                        cur = i
                        continue
                    if self.get_range(i) < self.get_range(cur):
                        cur = i
                        continue

        return cur, gtarget

    def do_gather(self):
        if not self.resources.get_total():
            if self.gather_moveto:
                if self.rect.colliderect(self.gather_island.rect):
                    self.gather_moveto = None
                    self.anchored_to = self.gather_island
                    self.resources.fill_by_type(self.gather_target, self.hold_capacity)
                    self.can_move = False
                    print str(self.resources)
                    return None
                if self.hopping:
                    if self.vertical_offset < 50:
                        self.vertical_offset += 2
                else:
                    if self.vertical_offset > 0:
                        self.vertical_offset -= 4
                        if self.vertical_offset < 0:
                            self.vertical_offset = 0
                self.goto = self.gather_moveto
                self.pos = self.rect.center = self.get_next_pos()
                if not self.goto:
                    self.gather_moveto = None
                    self.vertical_offset = 0
                    self.hopping = False
                    self.can_move = False
                    return None
                self.goto = None

                self.hopping = False
                self.anchored_to = None
                for i in self.territory.islands:
                    if i.rect.collidepoint(self.rect.center):
                        if i.rect.collidepoint(self.gather_moveto):
                            if i == self.gather_island:
                                self.resources.fill_by_type(self.gather_target, self.hold_capacity)
                                print str(self.resources)
                            self.vertical_offset = 0
                            self.hopping = False
                            self.gather_moveto = None
                            self.anchored_to = i
                            self.can_move = False
                            return None
                        else:
                            self.hopping = True
                        break
            else:
                if self.can_move and self.owner.is_turn():
                    goto, t = self.get_gather_island()
                    if not goto:
                        return None
                    self.gather_moveto = self.get_goto_spot(goto.pos)
                    self.gather_island = goto
                    self.gather_target = t
        else:
            if self.gather_moveto:
                if self.territory.capitol.rect.collidepoint(self.rect.center):
                    self.gather_moveto = None
                    self.anchored_to = self.territory.capitol
                    self.owner.resources + self.resources
                    self.resources.clear()
                    self.can_move = False
                    return None
                if self.hopping:
                    if self.vertical_offset < 50:
                        self.vertical_offset += 2
                else:
                    if self.vertical_offset > 0:
                        self.vertical_offset -= 4
                        if self.vertical_offset < 0:
                            self.vertical_offset = 0
                self.goto = self.gather_moveto
                self.pos = self.rect.center = self.get_next_pos()
                if not self.goto:
                    self.gather_moveto = None
                    self.vertical_offset = 0
                    self.hopping = False
                    self.can_move = False
                    return None
                self.goto = None

                self.hopping = False
                self.anchored_to = None

                if self.territory.capitol.rect.collidepoint(self.rect.center):
                    self.gather_moveto = None
                    self.anchored_to = self.territory.capitol
                    self.owner.resources + self.resources
                    self.resources.clear()

                    self.vertical_offset = 0
                    self.hopping = False
                    self.can_move = False
                    return None

                for i in self.territory.islands:
                    if i.rect.collidepoint(self.rect.center):
                        if i.rect.collidepoint(self.gather_moveto):
                            self.vertical_offset = 0
                            self.hopping = False
                            self.gather_moveto = None
                            self.anchored_to = i
                            self.can_move = False
                            return None
                        else:
                            self.hopping = True
                        break
            elif self.can_move and self.owner.is_turn():
                self.gather_moveto = self.get_goto_spot(self.territory.capitol.pos)

    def move_to(self, pos):
        if self.can_move:
            co = self.camera.get_offset()
            if not pos in self.territory.pixels:
                distance_to_capital = math.sqrt((abs(pos[0]-self.territory.capitol.pos[0])**2) + \
                                                (abs(pos[1]-self.territory.capitol.pos[1])**2))
                if distance_to_capital < self.string:
                    distance = math.sqrt((abs(pos[0]-self.pos[0])**2) + (abs(pos[1]-self.pos[1])**2))
                    if not distance <= self.speed:
                        return False
                    self.goto = pos
                    self.can_move = False
                    self.distance_from_capitol = math.sqrt((abs(pos[0]-self.territory.capitol.pos[0])**2) +\
                                                           (abs(pos[1]-self.territory.capitol.pos[1])**2))
                    return True
                else:
                    return False
            else:
                if self.anchored_to:
                    if self.anchored_to.rect.collidepoint(pos):
                        return False
                distance = math.sqrt((abs(pos[0]-self.pos[0])**2) + (abs(pos[1]-self.pos[1])**2))
                if distance <= self.speed:
                    self.goto = pos
                    self.can_move = False
                    return True

    def get_next_pos(self):
        mx, my = self.goto
        x, y = self.pos
        x -= mx
        y -= my

        angle = math.atan2(y, x)
        if angle:
            mangle = int(270.0 - (angle * 180) / math.pi)
        else:
            mangle = 0

        x, y = self.pos
        x += int(math.sin(math.radians(mangle))*3)
        y += int(math.cos(math.radians(mangle))*3)

        if abs(x-mx) + abs(y-my) < 5:
            self.goto = None
            self.can_move = False
            return mx, my

        return x, y

    def update(self):
        if self.am_gathering:
            self.do_gather()
        elif self.goto:
            if self.hopping:
                if self.vertical_offset < 50:
                    self.vertical_offset += 2
            else:
                if self.vertical_offset > 0:
                    self.vertical_offset -= 4
                    if self.vertical_offset < 0:
                        self.vertical_offset = 0
            self.pos = self.rect.center = self.get_next_pos()

            if not self.goto:
                self.vertical_offset = 0
                self.hopping = False
                return None

            self.hopping = False
            self.anchored_to = None
            for i in self.owner.state.world.islands:
                if i.rect.collidepoint(self.rect.center):
                    if i.rect.collidepoint(self.goto):
                        self.vertical_offset = 0
                        self.hopping = False
                        self.goto = None
                        self.anchored_to = i
                        return None
                    else:
                        self.hopping = True
                        break
        else:
            self.vertical_offset = 0
            self.hopping = False

    def render(self, screen, offset):
        ox, oy = offset
        x, y = self.rect.topleft
        x -= ox
        y -= oy
        if self.hopping:
            screen.blit(self.shadow, (x, y))
        screen.blit(self.image, (x, y-self.vertical_offset))
        if self.anchored_to:
            screen.blit(self.anchor, (x+self.aoff[0], y+self.aoff[1]))

    def get_range(self, target):
        distance = math.sqrt((abs(target.pos[0]-self.pos[0])**2) 
            + (abs(target.pos[1]-self.pos[1])**2))

        if distance <= self.close_range:
            return 'close'
        if distance <= self.medium_range:
            return 'medium'
        if distance <= self.long_range:
            return 'long'
        else:
            return None

    def sink(self):
        """Sinks this ship taking all who crew her to the depths."""
        self.owner.ships.remove(self)

    def take_ship(self, oldship):
        """Captures an enemy ship and "does the right thing" with all its 
        data"""
        oldship.owner.ships.remove(oldship)
        ship = Ship(self.territory, self.owner, oldship.type, oldship=oldship)
        ship.pos = oldship.pos
        ship.goto = self.pos
        ship.crew = 20
        self.owner.ships.append(ship)

    def _get_spawn_pos(self):
        r = self.territory.capitol.rect
        choices = (r.topleft, r.topright, r.bottomright, r.bottomleft)
        return random.choice(choices)

class Resources(object):
    def __init__(self, gold, string, crew):
        self.gold = gold
        self.string = string
        self.crew = crew

    def fill_by_type(self, name, amount):
        self.clear()
        setattr(self, name, amount)

    def add_by_type(self, name, amount):
        setattr(self, name, getattr(self, name)+amount)

    def __add__(self, arg):
        self.gold += arg.gold
        self.string += arg.string
        self.crew += arg.crew

    def __sub__(self, arg):
        self.gold -= arg.gold
        self.string -= arg.string
        self.crew -= arg.crew

    def clear(self):
        self.gold = 0
        self.string = 0
        self.crew = 0

    def __lt__(self, arg):
        return self.gold < arg.gold or self.string < arg.string or self.crew < arg.crew
    def __gt__(self, arg):
        return self.gold > arg.gold or self.string > arg.string or self.crew > arg.crew
    def __le__(self, arg):
        return self.gold <= arg.gold or self.string <= arg.string or self.crew <= arg.crew
    def __ge__(self, arg):
        return self.gold >= arg.gold or self.string >= arg.string or self.crew >= arg.crew
    def __str__(self):
        return "gold %s, string %s, crew %s" % (self.gold, self.string, self.crew)

    def get_total(self):
        return self.gold + self.string + self.crew

class Island(object):
    def __init__(self, pos):
        self.pos = pos
        self.image = random.choice([data.image("island.png"), data.image("island2.png"), data.image("island3.png")])
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.capitol = False
        self.capitol_image = data.image("island_capitol-test.png")
        self.cap_rect = self.capitol_image.get_rect()
        self.cap_rect.midbottom = self.rect.center

        self.resources = [] #can be gold, crew and string
        self.font = data.font(None, 20)

    def render(self, screen, offset):
        ox, oy = offset
        x, y = self.rect.topleft
        x -= ox
        y -= oy
        if (x < -self.rect.width) or (x >= 640 + self.rect.width) or\
           (y < -self.rect.height) or (y >= 480 +self.rect.height):
            return None
        screen.blit(self.image, (x, y))
        if self.capitol:
            cx, cy = self.cap_rect.topleft
            cx -= ox
            cy -= oy
            screen.blit(self.capitol_image, (cx, cy))
        off = 15
        for i in self.resources:
            screen.blit(self.font.render(i, True, [0,0,0]), (x, y - off))
            off += 15

    def get_random_resources(self):
        choices = ["gold", "string", "crew"]
        num = random.randint(1,3)
        for i in xrange(num):
            x = random.choice(choices)
            choices.remove(x)
            self.resources.append(x)
