import random

# Minimum and maximum damage
min_dmg = 10
max_dmg = 25

battle_rounds = 3

# Percentages of damage for each ammo type
_dmg_table = {
        'ball'  : {'hull' : 70, 'crew' : 25, 'speed' : 5 },
        'chain' : {'hull' : 30, 'crew' : 20, 'speed' : 50 },
        'grape' : {'hull' : 25, 'crew' : 70, 'speed' : 5 }
        }

_range_modifiers = { 'long' : 0.5, 'medium' : 1, 'close' : 1.2 }

class Battle:
    """Represents a single battle between two ships. The two opponents should
    be passed as a tuple. The attack_type is a tuple of (shot_type, range)."""
    # TODO: the defender needs to pick a shot type, probably mostly ball, but perhaps grape
    def __init__(self, opponents, attack_type):
        self.opponents = opponents

    def execute(self):
        """Calculate battle results."""
        # Each ship attacks battle_rounds times, taking turns until one dies or
        # the rounds run out. Attacker goes first.
        for i in range(battle_rounds):
            if self._do_damage(0,1):
                print 'Ship', 1, 'sunk', 0
                break
            if self._do_damage(1,0): # Tip for tap
                print 'Ship', 0, 'sunk', 1
                break

        print 'Combat end. Ship 0:', self.opponents[0].hull, 'Ship 1:', self.opponents[1].hull

    def _do_damage(self, giver, taker):
        """Calculates and applies damage. If a ship is dead, returns True so
        the battle can end."""
        ship = self.opponents[giver]
        if not ship.is_alive():
            return True
        damage = ship.damage_multiplier * random.randint(min_dmg, max_dmg)
        self.opponents[taker].hull -= damage
        print "Ship %s attack" % giver, damage

