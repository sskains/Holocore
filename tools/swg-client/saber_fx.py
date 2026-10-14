"""Generate lightsaber effect textures: hit spark (pt_lightsaber_spark.dds) and swing trail (sw_light_saber_add.dds).
Both are drawn additively (effect/e_particle_emisadd_2x.eft), grayscale; colors come from the particle/swoosh files."""
import numpy as np
from PIL import Image

def spark(n=256, seed=5):
    ys, xs = np.mgrid[0:n, 0:n].astype(float)
    c = (n - 1) / 2; dx, dy = xs - c, ys - c
    r = np.hypot(dx, dy) / (n / 2); ang = np.arctan2(dy, dx)
    hot = np.exp(-(r / 0.035) ** 2)                       # white-hot pinpoint
    halo = 0.55 * np.exp(-(r / 0.22) ** 2)                # soft bloom around it
    rays = np.zeros_like(r)
    rng = np.random.default_rng(seed)
    for k, a0 in enumerate(np.linspace(0, np.pi, 4, endpoint=False) + 0.2):   # 8 rays (4 lines through center)
        width = 0.010 if k % 2 == 0 else 0.006
        length = 0.95 if k % 2 == 0 else 0.6
        d = np.abs(np.sin(ang - a0)) * r                     # distance to the ray line
        rays += (0.9 if k % 2 == 0 else 0.5) * np.exp(-(d / width) ** 2) * np.clip(1 - r / length, 0, 1) ** 1.5
    rgb = np.clip(hot + 0.6 * halo + rays, 0, 1)
    alpha = np.clip(0.9 * np.exp(-(r / 0.30) ** 2) + 0.5 * rays + hot, 0, 1)
    edge = np.clip((1 - r) / 0.08, 0, 1)                   # nothing touches the image border
    rgb *= edge; alpha *= edge
    g = Image.fromarray((rgb * 255).astype(np.uint8)); a = Image.fromarray((alpha * 255).astype(np.uint8))
    return Image.merge('RGBA', (g, g, g, a))

def trail(n=256, seed=7):
    xs = np.linspace(0, 1, n)
    rng = np.random.default_rng(seed)
    ridge = np.exp(-0.5 * ((xs - 0.56) / 0.13) ** 2)        # bright band (stock peaks slightly right of center)
    soft = 0.35 * np.exp(-0.5 * ((xs - 0.5) / 0.30) ** 2)
    streaks = np.convolve(rng.standard_normal(n), np.ones(3) / 3, 'same') * 0.06   # fine motion streaks
    a = np.clip(ridge + soft + streaks * ridge, 0, 1)
    a *= np.clip(np.minimum(xs, 1 - xs) / 0.06, 0, 1)        # fade the ribbon's edges
    alpha = np.tile((a * 255).astype(np.uint8), (n, 1))
    white = np.full((n, n), 255, np.uint8)
    return Image.merge('RGBA', [Image.fromarray(white)] * 3 + [Image.fromarray(alpha)])
