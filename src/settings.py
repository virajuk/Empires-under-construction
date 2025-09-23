# game setup
WIDTH = 1280
HEIGHT = 704  # World (grass) area height
PANEL_HEIGHT = 48
SCREEN_HEIGHT = HEIGHT + PANEL_HEIGHT  # Total window height
FPS = 60
TILE_SIZE = 64

SHOW_HEALTH = False # Set to True to show health bars for all entities

WORLD_MAP = [
['grass','grass','tree','tree','tree','tree','grass','grass','grass','grass','grass','grass','grass','tree','tree','tree','tree','grass','grass','grass'],
['grass','grass','grass','tree','tree','grass','grass','grass','grass','grass','grass','grass','grass','tree','grass','grass','grass','grass','grass','grass'],
['grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass'],
['grass','grass','grass','tree','tree','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass'],
['grass','grass','tree','tree','tree','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass'],
['grass','tree','tree','tree','tree','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','home','grass','grass','grass','grass'],
['grass','grass','grass','tree','grass','grass','grass','grass','grass','tree','tree','grass','grass','grass','grass','grass','grass','grass','grass','grass'],
['grass','grass','grass','tree','grass','grass','grass','grass','grass','tree','tree','grass','grass','grass','grass','grass','grass','grass','grass','grass'],
['grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass'],
['grass','grass','grass','grass','grass','grass','grass','grass','tree','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass'],
['grass','grass','grass','grass','grass','grass','grass','tree','tree','tree','grass','grass','grass','grass','grass','grass','grass','grass','grass','grass']
]