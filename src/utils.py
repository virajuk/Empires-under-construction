import pygame
import itertools
import string
from collections import deque
import math

from src.config import get as get_config
from src.game_state import current_game_state
from agent import rl_agent

def get_font(size=32):

    """Get a font object, creating it only when pygame is initialized"""
    return pygame.font.SysFont(None, size)

def create_tree_patch(center, size):

    print(center, size, current_game_state.TILE_SIZE)

def bottom_panel(display_surface):
    
    # Draw bottom panel in area settings.HEIGHT to config SCREEN_HEIGHT
    panel_height = get_config('PANEL_HEIGHT', 48)
    # screen_height = game_state.HEIGHT + panel_height
    panel_rect = pygame.Rect(0, current_game_state.HEIGHT, current_game_state.WIDTH, panel_height)
    pygame.draw.rect(display_surface, (40, 40, 40), panel_rect)
    pygame.draw.line(display_surface, (100, 100, 100), (0, current_game_state.HEIGHT), (current_game_state.WIDTH, current_game_state.HEIGHT), 2)

    font = get_font(32)
    score_text = font.render(f"Score: {math.ceil(current_game_state.score)}", True, (255, 255, 255))
    display_surface.blit(score_text, (16, current_game_state.HEIGHT + 8))

    resource_text = font.render(f"Wood: {current_game_state.wood}", True, (255, 255, 255))
    display_surface.blit(resource_text, (128, current_game_state.HEIGHT + 8))
    
    go_for_a_tree(display_surface)

    # Show villager wood carrying info
    if hasattr(current_game_state, 'board') and hasattr(current_game_state.board, 'villager_sprites'):
        for idx, villager in enumerate(current_game_state.board.villager_sprites):
            if hasattr(villager, 'wood_carried') and villager.wood_carried > 0:
                villager_wood_text = font.render(f"{villager.name} Wood: {villager.wood_carried}/{villager.max_wood_capacity}", True, (255, 255, 255))
                display_surface.blit(villager_wood_text, (280 + idx * 200, current_game_state.HEIGHT + 8))
        
def go_for_a_tree(display_surface):

    if rl_agent.tree is None:
        rl_agent.pick_a_tree()

    if rl_agent.tree is not None:
        rl_agent.pick_villager()
        font = get_font(32)
        agent_text = font.render(f"Agent Target Tree: {rl_agent.tree.rect.center} by Villager {rl_agent.villager.rect.center}", True, (255, 255, 255))
        display_surface.blit(agent_text, (16, current_game_state.HEIGHT + 48))

    # path = shortest_path(agent.villager.rect.center, agent.tree.rect.center, current_game_state.HEIGHT, current_game_state.WIDTH)
    # path_text = font.render(f"Path: {path}", True, (255, 255, 255))
    # display_surface.blit(path_text, (360, current_game_state.HEIGHT + 48))

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
        col = x // current_game_state.TILE_SIZE
        row = y // current_game_state.TILE_SIZE
        return row, col
    def to_coord(row, col):
        x = col * current_game_state.TILE_SIZE + current_game_state.TILE_SIZE // 2
        y = row * current_game_state.TILE_SIZE + current_game_state.TILE_SIZE // 2
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
