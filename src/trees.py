import random
from glob import glob
import pygame
from src.config import get as get_config
from src.map_loader import load_map

# Always use TILE_SIZE from the selected map
_map_name = get_config('SELECTED_MAP', 'map_1')
_, _, TILE_SIZE, _ = load_map(_map_name)

class Tree(pygame.sprite.Sprite):
    def __init__(self, pos, groups, id):
        super().__init__(groups)
        self.images = glob('graphics/tree/*.png')
        self.image = pygame.image.load(random.choice(self.images)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(center=pos)
        self.id = id
