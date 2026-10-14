"""Brighten dim lightsaber crystal colors in palette/wp_lightsaber.pal (RIFF PAL, 32 RGBx entries).
The blade glow is additive, so dark palette colors barely show in daylight. Each color keeps its hue;
dim ones rise a lot, bright ones barely (new max channel = max(old, 150 + 0.45 * old))."""
import sys

def brighten(src, dst):
    d = bytearray(open(src, 'rb').read())
    count = int.from_bytes(d[22:24], 'little')
    for i in range(count):
        o = 24 + 4 * i; rgb = d[o:o + 3]; m = max(rgb)
        if m == 0: continue
        s = max(m, round(150 + 0.45 * m)) / m
        d[o:o + 3] = bytes(min(255, round(c * s)) for c in rgb)
    open(dst, 'wb').write(d)

if __name__ == '__main__':
    brighten(sys.argv[1], sys.argv[2])
