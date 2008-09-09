import pygame
from pygame.locals import *

from world import *
from objects import *
import tools
from state import *

import random

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))

    world = World(world_size=(1500, 1500))
    state = State(world)

    state.add_player()
    state.add_player(AIController)

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return None

            state.event(event)

        state.update()

        x, y = pygame.mouse.get_pos()
        if x <= 5:
            world.camera.move(-5, 0)
        if x >= 635:
            world.camera.move(5, 0)
        if y <= 5:
            world.camera.move(0, -5)
        if y >= 475:
            world.camera.move(0, 5)

        world.render(screen)
        state.render(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
