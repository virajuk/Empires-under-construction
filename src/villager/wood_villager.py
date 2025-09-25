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
        
        self.load_chopping_frames()

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

    def gather_wood_from_tree(self, tree_sprites):

        """Gather wood when chopping"""
        villager_col = self.rect.centerx // current_game_state.TILE_SIZE
        villager_row = self.rect.centery // current_game_state.TILE_SIZE
        adjacent_positions = [
            (villager_row - 1, villager_col),  # up
            (villager_row + 1, villager_col),  # down
            (villager_row, villager_col - 1),  # left
            (villager_row, villager_col + 1),  # right
        ]
        for tree in tree_sprites:
            tree_col = tree.rect.centerx // current_game_state.TILE_SIZE
            tree_row = tree.rect.centery // current_game_state.TILE_SIZE
            if (tree_row, tree_col) in adjacent_positions:
                wood_gathered = min(1, self.max_wood_capacity - self.wood_carried)
                if wood_gathered > 0:
                    tree.reduce_wood(wood_gathered)
                    self.wood_carried += wood_gathered
                return True
        return False

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
    
    def get_tree_direction(self):

        """Get the direction towards the nearest adjacent tree"""
        # Get villager's grid position
        villager_col = self.rect.centerx // current_game_state.TILE_SIZE
        villager_row = self.rect.centery // current_game_state.TILE_SIZE
        
        # Check adjacent tiles with their directions
        adjacent_checks = [
            (villager_row - 1, villager_col, 'up'),    # up
            (villager_row + 1, villager_col, 'down'),  # down
            (villager_row, villager_col - 1, 'left'),  # left
            (villager_row, villager_col + 1, 'right'), # right
        ]
        
        world_map = current_game_state.WORLD_MAP
        if not world_map:
            return self.last_move_direction
            
        for row, col, direction in adjacent_checks:
            # Check bounds
            if 0 <= row < len(world_map) and 0 <= col < len(world_map[0]):
                if world_map[row][col] == 'tree':
                    return direction
        
        # Fallback to last move direction if no tree found
        return self.last_move_direction
    
    def chopping_wood(self, now):

        self.chopping_woods_animation()
        
        # Damage adjacent trees every second
        if now - self.last_chop_time >= 1000:  # 1000ms = 1 second
            if hasattr(current_game_state, 'board') and hasattr(current_game_state.board, 'tree_sprites'):
                tree_found = self.gather_wood_from_tree(current_game_state.board.tree_sprites)
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