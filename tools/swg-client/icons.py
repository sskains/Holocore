"""Replace SWG UI icons with higher-resolution art in a new atlas, rewiring ui_styles.inc.

Every ImageStyle anywhere in ui_styles.inc whose (Source, SourceRect) matches a replaced cell is
pointed at the new atlas, so all namespaces that reuse an icon (command, jedi, space...) update together.
"""
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CELL = 128; GRID = 8; ATLAS = CELL * GRID   # 64 icons at 128x128 in one 1024x1024 texture

def rounded_mask(size=CELL, radius_frac=0.085):
    """Rounded-corner alpha like the stock icons (they cut ~4px corners at 48px)."""
    big = size * 4
    m = Image.new('L', (big, big), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, big - 1, big - 1), radius=int(big * radius_frac), fill=255)
    return m.resize((size, size), Image.LANCZOS)

def build_atlas(icon_images):
    """icon_images: list of RGB/RGBA PIL images (any size), in slot order. Returns (atlas, rects)."""
    atlas = Image.new('RGBA', (ATLAS, ATLAS), (0, 0, 0, 0))
    mask = rounded_mask(); rects = []
    for i, im in enumerate(icon_images):
        r, c = divmod(i, GRID)
        tile = im.convert('RGB').resize((CELL, CELL), Image.LANCZOS)
        tile = Image.merge('RGBA', (*tile.split(), mask))
        atlas.paste(tile, (c * CELL, r * CELL))
        x0, y0 = c * CELL, r * CELL
        rects.append(f'{x0},{y0},{x0 + CELL - 1},{y0 + CELL - 1}')   # inclusive, like the stock rects
    return atlas, rects

def rewire(styles_text, replacements, new_source):
    """replacements: {(old_source, old_rect): new_rect}. Returns (new_text, count)."""
    tag = re.compile(r"<ImageStyle\b[^>]*?/?>", re.S)
    count = 0
    def fix(m):
        nonlocal count
        t = m.group(0)
        src = re.search(r"Source='([^']*)'", t); rect = re.search(r"SourceRect='([^']*)'", t)
        if not src or not rect: return t
        key = (src.group(1), rect.group(1).replace(' ', ''))
        if key not in replacements: return t
        count += 1
        t = t.replace(src.group(0), f"Source='{new_source}'")
        return t.replace(rect.group(0), f"SourceRect='{replacements[key]}'")
    return tag.sub(fix, styles_text), count
