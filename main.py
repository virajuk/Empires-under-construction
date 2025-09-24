import pygame
import sys
from src import Board
from src.config import get as get_config
from src import game_state
from src.map_loader import load_map

from src import utils

class Game:
    def __init__(self):
        """
        Initializes the Game environment:
        - Sets up Pygame and the display window with configured WIDTH and HEIGHT.
        - Sets the window caption to "EMPIRES".
        - Initializes the game clock for frame rate control.
        - Instantiates the Objects world, which manages all sprites and world generation.
        """

        # Load selected map from config and store in game_state
        map_name = get_config('SELECTED_MAP', 'map_1')
        WIDTH, HEIGHT, TILE_SIZE, WORLD_MAP = load_map(map_name)
        game_state.WIDTH = WIDTH
        game_state.HEIGHT = HEIGHT
        game_state.TILE_SIZE = TILE_SIZE
        game_state.WORLD_MAP = WORLD_MAP
        game_state.MAP_NAME = map_name

        pygame.init()
        panel_height = get_config('PANEL_HEIGHT', 48)
        screen_height = game_state.HEIGHT + panel_height
        self.screen = pygame.display.set_mode((game_state.WIDTH, screen_height))
        pygame.display.set_caption(f"EMPIRES - {game_state.MAP_NAME}")
        self.clock = pygame.time.Clock()
        self.board = Board()

    def run(self):
        """
        Main game loop. Handles:
        - Continuous frame updates at ~60 FPS.
        - Event processing: window close and ESC key to quit.
        - Calls self.objects.run() to update and render all world sprites.
        - Updates display and enforces frame rate cap.
        """

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()
            self.board.run()
            pygame.display.update()
            self.clock.tick(get_config('FPS', 60))

            # trees = list(game_state.board.tree_sprites)
            # print(f"Trees: {len(trees)}")


            # for tree in trees:
            #     print(f"Tree: {tree.id} Wood: {tree.wood}")
            #     x, y = utils.get_tree_center_from_id(tree.id, game_state.TILE_SIZE)
            #     print(f"Tree Center: ({x}, {y})")

if __name__ == '__main__':
    game = Game()
    game.run()
