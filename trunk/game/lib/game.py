import pygame
from pygame.locals import *

from world import *
from objects import *
import tools
from state import *
import data

import random

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))

    world = World(world_size=(1500, 1500))
    state = State(world)

    state.add_player()
    state.add_player()

    font = data.font(None, 30)

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
        screen.blit(font.render("turn: %s"%state.turn, 1, [0,0,0],[255,255,255]), (0,0))
        screen.blit(font.render("player: %s"%state.uturn, 1, state.colors[state.uturn],[255,255,255]), (250,0))
        pygame.display.flip()

if __name__ == "__main__":
    main()
