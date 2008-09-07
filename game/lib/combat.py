import random
# TODO list:
# Adjust for crew size
# Probably give a defender bonus, defender currently loses most of the time
# because the defender deals damage second
# Implement boarding
# Check for wiped out crew, but intact ship, in which case the ship can change hands
# Implement misses?

# Minimum and maximum damage
min_dmg = 15
max_dmg = 30

battle_rounds = 3

# Percentages of damage for each ammo type
_dmg_table = {
        'ball'  : {'hull' : .70, 'crew' : .25, 'speed' : .05 },
        'chain' : {'hull' : .30, 'crew' : .20, 'speed' : .50 },
        'grape' : {'hull' : .25, 'crew' : .70, 'speed' : .05 }
        }

_range_modifiers = { 'long' : 0.5, 'medium' : 1, 'close' : 1.2 }

class Battle:
    """Represents a single battle between two ships. The two opponents should
    be passed as a tuple. The attack_type is a tuple of (shot_type, range)."""
    def __init__(self, opponents, attack_type):
        self.opponents = opponents

        # Set up defender shot type, range is fixed
        d_shot_type = ''
        rand = random.randint(0, 10)
        if rand <= 7:
            d_shot_type = 'ball'
        else:
            d_shot_type = 'grape'
        print "Attack types: 0 - %s, 1 - %s, %s range." % (attack_type[0], d_shot_type, attack_type[1])

        self.shot_types = (attack_type[0], d_shot_type)
        self.range = attack_type[1]

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

        # Check attacker's status one more time
        if not self.opponents[0].is_alive():
                print 'Ship', 1, 'sunk', 0

        s0 = self.opponents[0]
        s1 = self.opponents[1]
        print 'Combat end. Ship 0:', s0.hull, s0.crew, s0.speed, 'Ship 1:', s1.hull, s1.crew, s1.speed

    def choose_attack_type(self):
        """Selects the most optimal attack based on the condition of the target."""

    def _do_damage(self, giver, taker):
        """Calculates and applies damage. If a ship is dead, returns True so
        the battle can end."""
        ship = self.opponents[giver]
        if not ship.is_alive():
            return True
        damage = ship.damage_multiplier * _range_modifiers[self.range] * random.randint(min_dmg, max_dmg)

        hull, crew, speed = self._get_dmg_distribution(damage, self.shot_types[giver])
        self.opponents[taker].hull -= hull
        self.opponents[taker].crew -= crew
        self.opponents[taker].speed -= speed
        print "Ship %s attack" % giver, damage

    def _get_dmg_distribution(self, damage, shot_type):
        """Computes the distribution of damage based on the shot_type and
        returns damage for hull, crew, speed in that order."""
        dist = _dmg_table[shot_type]
        # Truncate so we don't deal fractional damage
        hull = int(damage * dist['hull'])
        crew = int(damage * dist['crew'])
        speed = int(damage * dist['speed'])
        return (hull, crew, speed)

