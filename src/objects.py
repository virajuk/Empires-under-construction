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
                AnimatedPlayer((center_x, center_y), (self.player_sprites,), start_cell=cell_id)

        self.plant_trees()

    def reset(self):
        """Respawn players only: remove existing players and spawn two new ones.

        Keep map, trees, and stats intact.
        """
        # Kill existing players
        for p in list(self.player_sprites):
            p.kill()

        # Spawn two players again at random tiles
        if self.cell_labels and len(self.cell_labels) > 1:
            cell_choices = random.sample(self.cell_labels, 2)
            for cell_id, (center_x, center_y) in cell_choices:
                AnimatedPlayer((center_x, center_y), (self.player_sprites,), start_cell=cell_id)

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

                # Determine tile type from WORLD_MAP when present
                tile_type = None
                if world_map and row_idx < len(world_map) and col_idx < len(world_map[row_idx]):
                    tile_type = world_map[row_idx][col_idx]

                # Place GreenGrass on 'grass' tiles and also beneath trees so trees overlay transparently
                if tile_type in ('grass', 'tree') or tile_type is None:
                    GreenGrass((x, y), (self.visible_sprites,), cell)

                # Always draw the grid overlay
                Grid((x, y), (self.visible_sprites,))

                center_x = x + settings.TILE_SIZE // 2
                center_y = y + settings.TILE_SIZE // 2
                self.cell_labels.append((cell, (center_x, center_y)))

        # Store grid dimensions for cell navigation
        self.grid_rows = rows
        self.grid_cols = cols


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

        # Prefer placing trees from WORLD_MAP if it contains 'tree' entries
        world_map = getattr(settings, 'WORLD_MAP', None)
        if world_map:
            for row_idx, row in enumerate(world_map):
                for col_idx, val in enumerate(row):
                    if val == 'tree':
                        x = col_idx * settings.TILE_SIZE
                        y = row_idx * settings.TILE_SIZE
                        # Instantiate tree and ensure it's added to both visible tree group and obstacles
                        tree = Trees((x, y), (self.tree_sprites,))
                        # Also add to obstacles so players cannot enter that tile
                        self.obstacles_sprites.add(tree)

    
    def run(self):

        # Update player animation and movement
        self.player_sprites.update()

        # Check for player-player collisions and reduce health
        players = list(self.player_sprites)
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                if players[i].rect.colliderect(players[j].rect):
                    # Reduce health by 5 for both players
                    players[i].health = max(0, players[i].health - 5)
                    players[j].health = max(0, players[j].health - 5)
                    # Set both to reverse next move
                    if hasattr(players[i], 'reverse_next_move'):
                        players[i].reverse_next_move = True
                    if hasattr(players[j], 'reverse_next_move'):
                        players[j].reverse_next_move = True

        # (Previously we reset the whole world when any player died.)
        # Now we handle death replacement per-player after obstacle collisions below.

        # Prevent players from entering obstacle tiles (trees)
        for player in list(self.player_sprites):
            # If player collides with any obstacle, revert to previous position and punish
            collided = pygame.sprite.spritecollideany(player, self.obstacles_sprites)
            if collided:
                # Revert position to previous rect if available
                if hasattr(player, 'prev_rect'):
                    player.rect = player.prev_rect.copy()
                # Hurt player and reverse next move
                if hasattr(player, 'health'):
                    player.health = max(0, player.health - 5)
                if hasattr(player, 'reverse_next_move'):
                    player.reverse_next_move = True

        # Replace any dead players individually (kill and spawn a new player at a random tile)
        # Recompute current players list
        players_after = list(self.player_sprites)
        for player in players_after:
            if hasattr(player, 'health') and player.health <= 0:
                # Kill the dead player sprite
                player.kill()
                # Spawn a replacement at a random cell
                if self.cell_labels:
                    cell_id, (cx, cy) = random.choice(self.cell_labels)
                    AnimatedPlayer((cx, cy), (self.player_sprites,), start_cell=cell_id)

        # Draw world (grass, sprites) in area 0 to settings.HEIGHT
        world_clip = pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT)
        prev_clip = self.display_surface.get_clip()
        self.display_surface.set_clip(world_clip)
        self.visible_sprites.draw(self.display_surface)
        # Draw trees on top of base tiles but beneath players
        self.tree_sprites.draw(self.display_surface)
        self.player_sprites.draw(self.display_surface)
        # Draw health bars above each player
        for player in self.player_sprites:
            if hasattr(player, 'draw_health_bar'):
                player.draw_health_bar(self.display_surface)
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

        # Show each player's cell id and score in the panel, styled like score/resources
        for idx, player in enumerate(self.player_sprites):
            # Find closest cell label to player center
            px, py = player.rect.center
            closest = min(self.cell_labels, key=lambda c: (c[1][0] - px) ** 2 + (c[1][1] - py) ** 2)
            current_cell = closest[0]

            # Increment player's score when they enter a new cell (don't count initial spawn)
            if hasattr(player, 'last_cell_id'):
                if player.last_cell_id is None:
                    player.last_cell_id = current_cell
                elif player.last_cell_id != current_cell:
                    player.score = getattr(player, 'score', 0) + 1
                    player.last_cell_id = current_cell

            # Render label and score
            label = f"Player {idx+1}: {current_cell}  Score: {getattr(player, 'score', 0)}"
            pid_text = font.render(label, True, (0, 255, 255))
            # Place after resources, with spacing
            text_x = 420 + idx * 300
            text_y = settings.HEIGHT + 8
            self.display_surface.blit(pid_text, (text_x, text_y))
