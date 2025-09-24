import pygame
import random
from src.game_state import game_state

class Scout(pygame.sprite.Sprite):

    def __init__(self, pos, groups, start_cell=None):

        super().__init__(groups)

        self.frame_index = 0
        self.animation_speed = 0.15
        self.current_direction = 'down'  # Default facing direction
        self.load_walk_frames()
        self.image = self.frames[self.current_direction][0]
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2()
        # For collision reversion (if needed)
        self.prev_rect = self.rect.copy()

        # Health
        self.health = 100  # Max 100

        # Reverse direction flag (for obstacle collision)
        self.reverse_next_move = False

        # Autonomous movement state (AI) - Scouts are faster and more active
        self.ai_mode = True
        self.speed = 3  # Slightly faster than villagers
        self.is_moving = False
        self.ai_next_change = 0  # Always triggers direction pick on first update
        self.ai_move_duration = 0
        self.ai_directions = ['up', 'down', 'left', 'right', 'idle']
        
        # Track trees discovered by this scout
        self.discovered_trees = []

    @staticmethod
    def spawn_position(cell_labels):

        # Spawn left of home tile, fallback to random
        world_map = game_state.WORLD_MAP
        tile_size = game_state.TILE_SIZE
        home_row, home_col = None, None
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
            scout_x = scout_col * tile_size + tile_size // 2
            scout_y = scout_row * tile_size + tile_size // 2
            scout_cell_id = None
            for cell_id, (center_x, center_y) in cell_labels:
                if abs(center_x - scout_x) < tile_size // 2 and abs(center_y - scout_y) < tile_size // 2:
                    scout_cell_id = cell_id
                    break
            return (scout_x, scout_y), scout_cell_id
        else:
            # Fallback: spawn at random if home not found
            if cell_labels:
                cell_id, (center_x, center_y) = random.choice(cell_labels)
                return (center_x, center_y), cell_id
            return None, None

    def draw_health_bar(self, surface):
        
        """Draw a health bar above the scout sprite"""
        bar_width = game_state.TILE_SIZE * 0.7
        bar_height = 8
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top

        # Background
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        # Health amount
        health_ratio = max(0, min(1, self.health / 100))
        fill_width = int(bar_width * health_ratio)
        pygame.draw.rect(surface, (40, 200, 40), (bar_x, bar_y, fill_width, bar_height))  # Green health bar for scouts
        # Border
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)


    def load_walk_frames(self):
        """Load walking animation frames from graphics/scout/walk.png organized by direction (4x9 grid)"""
        sprite_sheet = pygame.image.load('graphics/scout/walk.png').convert_alpha()
        sheet_width, sheet_height = sprite_sheet.get_size()
        rows, cols = 4, 9
        frame_width = sheet_width // cols
        frame_height = sheet_height // rows
        directions = ['up', 'left', 'down', 'right']
        self.frames = {d: [] for d in directions}
        for i, direction in enumerate(directions):
            for c in range(cols):
                rect = pygame.Rect(c * frame_width, i * frame_height, frame_width, frame_height)
                frame = sprite_sheet.subsurface(rect).copy()
                frame = pygame.transform.scale(frame, (game_state.TILE_SIZE, game_state.TILE_SIZE))
                if frame.get_flags() & pygame.SRCALPHA:
                    frame = frame.convert_alpha()
                else:
                    bg = frame.get_at((0, 0))[:3]
                    frame.set_colorkey(bg)
                self.frames[direction].append(frame)


    def update(self):
        
        now = pygame.time.get_ticks()

        # Reverse direction logic (matching Villager)
        if hasattr(self, 'reverse_next_move') and self.reverse_next_move:
            if self.direction.x == 1:
                self.direction.x = -1
                self.current_direction = 'left'
            elif self.direction.x == -1:
                self.direction.x = 1
                self.current_direction = 'right'
            elif self.direction.y == 1:
                self.direction.y = -1
                self.current_direction = 'up'
            elif self.direction.y == -1:
                self.direction.y = 1
                self.current_direction = 'down'
            self.reverse_next_move = False

        # Store old position for collision/bounds check (used to revert on obstacle collision)
        self.prev_rect = self.rect.copy()

        # Autonomous random movement (AI) - Scouts change direction more frequently
        if self.ai_mode:
            if now > self.ai_next_change:
                direction = random.choices(
                    self.ai_directions,
                    weights=[4, 4, 4, 4, 1], k=1  # More movement-oriented than villagers
                )[0]
                if direction == 'up':
                    self.direction.x, self.direction.y = 0, -1
                    self.current_direction = 'up'
                elif direction == 'down':
                    self.direction.x, self.direction.y = 0, 1
                    self.current_direction = 'down'
                elif direction == 'left':
                    self.direction.x, self.direction.y = -1, 0
                    self.current_direction = 'left'
                elif direction == 'right':
                    self.direction.x, self.direction.y = 1, 0
                    self.current_direction = 'right'
                else:
                    self.direction.x, self.direction.y = 0, 0
                self.ai_move_duration = random.randint(300, 1500)  # Shorter duration than villagers
                self.ai_next_change = now + self.ai_move_duration

        # Check if moving
        self.is_moving = self.direction.magnitude() > 0

        # Normalize diagonal movement
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Update position
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Check for collision with outer bounds (match Villager)
        if self.rect.left < 0 or self.rect.right > game_state.WIDTH or self.rect.top < 0 or self.rect.bottom > game_state.HEIGHT:
            # self.health = max(0, self.health - 5)
            self.rect.clamp_ip(pygame.Rect(0, 0, game_state.WIDTH, game_state.HEIGHT))
            self.reverse_next_move = True

        # Animate only when moving
        current_frames = self.frames[self.current_direction]
        if self.is_moving and current_frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(current_frames):
                self.frame_index = 0
            self.image = current_frames[int(self.frame_index)]
        elif current_frames:
            self.image = current_frames[0]