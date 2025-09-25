import random

from src.game_state import current_game_state

class Agent():

    def __init__(self, game_state):
        self.game_state = current_game_state
        self.action_cooldown = 500  # milliseconds

    def pick_a_tree(self):

        """Pick a tree to chop down"""
        trees = list(self.game_state.board.tree_sprites)
        if not trees:
            self.tree = None
        
        self.tree = random.choice(trees)

    def pick_villager(self):

        """Pick a villager to send to the tree"""
        villagers = list(self.game_state.board.villager_sprites)
        if not villagers:
            self.villager = None
        
        self.villager = random.choice(villagers)

agent = Agent(current_game_state)