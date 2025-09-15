# Maps: Tile-Based Sandbox with Procedural Ponds

A small Python 3 + Pygame sandbox for experimenting with tile-based world generation using Perlin noise. The project renders a grid of grass tiles, overlays a visual grid, and procedurally places water ponds (and optionally trees) using noise-based placement. All graphics are loaded and scaled to a configurable tile size.

## Features
- **Grid-based world:** The screen is filled with grass tiles, each snapped to a uniform grid.
- **Procedural ponds:** Water tiles are placed using Perlin noise, creating organic pond shapes.
- **Optional trees:** Tree placement uses similar noise logic (currently disabled by default).
- **Configurable:** Change `WIDTH`, `HEIGHT`, `TILE_SIZE` in `src/settings.py` to adjust resolution and grid density.
- **Simple rendering:** Sprites are drawn in layers—terrain first, then decorations.

## Quick Start

### Prerequisites
- Python 3.x
- [pygame](https://www.pygame.org/)
- [numpy](https://numpy.org/)

### Installation
```sh
python -m pip install -r requirements.txt
```

### Run the Game
```sh
python main.py
```

### Controls
- **ESC** or close window: Quit the game.

## Project Structure
```
main.py                # Entry point, game loop
src/
  objects.py           # World generation, sprite groups, rendering
  tile.py              # Terrain/grid sprite classes
  trees.py             # Tree sprite class
  settings.py          # Resolution, FPS, tile size
vendor/
  perlin2d.py          # Perlin/fractal noise utilities
graphics/              # Image assets (grass, grid, etc.)
```

## How World Generation Works
- **Grass/grid:** `Objects.create_map()` fills the screen with grass tiles and overlays a semi-transparent grid.
- **Water ponds:** `Objects.digging_ponds()` uses Perlin noise to place water tiles where noise values fall within a threshold. Water overlays grass.
- **Trees:** `Objects.plant_trees()` (disabled by default) uses noise to place trees as decorations.
- **Sprite groups:** Terrain and decorations are managed in separate groups for draw order.

## Customization & Extensions
- Change `TILE_SIZE` in `src/settings.py` to adjust grid density and image scaling.
- Tweak pond density/shape by editing the noise resolution and threshold in `Objects.digging_ponds()`.
- Add new tile types by following the pattern in `src/tile.py` and placing them with a new function in `Objects`.

## Troubleshooting
- Run from the repo root to ensure asset paths resolve correctly.
- Large resolutions or small tile sizes may impact performance due to sprite count.
- If you add new features, update draw order and sprite groups as needed.

## License
This project is for educational and sandbox purposes. See individual asset files for their respective licenses.
