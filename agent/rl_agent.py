import random
import pygame

from src.game_state import current_game_state
from src.objects import Tree
from src.villager.villager import WoodVillager

class Agent():

    def __init__(self):

        # self.game_state = current_game_state
        self.action_cooldown = 500  # milliseconds
        self.tree = None
        self.berry_bush = None
        self.villager = None
        self.agent_control = True  # Flag to indicate agent is controlling villager

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

    def action_chop_wood(self):

        if self.villager is None:
            self.pick_a_villager()

            self.villager.__class__ = WoodVillager
            self.villager.init_as_wood_villager()
            
        if self.tree not in current_game_state.board.tree_sprites:
            self.pick_closest_tree()  # Use closest tree selection after picking villager

        # villager should return home if at max capacity
        if self.villager.should_drop_wood():
            self.villager.walk_home_to_drop_wood()

            if self.villager.is_at_home():
                self.villager.drop_wood()
            return

        # Walk villager to tree if we have both
        if self.villager and self.tree:

            if not self.villager.is_at_tree(self.tree):
                self.villager.walk_to_tree(self.tree)
            else:
                self.villager.chopping_wood(self.tree)

    def pick_closest_berry_bush(self):

        """Pick the closest berry bush to the selected villager"""
        if self.villager is None:
            self.berry_bush = None
            return
            
        berry_bushes = list(current_game_state.board.berry_bush_sprites)
        if not berry_bushes:
            self.berry_bush = None
            return
            
        villager_pos = self.villager.rect.center
        closest_berry_bush = None
        min_distance = float('inf')

        for berry_bush in berry_bushes:
            berry_bush_pos = berry_bush.rect.center
            # Calculate Manhattan distance (simpler than Euclidean for grid-based movement)
            distance = abs(villager_pos[0] - berry_bush_pos[0]) + abs(villager_pos[1] - berry_bush_pos[1])

            if distance < min_distance:
                min_distance = distance
                closest_berry_bush = berry_bush

        self.berry_bush = closest_berry_bush

    def action_gather_food(self):
        
        if self.villager is None:
            self.pick_a_villager()

            self.villager.__class__ = WoodVillager
            self.villager.init_as_wood_villager()

        if self.berry_bush not in current_game_state.board.berry_bush_sprites:
            self.pick_closest_berry_bush()

    def run(self):
        
        self.action_chop_wood()
        # self.action_gather_food()

rl_agent = Agent()