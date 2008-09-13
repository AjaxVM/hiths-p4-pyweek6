import random

# Minimum and maximum damage
_min_dmg = 25
_max_dmg = 80

# Percentages of damage for each ammo type
_dmg_table = {
    'ball'  : {'hull' : .70, 'crew' : .25, 'speed' : .05 },
    'chain' : {'hull' : .30, 'crew' : .30, 'speed' : .40 },
    'grape' : {'hull' : .25, 'crew' : .70, 'speed' : .05 }
}
_dmg_balance = { 'hull' : 1, 'crew' : 0.75, 'speed' : 8 }

_range_modifiers = { 'long' : 0.7, 'medium' : 1, 'close' : 1.2 }
_speed_defense_bonus = { 'long' : 0.1, 'medium' : 0.05, 'close' : 0 }
_low_crew_penalty = 0.2

# Boarding
_board_min = 2
_board_max = 5
_board_min_factor = 0.2

class Battle:
    """Represents a single battle between two ships. The two opponents should
    be passed as a tuple. The remaining variables should all be strings that
    are valid for what they are."""
    def __init__(self, opponents, attack_shot_type, defend_shot_type, range):
        self.opponents = opponents
        self.results = {}
        self.results['damage'] = {}
        self.range = range
        self.shot_types = attack_shot_type, defend_shot_type

    def execute(self):
        """Calculate battle results."""
        if self.shot_types[0] == 'board' or self.shot_types[1] == 'board':
            self._calculate_boarding()
        else:
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
            self.results['winner'] = self.opponents[1]
        elif self.opponents[1].crew <= 0:
            self.results['captured'] = self.opponents[1]
            self.results['winner'] = self.opponents[0]
        else:
            self.results['captured'] = None # Make sure this exists in results

        # For prettying up the results, comment out for real stats
        self._fix_stats()

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

        range_modifier = _range_modifiers[self.range] 
        # Grape is useless at long range
        if self.range == 'long' and self.shot_types[giver] == 'grape':
            range_modifier = 0

        damage = (ship.damage_multiplier * range_modifier \
                * random.randint(_min_dmg, _max_dmg)) - crew_penalty

        # Subtract some damage for fast target. 
        # The longer the range, the more damage subtracted.
        damage -= int(_speed_defense_bonus[self.range] * self.opponents[taker].speed)

        if damage < 0:
            damage = 0 # No negative damage

        hull, crew, speed = self._get_dmg_distribution(damage, self.shot_types[giver])
        self.opponents[taker].hull -= hull
        self.opponents[taker].crew -= crew
        self.opponents[taker].speed -= speed
        # Record damage information
        self.results['damage'][self.opponents[taker]] = (hull, crew, speed)

    def _calculate_boarding(self):
        """Compute a boarding attempt. Largest crew has the best advantage, but
        there is a deal of randomness."""
        # Use min factor to only slightly affect the numbers
        crew0_attack = random.randint(_board_min, _board_max) * _board_min_factor
        crew1_attack = random.randint(_board_min, _board_max) * _board_min_factor
##        print 'crew attack', crew0_attack, crew1_attack

        crew0_dmg = int(self.opponents[1].crew * crew1_attack)
        crew1_dmg = int(self.opponents[0].crew * crew0_attack)
        self.opponents[0].crew -= crew0_dmg
        self.opponents[1].crew -= crew1_dmg

        # Record damage information
        self.results['damage'][self.opponents[0]] = (0, crew1_dmg, 0)
        self.results['damage'][self.opponents[1]] = (0, crew0_dmg, 0)

    def _get_dmg_distribution(self, damage, shot_type):
        """Computes the distribution of damage based on the shot_type and
        returns damage for hull, crew, speed in that order."""
        dist = _dmg_table[shot_type]
        # Truncate so we don't deal fractional damage
        hull = int(damage * dist['hull'] * _dmg_balance['hull'])
        crew = int(damage * dist['crew'] * _dmg_balance['crew'])
        speed = int(damage * dist['speed'] * _dmg_balance['speed'])
        return (hull, crew, speed)

    def _get_crew_penalty(self, ship):
        """Get the penalty for having less than 50% crew. The penalty is
        relative to the number of missing crew."""
        if ship.crew <= (ship.crew_max / 2):
##            print 'Ship', ship.owner, 'suffering crew penalty'
            return int((ship.crew_max - ship.crew) * _low_crew_penalty)
        else:
            return 0

    def _fix_stats(self):
        for i in self.opponents:
            if i.hull < 0:
                i.hull = 0
            if i.crew < 0:
                i.crew = 0
            if i.speed < 5:
                i.speed = 5

