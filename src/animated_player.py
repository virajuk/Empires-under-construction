import pygame
import random
from glob import glob
from src import settings


class AnimatedPlayer(pygame.sprite.Sprite):
    
    """
    Animated player sprite with walking animation.
    Supports both sprite sheets and individual frame files.
    """

    def __init__(self, pos, groups, start_cell=None):
        super().__init__(groups)
        
        # Animation properties
        self.frame_index = 0
        self.animation_speed = 0.15  # Higher = faster animation
        self.frames = {'up': [], 'left': [], 'down': [], 'right': []}
        self.current_direction = 'down'  # Default facing direction
        self.load_walk_frames()
        # Health
        self.health = 100  # Max 100

        # Set initial image
        if any(self.frames.values()):
            self.image = self.frames[self.current_direction][0] if self.frames[self.current_direction] else list(self.frames.values())[0][0]
        else:
            # Fallback to solid color if no frames found
            self.image = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
            self.image.fill((255, 0, 0))  # Red square
            
        self.rect = self.image.get_rect(center=pos)
        # track previous rect for collision reversion
        self.prev_rect = self.rect.copy()
        
        # Movement
        self.direction = pygame.math.Vector2()
        self.speed = 2
        self.is_moving = False

        # Autonomous movement state
        self.ai_mode = True  # Set to True for random movement
        self.ai_next_change = 0
        self.ai_move_duration = 0
        self.ai_directions = ['up', 'down', 'left', 'right', 'idle']

        # Reverse direction flag
        self.reverse_next_move = False

        # Per-player scoring: total score and last visited cell id
        self.score = 0
        # Initialize last cell to the starting cell so initial spawn doesn't score
        self.last_cell_id = start_cell

    def draw_health_bar(self, surface):
        bar_width = settings.TILE_SIZE
        bar_height = 8
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top
        # Show class name above health bar
        font = pygame.font.SysFont(None, 16)
        class_name = type(self).__name__
        text = font.render(class_name, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.rect.centerx, bar_y - 8))
        surface.blit(text, text_rect)
        # Background
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        # Health amount
        health_ratio = max(0, min(1, self.health / 100))
        fill_width = int(bar_width * health_ratio)
        pygame.draw.rect(surface, (200, 40, 40), (bar_x, bar_y, fill_width, bar_height))
        # Border
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

    def load_walk_frames(self):
        """Load walking animation frames from graphics/sprite/ organized by direction"""
        
        # Try to load individual frame files first (walk_up_0.png, walk_left_1.png, etc.)
        directions = ['up', 'left', 'down', 'right']
        for direction in directions:
            walk_files = sorted(glob(f'graphics/sprite/walk_{direction}_*.png'))
            if walk_files:
                for file_path in walk_files:
                    frame = pygame.image.load(file_path).convert_alpha()
                    frame = pygame.transform.scale(frame, (settings.TILE_SIZE, settings.TILE_SIZE))
                    self.frames[direction].append(frame)
        
        # If no individual files, try to load sprite sheet walk.png and split by rows
        if not any(self.frames.values()):
            try:
                sprite_sheet = pygame.image.load('graphics/sprite/walk.png').convert_alpha()
                sheet_width = sprite_sheet.get_width()
                sheet_height = sprite_sheet.get_height()
                
                # Assume 4 rows for 4 directions, determine frame size
                rows = 4
                frame_height = sheet_height // rows
                frame_width = frame_height  # Assume square frames
                frames_per_row = sheet_width // frame_width
                
                direction_rows = {'up': 0, 'left': 1, 'down': 2, 'right': 3}
                
                for direction, row_index in direction_rows.items():
                    for frame_col in range(frames_per_row):
                        x = frame_col * frame_width
                        y = row_index * frame_height
                        frame_rect = pygame.Rect(x, y, frame_width, frame_height)
                        
                        # Ensure we don't go outside the image bounds
                        if x + frame_width <= sheet_width and y + frame_height <= sheet_height:
                            frame = sprite_sheet.subsurface(frame_rect)
                            frame = pygame.transform.scale(frame, (settings.TILE_SIZE, settings.TILE_SIZE))
                            self.frames[direction].append(frame)
                    
            except pygame.error:
                # If walk.png doesn't exist, create placeholder frames for each direction
                colors = {'up': (255, 100, 100), 'left': (100, 255, 100), 'down': (100, 100, 255), 'right': (255, 255, 100)}
                for direction in directions:
                    for i in range(4):
                        frame = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA)
                        frame.fill(colors[direction])
                        # Add a small indicator for frame number
                        pygame.draw.circle(frame, (0, 0, 0), (i * 4 + 4, 4), 2)
                        self.frames[direction].append(frame)
                # If walk.png doesn't exist, create placeholder frames
                for i in range(4):
                    frame = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA)
                    # Different colors for each frame to show animation
                    colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
                    frame.fill(colors[i])
                    self.frames.append(frame)

    def update(self):
        """Update animation and movement"""
        now = pygame.time.get_ticks()
        if self.reverse_next_move:
            # Reverse direction vector and current_direction
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

        if self.ai_mode:
            # Autonomous random movement
            if now > self.ai_next_change:
                direction = random.choice(self.ai_directions)
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
                # Next direction change in 0.5-2 seconds
                self.ai_move_duration = random.randint(500, 2000)
                self.ai_next_change = now + self.ai_move_duration
        else:
            # Handle input and determine direction
            keys = pygame.key.get_pressed()
            self.direction.x = 0
            self.direction.y = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1
                self.current_direction = 'left'
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.current_direction = 'right'
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -1
                self.current_direction = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                self.current_direction = 'down'

        # Check if moving
        self.is_moving = self.direction.magnitude() > 0

        # Normalize diagonal movement
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Store old position for collision/bounds check (used to revert on obstacle collision)
        self.prev_rect = self.rect.copy()

        # Update position
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Check for collision with outer bounds
        out_of_bounds = False
        if self.rect.left < 0 or self.rect.right > settings.WIDTH or self.rect.top < 0 or self.rect.bottom > settings.HEIGHT:
            out_of_bounds = True
            self.health = max(0, self.health - 5)
            # Clamp to screen
            self.rect.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))
            self.reverse_next_move = True

        # Animate only when moving
        current_frames = self.frames[self.current_direction]
        if self.is_moving and current_frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(current_frames):
                self.frame_index = 0
            self.image = current_frames[int(self.frame_index)]
        elif current_frames:
            # Show first frame when idle
            self.image = current_frames[0]