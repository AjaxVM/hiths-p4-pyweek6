import game

def main():
    gstate = game.State()
    gstate.attack_ship(0, gstate.find_ship((42, 123)))

if __name__ == '__main__':
    main()

