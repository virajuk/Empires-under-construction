import os
import yaml

CONFIG_PATH = os.path.join('config', 'config.yaml')
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

def get(key, default=None):
    return config.get(key, default)

# Example: get('SHOW_HEALTH', True)
