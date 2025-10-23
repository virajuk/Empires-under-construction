import pygame
from src.game_state import current_game_state

class FoodVillager():

    def __init__(self):
        # food carrying
        self.food_carried = 0
        self.max_food_capacity = 10

        self.using_axe = False
        self.chopping = False
        self.last_chop_time = 0

        self.returning_home = False  # Flag to indicate returning home
        
        self.load_gathering_frames()

    def gathering_food_animation(self):

        # Render gathering animation towards the food tile
        direction = self.get_food_direction()
        current_frames = self.gather_frames.get(direction, [])
        self.frame_index += self.animation_speed
        if self.frame_index >= len(current_frames):
            self.frame_index = 0
        if current_frames:
            self.image = current_frames[int(self.frame_index)]

    def get_berry_bush_direction(self):
        """Get the direction towards the nearest adjacent berry bush"""
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
                    rect = pygame.Rect(c * frame_width, i * frame_height, frame_width, frame_height)
                    frame = sprite_sheet.subsurface(rect).copy()
                    frame = pygame.transform.scale(frame, (current_game_state.TILE_SIZE, current_game_state.TILE_SIZE))
                    if frame.get_flags() & pygame.SRCALPHA:
                        frame = frame.convert_alpha()
                    else:
                        bg = frame.get_at((0, 0))[:3]
                        frame.set_colorkey(bg)
                    self.gather_frames[direction].append(frame)
        except Exception:
            self.chop_frames = {d: [] for d in ['up', 'left', 'down', 'right']}

    def should_drop_food(self):
        """Check if villager should drop food (at max capacity)"""
        return self.food_carried >= self.max_food_capacity