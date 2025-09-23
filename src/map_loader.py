import importlib.util
import os

MAPS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'maps')

def list_maps():
    """Return a list of available map filenames (without .py extension)."""
    return [f[:-3] for f in os.listdir(MAPS_DIR) if f.endswith('.py')]

def load_map(map_name):
    """Dynamically load a map module and return its WIDTH, HEIGHT, TILE_SIZE, WORLD_MAP."""
    map_path = os.path.join(MAPS_DIR, f'{map_name}.py')
    spec = importlib.util.spec_from_file_location(map_name, map_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.WIDTH, module.HEIGHT, module.TILE_SIZE, module.WORLD_MAP
