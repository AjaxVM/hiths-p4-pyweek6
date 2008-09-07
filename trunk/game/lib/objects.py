import math, pygame

class Ship:
    graphic = 'generic_ship' # Image series the game should use to render

    def __init__(self, pos):
        self._alive = True

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

        self.hold_capacity = 40 # Resources can only be this number total
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

class Resources:
    def __init__(self, wood, string, crew):
        self.wood = wood
        self.string = string
        self.crew = crew

