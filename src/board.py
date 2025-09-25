import random
import itertools
import string

import pygame
import numpy as np

from src.config import get as get_config
from src.tile import GreenGrass, Sand, Water, Grid, Home
from src.trees import Tree
from src.villager.villager import Villager
from src.scout import Scout
from src.game_state import current_game_state

from src.utils import bottom_panel

from vendor.perlin2d import generate_perlin_noise_2d, generate_fractal_noise_2d

from src.config import get as get_config
from src.map_loader import load_map

from agent import agent

class Board:
    def __init__(self):

        # Load map details directly
        map_name = get_config('SELECTED_MAP', 'map_1')
        self.width, self.height, self.tile_size, self.world_map = load_map(map_name)
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = pygame.sprite.Group()
        self.obstacles_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.villager_sprites = pygame.sprite.Group()
        self.scout_sprites = pygame.sprite.Group()
        self.cell_labels = []
        self.selected_cell_idx = None
        self.last_cell_change = 0
        self.discovered_trees = []
        self.grid_sprites = {}
        self.create_map()
        # self.add_scout()
        self.add_villager()

        current_game_state.board = self

    def add_villager(self):

        # Use Villager.spawn_position to determine spawn location
        pos, cell_id = Villager.spawn_position(self.cell_labels)
        if pos and cell_id:
            Villager(pos, (self.villager_sprites,), start_cell=cell_id)
    
    def add_scout(self):

        # Use Scout.spawn_position to determine spawn location
        pos, cell_id = Scout.spawn_position(self.cell_labels)
        if pos and cell_id:
            Scout(pos, (self.scout_sprites,), start_cell=cell_id)

    def reset(self):

        """Respawn players only: remove existing players and spawn two new ones.

        Keep map, trees, and stats intact.
        """
        # Kill existing players
        for p in list(self.villager_sprites):
            p.kill()
        for p in list(self.scout_sprites):
            p.kill()

        # Spawn villagers and scouts again at random tiles
        if self.cell_labels and len(self.cell_labels) > 2:
            cell_choices = random.sample(self.cell_labels, min(3, len(self.cell_labels)))
            for i, (cell_id, (center_x, center_y)) in enumerate(cell_choices):
                if i == 0:
                    Villager((center_x, center_y), (self.villager_sprites,), start_cell=cell_id)
                elif i == 1:
                    Scout((center_x, center_y), (self.scout_sprites,), start_cell=cell_id)
                else:
                    # Add more villagers if we have more cells
                    Villager((center_x, center_y), (self.villager_sprites,), start_cell=cell_id)

    def create_map(self):
        world_map = self.world_map
        if world_map and len(world_map) > 0 and len(world_map[0]) > 0:
            rows = len(world_map)
            cols = len(world_map[0])
        else:
            rows = int(self.height / self.tile_size)
            cols = int(self.width / self.tile_size)
        self.map_size = [rows, cols]
        a = string.ascii_lowercase
        com = itertools.product(a, a)
        for row_idx in range(rows):
            y = row_idx * self.tile_size
            row_str = "".join(next(com))
            for col_idx in range(cols):
                x = col_idx * self.tile_size
                cell = row_str + str(col_idx)
                tile_type = None
                if world_map and row_idx < len(world_map) and col_idx < len(world_map[row_idx]):
                    tile_type = world_map[row_idx][col_idx]
                center_x = x + self.tile_size // 2
                center_y = y + self.tile_size // 2
                GreenGrass((x, y), (self.visible_sprites,), cell)
                if tile_type in ('tree'):
                    Tree((center_x, center_y), (self.visible_sprites, self.obstacles_sprites, self.tree_sprites), cell)
                if tile_type in ('home'):
                    Home((center_x, center_y), (self.visible_sprites, self.obstacles_sprites), cell)
                grid_sprite = Grid((center_x, center_y), (self.visible_sprites,), cell)
                self.grid_sprites[(row_idx, col_idx)] = grid_sprite
                if tile_type == 'home':
                    grid_sprite.image.set_alpha(20)
                self.cell_labels.append((cell, (center_x, center_y)))
        self.grid_rows = rows
        self.grid_cols = cols

    def avoid_unit_collisions(self):
        
        # Check for unit collisions
        all_entities = list(self.villager_sprites) + list(self.scout_sprites)
        for i in range(len(all_entities)):
            for j in range(i + 1, len(all_entities)):
                if all_entities[i].rect.colliderect(all_entities[j].rect):
                    # Set both to reverse next move
                    if hasattr(all_entities[i], 'reverse_next_move'):
                        all_entities[i].reverse_next_move = True
                    if hasattr(all_entities[j], 'reverse_next_move'):
                        all_entities[j].reverse_next_move = True

    def avoid_collisions(self):

        all_entities = list(self.villager_sprites) + list(self.scout_sprites)
        # Check for collisions between entities and obstacles
        for entity in all_entities:
            collided = pygame.sprite.spritecollideany(entity, self.obstacles_sprites)
            if collided:
                # Reveal fog for obstacle tile when unit collides
                self.reveal_cell(collided.rect.centerx, collided.rect.centery)
                # Revert position to previous rect if available
                if hasattr(entity, 'prev_rect'):
                    entity.rect = entity.prev_rect.copy()
                # Always reverse direction
                if hasattr(entity, 'reverse_next_move'):
                    entity.reverse_next_move = True

    def reveal_cell(self, x, y):

        col = x // self.tile_size
        row = y // self.tile_size
        grid_sprite = self.grid_sprites.get((row, col))
        if grid_sprite:
            grid_sprite.image.set_alpha(20)

    def draw_health_bars(self):

        living_entities = list(self.villager_sprites) + list(self.scout_sprites)
        # Draw health bars above each entity
        if get_config('SHOW_HEALTH', True):
            for entity in living_entities:
                if hasattr(entity, 'draw_health_bar'):
                    entity.draw_health_bar(self.display_surface)
        
        # Draw health bars above trees that have been chopped
        for tree in self.tree_sprites:
            if hasattr(tree, 'draw_health_bar') and hasattr(tree, 'wood') and hasattr(tree, 'max_wood'):
                if tree.wood < tree.max_wood:  # Only show if tree has been chopped
                    tree.draw_health_bar(self.display_surface)

    def run(self):

        # Update animation and movement
        self.villager_sprites.update()
        self.scout_sprites.update()

        # Reveal fog for scouts
        for scout in self.scout_sprites:
            self.reveal_cell(scout.rect.centerx, scout.rect.centery)

        # Reveal fog for villagers
        for villager in self.villager_sprites:
            self.reveal_cell(villager.rect.centerx, villager.rect.centery)

        self.avoid_unit_collisions()
        self.avoid_collisions()

        # Replace any dead entities individually
        all_entities = list(self.villager_sprites) + list(self.scout_sprites)
        for entity in all_entities:
            if hasattr(entity, 'health') and entity.health <= 0:
                entity.kill()

        # Draw world (grass, sprites) in area 0 to self.height
        world_clip = pygame.Rect(0, 0, self.width, self.height)
        prev_clip = self.display_surface.get_clip()
        self.display_surface.set_clip(world_clip)
        self.visible_sprites.draw(self.display_surface)

        # Draw trees on top of base tiles but beneath entities
        if get_config('FOG_OF_WAR', True):
            # Only draw trees in revealed areas
            for tree in self.tree_sprites:
                tree_col = tree.rect.centerx // self.tile_size
                tree_row = tree.rect.centery // self.tile_size
                grid_sprite = self.grid_sprites.get((tree_row, tree_col))
                if grid_sprite and grid_sprite.image.get_alpha() <= 20:  # Revealed area
                    self.display_surface.blit(tree.image, tree.rect)
        else:
            # No fog of war, draw all trees
            self.tree_sprites.draw(self.display_surface)
        
        self.villager_sprites.draw(self.display_surface)
        self.scout_sprites.draw(self.display_surface)

        self.display_surface.set_clip(prev_clip)
        self.draw_health_bars()

        bottom_panel(self.display_surface)