import random
# TODO list:
# Implement boarding
# Implement misses based on opponent speed and range
# Make adjustments to the damage distribution based on what is being damaged,
# then we can have a realistically sized crew and also adequate speed.

# Minimum and maximum damage
_min_dmg = 20
_max_dmg = 60

# Percentages of damage for each ammo type
_dmg_table = {
        'ball'  : {'hull' : .70, 'crew' : .25, 'speed' : .05 },
        'chain' : {'hull' : .30, 'crew' : .20, 'speed' : .50 },
        'grape' : {'hull' : .25, 'crew' : .70, 'speed' : .05 }
        }

_range_modifiers = { 'long' : 0.5, 'medium' : 1, 'close' : 1.2 }
_low_crew_penalty = 0.2

class Battle:
    """Represents a single battle between two ships. The two opponents should
    be passed as a tuple. The attack_type is a tuple of (shot_type, range)."""
    def __init__(self, opponents, attack_type):
        self.opponents = opponents
        self.results = {}
        self.results['damage'] = {}

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
        # Ships attack eachother simultaneously
        self._do_damage(0,1)
        self._do_damage(1,0)

        # Check if either crew was wiped out, or if both were
        if self.opponents[0].crew <= 0 and self.opponents[1].crew <= 0:
            # The sea claims both unmanned ships..
            # These ships will fail the next checks
            self.opponents[0].hull = -1
            self.opponents[1].hull = -1
            self.results['captured'] = 0
        elif self.opponents[0].crew <= 0:
            self.results['captured'] = self.opponents[0]
        elif self.opponents[1].crew <= 0:
            self.results['captured'] = self.opponents[1]

        # Check ship status and set winner
        if not self.opponents[0].is_alive():
            self.results['winner'] = self.opponents[1] # Assume the other ship won
        if not self.opponents[1].is_alive():
            if 'winner' in self.results:
                del self.results['winner'] # Both ships sank
            else:
                self.results['winner'] = self.opponents[0]

    def _do_damage(self, giver, taker):
        """Calculates and applies damage."""
        ship = self.opponents[giver]
        crew_penalty = self._get_crew_penalty(ship)

        damage = (ship.damage_multiplier * _range_modifiers[self.range] \
                * random.randint(_min_dmg, _max_dmg)) - crew_penalty

        hull, crew, speed = self._get_dmg_distribution(damage, self.shot_types[giver])
        self.opponents[taker].hull -= hull
        self.opponents[taker].crew -= crew
        self.opponents[taker].speed -= speed
        # Record damage information
        self.results['damage'][ship] = (hull, crew, speed)

    def _get_dmg_distribution(self, damage, shot_type):
        """Computes the distribution of damage based on the shot_type and
        returns damage for hull, crew, speed in that order."""
        dist = _dmg_table[shot_type]
        # Truncate so we don't deal fractional damage
        hull = int(damage * dist['hull'])
        crew = int(damage * dist['crew'])
        speed = int(damage * dist['speed'])
        return (hull, crew, speed)

    def _get_crew_penalty(self, ship):
        """Get the penalty for having less than 50% crew. The penalty is
        relative to the number of missing crew."""
        if ship.crew <= (ship.crew_max / 2):
            print 'Ship', ship.owner, 'suffering crew penalty'
            return int((ship.crew_max - ship.crew) * _low_crew_penalty)
        else:
            return 0

