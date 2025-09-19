import random
import itertools
import string

import pygame
import numpy as np

from src import settings
from src.tile import GreenGrass, Sand, Water, Grid
from src.trees import Trees
from src.animated_player import AnimatedPlayer

from vendor.perlin2d import generate_perlin_noise_2d, generate_fractal_noise_2d


class Objects:

    def __init__(self):
        # Game stats (must be set before any method that uses them)
        self.score = 0
        self.resources = 0

        self.display_surface = pygame.display.get_surface()

        self.visible_sprites = pygame.sprite.Group()
        self.obstacles_sprites = pygame.sprite.Group()

        self.tree_sprites = pygame.sprite.Group()
        self.player_sprites = pygame.sprite.Group()

        self.cell_labels = []  # Store (id, (x, y)) for each tile
        self.selected_cell_idx = None  # Index of currently selected cell
        self.last_cell_change = 0  # Timestamp for cell selection

        self.create_map()
        # self.digging_ponds()

        # Create two animated players at different random tile centers
        if self.cell_labels and len(self.cell_labels) > 1:
            cell_choices = random.sample(self.cell_labels, 2)
            for cell_id, (center_x, center_y) in cell_choices:
                AnimatedPlayer((center_x, center_y), (self.player_sprites,))

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

        # Update player animation and movement
        self.player_sprites.update()

        # Draw world (grass, sprites) in area 0 to settings.HEIGHT
        world_clip = pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT)
        prev_clip = self.display_surface.get_clip()
        self.display_surface.set_clip(world_clip)
        self.visible_sprites.draw(self.display_surface)
        # self.tree_sprites.draw(self.display_surface)
        self.player_sprites.draw(self.display_surface)
        self.display_surface.set_clip(prev_clip)

        # Draw bottom panel in area settings.HEIGHT to settings.SCREEN_HEIGHT
        panel_rect = pygame.Rect(0, settings.HEIGHT, settings.WIDTH, settings.PANEL_HEIGHT)
        pygame.draw.rect(self.display_surface, (40, 40, 40), panel_rect)
        pygame.draw.line(self.display_surface, (100, 100, 100), (0, settings.HEIGHT), (settings.WIDTH, settings.HEIGHT), 2)

        font = pygame.font.SysFont(None, 32)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        resources_text = font.render(f"Resources: {self.resources}", True, (255, 255, 255))
        self.display_surface.blit(score_text, (16, settings.HEIGHT + 8))
        self.display_surface.blit(resources_text, (220, settings.HEIGHT + 8))
