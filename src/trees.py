import random

from glob import glob
import pygame

from src import settings

class Tree(pygame.sprite.Sprite):
    
    def __init__(self, pos, groups, id):

        super().__init__(groups)
        self.images = glob('graphics/tree/*.png')
        self.image = pygame.image.load(random.choice(self.images)).convert_alpha()
        self.image = pygame.transform.scale(self.image,(settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(center=pos)
        self.id = id
