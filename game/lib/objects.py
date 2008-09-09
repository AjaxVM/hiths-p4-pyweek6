import math, pygame, random
import data

class Ship(object):

    def __init__(self, territory, owner): # TODO: owner should be a reference to a player
        self._alive = True
        self.owner = owner
        self.territory = territory

        self.hull_max = 70
        self.hull = self.hull_max
        self.crew_max = 30
        self.crew = self.crew_max
        self.speed_max = 100
        self.speed = self.speed_max
        self.damage_multiplier = 1

        self.long_range = 200
        self.medium_range = 150
        self.short_range = 60

        self.image = data.image("ship.png")
        
        self.pos = list(self.territory.capitol.pos)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        self.hold_capacity = 40 # Resources can only equal this number total
        self.resources = Resources(0, 0, 0) # Start empty
        self.string = 300
        self.distance_from_capitol = 0

        self.can_move = True
        self.can_attack = True
        self.goto = None
        self.camera = self.owner.state.world.camera

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

    def move_to(self, pos):
        if self.can_move:
            co = self.camera.get_offset()
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
        if self.goto:
            self.pos = self.rect.center = self.get_next_pos()

    def render(self, screen, offset):
        ox, oy = offset
        x, y = self.rect.topleft
        x -= ox
        y -= oy
        screen.blit(self.image, (x, y))

class Resources(object):
    def __init__(self, gold, string, crew):
        self.gold = gold
        self.string = string
        self.crew = crew

class Island(object):
    def __init__(self, pos):
        self.pos = pos
        self.image = random.choice([data.image("island.png"), data.image("island2.png"), data.image("island3.png")])
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

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
        off = 15
        for i in self.resources:
            screen.blit(self.font.render(i, True, [0,0,0]), (x, y - off))
            off += 15

    def get_random_resources(self):
        choices = ["gold", "string", "crew"]
        num = random.randint(0,3)
        for i in xrange(num):
            x = random.choice(choices)
            choices.remove(x)
            self.resources.append(x)
