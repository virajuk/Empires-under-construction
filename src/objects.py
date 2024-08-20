import random
import itertools
import string

import pygame
import numpy as np

from src import settings
from src.tile import GreenGrass, Sand, Water, Grid
from src.trees import Trees

from vendor.perlin2d import generate_perlin_noise_2d, generate_fractal_noise_2d


class Objects:

    def __init__(self):

        self.display_surface = pygame.display.get_surface()

        self.visible_sprites = pygame.sprite.Group()
        self.obstacles_sprites = pygame.sprite.Group()

        self.tree_sprites = pygame.sprite.Group()

        self.create_map()
        self.create_trees()

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

                # tile = random.choices([GreenGrass, Sand, Water], weights=[100, 1, 1], k=1)[0]
                tile = random.choices([GreenGrass], weights=[100], k=1)[0]
                tile((x, y), (self.visible_sprites, ), cell)
                Grid((x, y), (self.visible_sprites,))


        # for alien in self.visible_sprites.sprites():
        #     print(alien.rect.center)

    def create_trees(self):

        # noise = generate_fractal_noise_2d((settings.WIDTH, settings.HEIGHT), (8, 6), 5)
        # noise = generate_fractal_noise_2d((settings.WIDTH, settings.HEIGHT), (8, 6))

        noise = generate_perlin_noise_2d((settings.WIDTH, settings.HEIGHT), (8, 6))

        lower_bound, higher_bound = 0.4555, 0.456

        combined_condition = np.logical_and(noise >= lower_bound, noise <= higher_bound)
        indices = np.where(combined_condition)

        for location in zip(indices[0], indices[1]):

            # print(location)

            Trees((location[0], location[1]), (self.tree_sprites,))

        # patch_1 = (int(self.map_size[1]/4), int(self.map_size[0]/4))
        # patch_2 = (int(3*self.map_size[1]/4), int(self.map_size[0]/4))
        # patch_3 = (int(self.map_size[1]/4), int(3*self.map_size[0]/4))
        # patch_4 = (int(3*self.map_size[1]/4), int(3*self.map_size[0]/4))

        # patch_1 = (int(15), int(3))

        # print(patch_1)

        # Trees((patch_1[0]*settings.TILE_SIZE, patch_1[1]*settings.TILE_SIZE), (self.tree_sprites, ))
        # Trees((patch_2[0]*settings.TILE_SIZE, patch_2[1]*settings.TILE_SIZE), (self.tree_sprites, ))
        # Trees((patch_3[0]*settings.TILE_SIZE, patch_3[1]*settings.TILE_SIZE), (self.tree_sprites, ))
        # Trees((patch_4[0]*settings.TILE_SIZE, patch_4[1]*settings.TILE_SIZE), (self.tree_sprites, ))

        # print(self.tree_sprites)
        # print(pygame.math.clamp(0, 2, 25))
        # print(pygame.math.lerp(0, 50, 0.3))

    def run(self):

        self.visible_sprites.draw(self.display_surface)
        self.tree_sprites.draw(self.display_surface)
