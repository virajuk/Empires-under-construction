
class GameState:

    def __init__(self):
        self.score = 0
        self.wood = 0
        self.gold = 0
        self.food = 0
        self.game_over = False

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

game_state = GameState()