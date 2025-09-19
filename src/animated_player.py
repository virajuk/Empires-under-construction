import pygame
from glob import glob
from src import settings


class AnimatedPlayer(pygame.sprite.Sprite):
    """
    Animated player sprite with walking animation.
    Supports both sprite sheets and individual frame files.
    """

    def __init__(self, pos, groups):
        super().__init__(groups)
        
        # Animation properties
        self.frame_index = 0
        self.animation_speed = 0.15  # Higher = faster animation
        self.frames = {'up': [], 'left': [], 'down': [], 'right': []}
        self.current_direction = 'down'  # Default facing direction
        self.load_walk_frames()
        
        # Set initial image
        if any(self.frames.values()):
            self.image = self.frames[self.current_direction][0] if self.frames[self.current_direction] else list(self.frames.values())[0][0]
        else:
            # Fallback to solid color if no frames found
            self.image = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
            self.image.fill((255, 0, 0))  # Red square
            
        self.rect = self.image.get_rect(topleft=pos)
        
        # Movement
        self.direction = pygame.math.Vector2()
        self.speed = 2
        self.is_moving = False

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
            
        # Update position
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        # Keep player on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))
        
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