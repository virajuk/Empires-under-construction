import random
import itertools
import string

import pygame
import numpy as np

from src import settings
from src.tile import GreenGrass, Sand, Water, Grid, Home
from src.trees import Tree
from src.villager import Villager
from src.scout import Scout
from src.game_state import GameState

from vendor.perlin2d import generate_perlin_noise_2d, generate_fractal_noise_2d


class Objects:

    def __init__(self):

        # Restore display surface for drawing
        self.display_surface = pygame.display.get_surface()

        self.visible_sprites = pygame.sprite.Group()
        self.obstacles_sprites = pygame.sprite.Group()

        self.tree_sprites = pygame.sprite.Group()
        self.villager_sprites = pygame.sprite.Group()
        self.scout_sprites = pygame.sprite.Group()

        self.cell_labels = []  # Store (id, (x, y)) for each tile
        self.selected_cell_idx = None  # Index of currently selected cell
        self.last_cell_change = 0  # Timestamp for cell selection
        self.discovered_trees = []  # Track tree IDs discovered by scouts

        self.game_state = GameState()

        self.grid_sprites = {}  # (row, col) -> Grid sprite

        self.create_map()
        self.add_scout()

    def add_villager(self):

        # Create a villager at a random tile center
        if self.cell_labels:
            cell_id, (center_x, center_y) = random.choice(self.cell_labels)
            Villager((center_x, center_y), (self.villager_sprites,), start_cell=cell_id)

    def add_scout(self):

        # Dynamically find the home tile location from WORLD_MAP
        world_map = getattr(settings, 'WORLD_MAP', None)
        home_row, home_col = None, None
        if world_map:
            for r, row in enumerate(world_map):
                for c, val in enumerate(row):
                    if val == 'home':
                        home_row, home_col = r, c
                        break
                if home_row is not None:
                    break
        if home_row is not None and home_col is not None and home_col > 0:
            scout_row, scout_col = home_row, home_col - 1
            scout_x = scout_col * settings.TILE_SIZE + settings.TILE_SIZE // 2
            scout_y = scout_row * settings.TILE_SIZE + settings.TILE_SIZE // 2
            # Find the corresponding cell ID for this position
            scout_cell_id = None
            for cell_id, (center_x, center_y) in self.cell_labels:
                if abs(center_x - scout_x) < settings.TILE_SIZE // 2 and abs(center_y - scout_y) < settings.TILE_SIZE // 2:
                    scout_cell_id = cell_id
                    break
            Scout((scout_x, scout_y), (self.scout_sprites,), start_cell=scout_cell_id)
        else:
            # Fallback: spawn at random if home not found
            if self.cell_labels:
                cell_id, (center_x, center_y) = random.choice(self.cell_labels)
                Scout((center_x, center_y), (self.scout_sprites,), start_cell=cell_id)

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

        """
        Fills the screen with a grid of GreenGrass tiles and overlays grid cells.
        - Computes grid size from HEIGHT, WIDTH, and TILE_SIZE.
        - Each tile is placed at snapped pixel coordinates and given a unique id (2-letter row + column index).
        - Adds both terrain and grid sprites to visible_sprites for rendering.
        """
        # Prefer WORLD_MAP from settings when available
        world_map = getattr(settings, 'WORLD_MAP', None)
        if world_map and len(world_map) > 0 and len(world_map[0]) > 0:
            rows = len(world_map)
            cols = len(world_map[0])
        else:
            # Fallback to sizing based on pixel dimensions
            rows = int(settings.HEIGHT / settings.TILE_SIZE)
            cols = int(settings.WIDTH / settings.TILE_SIZE)
        
        self.map_size = [rows, cols]

        a = string.ascii_lowercase
        com = itertools.product(a, a)

        for row_idx in range(rows):
            y = row_idx * settings.TILE_SIZE
            row_str = "".join(next(com))

            for col_idx in range(cols):
                x = col_idx * settings.TILE_SIZE
                cell = row_str + str(col_idx)
                # Always assign tile_type before any usage
                tile_type = None
                if world_map and row_idx < len(world_map) and col_idx < len(world_map[row_idx]):
                    tile_type = world_map[row_idx][col_idx]
                center_x = x + settings.TILE_SIZE // 2
                center_y = y + settings.TILE_SIZE // 2

                # Place GreenGrass on 'grass' tiles and also beneath trees so trees overlay transparently
                GreenGrass((x, y), (self.visible_sprites,), cell)

                # Place trees on 'tree' tiles
                if tile_type in ('tree'):
                    Tree((center_x, center_y), (self.visible_sprites, self.obstacles_sprites), cell)
                
                # Place home on 'home' tiles
                if tile_type in ('home'):
                    Home((center_x, center_y), (self.visible_sprites, self.obstacles_sprites), cell)

                # Always draw the grid overlay, by default alpha=200
                grid_sprite = Grid((center_x, center_y), (self.visible_sprites,), cell)
                self.grid_sprites[(row_idx, col_idx)] = grid_sprite

                # If this is the home tile, set its grid alpha to 20
                if tile_type == 'home':
                    grid_sprite.image.set_alpha(20)
                self.cell_labels.append((cell, (center_x, center_y)))

        # Store grid dimensions for cell navigation
        self.grid_rows = rows
        self.grid_cols = cols

    def bottom_panel(self):

        # Draw bottom panel in area settings.HEIGHT to settings.SCREEN_HEIGHT
        panel_rect = pygame.Rect(0, settings.HEIGHT, settings.WIDTH, settings.PANEL_HEIGHT)
        pygame.draw.rect(self.display_surface, (40, 40, 40), panel_rect)
        pygame.draw.line(self.display_surface, (100, 100, 100), (0, settings.HEIGHT), (settings.WIDTH, settings.HEIGHT), 2)

        font = pygame.font.SysFont(None, 32)
        score_text = font.render(f"Score: {self.game_state.score}", True, (255, 255, 255))
        self.display_surface.blit(score_text, (16, settings.HEIGHT + 8))
        
        # Display discovered trees
        if self.discovered_trees:
            trees_text = f"Discovered Trees: {', '.join(self.discovered_trees)}"
            trees_render = font.render(trees_text, True, (255, 255, 0))  # Yellow color for tree discoveries
            self.display_surface.blit(trees_render, (220, settings.HEIGHT + 8))

        # Show each villager's and scout's cell id and score in the panel
        # all_entities = list(self.villager_sprites) + list(self.scout_sprites)
        # for idx, entity in enumerate(all_entities):
        #     # Find closest cell label to entity center
        #     px, py = entity.rect.center
        #     closest = min(self.cell_labels, key=lambda c: (c[1][0] - px) ** 2 + (c[1][1] - py) ** 2)
        #     current_cell = closest[0]

            # Increment entity's score when they enter a new cell (don't count initial spawn)
            # if hasattr(entity, 'last_cell_id'):
            #     if entity.last_cell_id is None:
            #         entity.last_cell_id = current_cell
            #     elif entity.last_cell_id != current_cell:
            #         entity.score = getattr(entity, 'score', 0) + 1
            #         entity.last_cell_id = current_cell

            # # Show class name (type) in label
            # class_name = type(entity).__name__
            # label = f"{class_name} {idx+1}: {current_cell}  Score: {getattr(entity, 'score', 0)}"
            # pid_text = font.render(label, True, (0, 255, 255))
            # # Place after resources, with spacing
            # text_x = 420 + idx * 300
            # text_y = settings.HEIGHT + 8
            # self.display_surface.blit(pid_text, (text_x, text_y))

    def avoid_collisions(self):

        # Check for player-player collisions (villagers and scouts)
        all_entities = list(self.villager_sprites) + list(self.scout_sprites)
        for i in range(len(all_entities)):
            for j in range(i + 1, len(all_entities)):
                if all_entities[i].rect.colliderect(all_entities[j].rect):
                    # Set both to reverse next move
                    if hasattr(all_entities[i], 'reverse_next_move'):
                        all_entities[i].reverse_next_move = True
                    if hasattr(all_entities[j], 'reverse_next_move'):
                        all_entities[j].reverse_next_move = True

        # Check for collisions between entities and obstacles
        for entity in all_entities:
            collided = pygame.sprite.spritecollideany(entity, self.obstacles_sprites)
            if collided:
                # If it's a scout colliding with a tree, record the tree discovery
                if type(entity).__name__ == 'Scout' and type(collided).__name__ == 'Tree':
                    tree_id = getattr(collided, 'id', 'unknown')
                    # Add to global discovered trees list if not already there
                    if tree_id not in self.discovered_trees:
                        self.discovered_trees.append(tree_id)
                        self.game_state.update_score(10)  # Add 10 points for new tree discovery
                    # Add to scout's personal discovered trees list if not already there
                    if hasattr(entity, 'discovered_trees') and tree_id not in entity.discovered_trees:
                        entity.discovered_trees.append(tree_id)
                # Reveal fog for obstacle tile when scout collides
                if type(entity).__name__ == 'Scout':
                    self.reveal_cell(collided.rect.centerx, collided.rect.centery)
                # Revert position to previous rect if available
                if hasattr(entity, 'prev_rect'):
                    entity.rect = entity.prev_rect.copy()
                # Always reverse direction
                if hasattr(entity, 'reverse_next_move'):
                    entity.reverse_next_move = True

    def reveal_cell(self, x, y):
        col = x // settings.TILE_SIZE
        row = y // settings.TILE_SIZE
        grid_sprite = self.grid_sprites.get((row, col))
        if grid_sprite:
            grid_sprite.image.set_alpha(20)

    def run(self):

        # Update player animation and movement
        self.villager_sprites.update()
        self.scout_sprites.update()
        # Reveal fog for scouts
        for scout in self.scout_sprites:
            self.reveal_cell(scout.rect.centerx, scout.rect.centery)
        self.avoid_collisions()

        # Replace any dead entities individually
        all_entities = list(self.villager_sprites) + list(self.scout_sprites)
        for entity in all_entities:
            if hasattr(entity, 'health') and entity.health <= 0:
                # Kill the dead entity sprite
                entity.kill()
        
        # Draw world (grass, sprites) in area 0 to settings.HEIGHT
        world_clip = pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT)
        prev_clip = self.display_surface.get_clip()
        self.display_surface.set_clip(world_clip)
        self.visible_sprites.draw(self.display_surface)

        # Draw trees on top of base tiles but beneath entities
        self.tree_sprites.draw(self.display_surface)
        self.villager_sprites.draw(self.display_surface)
        self.scout_sprites.draw(self.display_surface)
        
        # Draw health bars above each entity
        show_health = getattr(settings, 'SHOW_HEALTH', False)
        if show_health:
            for entity in all_entities:
                if hasattr(entity, 'draw_health_bar'):
                    entity.draw_health_bar(self.display_surface)
        
        self.display_surface.set_clip(prev_clip)

        self.bottom_panel()
