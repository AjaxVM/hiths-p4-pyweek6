import game
from objects import *
from combat import *

def main():
    ships = []
    # Make some ships for testing real quick
    for i in range(2):
        ship = Ship((0,0))
        ships.append(ship)

    b = Battle((ships[0], ships[1]), ('ball', 'medium'))
    while ships[0].is_alive() and ships[1].is_alive():
        b.execute()

if __name__ == '__main__':
    main()

