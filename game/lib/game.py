from objects import *
from combat import *

class State:
    """The black box. Contains all information about the game world and
    functions for interacting with it."""

    def __init__(self):
        self._ships = []

        # Make some ships for testing real quick
        for i in range(2):
            ship = Ship()
            self._ships.append(ship)

    def attack_ship(self, attacker, target, attack_type = ('ball', 'medium')):
        if attacker == target:
            return # Can't attack self
        b = Battle((self._ships[attacker], self._ships[target]), attack_type)
        b.execute()

    def find_ship(self, coords=(0,0)):
        """This will find a ship at the given map coordinates and return its 
        index for use in other operations."""
        return 1
