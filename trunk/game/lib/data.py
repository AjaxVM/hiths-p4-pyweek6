import pygame
import os

all_images = {}
def image(name):
    if name in all_images:
        return all_images[name]
    return pygame.image.load(os.path.join("data", name)).convert_alpha()
