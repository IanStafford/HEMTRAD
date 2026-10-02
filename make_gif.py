"""Assemble plot_posVd.py frames into a GIF.

usage: python3 make_gif.py frames_dir out.gif [ms_per_frame [hold_last_ms]]
Frames are named Vd_<v>.png and sorted by Vd. Uses one shared palette for all
frames (the surfaces share a colour scale, so this avoids frame-to-frame
dithering flicker). The last frame is held longer before the loop restarts.
"""
import glob
import os
import sys

from PIL import Image

src, out = sys.argv[1], sys.argv[2]
ms = int(sys.argv[3]) if len(sys.argv) > 3 else 350
hold = int(sys.argv[4]) if len(sys.argv) > 4 else 2000

files = sorted(glob.glob(os.path.join(src, "Vd_*.png")),
               key=lambda f: float(os.path.basename(f)[3:-4]))
frames = [Image.open(f).convert("RGB") for f in files]
pal = frames[-1].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
q[0].save(out, save_all=True, append_images=q[1:], loop=0, optimize=True,
          duration=[ms] * (len(q) - 1) + [hold])
print(f"{len(q)} frames ({files[0]} … {files[-1]}) -> {out}, {os.path.getsize(out) / 1e6:.1f} MB")
