"""Write an uncompressed 32-bit BGRA .dds with a full mipmap chain (DirectX 9 friendly)."""
import struct
from PIL import Image

def save_dds(img: Image.Image, path: str):
    img = img.convert('RGBA'); w, h = img.size
    levels = []; cur = img
    while True:
        levels.append(cur)
        if cur.size == (1, 1): break
        cur = cur.resize((max(1, cur.width // 2), max(1, cur.height // 2)), Image.LANCZOS)
    DDSD = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000 | 0x20000   # caps|height|width|pitch|pixelformat|mipmapcount
    pf = struct.pack('<II4sIIIII', 32, 0x41, b'\0\0\0\0', 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)  # RGB|ALPHAPIXELS, A8R8G8B8
    caps = 0x1000 | 0x8 | 0x400000  # texture|complex|mipmap
    header = struct.pack('<I I I I I I I 44s', 124, DDSD, h, w, w * 4, 0, len(levels), b'\0' * 44) + pf + struct.pack('<IIIII', caps, 0, 0, 0, 0)
    with open(path, 'wb') as f:
        f.write(b'DDS ' + header)
        for lv in levels:
            r, g, b, a = lv.split()
            f.write(Image.merge('RGBA', (b, g, r, a)).tobytes())  # stored as BGRA
