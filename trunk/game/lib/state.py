import sys
import pygame
from pygame.locals import *
import tools
import constants
import objects
import data
from combat import Battle

from gui import gui

import ai

class InputController(object):
    """A class that handles the player based on user input"""
    def __init__(self, state, player):
        self.state = state
        self.player = player

        self.tdraw = tools.TerritoryDrawer(self.player, self.state.world)
        self.player.to_be_rendered_objects.append(self.tdraw)

        self.selected_territory = None
        self.selected_unit = None
        self.battle_win = None

        self.busy = True

    def unselect_unit(self):
        try:
            self.player.to_be_rendered_objects.remove(self.selected_unit[1])
        except:
            pass
        self.selected_unit = None

    def unselect_terr(self):
        self.selected_territory = None
        for i in self.player.to_be_rendered_objects:
            if isinstance(i, tools.SelectedTerritoryRender):
                self.player.to_be_rendered_objects.remove(i)

    def event(self, event):
        if not self.battle_win == None:
            self.battle_win.event(event)
            if self.battle_win.finished:
                self.battle_win.kill()
                self.battle_win = None
            return None
        if event.type == gui.GUI_EVENT:
            if event.action == gui.GUI_EVENT_CLICK:
                if event.name == "NBB-ENDTURN":
                    self.player.end_turn()
                    self.state.gui.set_current()
                if event.name == "NBB-DRAWTERR":
                    if self.battle_win:
                        self.battle_win.kill()
                    self.battle_win = None
                    self.tdraw.active = True
                    self.unselect_unit()
                    self.unselect_terr()
                    self.state.gui.set_current()
                if event.name == "TBB-BUILD":
                    self.unselect_unit()
                    self.state.gui.set_current(self.state.gui.tbbB)
                if event.name.startswith("TBBB-"):
                    self.player.build_ship(self.selected_territory, event.name[5::])
                    self.state.gui.set_current(self.state.gui.tbb)

        if event.type == KEYDOWN:
            if event.key == K_r:
                self.tdraw.active = True
                self.unselect_unit()
                self.unselect_terr()
                self.state.gui.set_current()
            if event.key == K_RETURN:
                self.player.end_turn()
                self.state.gui.set_current()
            if event.key == K_SPACE and self.selected_territory:
                self.state.gui.set_current(self.state.gui.tbbB)
            if event.key == K_g:
                if self.selected_unit:
                    self.selected_unit[0].am_gathering = True
                    self.unselect_unit()

        if event.type == MOUSEBUTTONDOWN:
            if not self.state.world.camera.screen_rect.collidepoint(event.pos):
                return None
            if self.tdraw.active:
                self.tdraw.update_event(event)
                return None
            x, y = event.pos
            mx, my = self.state.world.camera.get_offset()
            x += mx
            y += my
            x += self.state.world.camera.screen_rect.left
            y += self.state.world.camera.screen_rect.top
            p = (x, y)
            x -= self.state.world.camera.screen_rect.left*2
            y -= self.state.world.camera.screen_rect.top*2
            p2 = (x, y)
            if event.button == 1:
                if self.selected_unit:
                    self.unselect_unit()

                self.player.ships.reverse()
                for i in self.player.ships:
                    if self.selected_unit and i == self.selected_unit[0]:
                        continue
                    if i.rect.collidepoint(p2):
                        self.selected_unit = [i, tools.ShipRangeRender(i, self.player, self.state.world)]
                        self.player.to_be_rendered_objects.append(self.selected_unit[1])
                        self.state.gui.ss.ship = i
                        self.state.gui.set_current(self.state.gui.ss)
                        self.unselect_terr()
                        self.player.ships.reverse()
                        return
                self.player.ships.reverse()

                for i in self.player.territories:
                    if p2 in i.pixels:
                        self.unselect_terr()
                        self.selected_territory = i
                        self.player.to_be_rendered_objects.append(
                            tools.SelectedTerritoryRender(self.player, i, self.state.world))
                        self.state.gui.set_current(self.state.gui.tbb)
                        return
                self.unselect_terr()
                self.state.gui.set_current()
            if event.button == 3:
                if self.selected_unit:
                    # Check for attack
                    if self.selected_unit[0].can_attack:
                        for i in self.state.players:
                            if i is self.player:
                                continue
                            for j in i.ships:
                                #print 'click', p2, 'center', j.rect.center
                                if j.rect.collidepoint(p2):
                                    range = self.selected_unit[0].get_range(j)
                                    if not range:
                                        return # Out of range
                                    x = self.selected_unit[0]
                                    if x.owner.is_human() and j.owner.is_human():
                                        self.battle_win = tools.HotseatUserBattle(
                                            self.selected_unit[0], j,
                                            self.state.gui)

                    # Didn't click on a ship, try to move
                    x = self.selected_unit[0].move_to(p2)
                    if x:
                        self.player.to_be_rendered_objects.remove(self.selected_unit[1])
                        self.selected_unit = None

    def update(self):
        if self.selected_unit:
            if not self.selected_unit[0] in self.player.ships:
                self.unselect_unit()
        if self.battle_win:
            self.battle_win.update()

    def update_ships(self):
        self.busy = False
        for i in self.player.ships:
            if i.moving():
                self.busy = True
                return

    def start_turn(self):
        self.can_end_turn = False
        self.tdraw.t = None
        self.tdraw.active = False
        for i in self.player.ships:
            i.end_turn() #reset!

    def end_turn(self):
        self.tdraw.t = None
        self.tdraw.active = False
        for i in self.player.ships:
            i.end_turn()
        if self.selected_unit:
            self.unselect_unit()
        self.player.to_be_rendered_objects = [self.tdraw]

        data.sound("endturn.wav").play()


class AIController(object):
    def __init__(self, state, player):
        self.state = state
        self.player = player

        self.ai = ai.AI(state, player)
        self.busy = True

    def event(self, event):
        pass

    def update(self):
        self.think()

    def update_ships(self):
        self.busy = False
        for i in self.player.ships:
            if i.moving():
                self.busy = True
                return

    def think(self):
        print "thinking..."
        self.ai.think()

    def start_turn(self):
        for i in self.player.ships:
            i.end_turn() #reset!

    def end_turn(self):
        for i in self.player.ships:
            i.end_turn()


class NetworkController(object):
    """Think we could make this the way to interact with the network?
       Maybe if we make it so that each controller action is then announced to
       all other controllers - then that can be sent across the network.
       Also, then this controller will have functions callable by a client, but will only
       listen if it is this players turn.
       Thoughts?"""
    def __init__(self, state, player):
        self.state = state
        self.player = player

        self.busy = False

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
        self.pnum = num
        self.color = self.state.colors[self.pnum]

        self.to_be_rendered_objects = []

        self.controller = controller(state, self)
        self.territories = self.state.world.mo.get_territories(self.pnum)
        self.ships = []
        self.resources = objects.Resources(500, 800, 300)

    def is_human(self):
        return isinstance(self.controller, InputController)

    def is_turn(self):
        return self.state.uturn == self.pnum

    def end_turn(self):
        print "called!"
        self.state.next_player_turn()

    def do_end_turn(self):
        self.controller.end_turn()

    def render(self, screen):
        #this allows us to render player actions to the screen.
        #Like the territory drawing will go through here now - because
        #it is highly dependant on turn and other user actions.
        pos = self.state.world.camera.get_offset()
        for i in self.ships:
            if i.rect.colliderect(self.state.world.camera.rect.inflate(45, 45)):
                i.render(screen, pos)

    def render_turn(self, screen):
        for i in self.to_be_rendered_objects:
            i.render(screen)

    def start_turn(self):
        self.controller.start_turn()
        for i in self.territories:
            self.resources + objects.Resources(5, 5, 5) #so we can at least get something in these capitols!
        pass

    def update_ships(self):
        for i in self.ships:
            i.update()
        self.controller.update_ships()

    def build_ship(self, territory, type):
        x = []
        for i in self.ships:
            if i.territory == territory:
                x.append(i)
        if len(x) >= territory.pop_cap:
            print "too many ships here!"
            return None
        new = objects.Ship(territory, self, type)
        cost = objects.Resources(objects.ship_types[type]['cost'], 0, new.crew_max)
        if self.resources < cost:
            print "You're too poor!"
            # TODO: notify the player visually
            return None
        self.resources - cost
        self.ships.append(new)
        return True
        # TODO: allow the player to give ship some string by default?

class State(object):
    def __init__(self, world):
        self.world = world
        self.players = []
        self.turn = 0
        self.uturn = 0 #which users turn it is
        self.pt_index = 0 #this is the index available for the next player
        self.max_players = 5 #tweak this - probably less is better though
        self.colors = constants.player_colors #this will be the color of the players -
                                          #and the color of the flags by the ships

        self.gui = None
        self.waiting = False

    def add_player(self, control_type=InputController):
        self.players.append(Player(self, control_type, self.pt_index))
        self.pt_index += 1

    def get_current_player(self):
        if not self.waiting:
            return self.players[self.uturn]
        return self.players[-1]

    def event(self, event):
        if not self.waiting:
            self.players[self.uturn].controller.event(event)

    def update(self):
        if self.waiting:
            good = True
            for i in self.players:
                if i.controller.busy:
                    good = False
                    break
            if good:
                self.uturn = 0
                self.turn += 1
                self.players[0].start_turn()
                self.waiting = False
        for i in self.players:
            i.update_ships()
        if not self.waiting:
            self.players[self.uturn].controller.update()

    def next_player_turn(self):
        self.players[self.uturn].do_end_turn()
        self.uturn += 1
        if self.uturn == len(self.players):
            self.waiting = True
            return None
        self.players[self.uturn].start_turn()

    def render(self, screen):
        if not self.waiting:
            self.players[self.uturn].render_turn(screen)
        for i in self.players:
            i.render(screen)

