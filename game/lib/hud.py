import pygame
from pygame.locals import *

from gui import gui
import data


class TopBar(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app

        self.turn_label = gui.Label(self.app, (5, 5), "Topbar-Label1", " 0", icon="turn.png")
        self.turn_label.over_width = 100

        self.player_label = gui.Label(self.app, (110, 5), "Topbar-Label2", " 0", icon="player.png")
        self.player_label.over_width = 100

        self.string_label = gui.Label(self.app, (215, 5), "Topbar-Label3", " 0", icon="string.png")
        self.string_label.over_width = 100

        self.crew_label = gui.Label(self.app, (320, 5), "Topbar-Label4", " 0", icon="crew.png")
        self.crew_label.over_width = 100

        self.gold_label = gui.Label(self.app, (425, 5), "Topbar-Label5", " 0", icon="gold.png")
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
        self.turn_label.theme.label["text-color"] = (255, 215, 0)
        self.gold_label.make_image()


class NormalBottomBar(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app

        self.end_turn_button = gui.Button(self.app, (640, 480), "NBB-ENDTURN", "End Turn", "bottomright")

    def active(self):
        self.end_turn_button.active = True

    def inactive(self):
        self.end_turn_button.active = False


class Hud(object):
    def __init__(self, screen, state):
        self.state = state


        self.app = gui.App(screen, (0,0,0))
        self.app.theme = data.theme()

        self.status_bar = TopBar(self.state, self.app)
        self.normal_button_bar = NormalBottomBar(self.state, self.app)

    def event(self, event):
        return self.app.event(event)

    def render(self, screen):
        self.status_bar.update()
        self.app.render()
