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

# Line height for panel text (avoid overlap)
PANEL_LINE_HEIGHT = 24


def bottom_panel(display_surface):
    base_y = current_game_state.HEIGHT
    panel_height = get_config('PANEL_HEIGHT', 120)
    panel_rect = pygame.Rect(0, base_y, current_game_state.WIDTH, panel_height)
    pygame.draw.rect(display_surface, (40, 40, 40), panel_rect)
    pygame.draw.line(display_surface, (100, 100, 100), (0, base_y), (current_game_state.WIDTH, base_y), 2)

    font = get_font(32)
    line_y = base_y + 8

    # Line 0: Score, Wood, Food
    display_surface.blit(font.render(f"Score: {math.ceil(current_game_state.score)}", True, (255, 255, 255)), (16, line_y))
    display_surface.blit(font.render(f"Wood: {current_game_state.wood}", True, (255, 255, 255)), (128, line_y))
    display_surface.blit(font.render(f"Food: {current_game_state.food}", True, (255, 255, 255)), (240, line_y))
    line_y += PANEL_LINE_HEIGHT

    # Right side of panel: villager carrying food/wood
    right_padding = 16
    panel_right_x = current_game_state.WIDTH - right_padding

    # Line 1: Villager carrying food (if any)
    if hasattr(current_game_state, 'board') and hasattr(current_game_state.board, 'villager_sprites'):
        for villager in current_game_state.board.villager_sprites:
            if hasattr(villager, 'food_carried') and villager.food_carried > 0:
                text_surf = font.render(f"{villager.name} carrying Food: {villager.food_carried}/{villager.max_food_capacity}", True, (255, 255, 255))
                display_surface.blit(text_surf, (panel_right_x - text_surf.get_width(), line_y))
                line_y += PANEL_LINE_HEIGHT
                break

    # Line 2: Villager carrying wood (if any)
    if hasattr(current_game_state, 'board') and hasattr(current_game_state.board, 'villager_sprites'):
        for villager in current_game_state.board.villager_sprites:
            if hasattr(villager, 'wood_carried') and villager.wood_carried > 0:
                text_surf = font.render(f"{villager.name} carrying Wood: {villager.wood_carried}/{villager.max_wood_capacity}", True, (255, 255, 255))
                display_surface.blit(text_surf, (panel_right_x - text_surf.get_width(), line_y))
                line_y += PANEL_LINE_HEIGHT
                break

    # Right side: agent targets (fixed Y, independent of villager carry lines above)
    agent_right_y = base_y + 8
    if rl_agent.berry_bush is not None:
        text_surf = font.render(f"Agent Target Berry Bush: {rl_agent.berry_bush.rect.center} Villager: {rl_agent.villager.name if rl_agent.villager else 'None'}", True, (255, 255, 255))
        display_surface.blit(text_surf, (panel_right_x - text_surf.get_width(), agent_right_y))
        agent_right_y += PANEL_LINE_HEIGHT
    if rl_agent.tree is not None:
        text_surf = font.render(f"Agent Target Tree: {rl_agent.tree.rect.center} Villager: {rl_agent.villager.name if rl_agent.villager else 'None'}", True, (255, 255, 255))
        display_surface.blit(text_surf, (panel_right_x - text_surf.get_width(), agent_right_y))

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
