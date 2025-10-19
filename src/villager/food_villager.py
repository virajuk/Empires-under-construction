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
        
        # self.load_chopping_frames()

    def gathering_food_animation(self):

        # Render gathering animation towards the food tile
        direction = self.get_food_direction()
        current_frames = self.gather_frames.get(direction, [])
        self.frame_index += self.animation_speed
        if self.frame_index >= len(current_frames):
            self.frame_index = 0
        if current_frames:
            self.image = current_frames[int(self.frame_index)]