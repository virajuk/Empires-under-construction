# deprecated to keep older scripts who import this from breaking
from src.objects import Objects
from src import settings
from src.villager import Villager
from src.scout import Scout
from src.tile import GreenGrass, Sand, Water, Grid, Home
from src.trees import Tree

__all__ = ['Objects', 'settings', 'Villager', 'Scout', 'AnimatedPlayer', 'GreenGrass', 'Tree', 'Sand', 'Water', 'Grid', 'Home']