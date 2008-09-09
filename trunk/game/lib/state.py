import pygame
from pygame.locals import *
import tools
import constants

class InputController(object):
    """A class that handles the player based on user input"""
    def __init__(self, state, player):
        self.state = state
        self.player = player

        self.tdraw = tools.TerritoryDrawer(self.player, self.state.world)
        self.player.to_be_rendered_objects.append(self.tdraw)

    def event(self, event):
        if self.player.is_turn():
            if event.type == KEYDOWN:
                if event.key == K_r:
                    self.tdraw.active = True
                if event.key == K_RETURN:
                    self.player.end_turn()
                    return True
            self.tdraw.update_event(event)

    def update(self):
        pass

    def start_turn(self):
        self.tdraw.t = None
        self.tdraw.active = False

    def end_turn(self):
        self.tdraw.t = None
        self.tdraw.active = False


class AIController(object):
    def __init__(self, state, player):
        self.state = state
        self.player = player

    def event(self, event):
        pass

    def update(self):
        if self.player.is_turn():
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
        pass

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
        for i in self.to_be_rendered_objects:
            i.render(screen)

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
        for i in self.players:
            x = i.controller.event(event)
            if x:  return

    def update(self):
        for i in self.players:
            i.controller.update()

    def next_player_turn(self):
        self.players[self.uturn].do_end_turn()
        self.uturn += 1
        if self.uturn == len(self.players):
            self.uturn = 0
            self.turn += 1
        self.players[self.uturn].start_turn()

    def render(self, screen):
        for i in self.players:
            i.render(screen)
