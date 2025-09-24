import pygame
import random
from src.game_state import game_state
from src.config import get as get_config

class Villager(pygame.sprite.Sprite):
    def __init__(self, pos, groups, start_cell=None):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.15
        self.current_direction = 'down'
        self.load_walk_frames()
        self.load_axe_frames()
        self.using_axe = False
        self.chopping = False
        self.load_chopping_frames()
        self.health = 100
        self.speed = 2

        self.ai_mode = get_config('AI_MODE', True)
        self.is_moving = False
        self.ai_next_change = 0
        self.ai_move_duration = 0
        self.ai_directions = ['up', 'down', 'left', 'right', 'idle']
        self.last_chop_time = 0

        # Wood carrying
        self.wood_carried = 0
        self.max_wood_capacity = 50

        self.direction = pygame.math.Vector2()
        self.last_move_direction = self.current_direction
        self.image = self.frames[self.current_direction][0]
        self.rect = self.image.get_rect(center=pos)
        self.prev_rect = self.rect.copy()

    def load_chopping_frames(self):
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
                    cx = c * frame_width + frame_width // 2
                    cy = i * frame_height + frame_height // 2
                    crop_rect = pygame.Rect(cx - 32, cy - 32, 64, 64)
                    frame = sprite_sheet.subsurface(crop_rect).copy()
                    frame = pygame.transform.scale(frame, (game_state.TILE_SIZE, game_state.TILE_SIZE))
                    if frame.get_flags() & pygame.SRCALPHA:
                        frame = frame.convert_alpha()
                    else:
                        bg = frame.get_at((0, 0))[:3]
                        frame.set_colorkey(bg)
                    self.chop_frames[direction].append(frame)
        except Exception:
            self.chop_frames = {d: [] for d in ['up', 'left', 'down', 'right']}
    
    def load_axe_frames(self):
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
                    frame = pygame.transform.scale(frame, (game_state.TILE_SIZE, game_state.TILE_SIZE))
                    if frame.get_flags() & pygame.SRCALPHA:
                        frame = frame.convert_alpha()
                    else:
                        bg = frame.get_at((0, 0))[:3]
                        frame.set_colorkey(bg)
                    self.axe_frames[direction].append(frame)
        except Exception:
            self.axe_frames = {d: [] for d in ['up', 'left', 'down', 'right']}
    
    def draw_health_bar(self, surface):

        bar_width = game_state.TILE_SIZE*0.7
        bar_height = 8
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top

        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        health_ratio = max(0, min(1, self.health / 100))
        fill_width = int(bar_width * health_ratio)
        pygame.draw.rect(surface, (200, 40, 40), (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
    
    def load_walk_frames(self):

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
                frame = pygame.transform.scale(frame, (game_state.TILE_SIZE, game_state.TILE_SIZE))
                if frame.get_flags() & pygame.SRCALPHA:
                    frame = frame.convert_alpha()
                else:
                    bg = frame.get_at((0, 0))[:3]
                    frame.set_colorkey(bg)
                self.frames[direction].append(frame)
    
    def chopping_woods_animation(self):
        # Render chopping animation towards the tree tile
        direction = self.get_tree_direction()
        current_frames = self.chop_frames.get(direction, [])
        self.frame_index += self.animation_speed
        if self.frame_index >= len(current_frames):
            self.frame_index = 0
        if current_frames:
            self.image = current_frames[int(self.frame_index)]
    
    def walk_with_axe_animation(self):
        current_frames = self.axe_frames[self.current_direction]
        if self.is_moving and current_frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(current_frames):
                self.frame_index = 0
            self.image = current_frames[int(self.frame_index)]
        elif current_frames:
            self.image = current_frames[0]
    
    def can_chop_tree(self):

        """Check if villager is adjacent to a tree and can chop it"""
        # Get villager's grid position
        villager_col = self.rect.centerx // game_state.TILE_SIZE
        villager_row = self.rect.centery // game_state.TILE_SIZE
        
        # Check adjacent tiles (up, down, left, right)
        adjacent_positions = [
            (villager_row - 1, villager_col),  # up
            (villager_row + 1, villager_col),  # down
            (villager_row, villager_col - 1),  # left
            (villager_row, villager_col + 1),  # right
        ]
        
        world_map = game_state.WORLD_MAP
        if not world_map:
            return False
            
        for row, col in adjacent_positions:
            # Check bounds
            if 0 <= row < len(world_map) and 0 <= col < len(world_map[0]):
                if world_map[row][col] == 'tree':
                    return True
        return False
    
    def reach_maximum_resource_carrying_limit(self):

        if self.max_wood_capacity <= self.wood_carried:
            self.chopping = False

    def get_tree_direction(self):
        """Get the direction towards the nearest adjacent tree"""
        # Get villager's grid position
        villager_col = self.rect.centerx // game_state.TILE_SIZE
        villager_row = self.rect.centery // game_state.TILE_SIZE
        
        # Check adjacent tiles with their directions
        adjacent_checks = [
            (villager_row - 1, villager_col, 'up'),    # up
            (villager_row + 1, villager_col, 'down'),  # down
            (villager_row, villager_col - 1, 'left'),  # left
            (villager_row, villager_col + 1, 'right'), # right
        ]
        
        world_map = game_state.WORLD_MAP
        if not world_map:
            return self.last_move_direction
            
        for row, col, direction in adjacent_checks:
            # Check bounds
            if 0 <= row < len(world_map) and 0 <= col < len(world_map[0]):
                if world_map[row][col] == 'tree':
                    return direction
        
        # Fallback to last move direction if no tree found
        return self.last_move_direction
    
    def gather_wood_from_tree(self, tree_sprites):
        """Gather wood when chopping"""
        # Get villager's grid position
        villager_col = self.rect.centerx // game_state.TILE_SIZE
        villager_row = self.rect.centery // game_state.TILE_SIZE
        
        # Check adjacent tiles
        adjacent_positions = [
            (villager_row - 1, villager_col),  # up
            (villager_row + 1, villager_col),  # down
            (villager_row, villager_col - 1),  # left
            (villager_row, villager_col + 1),  # right
        ]
        
        # Find trees in adjacent positions
        for tree in tree_sprites:
            tree_col = tree.rect.centerx // game_state.TILE_SIZE
            tree_row = tree.rect.centery // game_state.TILE_SIZE
            
            if (tree_row, tree_col) in adjacent_positions:
                wood_gathered = min(1, self.max_wood_capacity - self.wood_carried)  # Don't exceed capacity
                if wood_gathered > 0:
                    tree.reduce_wood(wood_gathered)
                    self.wood_carried += wood_gathered
                    # Add wood to game state resources
                    game_state.add_wood(wood_gathered)
                return True  # Tree was found and chopped
        
        return False  # No tree found to chop
    
    @staticmethod
    def spawn_position(cell_labels):

        # Spawn left of home tile, fallback to random
        world_map = game_state.WORLD_MAP
        tile_size = game_state.TILE_SIZE
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
            villager_row, villager_col = home_row, home_col - 1
            villager_x = villager_col * tile_size + tile_size // 2
            villager_y = villager_row * tile_size + tile_size // 2
            villager_cell_id = None
            for cell_id, (center_x, center_y) in cell_labels:
                if abs(center_x - villager_x) < tile_size // 2 and abs(center_y - villager_y) < tile_size // 2:
                    villager_cell_id = cell_id
                    break
            return (villager_x, villager_y), villager_cell_id
        else:
            # Fallback: spawn at random if home not found
            if cell_labels:
                cell_id, (center_x, center_y) = random.choice(cell_labels)
                return (center_x, center_y), cell_id
            return None, None


    def update(self):

        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # Check if manual control is enabled (AI_MODE is False)
        if not get_config('AI_MODE', True):
            move_x, move_y = 0, 0
            if keys[pygame.K_w]:
                move_y = -1
                self.current_direction = 'up'
            elif keys[pygame.K_s]:
                move_y = 1
                self.current_direction = 'down'
            if keys[pygame.K_a]:
                move_x = -1
                self.current_direction = 'left'
            elif keys[pygame.K_d]:
                move_x = 1
                self.current_direction = 'right'
            self.direction.x = move_x
            self.direction.y = move_y
            self.ai_mode = False
        else:
            self.ai_mode = True

        # if keys[pygame.K_c]:
        #     if not hasattr(self, '_axe_toggle_last') or not self._axe_toggle_last:
        #         self.using_axe = not self.using_axe
        #     self._axe_toggle_last = True
        # else:
        #     self._axe_toggle_last = False

        self.reach_maximum_resource_carrying_limit()
        
        if keys[pygame.K_p]:
            if not hasattr(self, '_chop_toggle_last') or not self._chop_toggle_last:
                # Only allow chopping if adjacent to a tree
                if self.can_chop_tree():
                    self.chopping = not self.chopping
            self._chop_toggle_last = True
        else:
            self._chop_toggle_last = False
        
        self.prev_rect = self.rect.copy()
        
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
        self.is_moving = self.direction.magnitude() > 0

        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        if self.rect.left < 0 or self.rect.right > game_state.WIDTH or self.rect.top < 0 or self.rect.bottom > game_state.HEIGHT:
            self.rect.clamp_ip(pygame.Rect(0, 0, game_state.WIDTH, game_state.HEIGHT))
    
        if self.chopping:
            self.direction.x = 0
            self.direction.y = 0
            self.current_direction = self.last_move_direction
            self.chopping_woods_animation()
            # Damage adjacent trees every second
            if now - self.last_chop_time >= 1000:  # 1000ms = 1 second
                if hasattr(game_state, 'board') and hasattr(game_state.board, 'tree_sprites'):
                    tree_found = self.gather_wood_from_tree(game_state.board.tree_sprites)
                    if not tree_found:
                        # No trees left to chop, stop chopping
                        self.chopping = False
                self.last_chop_time = now
        elif self.using_axe:
            self.walk_with_axe_animation()
        else:
            current_frames = self.frames[self.current_direction]
            if self.is_moving and current_frames:
                self.frame_index += self.animation_speed
                if self.frame_index >= len(current_frames):
                    self.frame_index = 0
                self.image = current_frames[int(self.frame_index)]
                self.last_move_direction = self.current_direction
            elif current_frames:
                self.image = current_frames[0]

