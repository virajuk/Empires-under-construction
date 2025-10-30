import pygame
import random
from src.game_state import current_game_state
from src.config import get as get_config
# from src.villager.wood_villager import WoodVillager

class Villager(pygame.sprite.Sprite):

    def __init__(self, pos, groups, start_cell=None):
        pygame.sprite.Sprite.__init__(self, groups)

        self.frame_index = 0
        self.animation_speed = 0.15
        self.current_direction = 'down'
        self.load_walk_frames()
        
        self.health = 100
        self.speed = 2

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

        names = ["Eleanor", "Aveline", "Hildegard", "Catalina", "Rhiannon"]
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

    def _villager_adjacent_positions(self):

        """Check if villager is adjacent to a home tile to allow wood drop."""
        villager_col = self.rect.centerx // current_game_state.TILE_SIZE
        villager_row = self.rect.centery // current_game_state.TILE_SIZE
        adjacent_positions = [
            (villager_row - 1, villager_col, 'up'),    # up
            (villager_row + 1, villager_col, 'down'),  # down
            (villager_row, villager_col - 1, 'left'),  # left
            (villager_row, villager_col + 1, 'right'), # right
        ]
        return adjacent_positions

    def is_at_home(self):

        adjacent_positions = self._villager_adjacent_positions()

        home_tile_pos = current_game_state.home_cell

        for row, col, _ in adjacent_positions:
            if (row, col) == home_tile_pos:
                return True
        
        return False

    def update(self):
        
        self.prev_rect = self.rect.copy()
        
        self.is_moving = self.direction.magnitude() > 0

        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Keep within screen bounds
        if self.rect.left < 0 or self.rect.right > current_game_state.WIDTH or self.rect.top < 0 or self.rect.bottom > current_game_state.HEIGHT:
            self.rect.clamp_ip(pygame.Rect(0, 0, current_game_state.WIDTH, current_game_state.HEIGHT))
        
class WoodVillager(Villager):
    
    def init_as_wood_villager(self):

        self.wood_carried = 0
        self.max_wood_capacity = 10
        self.using_axe = False
        self.chopping = False
        self.last_chop_time = 0
        self.returning_home = False  # Flag to indicate returning home

        self.load_chopping_frames()

    def drop_wood(self):

        """Drop all carried wood if adjacent to home tile. Returns amount dropped and adds to game state."""
        if self.wood_carried > 0 and self.is_at_home():
            dropped = self.wood_carried
            self.wood_carried = 0
            current_game_state.add_wood(dropped)
            current_game_state.update_score(dropped*1.2)
            return dropped
        return 0

    def gather_wood_from_tree(self, tree):

        """Gather wood when chopping"""
        wood_gathered = min(1, self.max_wood_capacity - self.wood_carried)
        if wood_gathered > 0:
            tree.reduce_wood(wood_gathered)
            self.wood_carried += wood_gathered
            
            # Check if at max capacity and should return home
            if self.wood_carried >= self.max_wood_capacity:
                self.chopping = False  # Stop chopping
                self.returning_home = True  # Start returning home
                
        return True

    def can_chop_tree(self):

        adjacent_positions = self._villager_adjacent_positions()
        world_map = current_game_state.WORLD_MAP
        if not world_map:
            return False
            
        for row, col, _ in adjacent_positions:
            # Check bounds
            if 0 <= row < len(world_map) and 0 <= col < len(world_map[0]):
                if world_map[row][col] == 'tree':
                    return True
        return False

    def is_at_tree(self, tree):

        """Check if villager is adjacent to the tree (can chop)"""
        if self is None or tree is None:
            return False
        
        villager_pos = self.rect.center
        tree_pos = tree.rect.center
        
        # Calculate distance
        dx = abs(villager_pos[0] - tree_pos[0])
        dy = abs(villager_pos[1] - tree_pos[1])
        
        # Check if adjacent (within one tile distance)
        tile_size = current_game_state.TILE_SIZE
        return dx <= tile_size and dy <= tile_size

    def walk_to_tree(self, tree):

        """Walk the villager to the selected tree"""
        if self is None or tree is None:
            return False

        villager_pos = self.rect.center
        tree_pos = tree.rect.center

        # Calculate direction to tree
        dx = tree_pos[0] - villager_pos[0]
        dy = tree_pos[1] - villager_pos[1]
        
        # Determine movement direction (one step at a time)
        move_x = 0
        move_y = 0
        
        # Prioritize larger distance first
        if abs(dx) > abs(dy):
            if dx > 0:
                move_x = 1  # Move right
            elif dx < 0:
                move_x = -1  # Move left
        else:
            if dy > 0:
                move_y = 1  # Move down
            elif dy < 0:
                move_y = -1  # Move up
        
        # Apply movement to villager
        if move_x != 0 or move_y != 0:
            # Disable AI mode to allow agent control
            self.ai_mode = False
            
            # Mark villager as under agent control
            self.agent_controlled = True
            
            # Set villager direction and movement (same as walk_to_home)
            self.direction.x = move_x
            self.direction.y = move_y
            
            # Update current direction for animation
            if move_x > 0:
                self.current_direction = 'right'
            elif move_x < 0:
                self.current_direction = 'left'
            elif move_y > 0:
                self.current_direction = 'down'
            elif move_y < 0:
                self.current_direction = 'up'

            return True
        
        # Already at tree (adjacent or same position)
        return False

    def should_drop_wood(self):

        """Check if villager should drop wood (at max capacity)"""
        return self.wood_carried >= self.max_wood_capacity

    def walk_home_to_drop_wood(self):
        
        """Walk villager towards an adjacent position to the home tile"""
        # Check if already adjacent to home
        if self.is_at_home():
            return False  # Already at home
        
        # Find home tile position
        world_map = current_game_state.WORLD_MAP
        if not world_map:
            return False
        
        home_tile_pos = current_game_state.home_cell

        if not home_tile_pos:
            return False
        
        home_row, home_col = home_tile_pos
        villager_col = self.rect.centerx // current_game_state.TILE_SIZE
        villager_row = self.rect.centery // current_game_state.TILE_SIZE
        
        # Find the best adjacent position to home
        adjacent_positions = [
            (home_row - 1, home_col, 'up'),    # north of home
            (home_row + 1, home_col, 'down'),  # south of home
            (home_row, home_col - 1, 'left'),  # west of home
            (home_row, home_col + 1, 'right'), # east of home
        ]
        
        # Choose the closest valid adjacent position
        best_target = None
        min_distance = float('inf')
        
        for target_row, target_col, direction in adjacent_positions:
            # Check if position is valid (within bounds and not an obstacle)
            if (0 <= target_row < len(world_map) and 
                0 <= target_col < len(world_map[0]) and
                world_map[target_row][target_col] != 'tree'):  # Avoid tree obstacles
                
                # Calculate Manhattan distance
                distance = abs(villager_row - target_row) + abs(villager_col - target_col)
                if distance < min_distance:
                    min_distance = distance
                    best_target = (target_row, target_col)
        
        if not best_target:
            return False
        
        target_row, target_col = best_target
        
        # Move towards the best adjacent position with obstacle avoidance
        move_x = 0
        move_y = 0
        
        # Determine movement direction (one step at a time)
        dx = target_col - villager_col
        dy = target_row - villager_row
        
        # Try primary movement directions with obstacle checking
        possible_moves = []
        
        # Prioritize larger distance first
        if abs(dx) > abs(dy):
            # Primary: horizontal movement
            if dx > 0:
                possible_moves.append((1, 0, 'right'))  # Move right
            elif dx < 0:
                possible_moves.append((-1, 0, 'left'))  # Move left
            # Secondary: vertical movement
            if dy > 0:
                possible_moves.append((0, 1, 'down'))  # Move down
            elif dy < 0:
                possible_moves.append((0, -1, 'up'))  # Move up
        else:
            # Primary: vertical movement
            if dy > 0:
                possible_moves.append((0, 1, 'down'))  # Move down
            elif dy < 0:
                possible_moves.append((0, -1, 'up'))  # Move up
            # Secondary: horizontal movement
            if dx > 0:
                possible_moves.append((1, 0, 'right'))  # Move right
            elif dx < 0:
                possible_moves.append((-1, 0, 'left'))  # Move left
        
        # Try each movement option, avoiding obstacles
        for test_move_x, test_move_y, direction in possible_moves:
            next_col = villager_col + test_move_x
            next_row = villager_row + test_move_y
            
            # Check if next position is within bounds
            if (0 <= next_row < len(world_map) and 
                0 <= next_col < len(world_map[0])):
                
                # Check if next position is not an obstacle
                next_tile = world_map[next_row][next_col]
                if next_tile not in ['tree']:  # Add other obstacles here as needed
                    # Valid move found
                    move_x = test_move_x
                    move_y = test_move_y
                    self.current_direction = direction
                    break
        
        # Apply movement if a valid direction was found
        if move_x != 0 or move_y != 0:
            self.direction.x = move_x
            self.direction.y = move_y
            return True
        
        # No valid movement found (blocked by obstacles)
        return False

    def get_tree_direction(self):
        
        adjacent_positions = self._villager_adjacent_positions()

        world_map = current_game_state.WORLD_MAP
        if not world_map:
            return self.last_move_direction
        
        for row, col, direction in adjacent_positions:
            # Check bounds
            if 0 <= row < len(world_map) and 0 <= col < len(world_map[0]):
                if world_map[row][col] == 'tree':
                    return direction
        
        # Fallback to last move direction if no tree found
        return self.last_move_direction
        
    def chopping_wood(self, tree):
        
        now = pygame.time.get_ticks()
        self.chopping = True
        self.chopping_woods_animation()
        
        # Damage adjacent trees every second
        if now - self.last_chop_time >= 1000:  # 1000ms = 1 second
            if hasattr(current_game_state, 'board') and hasattr(current_game_state.board, 'tree_sprites'):
                tree_found = self.gather_wood_from_tree(tree)
                if not tree_found:
                    # No trees left to chop, stop chopping
                    self.chopping = False
            self.last_chop_time = now

    def chopping_woods_animation(self):

        # Render chopping animation towards the tree tile
        direction = self.get_tree_direction()
        current_frames = self.chop_frames.get(direction, [])
        self.frame_index += self.animation_speed
        if self.frame_index >= len(current_frames):
            self.frame_index = 0
        if current_frames:
            self.image = current_frames[int(self.frame_index)]

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
                    frame = pygame.transform.scale(frame, (current_game_state.TILE_SIZE, current_game_state.TILE_SIZE))
                    if frame.get_flags() & pygame.SRCALPHA:
                        frame = frame.convert_alpha()
                    else:
                        bg = frame.get_at((0, 0))[:3]
                        frame.set_colorkey(bg)
                    self.chop_frames[direction].append(frame)
        except Exception:
            self.chop_frames = {d: [] for d in ['up', 'left', 'down', 'right']}

    def update(self):

        super().update()

        if self.chopping:

            self.direction.x, self.direction.y = 0, 0
            self.current_direction = self.last_move_direction

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

class FoodVillager(Villager):
    
    def init_as_food_villager(self):

        self.food_carried = 0
        self.max_food_capacity = 10
        self.gathering = False
        self.last_gather_time = 0
        self.returning_home = False  # Flag to indicate returning home

        self.load_gathering_frames()

    def drop_food(self):

        """Drop all carried food if adjacent to home tile. Returns amount dropped and adds to game state."""
        if self.food_carried > 0 and self.is_at_home():
            dropped = self.food_carried
            self.food_carried = 0
            current_game_state.add_food(dropped)
            current_game_state.update_score(dropped)
            return dropped
        return 0

    def load_gathering_frames(self):

        try:
            sprite_sheet = pygame.image.load('graphics/villager/food_picking.png').convert_alpha()
            sheet_width, sheet_height = sprite_sheet.get_size()
            rows, cols = 4, 6
            frame_width = sheet_width // cols
            frame_height = sheet_height // rows
            directions = ['up', 'left', 'down', 'right']
            self.gather_frames = {d: [] for d in directions}
            for i, direction in enumerate(directions):
                for c in range(cols):
                    cx = c * frame_width + frame_width // 2
                    cy = i * frame_height + frame_height // 2
                    crop_rect = pygame.Rect(cx - 32, cy - 32, 64, 64)
                    frame = sprite_sheet.subsurface(crop_rect).copy()
                    frame = pygame.transform.scale(frame, (current_game_state.TILE_SIZE, current_game_state.TILE_SIZE))
                    if frame.get_flags() & pygame.SRCALPHA:
                        frame = frame.convert_alpha()
                    else:
                        bg = frame.get_at((0, 0))[:3]
                        frame.set_colorkey(bg)
                    self.gather_frames[direction].append(frame)
        except Exception:
            self.gather_frames = {d: [] for d in ['up', 'left', 'down', 'right']}

    def is_at_berry_bush(self, berry_bush):

        """Check if villager is adjacent to the berry bush (can gather)"""
        if self is None or berry_bush is None:
            return False
        
        villager_pos = self.rect.center
        berry_bush_pos = berry_bush.rect.center
        
        # Calculate distance
        dx = abs(villager_pos[0] - berry_bush_pos[0])
        dy = abs(villager_pos[1] - berry_bush_pos[1])

        # Check if adjacent (within one tile distance)
        tile_size = current_game_state.TILE_SIZE
        return dx <= tile_size and dy <= tile_size

    def walk_to_berry_bush(self, berry_bush):

        """Walk the villager to the selected berry bush"""
        if self is None or berry_bush is None:
            return False

        villager_pos = self.rect.center
        berry_bush_pos = berry_bush.rect.center

        # Calculate direction to berry bush
        dx = berry_bush_pos[0] - villager_pos[0]
        dy = berry_bush_pos[1] - villager_pos[1]
        
        # Determine movement direction (one step at a time)
        move_x = 0
        move_y = 0
        
        # Prioritize larger distance first
        if abs(dx) > abs(dy):
            if dx > 0:
                move_x = 1  # Move right
            elif dx < 0:
                move_x = -1  # Move left
        else:
            if dy > 0:
                move_y = 1  # Move down
            elif dy < 0:
                move_y = -1  # Move up
        
        # Apply movement to villager
        if move_x != 0 or move_y != 0:
            # Disable AI mode to allow agent control
            self.ai_mode = False
            
            # Mark villager as under agent control
            self.agent_controlled = True
            
            # Set villager direction and movement (same as walk_to_home)
            self.direction.x = move_x
            self.direction.y = move_y
            
            # Update current direction for animation
            if move_x > 0:
                self.current_direction = 'right'
            elif move_x < 0:
                self.current_direction = 'left'
            elif move_y > 0:
                self.current_direction = 'down'
            elif move_y < 0:
                self.current_direction = 'up'

            return True
        
        # Already at berry bush (adjacent or same position)
        return False

    def should_drop_food(self):

        """Check if villager should drop food (at max capacity)"""
        return self.food_carried >= self.max_food_capacity

    def walk_home_to_drop_food(self):

        """Walk villager towards an adjacent position to the home tile"""
        # Check if already adjacent to home
        if self.is_at_home():
            return False  # Already at home
        
        # Find home tile position
        world_map = current_game_state.WORLD_MAP
        if not world_map:
            return False
        
        home_tile_pos = current_game_state.home_cell

        if not home_tile_pos:
            return False
        
        home_row, home_col = home_tile_pos
        villager_col = self.rect.centerx // current_game_state.TILE_SIZE
        villager_row = self.rect.centery // current_game_state.TILE_SIZE
        
        # Find the best adjacent position to home
        adjacent_positions = [
            (home_row - 1, home_col, 'up'),    # north of home
            (home_row + 1, home_col, 'down'),  # south of home
            (home_row, home_col - 1, 'left'),  # west of home
            (home_row, home_col + 1, 'right'), # east of home
        ]

        # Choose the closest valid adjacent position
        best_target = None
        min_distance = float('inf')

        for target_row, target_col, direction in adjacent_positions:
            # Check if position is valid (within bounds and not an obstacle)
            if (0 <= target_row < len(world_map) and 
                0 <= target_col < len(world_map[0]) and
                world_map[target_row][target_col] != 'tree'):  # Avoid tree obstacles
                
                # Calculate Manhattan distance
                distance = abs(villager_row - target_row) + abs(villager_col - target_col)
                if distance < min_distance:
                    min_distance = distance
                    best_target = (target_row, target_col)

        if not best_target:
            return False
        
        target_row, target_col = best_target
        
        # Move towards the best adjacent position with obstacle avoidance
        move_x = 0
        move_y = 0
        
        # Determine movement direction (one step at a time)
        dx = target_col - villager_col
        dy = target_row - villager_row
        
        # Try primary movement directions with obstacle checking
        possible_moves = []

        # Prioritize larger distance first
        if abs(dx) > abs(dy):
            # Primary: horizontal movement
            if dx > 0:
                possible_moves.append((1, 0, 'right'))  # Move right
            elif dx < 0:
                possible_moves.append((-1, 0, 'left'))  # Move left
            # Secondary: vertical movement
            if dy > 0:
                possible_moves.append((0, 1, 'down'))  # Move down
            elif dy < 0:
                possible_moves.append((0, -1, 'up'))  # Move up
        else:
            # Primary: vertical movement
            if dy > 0:
                possible_moves.append((0, 1, 'down'))  # Move down
            elif dy < 0:
                possible_moves.append((0, -1, 'up'))  # Move up
            # Secondary: horizontal movement
            if dx > 0:
                possible_moves.append((1, 0, 'right'))  # Move right
            elif dx < 0:
                possible_moves.append((-1, 0, 'left'))  # Move left

        # Try each movement option, avoiding obstacles
        for test_move_x, test_move_y, direction in possible_moves:
            next_col = villager_col + test_move_x
            next_row = villager_row + test_move_y
            
            # Check if next position is within bounds
            if (0 <= next_row < len(world_map) and 
                0 <= next_col < len(world_map[0])):
                
                # Check if next position is not an obstacle
                next_tile = world_map[next_row][next_col]
                if next_tile not in ['tree']:  # Add other obstacles here as needed
                    # Valid move found
                    move_x = test_move_x
                    move_y = test_move_y
                    self.current_direction = direction
                    break
        
        # Apply movement if a valid direction was found
        if move_x != 0 or move_y != 0:
            self.direction.x = move_x
            self.direction.y = move_y
            return True
        
        # No valid movement found (blocked by obstacles)
        return False
        
    def gather_food_from_berry_bush(self, berry_bush):

        """Gather food when at berry bush"""
        food_gathered = min(1, self.max_food_capacity - self.food_carried)
        if food_gathered > 0:
            berry_bush.reduce_food(food_gathered)
            self.food_carried += food_gathered

            # Check if at max capacity and should return home
            if self.food_carried >= self.max_food_capacity:
                self.gathering = False  # Stop gathering
                self.returning_home = True  # Start returning home
                
        return True
    
    def gathering_food(self, berry_bush):

        """Gather food when at berry bush"""
        now = pygame.time.get_ticks()
        self.gathering = True
        self.gathering_food_animation()
        
        # Gather food every second
        if now - self.last_gather_time >= 1000:  # 1000ms = 1 second
            if hasattr(current_game_state, 'board') and hasattr(current_game_state.board, 'berry_bush_sprites'):
                berry_bush_found = self.gather_food_from_berry_bush(berry_bush)
                if not berry_bush_found:
                    # No berry bushes left to gather, stop gathering
                    self.gathering = False

            self.last_gather_time = now

    def get_berry_bush_direction(self):
        
        adjacent_positions = self._villager_adjacent_positions()

        world_map = current_game_state.WORLD_MAP
        if not world_map:
            return self.last_move_direction
        
        for row, col, direction in adjacent_positions:
            # Check bounds
            if 0 <= row < len(world_map) and 0 <= col < len(world_map[0]):
                if world_map[row][col] == 'berry_bush':
                    return direction
        
        # Fallback to last move direction if no berry bush found
        return self.last_move_direction

    def gathering_food_animation(self):

        # Render gathering animation towards the berry bush tile
        direction = self.get_berry_bush_direction()
        current_frames = self.gather_frames.get(direction, [])
        self.frame_index += self.animation_speed
        if self.frame_index >= len(current_frames):
            self.frame_index = 0
        if current_frames:
            self.image = current_frames[int(self.frame_index)]

    def update(self):

        super().update()

        if self.gathering:

            self.direction.x, self.direction.y = 0, 0
            self.current_direction = self.last_move_direction

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