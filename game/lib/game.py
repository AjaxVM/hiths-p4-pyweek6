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

try:
    import psyco
    psyco.background()
except:
    pass

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    game_size = (640, 350)
    map_size = (1600, 1600) # Best as a multiple of 82 (or minimap size)
    screen_rect = pygame.Rect(0, 30, 640, 350)
    game_screen = screen.subsurface(screen_rect)
    import os
    pygame.mixer.music.load(os.path.join('data', 'music', 'rio_grande.ogg'))
    pygame.mixer.music.play(-1)

    world = World(game_size, map_size, screen_rect, screen)
    state = State(world)

    state.add_player()
    state.add_player(AIController)

    gamehud = hud.Hud(screen, state)

    font = data.font(None, 30)

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return None

            if event.type == KEYDOWN and event.key == K_s:
                pygame.image.save(screen, "screenie.tga")

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                return None

            x = gamehud.event(event)
            if x: state.event(x)

        gamehud.update()
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

        world.render(game_screen)
        state.render(game_screen)
        gamehud.render()
        pygame.display.flip()

if __name__ == "__main__":
    main()
