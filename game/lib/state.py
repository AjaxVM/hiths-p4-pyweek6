import pygame
from pygame.locals import *
import tools
import constants
import objects

class InputController(object):
    """A class that handles the player based on user input"""
    def __init__(self, state, player):
        self.state = state
        self.player = player

        self.tdraw = tools.TerritoryDrawer(self.player, self.state.world)
        self.player.to_be_rendered_objects.append(self.tdraw)

        self.selected_territory = None
        self.selected_unit = None

    def event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_r:
                self.tdraw.active = True
            if event.key == K_RETURN:
                self.player.end_turn()
            if event.key == K_SPACE and self.selected_territory:
                new = objects.Ship(self.selected_territory.capitol.pos, self.player)
                self.player.ships.append(new)
        self.tdraw.update_event(event)

        if not self.tdraw.active:
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                mx, my = self.state.world.camera.get_offset()
                x += mx
                y += my
                p = (x, y)
                if event.button == 1:
                    for i in self.player.ships:
                        if self.selected_unit and i == self.selected_unit[0]:
                            continue
                        if i.rect.collidepoint(p):
                            self.selected_unit = [i, tools.ShipRangeRender(i, self.player, self.state.world)]
                            self.player.to_be_rendered_objects.append(self.selected_unit[1])
                            return

                    for i in self.player.territories:
                        if p in i.pixels:
                            self.selected_territory = i
                            return
                if event.button == 3:
                    if self.selected_unit:
                        x = self.selected_unit[0].move_to(p)
                        if x:
                            self.player.to_be_rendered_objects.remove(self.selected_unit[1])
                            self.selected_unit = None

    def update(self):
        for i in self.player.ships:
            i.update()

    def start_turn(self):
        self.tdraw.t = None
        self.tdraw.active = False

    def end_turn(self):
        self.tdraw.t = None
        self.tdraw.active = False
        for i in self.player.units:
            i.end_turn()


class AIController(object):
    def __init__(self, state, player):
        self.state = state
        self.player = player

    def event(self, event):
        pass

    def update(self):
        for i in self.player.units:
            i.update()
        self.think()

    def think(self):
        print "thinking..."
        self.player.end_turn()

    def start_turn(self):
        pass

    def end_turn(self):
        pass


class NetworkController(object):
    """Think we could make this the way to interact with the network?
       Maybe if we make it so that each controller action is then announced to
       all other controllers - then that can be sent across the network.
       Also, then this controller will have functions callable by a client, but will only
       listen if it this players turn.
       Thoughts?"""
    def __init__(self, state, player):
        self.state = state
        self.player = player

    def event(self, event):
        pass

    def update(self):
        for i in self.player.units:
            i.update()

    def start_turn(self):
        pass

    def end_turn(self):
        pass

class Player(object):
    def __init__(self, state, controller, num=0):
        self.state = state
        self.num = num
        self.color = self.state.colors[self.num]

        self.to_be_rendered_objects = []

        self.controller = controller(state, self)
        self.territories = []
        self.ships = []

    def is_turn(self):
        return self.state.uturn == self.num

    def end_turn(self):
        self.state.next_player_turn()

    def do_end_turn(self):
        self.controller.end_turn()

    def render(self, screen):
        #this allows us to render player actions to the screen.
        #Like the territory drawing will go through here now - because
        #it is highly dependant on turn and other user actions.
        pos = self.state.world.camera.get_offset()
        for i in self.to_be_rendered_objects:
            i.render(screen)
        for i in self.ships:
            i.render(screen, pos)

    def start_turn(self):
        self.controller.start_turn()
        pass

class State(object):
    def __init__(self, world):
        self.world = world
        self.players = []
        self.turn = 0
        self.uturn = 0 #which users turn it is
        self.pt_index = 0 #this is the index available for the next player
        self.max_players = 5 #tweak this - probably less is better though
        self.colors = constants.player_colors #this will be the color of the players -
                                          #and the color of the flags by the units

    def add_player(self, control_type=InputController):
        self.players.append(Player(self, control_type, self.pt_index))
        self.pt_index += 1

    def event(self, event):
        self.players[self.uturn].controller.event(event)

    def update(self):
        self.players[self.uturn].controller.update()

    def next_player_turn(self):
        self.players[self.uturn].do_end_turn()
        self.uturn += 1
        if self.uturn == len(self.players):
            self.uturn = 0
            self.turn += 1
        self.players[self.uturn].start_turn()

    def render(self, screen):
        self.players[self.uturn].render(screen)
