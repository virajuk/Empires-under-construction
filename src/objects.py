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

        self.cell_labels = []  # Store (id, (x, y)) for each tile
        self.selected_cell_idx = None  # Index of currently selected cell
        self.last_cell_change = 0  # Timestamp for cell selection

        self.create_map()
        # self.digging_ponds()

        # self.plant_trees()

    def create_map(self):
        """
        Fills the screen with a grid of GreenGrass tiles and overlays grid cells.
        - Computes grid size from HEIGHT, WIDTH, and TILE_SIZE.
        - Each tile is placed at snapped pixel coordinates and given a unique id (2-letter row + column index).
        - Adds both terrain and grid sprites to visible_sprites for rendering.
        """
        self.map_size = [int(settings.HEIGHT/settings.TILE_SIZE), int(settings.WIDTH/settings.TILE_SIZE)]

        a = string.ascii_lowercase
        com = itertools.product(a, a)

        for row_idx in range(self.map_size[0]):
            y = row_idx * settings.TILE_SIZE
            row_str = "".join(next(com))

            for col_idx in range(self.map_size[1]):
                x = col_idx * settings.TILE_SIZE
                cell = row_str + str(col_idx)

                tile = random.choices([GreenGrass], weights=[100], k=1)[0]
                tile((x, y), (self.visible_sprites,), cell)
                Grid((x, y), (self.visible_sprites,))
                center_x = x + settings.TILE_SIZE // 2
                center_y = y + settings.TILE_SIZE // 2
                self.cell_labels.append((cell, (center_x, center_y)))

            # Store grid dimensions for cell navigation
            self.grid_rows = self.map_size[0]
            self.grid_cols = self.map_size[1]


    def digging_ponds(self):

        noise = generate_perlin_noise_2d((settings.WIDTH, settings.HEIGHT), (32, 24))
        lower_bound, higher_bound = 0.4641, 0.5679
        combined_condition = np.logical_and(noise >= lower_bound, noise <= higher_bound)
        indices = np.where(combined_condition)
        print(len(indices[0]))

        for location in zip(indices[0], indices[1]):
            x = int(location[1] / settings.TILE_SIZE) * settings.TILE_SIZE
            y = int(location[0] / settings.TILE_SIZE) * settings.TILE_SIZE
            Water((x, y), (self.visible_sprites,), "asd")


    def plant_trees(self):

        # noise = generate_fractal_noise_2d((settings.WIDTH, settings.HEIGHT), (8, 6), 5)
        # noise = generate_fractal_noise_2d((settings.WIDTH, settings.HEIGHT), (8, 6))

        noise = generate_perlin_noise_2d((settings.WIDTH, settings.HEIGHT), (14, 7))

        lower_bound, higher_bound = 0.4943, 0.4944

        combined_condition = np.logical_and(noise >= lower_bound, noise <= higher_bound)
        indices = np.where(combined_condition)

        print(len(indices[0]))
        for location in zip(indices[0], indices[1]):

            x,y = int(location[0]/settings.TILE_SIZE)*settings.TILE_SIZE, int(location[1]/settings.TILE_SIZE)*settings.TILE_SIZE
            Trees((x, y), (self.tree_sprites,))


    def run(self):

        self.visible_sprites.draw(self.display_surface)
        # self.tree_sprites.draw(self.display_surface)

        # Render cell ids on top of each tile
        font = pygame.font.SysFont(None, max(16, settings.TILE_SIZE // 3))
        current_time = pygame.time.get_ticks()
        # Pick first cell randomly, then move to a random neighbor each second
        if self.cell_labels:
            if self.selected_cell_idx is None:
                # Pick a random starting cell
                self.selected_cell_idx = random.randint(0, len(self.cell_labels) - 1)
                self.last_cell_change = current_time
            elif current_time - self.last_cell_change >= 1000:
                # Move to a random neighbor
                row = self.selected_cell_idx // self.grid_cols
                col = self.selected_cell_idx % self.grid_cols
                direction = random.choice(['up', 'down', 'left', 'right'])
                if direction == 'up':
                    row = (row - 1) % self.grid_rows
                elif direction == 'down':
                    row = (row + 1) % self.grid_rows
                elif direction == 'left':
                    col = (col - 1) % self.grid_cols
                elif direction == 'right':
                    col = (col + 1) % self.grid_cols
                self.selected_cell_idx = row * self.grid_cols + col
                self.last_cell_change = current_time

            cell_id, (center_x, center_y) = self.cell_labels[self.selected_cell_idx]
            # Render cell ID
            id_surface = font.render(cell_id, True, (0, 0, 0))
            id_rect = id_surface.get_rect(center=(center_x, center_y - 8))
            self.display_surface.blit(id_surface, id_rect)

            # Render coordinates
            coord_text = f"({center_x},{center_y})"
            coord_surface = font.render(coord_text, True, (0, 0, 0))
            coord_rect = coord_surface.get_rect(center=(center_x, center_y + 8))
            self.display_surface.blit(coord_surface, coord_rect)
