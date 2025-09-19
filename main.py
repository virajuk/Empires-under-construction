import pygame
import sys

from src import Objects
from src import settings


class Game:

    def __init__(self):
        """
        Initializes the Game environment:
        - Sets up Pygame and the display window with configured WIDTH and HEIGHT.
        - Sets the window caption to "EMPIRES".
        - Initializes the game clock for frame rate control.
        - Instantiates the Objects world, which manages all sprites and world generation.
        """

        pygame.init()
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption("EMPIRES")
        self.clock = pygame.time.Clock()
        self.objects = Objects()

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

            self.objects.run()

            pygame.display.update()
            self.clock.tick(60)


if __name__ == '__main__':

    game = Game()
    game.run()
