import pygame
from pygame.locals import *

from gui import gui
import data, objects
from tools import Minimap


class TopBar(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app

        self.turn_label = gui.Label(self.app, (5, 3), "Topbar-Label1", " 0", icon="turn.png")
        self.turn_label.over_width = 100

        self.player_label = gui.Label(self.app, (110, 3), "Topbar-Label2", " 0", icon="player.png")
        self.player_label.over_width = 100

        self.string_label = gui.Label(self.app, (215, 3), "Topbar-Label3", " 0", icon="string.png")
        self.string_label.over_width = 100

        self.crew_label = gui.Label(self.app, (320, 3), "Topbar-Label4", " 0", icon="crew.png")
        self.crew_label.over_width = 100

        self.gold_label = gui.Label(self.app, (425, 3), "Topbar-Label5", " 0", icon="gold.png")
        self.gold_label.over_width = 100

        self.update()

    def update(self):
        player = self.state.get_current_player()
        self.turn_label.text = " "+str(self.state.turn)
        self.turn_label.theme.label["text-color"] = (0, 0, 0)
        self.turn_label.make_image()

        self.player_label.text = " "+str(self.state.uturn)
        self.player_label.theme.label["text-color"] = self.state.get_current_player().color
        self.player_label.make_image()

        self.string_label.text = " "+str(player.resources.string)
        self.string_label.theme.label["text-color"] = (0, 191, 255)
        self.string_label.make_image()

        self.crew_label.text = " "+str(player.resources.crew)
        self.crew_label.theme.label["text-color"] = (255, 0, 0)
        self.crew_label.make_image()

        self.gold_label.text = " "+str(player.resources.gold)
        self.turn_label.theme.label["text-color"] = (200, 175, 0)
        self.gold_label.make_image()

    def render_bg(self, screen):
        screen.blit(data.image("hud_bg_top.png"), (0,0))

class NormalBottomBar(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app

        self.end_turn_button = gui.Button(self.app, (635, 475), "NBB-ENDTURN", "End Turn", "bottomright")
        x, y = self.end_turn_button.rect.topright
        y -= 5
        self.draw_button = gui.Button(self.app, (x,  y), "NBB-DRAWTERR", "Expand", "bottomright")
        self.draw_button.over_width = self.end_turn_button.rect.width
        self.draw_button.make_image()

        self.minimap = Minimap(state, pygame.Rect(15, 390, 82, 82))

    def render_bg(self, screen):
        screen.blit(data.image("hud_bg_bottom.png"), (0,380))
        map = self.minimap.update()
        screen.blit(map, self.minimap.rect)

class TerritoryBottomBar(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app

        self.button1 = gui.Button(self.app, (125, 390), "TBB-BUILD", "Build Ship", "topleft")

        self.inactive()

    def active(self):
        self.button1.active = True
        self._active = True

    def inactive(self):
        self.button1.active = False
        self._active = False

    def isactive(self): return self._active
    def render(self, screen): pass

class TerritoryBottomBarBUILD(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app

        self.buttons = []

        button1 = gui.Button(self.app, (125, 390),
                             "TBBB-junk", "junk", "topleft",
                             icon="junk.png")
        button2 = gui.Button(self.app, (125, button1.rect.bottom+5),
                             "TBBB-frigate", "frigate", "topleft",
                             icon="frigate.png")
        button3 = gui.Button(self.app, (button1.rect.right+5, 390),
                             "TBBB-juggernaut", "juggernaut", "topleft",
                             icon="juggernaut.png")
        button1.over_width = button3.rect.width
        button1.make_image()
        button2.over_width = button3.rect.width
        button2.make_image()
        button3.rect.left = button1.rect.right + 5

        self.buttons.append(button1)
        self.buttons.append(button2)
        self.buttons.append(button3)

        font = data.font("Pieces-of-Eight.ttf", 18)
        h = font.get_height()

        values = ("hull", "crew", "speed", "hold_capacity", "damage_multiplier", "cost")
        nh = h * (len(values) + 2)

        surfs = {}
        for i in objects.ship_types:
            if i in ["junk", "frigate", "juggernaut"]: #hack, remove once we have all the ships in!!!
                new = pygame.Surface((250, nh)).convert()
                cur_i = 5
                new.blit(font.render("name: "+i, 1, (255, 255, 255)), (5, cur_i))
                cur_i += h
                for x in values:
                    new.blit(font.render(x.replace("_", " ")+": "+str(objects.ship_types[i][x]),
                                         1, (255, 255, 255)), (5, cur_i))
                    cur_i += h
                new.set_alpha(150)
                surfs[i] = new

        self.r = pygame.Rect(0,0,250,nh)
        self.r.bottom = 380
        self.s = surfs

        self.inactive()

    def active(self):
        for i in self.buttons:
            i.active = True
        self._active = True

    def inactive(self):
        for i in self.buttons:
            i.active = False
        self._active = False

    def isactive(self): return self._active

    def render(self, screen):
        mpos = pygame.mouse.get_pos()
        for i in self.buttons:
            if i.rect.collidepoint(mpos):
                screen.blit(self.s[i.text], self.r)


class SelectShip(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app
        self.ship = None

        self.inactive()

    def active(self):
        self._active = True

    def inactive(self):
        self._active = False

    def isactive(self):
        return self._active

    def render(self, screen):
        if self.ship:
            screen.blit(self.ship.image, (125, 390))

class Hud(object):
    def __init__(self, screen, state):
        self.state = state
        self.state.gui = self

        self.app = gui.App(screen)
        self.app.theme = data.theme()

        self.status_bar = TopBar(self.state, self.app)
        self.normal_button_bar = NormalBottomBar(self.state, self.app)

        self.tbb = TerritoryBottomBar(self.state, self.app)
        self.tbbB = TerritoryBottomBarBUILD(self.state, self.app)
        self.ss = SelectShip(self.state, self.app)

        self.special_states = [self.tbb, self.tbbB, self.ss]

    def set_current(self, x=None):
        for i in self.special_states:
            if i is x:
                i.active()
            else:
                i.inactive()

    def event(self, event):
        return self.app.event(event)

    def render(self):
        self.status_bar.update()
        self.status_bar.render_bg(self.app.surface)
        self.normal_button_bar.render_bg(self.app.surface)

        for i in self.special_states:
            if i.isactive():
                i.render(self.app.surface)

        self.app.render()
