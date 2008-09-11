import pygame
from pygame.locals import *

from world import *
from objects import *
import tools
from state import *
import data
import hud

import random
import gui

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    game_size = (640, 350)
    map_size = (1500, 1500)
    screen_rect = pygame.Rect(0, 30, 640, 350)
    game_screen = screen.subsurface(screen_rect)

    world = World(game_size, map_size, screen_rect)
    state = State(world)

    state.add_player()
    state.add_player()

    gamehud = hud.Hud(screen, state)

    font = data.font(None, 30)

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return None

            if event.type == KEYDOWN and event.key == K_s:
                pygame.image.save(screen, "screenie.tga")

            x = gamehud.event(event)
            state.event(x)

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

        gamehud.render(screen)
        world.render(game_screen)
        state.render(game_screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
