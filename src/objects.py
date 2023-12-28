import random
import itertools
import string

import pygame

from src import settings
from src.tile import GreenGrass, Sand, Water
from src.trees import Trees


class Objects:

    def __init__(self):

        self.display_surface = pygame.display.get_surface()

        self.visible_sprites = pygame.sprite.Group()
        self.obstacles_sprites = pygame.sprite.Group()

        self.tree_sprites = pygame.sprite.Group()

        self.create_map()
        # self.create_trees()

    def create_map(self):

        self.map_size = [int(settings.HEIGHT/settings.TILE_SIZE), int(settings.WIDTH/settings.TILE_SIZE)]

        a = string.ascii_lowercase
        com = itertools.product(a, a)

        for row_idx in range(self.map_size[0]):
            y = row_idx*settings.TILE_SIZE
            row_str = "".join(next(com))

            for col_idx in range(self.map_size[1]):
                x = col_idx * settings.TILE_SIZE
                cell = row_str + str(col_idx)

                tile = random.choices([GreenGrass, Sand, Water], weights=[100, 1, 1], k=1)[0]
                tile((x, y), (self.visible_sprites, ), cell)

        # for alien in self.visible_sprites.sprites():
        #     print(alien.id)

    def create_trees(self):

        patch_1 = (int(self.map_size[1]/4), int(self.map_size[0]/4))
        patch_2 = (int(3*self.map_size[1]/4), int(self.map_size[0]/4))
        patch_3 = (int(self.map_size[1]/4), int(3*self.map_size[0]/4))
        patch_4 = (int(3*self.map_size[1]/4), int(3*self.map_size[0]/4))

        Trees((patch_1[0]*settings.TILE_SIZE, patch_1[1]*settings.TILE_SIZE), (self.tree_sprites, ))
        Trees((patch_2[0]*settings.TILE_SIZE, patch_2[1]*settings.TILE_SIZE), (self.tree_sprites, ))
        Trees((patch_3[0]*settings.TILE_SIZE, patch_3[1]*settings.TILE_SIZE), (self.tree_sprites, ))
        Trees((patch_4[0]*settings.TILE_SIZE, patch_4[1]*settings.TILE_SIZE), (self.tree_sprites, ))

        # print(self.tree_sprites)
        # print(pygame.math.clamp(0, 2, 25))
        # print(pygame.math.lerp(0, 50, 0.3))

    def run(self):

        self.visible_sprites.draw(self.display_surface)
        # self.tree_sprites.draw(self.display_surface)
