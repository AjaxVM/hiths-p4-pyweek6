#! /usr/bin/env python

"""Click the ships (green circles) and right click to move them.
Press Spacebar to end  the turn"""

import pygame, data
from pygame.locals import *

from objects import *

def main():

    pygame.init()
    screen = pygame.display.set_mode((640, 480))

    ships = [Ship([64, 64], 0), Ship([240, 240], 0)]
    turn = 1
    ship_image = data.image("ship.png")
    print "Turn:",turn
	
    while 1:
	
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                return
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                pygame.quit()
                return
            if e.type == KEYDOWN and e.key == K_SPACE:
                for s in ships:
                    s.end_turn()
                turn += 1
                print "Turn:",turn
            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    for s in ships:
                        if s.rect.collidepoint(e.pos) and not s.moved:
                            s.selected = True
                        else:
                            s.selected = False
                if e.button == 3:
                    for s in ships:
                        if s.selected:
                            s.move()
	    
        screen.fill((0,0,255))
        for s in ships:
            screen.blit(ship_image, s.rect)
            if s.selected:
                pygame.draw.line(screen, (255, 255, 255), s.pos, s.get_mouse_pos()[0], 2)
                pygame.draw.circle(screen, (255, 255, 0), s.rect.center, 30, 2)
        pygame.display.flip()
	    
main()
