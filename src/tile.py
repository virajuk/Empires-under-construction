import random

from glob import glob
import pygame

from src import settings

class GreenGrass(pygame.sprite.Sprite):

    def __init__(self, pos, groups, id):

        super().__init__(groups)
        self.images = glob('graphics/grass/*.png')
        self.image = pygame.image.load(random.choice(self.images)).convert_alpha()
        self.image = pygame.transform.scale(self.image,(settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)
        self.id = id

class Sand(pygame.sprite.Sprite):

    def __init__(self, pos, groups, id):

        super().__init__(groups)
        self.images = glob('graphics/sand/*.png')
        self.image = pygame.image.load(random.choice(self.images)).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.id = id


class Water(pygame.sprite.Sprite):

    def __init__(self, pos, groups, id):

        super().__init__(groups)
        self.images = glob('graphics/water/*.png')
        self.image = pygame.image.load(random.choice(self.images)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)
        self.id = id


class Grid(pygame.sprite.Sprite):

    def __init__(self, pos, groups, id, alpha=200):
        super().__init__(groups)
        self.image = pygame.image.load('graphics/grid/grid.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.image.set_alpha(alpha)
        self.rect = self.image.get_rect(center=pos)
        self.id = id

class Home(pygame.sprite.Sprite):

    def __init__(self, pos, groups, id):
        
        super().__init__(groups)
        self.image = pygame.image.load('graphics/grid/home.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(center=pos)
        self.id = id