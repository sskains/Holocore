"""Modern HUD bar art (grayscale; the UI tints it per stat) + rewiring of the bar styles.

Replaces Styles.mfd.statusbars_small.current (bar fill/back, tiled -> smooth gloss) and
Styles.ham_new.bar (the pill frame each bar sits in). Source rects keep the stock cap widths
(the UI draws caps at their source width and stretches everything to the bar's height).
"""
import re
import numpy as np
from PIL import Image

H = 22                     # 2x the stock 11px slices, for smoother vertical shading
TEX = 64

def _fill_column():
    v = np.zeros(H); a = np.zeros(H)
    for y in range(H):
        t = (y - 2) / (H - 5)                       # 0 at top of body, 1 at bottom
        if y in (0, H - 1): a[y] = 0.0
        elif y in (1, H - 2): a[y] = 0.55
        else: a[y] = 1.0
        body = 0.86 - 0.24 * max(0.0, t)            # gentle darkening downward
        gloss = 0.14 * np.exp(-((y - 4.0) / 2.2) ** 2)   # soft highlight band near the top
        v[y] = min(1.0, body + gloss)
    v[2] = 1.0                                       # crisp top edge highlight
    return v, a

def build_texture():
    img = np.zeros((TEX, TEX, 4))
    fv, fa = _fill_column()
    img[0:H, 0:4, 0:3] = fv[:, None, None]; img[0:H, 0:4, 3] = fa[:, None]      # fill: x0-3

    # frame: translucent dark track with a thin light outline (rows 0-1 and H-2..H-1)
    def frame_px(edge):
        if edge < 1.0: return (0.80, 0.55)       # outline
        if edge < 2.0: return (0.45, 0.35)       # outline falloff
        return (0.05, 0.62)                      # dark interior
    for y in range(H):                           # center slice: x8-9
        e = min(y, H - 1 - y)
        c, al = frame_px(e); img[y, 8:10, 0:3] = c; img[y, 8:10, 3] = al
    W = 7                                        # caps: half-ellipse ends, x16-22 (west) and x24-30 (east)
    for y in range(H):
        for x in range(W):
            ny = (y + 0.5 - H / 2) / (H / 2); nx = (W - x - 0.5) / W        # west cap, curve on the left
            r = np.hypot(nx, ny)
            edge = (1.0 - r) * min(W, H / 2)
            if r > 1.0: continue
            c, al = frame_px(edge); aa = min(1.0, (1.0 - r) * W)
            img[y, 16 + x, 0:3] = c; img[y, 16 + x, 3] = al * aa
            img[y, 24 + (W - 1 - x), 0:3] = c; img[y, 24 + (W - 1 - x), 3] = al * aa   # mirrored east cap
    return Image.fromarray((np.clip(img, 0, 1) * 255).round().astype(np.uint8), 'RGBA')

NEW = {   # style path -> new SourceRect (inclusive)
    'Styles.mfd.statusbars_small.current.c': f'0,0,3,{H-1}',
    'Styles.mfd.statusbars_small.current.e': f'0,0,3,{H-1}',
    'Styles.mfd.statusbars_small.current.w': f'0,0,3,{H-1}',
    'Styles.ham_new.bar.c': f'8,0,9,{H-1}',
    'Styles.ham_new.bar.w': f'16,0,22,{H-1}',
    'Styles.ham_new.bar.e': f'24,0,30,{H-1}',
}

def rewire_styles(text, source_name):
    import uistyles
    edits = []
    for st in uistyles.image_styles(text):
        if st['path'] in NEW:
            tag = text[st['start']:st['end']]
            tag = re.sub(r"Source='[^']*'", f"Source='{source_name}'", tag)
            tag = re.sub(r"SourceRect='[^']*'", f"SourceRect='{NEW[st['path']]}'", tag)
            edits.append((st['start'], st['end'], tag))
    for s, e, t in sorted(edits, reverse=True):
        text = text[:s] + t + text[e:]
    return text, len(edits)

def soften_backs(layout_text, opacity='0.45'):
    """Make the empty part of each bar ('back' pages) translucent so the fill stands out."""
    count = 0
    def fix(m):
        nonlocal count
        t = m.group(0)
        if "Name='back'" in t and 'statusbars_small.current' in t:
            count += 1
            return re.sub(r"BackgroundOpacity='[^']*'", f"BackgroundOpacity='{opacity}'", t)
        return t
    return re.sub(r"<Page\b[^>]*?/>", fix, layout_text, flags=re.S), count
