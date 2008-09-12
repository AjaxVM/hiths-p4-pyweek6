from objects import *
from combat import *

def main():
    ships = []
    # Make some ships for testing real quick
    for i in range(2):
        ship = Ship(None, i, 'frigate', test=True)
        ships.append(ship)

    turn = 0
    print 'Player', ships[0].owner, ships[0].type, ' vs. ',
    print 'Player', ships[1].owner, ships[1].type

    while ships[0].is_alive() and ships[1].is_alive():
        print '-- Turn', turn,
        b = Battle((ships[0], ships[1]), ('ball', 'medium'), 'ball')
        b.execute()
        dmg = b.results['damage']
        print 'Damage: Ship', ships[0].owner, dmg[ships[0]], \
              'Ship', ships[1].owner, dmg[ships[1]]

        if 'captured' in b.results:
            if b.results['captured'] == 0:
                print 'Both crews were wiped out'
            else:
                print 'Ship', b.results['captured'].owner, 'was captured'
            break
        turn += 1

    print '--',
    print 'Ship 0:', ships[0].hull, ships[0].crew, ships[0].speed, \
          'Ship 1:', ships[1].hull, ships[1].crew, ships[1].speed
    if 'winner' in b.results:
        print 'Winner:', b.results['winner'].owner
    elif not (ships[0].is_alive() and ships[1].is_alive()):
        print 'Both ships sank'

if __name__ == '__main__':
    main()

