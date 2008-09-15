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
    selected = None
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
                        if s.rect.collidepoint(e.pos):
                            selected = s
                if e.button == 3:
                    if selected:
                        selected.move_to(e.pos)
	    
        screen.fill((0,0,255))
        for s in ships:
            s.update()
            s.render(screen,[0,0])
        if selected:
            s = selected
            pygame.draw.circle(screen, (255, 255, 0), s.rect.center, s.speed, 2)
        pygame.display.flip()
	    
main()
