import random
import pygame

from src.game_state import current_game_state
from src.trees import Tree

class Agent():

    def __init__(self):

        # self.game_state = current_game_state
        self.action_cooldown = 500  # milliseconds
        self.tree = None
        self.villager = None
        self.agent_control = True  # Flag to indicate agent is controlling villager

    def pick_a_tree(self):

        """Pick a tree to chop down (random selection)"""
        trees = list(current_game_state.board.tree_sprites)
        if trees:
            self.tree = random.choice(trees)
        # No trees available
        else:
            self.tree = None

    def pick_closest_tree(self):
        """Pick the closest tree to the selected villager"""
        if self.villager is None:
            self.tree = None
            return
            
        trees = list(current_game_state.board.tree_sprites)
        if not trees:
            self.tree = None
            return
            
        villager_pos = self.villager.rect.center
        closest_tree = None
        min_distance = float('inf')
        
        for tree in trees:
            tree_pos = tree.rect.center
            # Calculate Manhattan distance (simpler than Euclidean for grid-based movement)
            distance = abs(villager_pos[0] - tree_pos[0]) + abs(villager_pos[1] - tree_pos[1])
            
            if distance < min_distance:
                min_distance = distance
                closest_tree = tree
                
        self.tree = closest_tree

    def walk_villager_to_tree(self):
        """Walk the villager to the selected tree"""
        if self.villager is None or self.tree is None:
            return False
            
        villager_pos = self.villager.rect.center
        tree_pos = self.tree.rect.center
        
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
            self.villager.ai_mode = False
            
            # Mark villager as under agent control
            self.villager.agent_controlled = True
            
            # Set villager direction and movement (same as walk_to_home)
            self.villager.direction.x = move_x
            self.villager.direction.y = move_y
            
            # Update current direction for animation
            if move_x > 0:
                self.villager.current_direction = 'right'
            elif move_x < 0:
                self.villager.current_direction = 'left'
            elif move_y > 0:
                self.villager.current_direction = 'down'
            elif move_y < 0:
                self.villager.current_direction = 'up'
            
            # Let the villager's normal update cycle handle movement at consistent speed
            # (Movement will be applied in villager.update() using normalized direction * speed)
                
            return True
        
        # Already at tree (adjacent or same position)
        return False

    def is_villager_at_tree(self):
        """Check if villager is adjacent to the tree (can chop)"""
        if self.villager is None or self.tree is None:
            return False
            
        villager_pos = self.villager.rect.center
        tree_pos = self.tree.rect.center
        
        # Calculate distance
        dx = abs(villager_pos[0] - tree_pos[0])
        dy = abs(villager_pos[1] - tree_pos[1])
        
        # Check if adjacent (within one tile distance)
        tile_size = current_game_state.TILE_SIZE
        return dx <= tile_size and dy <= tile_size

    def pick_a_villager(self):

        """Pick a villager"""
        villagers = list(current_game_state.board.villager_sprites)
        if villagers:
            self.villager = random.choice(villagers)
            self.take_control_of_villager()
        # No villagers available
        else:
            self.villager = None

    def take_control_of_villager(self):
        """Take control of the villager from AI"""
        if self.villager:
            self.villager.ai_mode = False
            self.villager.agent_controlled = True
            # Stop any current movement
            self.villager.direction.x = 0
            self.villager.direction.y = 0
            
    def run(self):

        if self.villager is None:
            self.pick_a_villager()

        if self.tree not in current_game_state.board.tree_sprites:
            self.pick_closest_tree()  # Use closest tree selection after picking villager
            
        # villager should return home if at max capacity
        if self.villager.should_return_home():
            self.villager.walk_to_home()

            if self.villager.is_at_home():
                self.villager.drop_wood()
            return
        
        # Walk villager to tree if we have both
        if self.villager and self.tree:

            if not self.is_villager_at_tree():
                self.walk_villager_to_tree()
            else:
                self.villager.chopping_wood(self.tree)
                

rl_agent = Agent()