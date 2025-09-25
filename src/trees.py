import random
from glob import glob
import pygame
from src.game_state import current_game_state

class Tree(pygame.sprite.Sprite):
    def __init__(self, pos, groups, id):
        super().__init__(groups)
        self.images = glob('graphics/tree/*.png')
        self.image = pygame.image.load(random.choice(self.images)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (current_game_state.TILE_SIZE, current_game_state.TILE_SIZE))
        self.rect = self.image.get_rect(center=pos)
        self.id = id
        self.wood = 100
        self.max_wood = 100

    def reduce_wood(self, amount):
        """Reduce tree's wood by the specified amount"""
        self.wood = max(0, self.wood - amount)
        if self.wood <= 0:
            self.kill()  # Remove tree when wood reaches 0
    
    def draw_health_bar(self, surface):

        """Draw a health bar above the tree sprite"""
        bar_width = current_game_state.TILE_SIZE * 0.8
        bar_height = 6
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top

        # Background
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        # Wood amount (health)
        wood_ratio = max(0, min(1, self.wood / self.max_wood))
        fill_width = int(bar_width * wood_ratio)
        pygame.draw.rect(surface, (139, 69, 19), (bar_x, bar_y, fill_width, bar_height))  # Brown color for wood
        # Border
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)