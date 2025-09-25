import random
from glob import glob
import pygame
from src.game_state import game_state
from src.config import get as get_config

class GreenGrass(pygame.sprite.Sprite):
    def __init__(self, pos, groups, id):
        super().__init__(groups)
        self.images = glob('graphics/grass/*.png')
        self.image = pygame.image.load(random.choice(self.images)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (game_state.TILE_SIZE, game_state.TILE_SIZE))
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
        self.image = pygame.transform.scale(self.image, (game_state.TILE_SIZE, game_state.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)
        self.id = id

class Grid(pygame.sprite.Sprite):
    def __init__(self, pos, groups, id):
        
        super().__init__(groups)
        self.image = pygame.image.load('graphics/grid/grid.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (game_state.TILE_SIZE, game_state.TILE_SIZE))
        fog_enabled = get_config('FOG_OF_WAR', True)
        alpha_val = 200 if fog_enabled else 20
        self.image.set_alpha(alpha_val)
        self.rect = self.image.get_rect(center=pos)
        self.id = id

class Home(pygame.sprite.Sprite):
    def __init__(self, pos, groups, id):
        super().__init__(groups)
        self.image = pygame.image.load('graphics/grid/home.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (game_state.TILE_SIZE, game_state.TILE_SIZE))
        self.rect = self.image.get_rect(center=pos)
        self.id = id