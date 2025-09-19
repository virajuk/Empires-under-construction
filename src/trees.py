import random

from glob import glob
import pygame

from src import settings

class Trees(pygame.sprite.Sprite):
    
    # Cache frames per sheet path to avoid reloading/splitting for each instance
    _frames_cache = {}

    def __init__(self, pos, groups):

        super().__init__(groups)
        # Search for a sheet file in either graphics/tree or graphics/trees
        sheet_candidates = glob('graphics/tree/*sheet*.png') + glob('graphics/tree/*Sheet*.png') + glob('graphics/trees/*sheet*.png') + glob('graphics/trees/*Sheet*.png')

        frames = []
        sheet_path = None
        if sheet_candidates:
            sheet_path = sheet_candidates[0]
            # If cached, reuse
            if sheet_path in Trees._frames_cache:
                frames = Trees._frames_cache[sheet_path]
            else:
                try:
                    sheet = pygame.image.load(sheet_path).convert_alpha()
                    sheet_w, sheet_h = sheet.get_size()

                    # Prefer explicit 4x4 splitting (sheet is 4 columns x 4 rows -> 16 frames)
                    used = False
                    if sheet_w % 4 == 0 and sheet_h % 4 == 0:
                        frame_w = sheet_w // 4
                        frame_h = sheet_h // 4
                        tmp = []
                        for r in range(4):
                            for c in range(4):
                                    rect = pygame.Rect(c * frame_w, r * frame_h, frame_w, frame_h)
                                    frame = sheet.subsurface(rect).copy()
                                    # preserve alpha if present and use top-left pixel as colorkey fallback
                                    try:
                                        frame = frame.convert_alpha()
                                        bg = frame.get_at((0, 0))[:3]
                                    except Exception:
                                        bg = None
                                    frame = pygame.transform.scale(frame, (settings.TILE_SIZE, settings.TILE_SIZE))
                                    if bg is not None:
                                        frame.set_colorkey(bg)
                                    tmp.append(frame)
                        if len(tmp) >= 16:
                            frames = tmp[:16]
                            Trees._frames_cache[sheet_path] = frames
                            used = True
                    # Fallback to other layouts if exact 4x4 didn't match
                    if not used:
                        candidate_layouts = [(1,16),(2,8),(8,2),(16,1)]
                        for rows, cols in candidate_layouts:
                            if sheet_w % cols == 0 and sheet_h % rows == 0:
                                frame_w = sheet_w // cols
                                frame_h = sheet_h // rows
                                # collect frames in row-major order
                                tmp = []
                                for r in range(rows):
                                    for c in range(cols):
                                        rect = pygame.Rect(c * frame_w, r * frame_h, frame_w, frame_h)
                                        frame = sheet.subsurface(rect).copy()
                                        frame = pygame.transform.scale(frame, (settings.TILE_SIZE, settings.TILE_SIZE))
                                        tmp.append(frame)
                                if len(tmp) >= 16:
                                    frames = tmp[:16]
                                    Trees._frames_cache[sheet_path] = frames
                                    used = True
                                    break
                    if not used:
                        # Fallback: try to split into square frames using sheet height
                        frame_size = sheet_h if sheet_h > 0 else settings.TILE_SIZE
                        cols = max(1, sheet_w // frame_size)
                        tmp = []
                        for col in range(cols):
                            rect = pygame.Rect(col * frame_size, 0, frame_size, frame_size)
                            if rect.right <= sheet_w:
                                frame = sheet.subsurface(rect).copy()
                                try:
                                    frame = frame.convert_alpha()
                                    bg = frame.get_at((0, 0))[:3]
                                except Exception:
                                    bg = None
                                frame = pygame.transform.scale(frame, (settings.TILE_SIZE, settings.TILE_SIZE))
                                if bg is not None:
                                    frame.set_colorkey(bg)
                                tmp.append(frame)
                        if tmp:
                            frames = tmp
                            Trees._frames_cache[sheet_path] = frames
                except Exception:
                    frames = []

        # If still no frames, fallback to individual images
        if not frames:
            image_files = glob('graphics/tree/*.png') + glob('graphics/trees/*.png')
            if image_files:
                try:
                    imgs = []
                    for img_path in image_files:
                        try:
                            img = pygame.image.load(img_path)
                            img = img.convert_alpha()
                            bg = img.get_at((0, 0))[:3]
                        except Exception:
                            img = None
                            bg = None
                        if img is not None:
                            img = pygame.transform.scale(img, (settings.TILE_SIZE, settings.TILE_SIZE))
                            if bg is not None:
                                img.set_colorkey(bg)
                            imgs.append(img)
                    if imgs:
                        frames = imgs
                except Exception:
                    frames = []

        if frames:
            # pick one frame for this tree
            self.image = random.choice(frames)
        else:
            # Fallback placeholder (visible but distinct, semi-transparent)
            self.image = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA)
            self.image.fill((34, 139, 34, 180))

        self.rect = self.image.get_rect(topleft=pos)
