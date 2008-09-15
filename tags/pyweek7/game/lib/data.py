import pygame
import os, sys
from gui import gui
x, y = os.path.split(sys.path[0])
if y == "lib":
    data_path = os.path.join(x, "data")
else:
    data_path = "data"

class DummySound(object):
    def __init__(self):
        pass

    def play(self, loops=0, maxtime=0, fade_ms=0):
        pass

    def stop(self):
        pass

    def fadeout(self, t):
        pass

    def set_volume(self, value):
        pass

    def get_volume(self):
        return 1

    def get_num_channels(self):
        return 0

    def get_length(self):
        return 0

    def get_buffer(self):
        return None

all_sound = {}
def sound(name):
    if name in all_sound:
        return all_sound[name]
    try:
        s = pygame.mixer.Sound(os.path.join(data_path, name))
    except:
        s = DummySound()
    all_sound[name] = s
    return s

all_images = {}
def image(name):
    if name in all_images:
        return all_images[name]
    image = pygame.image.load(os.path.join(data_path, name)).convert_alpha()
    all_images[name] = image
    return image

all_fonts = {}
def font(name, size):
    if (name, size) in all_fonts:
        return all_fonts[(name, size)]

    if name:
        name = os.path.join(data_path, name)
    f = pygame.font.Font(name, size)
    all_fonts[(name, size)] = f
    return f

global ctheme
ctheme = None
def theme():
    global ctheme
    if not ctheme:
        ctheme = gui.make_theme(os.path.join(data_path, "theme"))
    return ctheme
