import pygame
import itertools
import string
from collections import deque

from src.config import get as get_config
from src.game_state import game_state

def create_tree_patch(center, size):

    print(center, size, game_state.TILE_SIZE)

def bottom_panel(display_surface):
        
        # Draw bottom panel in area settings.HEIGHT to config SCREEN_HEIGHT
        panel_height = get_config('PANEL_HEIGHT', 48)
        # screen_height = game_state.HEIGHT + panel_height
        panel_rect = pygame.Rect(0, game_state.HEIGHT, game_state.WIDTH, panel_height)
        pygame.draw.rect(display_surface, (40, 40, 40), panel_rect)
        pygame.draw.line(display_surface, (100, 100, 100), (0, game_state.HEIGHT), (game_state.WIDTH, game_state.HEIGHT), 2)

        font = pygame.font.SysFont(None, 32)
        score_text = font.render(f"Score: {game_state.score}", True, (255, 255, 255))
        display_surface.blit(score_text, (16, game_state.HEIGHT + 8))

        resource_text = font.render(f"Wood: {game_state.wood}", True, (255, 255, 255))
        display_surface.blit(resource_text, (128, game_state.HEIGHT + 8))
        
        # Show villager wood carrying info
        if hasattr(game_state, 'board') and hasattr(game_state.board, 'villager_sprites'):
            for idx, villager in enumerate(game_state.board.villager_sprites):
                if hasattr(villager, 'wood_carried') and villager.wood_carried > 0:
                    villager_wood_text = font.render(f"Villager {idx+1} Wood: {villager.wood_carried}/{villager.max_wood_capacity}", True, (139, 69, 19))
                    display_surface.blit(villager_wood_text, (280 + idx * 200, game_state.HEIGHT + 8))
                    break  # Show only first villager with wood for now

        # # Show each villager's and scout's cell id and score in the panel
        # all_entities = list(self.villager_sprites) + list(self.scout_sprites)
        # for idx, entity in enumerate(all_entities):
        #     # Find closest cell label to entity center
        #     px, py = entity.rect.center
        #     closest = min(self.cell_labels, key=lambda c: (c[1][0] - px) ** 2 + (c[1][1] - py) ** 2)
        #     current_cell = closest[0]

            # # Show class name (type) in label
            # class_name = type(entity).__name__
            # label = f"{class_name} {idx+1}: {current_cell}  Score: {getattr(entity, 'score', 0)}"
            # pid_text = font.render(label, True, (0, 255, 255))
            # # Place after resources, with spacing
            # text_x = 420 + idx * 300
            # text_y = HEIGHT + 8
            # self.display_surface.blit(pid_text, (text_x, text_y))

def get_tree_center_from_id(tree_id, tile_size):
    """
    Given a tree cell id (e.g. 'aa0'), return its center (x, y) coordinates.
    Assumes id is two letters + column index, and rows are iterated in order.
    """

    # Parse row string and col index
    row_str = tree_id[:2]
    col_str = tree_id[2:]
    try:
        col_idx = int(col_str)
    except ValueError:
        return None, None
    # Find row index by iterating product of ascii_lowercase
    a = string.ascii_lowercase
    com = list(itertools.product(a, a))
    row_idx = None
    for idx, tup in enumerate(com):
        if ''.join(tup) == row_str:
            row_idx = idx
            break
    if row_idx is None:
        return None, None
    x = col_idx * tile_size + tile_size // 2
    y = row_idx * tile_size + tile_size // 2
    return x, y

def shortest_path(start, end, grid_rows, grid_cols, obstacles=None):
    """
    Find shortest path from start to end on a grid using BFS.
    start, end: (x, y) coordinates (center of tile)
    grid_rows, grid_cols: grid size
    obstacles: set of (row, col) tuples to avoid
    Returns: list of (x, y) coordinates representing the path, or [] if no path
    """
    
    if obstacles is None:
        obstacles = set()
    # Convert coordinates to grid indices
    def to_grid(coord):
        x, y = coord
        col = x // game_state.TILE_SIZE
        row = y // game_state.TILE_SIZE
        return row, col
    def to_coord(row, col):
        x = col * game_state.TILE_SIZE + game_state.TILE_SIZE // 2
        y = row * game_state.TILE_SIZE + game_state.TILE_SIZE // 2
        return x, y
    start_rc = to_grid(start)
    end_rc = to_grid(end)
    queue = deque()
    queue.append((start_rc, [start_rc]))
    visited = set()
    visited.add(start_rc)
    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    while queue:
        (row, col), path = queue.popleft()
        if (row, col) == end_rc:
            return [to_coord(r, c) for r, c in path]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < grid_rows and 0 <= nc < grid_cols and (nr, nc) not in visited and (nr, nc) not in obstacles:
                queue.append(((nr, nc), path + [(nr, nc)]))
                visited.add((nr, nc))
    return []

if __name__ == '__main__':

    pass
    # create_tree_patch(center, size)
