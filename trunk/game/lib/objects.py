import math, pygame, random

class Ship(object):
    image = pygame.Surface((25, 25)) # Image series the game should use to render
    image.fill((255, 0, 0))

    def __init__(self, pos, owner): # TODO: owner should be a reference to a player
        self._alive = True
        self.owner = owner

        self.hull_max = 70
        self.hull = self.hull_max
        self.crew_max = 50
        self.crew = self.crew_max
        self.speed_max = 100
        self.speed = self.speed_max
        self.damage_multiplier = 1
        self.distance_left = self.speed
        
        self.pos = list(pos)
        self.moved = False
        self.selected = False

        self.hold_capacity = 40 # Resources can only equal this number total
        self.resources = Resources(0, 0, 0) # Start empty

    def is_alive(self):
        """Returns the status of the ship, but checks that status first, so the
        ship can be 'sunk' (pruned from list of living ships) if need be."""
        if self.hull <= 0:
            self._alive = False
            return False
        else:
            return True

    def end_turn(self):
        self.distance_left = self.speed
        self.moved = False

    def move(self):
        """Moves the player to the mouse pos."""
        if self.distance_left > 0:
            pos, distance = self.get_mouse_pos()
            self.pos = list(pos)
            self.distance_left -= distance
        else:
            self.moved = True
        
    def get_mouse_pos(self):
        """Returns the pos of the mouse minus the distance left
        that the ship can go, and the distance you can move"""
        mx, my = pygame.mouse.get_pos()
        x = self.pos[0] - mx
        y = self.pos[1] - my
        angle = math.atan2(y, x)
        mouse_angle = int(270.0 - (angle * 180.0)/math.pi)
        pos = list(self.pos)
        xdiff = abs(mx-pos[0])
        ydiff = abs(my-pos[1])
        distance = math.sqrt((xdiff**2)+(ydiff**2))
        if distance > self.distance_left:
            distance = self.distance_left
        pos[0] += math.sin(math.radians(mouse_angle))*distance
        pos[1] += math.cos(math.radians(mouse_angle))*distance
        return pos, distance

    def render(self, screen, offset):
        ox, oy = offset
        x, y = self.pos
        x -= ox
        y -= oy
        screen.blit(self.image, (x, y))

class Resources(object):
    def __init__(self, gold, string, crew):
        self.gold = gold
        self.string = string
        self.crew = crew

class Island(object):
    #This won't work when loading images... the screen has to initialise :P
    #Look at around line 263 in world.py
    #images = {"img-10.png": pygame.Surface((50, 50))}
    #images.values()[0].fill((0, 255, 0)) #fill the island square

    def __init__(self, pos, size):
        self.pos = pos
        self.image = self.images["img-%s.png"%size]
        self.size = size
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        self.resources = [] #can be gold, crew and string
        self.font = pygame.font.Font(None, 20)

    def render(self, screen, offset):
        ox, oy = offset
        x, y = self.pos
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
