import random

from glob import glob
import pygame


class Trees(pygame.sprite.Sprite):

    def __init__(self, pos, groups):

        super().__init__(groups)
        self.images = glob('graphics/trees/*.png')
        self.image = pygame.image.load(random.choice(self.images)).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
