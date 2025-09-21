# deprecated to keep older scripts who import this from breaking
from src.objects import Objects
from src import settings
from src.villager import Villager
from src.tile import GreenGrass, Sand, Water, Grid, Home
from src.trees import Tree

__all__ = ['Objects', 'settings', 'Villager', 'AnimatedPlayer', 'GreenGrass', 'Tree', 'Sand', 'Water', 'Grid', 'Home']