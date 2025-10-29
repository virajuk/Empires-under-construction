import pygame
from src.game_state import current_game_state

class WoodVillager():

    def __init__(self):
        # Wood carrying
        self.wood_carried = 0
        self.max_wood_capacity = 10
        self.using_axe = False
        self.chopping = False
        self.last_chop_time = 0
        self.returning_home = False  # Flag to indicate returning home
        
        self.load_chopping_frames()

    def __villager_adjacent_positions(self):

        """Check if villager is adjacent to a home tile to allow wood drop."""
        villager_col = self.rect.centerx // current_game_state.TILE_SIZE
        villager_row = self.rect.centery // current_game_state.TILE_SIZE
        adjacent_positions = [
            (villager_row - 1, villager_col),  # up
            (villager_row + 1, villager_col),  # down
            (villager_row, villager_col - 1),  # left
            (villager_row, villager_col + 1),  # right
        ]
        return adjacent_positions

    def can_drop_wood(self):
        
        """Check if villager is adjacent to a home tile to allow wood drop."""
        villager_col = self.rect.centerx // current_game_state.TILE_SIZE
        villager_row = self.rect.centery // current_game_state.TILE_SIZE
        adjacent_positions = [
            (villager_row - 1, villager_col),  # up
            (villager_row + 1, villager_col),  # down
            (villager_row, villager_col - 1),  # left
            (villager_row, villager_col + 1),  # right
        ]
        world_map = current_game_state.WORLD_MAP
        if not world_map:
            return False
        for row, col in adjacent_positions:
            if 0 <= row < len(world_map) and 0 <= col < len(world_map[0]):
                if world_map[row][col] == 'home':
                    return True
        return False

    def drop_wood(self):

        """Drop all carried wood if adjacent to home tile. Returns amount dropped and adds to game state."""
        if self.wood_carried > 0 and self.can_drop_wood():
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

        """Check if villager is adjacent to a tree and can chop it"""
        # Get villager's grid position
        villager_col = self.rect.centerx // current_game_state.TILE_SIZE
        villager_row = self.rect.centery // current_game_state.TILE_SIZE
        
        # Check adjacent tiles (up, down, left, right)
        adjacent_positions = [
            (villager_row - 1, villager_col),  # up
            (villager_row + 1, villager_col),  # down
            (villager_row, villager_col - 1),  # left
            (villager_row, villager_col + 1),  # right
        ]
        world_map = current_game_state.WORLD_MAP
        if not world_map:
            return False
            
        for row, col in adjacent_positions:
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
        if self.can_drop_wood():
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
        
        """Get the direction towards the nearest adjacent tree for animations"""
        # Get villager's grid position
        villager_col = self.rect.centerx // current_game_state.TILE_SIZE
        villager_row = self.rect.centery // current_game_state.TILE_SIZE
        
        # Check adjacent tiles with their directions
        adjacent_positions = [
            (villager_row - 1, villager_col, 'up'),    # up
            (villager_row + 1, villager_col, 'down'),  # down
            (villager_row, villager_col - 1, 'left'),  # left
            (villager_row, villager_col + 1, 'right'), # right
        ]
        
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