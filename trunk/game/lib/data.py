import pygame
import os, sys
from gui import gui
x, y = os.path.split(sys.path[0])
if y == "lib":
    data_path = os.path.join(x, "data")
else:
    data_path = "data"

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

    f = pygame.font.Font(name, size)
    all_fonts[(name, size)] = f
    return f

theme = gui.make_theme(os.path.join(data_path, "theme"))

