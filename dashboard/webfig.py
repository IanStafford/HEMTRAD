"""Make web-sized copies of figures for the work-log dashboard.

usage (from the repo root): python3 dashboard/webfig.py figures/a.png figures/b.png ...
Writes dashboard/fig/<name>.jpg (max 1600 px wide, JPEG q86; '+' dropped from
names). GIFs are copied unchanged. Prints each output path for the page's src=.
"""
import os
import shutil
import sys

from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
os.makedirs(OUT, exist_ok=True)
for f in sys.argv[1:]:
    base = os.path.basename(f).replace("+", "")
    if f.lower().endswith(".gif"):
        dst = os.path.join(OUT, base)
        shutil.copy(f, dst)
    else:
        im = Image.open(f).convert("RGB")
        if im.width > 1600:
            im = im.resize((1600, int(im.height * 1600 / im.width)), Image.LANCZOS)
        dst = os.path.join(OUT, base.rsplit(".", 1)[0] + ".jpg")
        im.save(dst, quality=86, optimize=True)
    print(f"fig/{os.path.basename(dst)}  {os.path.getsize(dst) / 1e3:.0f} kB")
