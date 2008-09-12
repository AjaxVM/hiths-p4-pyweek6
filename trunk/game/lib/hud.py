import pygame
from pygame.locals import *

from gui import gui
import data


class TopBar(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app

        self.turn_label = gui.Label(self.app, (5, 2), "Topbar-Label1", " 0", icon="turn.png")
        self.turn_label.over_width = 100

        self.player_label = gui.Label(self.app, (110, 2), "Topbar-Label2", " 0", icon="player.png")
        self.player_label.over_width = 100

        self.string_label = gui.Label(self.app, (215, 2), "Topbar-Label3", " 0", icon="string.png")
        self.string_label.over_width = 100

        self.crew_label = gui.Label(self.app, (320, 2), "Topbar-Label4", " 0", icon="crew.png")
        self.crew_label.over_width = 100

        self.gold_label = gui.Label(self.app, (425, 2), "Topbar-Label5", " 0", icon="gold.png")
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
##        x = screen.subsurface(0,0,640,30)
##        x.fill((189, 183, 107))
        screen.blit(data.image("hud_bg_top.png"), (0,0))

class NormalBottomBar(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app

        self.end_turn_button = gui.Button(self.app, (635, 475), "NBB-ENDTURN", "End Turn", "bottomright")
        self.active = True

    def active(self):
        self.end_turn_button.active = True
        self.active = True

    def inactive(self):
        self.end_turn_button.active = False
        self.active = False

    def render_bg(self, screen):
##        x = screen.subsurface(0,380,640,100)
##        x.fill((189, 183, 107))
        screen.blit(data.image("hud_bg_bottom.png"), (0,380))

class Hud(object):
    def __init__(self, screen, state):
        self.state = state


        self.app = gui.App(screen)
        self.app.theme = data.theme()

        self.status_bar = TopBar(self.state, self.app)
        self.normal_button_bar = NormalBottomBar(self.state, self.app)

    def event(self, event):
        return self.app.event(event)

    def render(self):
        self.status_bar.update()
        self.status_bar.render_bg(self.app.surface)
        self.normal_button_bar.render_bg(self.app.surface)
        self.app.render()
