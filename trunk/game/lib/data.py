import pygame
import os, sys
x, y = os.path.split(sys.path[0])
if y == "lib":
    data_path = os.path.join(x, "data")
else:
    data_path = "data"

all_images = {}
def image(name):
    if name in all_images:
        return all_images[name]
    return pygame.image.load(os.path.join(data_path, name)).convert_alpha()
