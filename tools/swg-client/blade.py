"""Generate SWG lightsaber blade textures (lightsaberblade_a..d.dds).

The blade pixel shader (pixel_program/e_h_lightsaberblade*.psh) does, with additive blending:
    color = saturate(tex.rgb * crystalColor + tex.a)
so RGB = glow that takes the crystal's color, alpha = white-hot core. Textures must stay grayscale.
Layout matches the stock textures: tip at the left (x=0), hilt end at the right, blade centered vertically.
"""
import numpy as np
from PIL import Image

W, H = 1024, 256
YC = 126.0                 # stock center row is ~31.5 of 64

def smooth_noise(n, seed, knots=12):
    rng = np.random.default_rng(seed)
    k = rng.standard_normal(knots + 3)
    x = np.linspace(0, knots, n)
    i = np.floor(x).astype(int); t = x - i
    t = t * t * (3 - 2 * t)
    return k[i] * (1 - t) + k[i + 1] * t

def capsule_distance(xs, ys, tip_x):
    """Distance from each pixel to the blade's center line, with a rounded tip at tip_x."""
    dx = np.clip(tip_x - xs, 0, None)
    return np.sqrt(dx ** 2 + (ys - YC) ** 2)

def frame(seed, core_half=8.0, core_peak=235, inner=17.0, outer=38.0):
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    wobble = 1.0 + 0.04 * smooth_noise(W, seed)[None, :]           # shimmer along the length
    pulse = 1.0 + 0.03 * np.random.default_rng(seed + 99).standard_normal()  # whole-blade flicker

    # white-hot core: flat-topped with a crisp but anti-aliased edge
    dc = capsule_distance(xs, ys, tip_x=64.0) / (core_half * (1 + 0.5 * (wobble - 1)))
    core = core_peak / 255.0 * np.exp(-(dc ** 6))

    # glow: tight bright inner layer + soft wide halo, extending a little past the core's tip
    dg = capsule_distance(xs, ys, tip_x=60.0)
    glow = (1.00 * np.exp(-0.5 * (dg / inner) ** 2) + 0.45 * np.exp(-0.5 * (dg / outer) ** 2)) * wobble * pulse

    # keep everything inside the texture: fade to zero at the top/bottom/tip edges
    edge = np.clip(np.minimum(ys, H - 1 - ys) / 12.0, 0, 1) * np.clip(xs / 8.0, 0, 1) ** 2
    # soften the hilt end slightly so the emitter seam isn't a hard line (stock does the same)
    base = 1.0 - 0.3 * np.clip((xs - (W - 24)) / 24.0, 0, 1)
    glow = np.clip(glow * edge * base, 0, 0.97)
    core = np.clip(core * edge * base, 0, 1)

    g = (glow * 255).round().astype(np.uint8)
    a = (core * 255).round().astype(np.uint8)
    return Image.merge('RGBA', [Image.fromarray(g)] * 3 + [Image.fromarray(a)])

def frames():
    return {s: frame(seed) for s, seed in zip('abcd', (11, 23, 37, 53))}
