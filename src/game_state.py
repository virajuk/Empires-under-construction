
class GameState:
    def __init__(self):
        self.score = 0
        self.wood = 0
        self.gold = 0
        self.food = 0
        self.game_over = False
        # Map settings (populated at game start)
        self.WIDTH = None
        self.HEIGHT = None
        self.TILE_SIZE = None
        self.WORLD_MAP = None
        self.MAP_NAME = None
        # Tree locations: list of (row, col) or (x, y) positions
        self.tree_locations = []

    def add_wood(self, amount):
        self.wood += amount

    def add_gold(self, amount):
        self.gold += amount

    def add_food(self, amount):
        self.food += amount

    def get_resources(self):
        return {
            'wood': self.wood,
            'gold': self.gold,
            'food': self.food
        }

    def update_score(self, points):
        self.score += points
    
    def reset(self):
        self.score = 0
        self.wood = 0
        self.gold = 0
        self.food = 0

current_game_state = GameState()