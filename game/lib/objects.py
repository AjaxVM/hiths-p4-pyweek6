class Ship:
    graphic = 'generic_ship' # Image series the game should use to render

    def __init__(self):
        self._alive = True

        self.hull_max = 50
        self.hull = self.hull_max
        self.crew_max = 50
        self.crew = self.crew_max
        self.speed_max = 10
        self.speed = self.speed_max
        self.damage_multiplier = 1

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

class Resources:
    def __init__(self, wood, string, crew):
        self.wood = wood
        self.string = string
        self.crew = crew

