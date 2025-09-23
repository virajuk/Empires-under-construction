import pygame
from src.config import get as get_config
from src.map_loader import load_map
from src.game_state import game_state

# Always use map values from the selected map
_map_name = get_config('SELECTED_MAP', 'map_1')
WIDTH, HEIGHT, TILE_SIZE, _ = load_map(_map_name)

def create_tree_patch(center, size):

    print(center, size, TILE_SIZE)

def bottom_panel(display_surface, discovered_trees):
        # Draw bottom panel in area settings.HEIGHT to config SCREEN_HEIGHT
        panel_height = get_config('PANEL_HEIGHT', 48)
        screen_height = get_config('SCREEN_HEIGHT', HEIGHT + panel_height)
        panel_rect = pygame.Rect(0, HEIGHT, WIDTH, panel_height)
        pygame.draw.rect(display_surface, (40, 40, 40), panel_rect)
        pygame.draw.line(display_surface, (100, 100, 100), (0, HEIGHT), (WIDTH, HEIGHT), 2)

        font = pygame.font.SysFont(None, 32)
        score_text = font.render(f"Score: {game_state.score}", True, (255, 255, 255))
        display_surface.blit(score_text, (16, HEIGHT + 8))
        
        # Display discovered trees
        if discovered_trees:
            trees_text = f"Discovered Trees: {', '.join(discovered_trees)}"
            trees_render = font.render(trees_text, True, (255, 255, 0))  # Yellow color for tree discoveries
            display_surface.blit(trees_render, (220, HEIGHT + 8))

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

if __name__ == '__main__':

    pass
    # create_tree_patch(center, size)
