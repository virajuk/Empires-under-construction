import pygame
import random
from src.game_state import current_game_state
from src.config import get as get_config
from src.villager.wood_villager import WoodVillager


class Villager(pygame.sprite.Sprite, WoodVillager):

    def __init__(self, pos, groups, start_cell=None):
        pygame.sprite.Sprite.__init__(self, groups)
        WoodVillager.__init__(self)

        self.frame_index = 0
        self.animation_speed = 0.15
        self.current_direction = 'down'
        self.load_walk_frames()
        
        self.health = 100
        self.speed = 2

        self.ai_mode = get_config('AI_MODE', True)
        self.is_moving = False
        self.ai_next_change = 0
        self.ai_move_duration = 0
        self.ai_directions = ['up', 'down', 'left', 'right', 'idle']
        
        self.direction = pygame.math.Vector2()
        self.last_move_direction = self.current_direction
        self.image = self.frames[self.current_direction][0]
        self.rect = self.image.get_rect(center=pos)
        self.prev_rect = self.rect.copy()

        self.name = self.random_name()

    def random_name(self):

        names = ["Agnes Axebearer", "Brunhild the Woodcutter", "Eda Timberhand", "Thyra Hewstone", "Griselda Ironarm"]
        return random.choice(names)

    def draw_health_bar(self, surface):

        bar_width = current_game_state.TILE_SIZE * 0.7
        bar_height = 8
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top

        # Draw health bar
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
                frame = pygame.transform.scale(frame, (current_game_state.TILE_SIZE, current_game_state.TILE_SIZE))
                if frame.get_flags() & pygame.SRCALPHA:
                    frame = frame.convert_alpha()
                else:
                    bg = frame.get_at((0, 0))[:3]
                    frame.set_colorkey(bg)
                self.frames[direction].append(frame)
    
    def reach_maximum_resource_carrying_limit(self):

        if self.max_wood_capacity <= self.wood_carried:
            self.chopping = False


    @staticmethod
    def spawn_position(cell_labels):

        # Spawn left of home tile, fallback to random
        world_map = current_game_state.WORLD_MAP
        tile_size = current_game_state.TILE_SIZE
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
        
    def manual_control(self):

        move_x, move_y = 0, 0
        if self.keys[pygame.K_w]:
            move_y = -1
            self.current_direction = 'up'
        elif self.keys[pygame.K_s]:
            move_y = 1
            self.current_direction = 'down'
        if self.keys[pygame.K_a]:
            move_x = -1
            self.current_direction = 'left'
        elif self.keys[pygame.K_d]:
            move_x = 1
            self.current_direction = 'right'
        self.direction.x, self.direction.y = move_x, move_y

        # Drop wood with 'g' key (only once per press)
        if self.keys[pygame.K_g]:
            if not hasattr(self, '_drop_toggle_last') or not self._drop_toggle_last:
                self.drop_wood()
            self._drop_toggle_last = True
        else:
            self._drop_toggle_last = False

        # Chop wood with 'c' key (only once per press)
        if self.keys[pygame.K_c]:
            if not hasattr(self, '_chop_toggle_last') or not self._chop_toggle_last:
                # Only allow chopping if adjacent to a tree
                if self.can_chop_tree():
                    self.chopping = not self.chopping
            self._chop_toggle_last = True
        else:
            self._chop_toggle_last = False

    def ai_control(self, now):

        move_x, move_y = 0, 0
        if now > self.ai_next_change:
            direction = random.choices(
                self.ai_directions,
                weights=[3, 3, 3, 3, 1], k=1
            )[0]
            if direction == 'up':
                move_y = -1
                self.current_direction = 'up'
            elif direction == 'down':
                move_y = 1
                self.current_direction = 'down'
            elif direction == 'left':
                move_x = -1
                self.current_direction = 'left'
            elif direction == 'right':
                move_x = 1
                self.current_direction = 'right'
            else:
                move_x, move_y = 0, 0
            self.direction.x, self.direction.y = move_x, move_y
        
            self.ai_move_duration = random.randint(500, 2000)
            self.ai_next_change = now + self.ai_move_duration

    def update(self):
        
        now = pygame.time.get_ticks()
        self.keys = pygame.key.get_pressed()

        # Check if manual control is enabled (AI_MODE is False)
        if not get_config('AI_MODE', True):
            self.manual_control()
        else:
            self.ai_control(now)

        self.reach_maximum_resource_carrying_limit()
        
        self.prev_rect = self.rect.copy()
        
        self.is_moving = self.direction.magnitude() > 0

        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Keep within screen bounds
        if self.rect.left < 0 or self.rect.right > current_game_state.WIDTH or self.rect.top < 0 or self.rect.bottom > current_game_state.HEIGHT:
            self.rect.clamp_ip(pygame.Rect(0, 0, current_game_state.WIDTH, current_game_state.HEIGHT))

        # If villager is chopping, override movement and play chopping animation
        if self.chopping:

            self.direction.x, self.direction.y = 0, 0
            self.current_direction = self.last_move_direction
    
            # self.chopping_wood(now)

        else:
            # Walking animation
            current_frames = self.frames[self.current_direction]
            if self.is_moving and current_frames:
                self.frame_index += self.animation_speed
                if self.frame_index >= len(current_frames):
                    self.frame_index = 0
                self.image = current_frames[int(self.frame_index)]
                self.last_move_direction = self.current_direction
            elif current_frames:
                self.image = current_frames[0]