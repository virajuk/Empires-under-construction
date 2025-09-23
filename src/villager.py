import pygame
import random
from src.config import get as get_config
from src.map_loader import load_map

# Always use map values from the selected map
_map_name = get_config('SELECTED_MAP', 'map_1')
WIDTH, HEIGHT, TILE_SIZE, _ = load_map(_map_name)


class Villager(pygame.sprite.Sprite):
    
    def __init__(self, pos, groups, start_cell=None):

        super().__init__(groups)

        self.frame_index = 0
        self.animation_speed = 0.15
        self.current_direction = 'down'  # Default facing direction
        
        self.load_walk_frames()
        self.load_axe_frames()
        self.using_axe = False
        self.chopping = False
        self.load_chopping_frames()
        
        
        # Health (match AnimatedPlayer)
        self.health = 100  # Max 100

        # Reverse direction flag (for obstacle collision)
        self.reverse_next_move = False

        # Autonomous movement state (AI)
        self.ai_mode = True
        self.speed = 2
        self.is_moving = False
        self.ai_next_change = 0  # Always triggers direction pick on first update
        self.ai_move_duration = 0
        self.ai_directions = ['up', 'down', 'left', 'right', 'idle']

        self.direction = pygame.math.Vector2()
        self.last_move_direction = self.current_direction
        
        # Ensure self.image is set after frames are loaded and current_direction is set
        self.image = self.frames[self.current_direction][0]
        self.rect = self.image.get_rect(center=pos)

        # For collision reversion (if needed)
        self.prev_rect = self.rect.copy()
    
    def load_chopping_frames(self):
        """Load chopping animation frames from graphics/villager/chopping_wood.png organized by direction (4x6 grid)"""
        try:
            sprite_sheet = pygame.image.load('graphics/villager/chopping_wood.png').convert_alpha()
            sheet_width, sheet_height = sprite_sheet.get_size()
            rows, cols = 4, 6
            frame_width = sheet_width // cols
            frame_height = sheet_height // rows
            directions = ['up', 'left', 'down', 'right']
            self.chop_frames = {d: [] for d in directions}
            for i, direction in enumerate(directions):
                for c in range(cols):

                    # Crop a 64x64 region centered in the 128x128 frame
                    cx = c * frame_width + frame_width // 2
                    cy = i * frame_height + frame_height // 2
                    crop_rect = pygame.Rect(cx - 32, cy - 32, 64, 64)
                    frame = sprite_sheet.subsurface(crop_rect).copy()

                    # No need to scale, already 64x64
                    if frame.get_flags() & pygame.SRCALPHA:
                        frame = frame.convert_alpha()
                    else:
                        bg = frame.get_at((0, 0))[:3]
                        frame.set_colorkey(bg)
                    self.chop_frames[direction].append(frame)
        except Exception:
            self.chop_frames = {d: [] for d in ['up', 'left', 'down', 'right']}

    def load_axe_frames(self):

        """Load axe-walking animation frames from graphics/villager/walk_with_axe.png organized by direction (4x9 grid)"""
        try:
            sprite_sheet = pygame.image.load('graphics/villager/walk_with_axe.png').convert_alpha()
            sheet_width, sheet_height = sprite_sheet.get_size()
            rows, cols = 4, 9
            frame_width = sheet_width // cols
            frame_height = sheet_height // rows
            directions = ['up', 'left', 'down', 'right']
            self.axe_frames = {d: [] for d in directions}
            for i, direction in enumerate(directions):
                for c in range(cols):
                    rect = pygame.Rect(c * frame_width, i * frame_height, frame_width, frame_height)
                    frame = sprite_sheet.subsurface(rect).copy()
                    frame = pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE))
                    if frame.get_flags() & pygame.SRCALPHA:
                        frame = frame.convert_alpha()
                    else:
                        bg = frame.get_at((0, 0))[:3]
                        frame.set_colorkey(bg)
                    self.axe_frames[direction].append(frame)
        except Exception:
            self.axe_frames = {d: [] for d in ['up', 'left', 'down', 'right']}
            

    def draw_health_bar(self, surface):
        """Draw a health bar above the villager sprite"""
        bar_width = TILE_SIZE
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
        """Load walking animation frames from graphics/villager/walk.png organized by direction (4x9 grid)"""
        sprite_sheet = pygame.image.load('graphics/villager/walk.png').convert_alpha()
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
                frame = pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE))
                if frame.get_flags() & pygame.SRCALPHA:
                    frame = frame.convert_alpha()
                else:
                    bg = frame.get_at((0, 0))[:3]
                    frame.set_colorkey(bg)
                self.frames[direction].append(frame)

    def chopping_woods_animation(self):

        # Animate using chopping frames in last movement direction
        direction = self.last_move_direction
        current_frames = self.chop_frames[direction]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(current_frames):
            self.frame_index = 0
        if current_frames:
            self.image = current_frames[int(self.frame_index)]

    def walk_with_axe_animation(self):

        # Animate using axe frames
        current_frames = self.axe_frames[self.current_direction]
        if self.is_moving and current_frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(current_frames):
                self.frame_index = 0
            self.image = current_frames[int(self.frame_index)]
        elif current_frames:
            self.image = current_frames[0]

    def update(self):
        
        now = pygame.time.get_ticks()

        # Toggle axe animation with 'c' key, chopping with 'p' key
        keys = pygame.key.get_pressed()
        if keys[pygame.K_c]:
            if not hasattr(self, '_axe_toggle_last') or not self._axe_toggle_last:
                self.using_axe = not self.using_axe
            self._axe_toggle_last = True
        else:
            self._axe_toggle_last = False

        if keys[pygame.K_p]:
            if not hasattr(self, '_chop_toggle_last') or not self._chop_toggle_last:
                self.chopping = not self.chopping
            self._chop_toggle_last = True
        else:
            self._chop_toggle_last = False

        # Reverse direction logic
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

        # Autonomous random movement (AI)
        if self.ai_mode:
            if now > self.ai_next_change:
                direction = random.choices(
                    self.ai_directions,
                    weights=[3, 3, 3, 3, 1], k=1
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
                self.ai_move_duration = random.randint(500, 2000)
                self.ai_next_change = now + self.ai_move_duration

        # Check if moving
        self.is_moving = self.direction.magnitude() > 0

        # Normalize diagonal movement
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Update position
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Check for collision with outer bounds (no health reduction)
        if self.rect.left < 0 or self.rect.right > WIDTH or self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
            self.reverse_next_move = True

        # Animate: use chopping animation if enabled, else axe, else normal
        if self.chopping:
            # Stop movement and play chopping animation in last movement direction
            self.direction.x = 0
            self.direction.y = 0
            self.current_direction = self.last_move_direction
            self.chopping_woods_animation()
        elif self.using_axe:
            self.walk_with_axe_animation()
        else:
            current_frames = self.frames[self.current_direction]
            if self.is_moving and current_frames:
                self.frame_index += self.animation_speed
                if self.frame_index >= len(current_frames):
                    self.frame_index = 0
                self.image = current_frames[int(self.frame_index)]
                # Update last movement direction when moving
                self.last_move_direction = self.current_direction
            elif current_frames:
                self.image = current_frames[0]

