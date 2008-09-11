import pygame
from pygame.locals import *

from gui import gui
import data


class TopBar(object):
    def __init__(self, state, player):
        self.state = state
        self.player = player

        self.app = gui.App(pygame.Surface((640, 30)), (0,0,0))
        self.app.theme = data.theme()

        self.turn_label = gui.Label(self.app, (5, 5), "Label1", " 0", icon="turn.png")
        self.turn_label.over_width = 100
        self.turn_label.theme.label["text-color"] = (0, 0, 0)

        self.player_label = gui.Label(self.app, (110, 5), "Label2", " 0", icon="player.png")
        self.player_label.over_width = 100

        self.string_label = gui.Label(self.app, (215, 5), "Label3", " 0", icon="string.png")
        self.string_label.over_width = 100
        self.string_label.theme.label["text-color"] = (0, 191, 255)

        self.crew_label = gui.Label(self.app, (320, 5), "Label4", " 0", icon="crew.png")
        self.crew_label.over_width = 100
        self.crew_label.theme.label["text-color"] = (255, 0, 0)

        self.gold_label = gui.Label(self.app, (425, 5), "Label5", " 0", icon="gold.png")
        self.gold_label.over_width = 100
        self.turn_label.theme.label["text-color"] = (255, 215, 0)

        self.update()

    def update(self):
        self.turn_label.text = " "+str(self.state.turn)

        self.player_label.text = " "+str(self.state.uturn)
        self.player_label.theme.label["text-color"] = self.state.get_current_player().color

        self.string_label.text = " "+str(self.player.resources.string)
        self.crew_label.text = " "+str(self.player.resources.crew)
        self.gold_label.text = " "+str(self.player.resources.gold)

        self.turn_label.make_image()
        self.player_label.make_image()
        self.string_label.make_image()
        self.crew_label.make_image()
        self.gold_label.make_image()

    def render(self, screen):
        self.update()
        screen.blit(self.app.render(), (0,0))
