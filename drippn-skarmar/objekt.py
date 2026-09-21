#!/usr/bin/env python3
"""Gör färdiga skärmobjekt av Dripp'ns riktiga Qopla-foton.

_frilagt/*.png är Higgsfields friläggningar. Här:
  - tre foton finns i 6400 px hos Qopla men frilades i 1280 px: masken skalas upp
    och läggs på originalet, så burgaren blir skarp även i helskärm
  - burgarnas pommes är avklippta i bildkanten: alfat tonas ut mot sidorna
  - skålarnas handtag är avklippt i vänsterkanten: tonas bort
  - allt beskärs till motivet och sparas som webp med alfa
"""
import sys, os
from PIL import Image, ImageFilter, ImageChops
import numpy as np

HOGUPP = {"cheese": "qopla/original/drippn-cheese.jpg", "vegan": "qopla/original/drippn-vegan.jpg",
          "dirty-fries": "qopla/original/dirty-fries.jpg"}
BURGARE = ["special", "original", "cheese", "tryffel", "hot-chilli", "bbq", "chipotle",
           "crispy-chicken", "halloumi", "vegan", "tropical", "combo"]
HANDTAG = ["hot-wings", "lokringar", "pommes", "sotpotatis", "nuggets", "mozzarella"]

def tona_sidor(a, andel):
    """Alfa 0 i ytterkant till 1 efter `andel` av bredden, på båda sidor."""
    w, h = a.size
    x = np.arange(w) / w
    ramp = np.clip(np.minimum(x, 1 - x) / andel, 0, 1)
    ramp = ramp * ramp * (3 - 2 * ramp)
    al = np.asarray(a.split()[3], dtype=np.float32) * ramp[None, :]
    a.putalpha(Image.fromarray(al.astype(np.uint8)))
    return a

def tona_vanster(a, andel):
    w, h = a.size
    x = np.arange(w) / w
    ramp = np.clip((x - 0.02) / andel, 0, 1)
    al = np.asarray(a.split()[3], dtype=np.float32) * ramp[None, :]
    a.putalpha(Image.fromarray(al.astype(np.uint8)))
    return a

def gor(namn, maxsida=1500):
    a = Image.open(f"_frilagt/{namn}.png").convert("RGBA")
    if namn in HOGUPP:
        o = Image.open(HOGUPP[namn]).convert("RGB")
        skala = 3200 / o.width
        o = o.resize((3200, int(o.height * skala)), Image.LANCZOS)
        m = a.split()[3].resize(o.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
        a = o.convert("RGBA"); a.putalpha(m)
        if namn in BURGARE:
            # vidvinkelbilderna: burgaren är liten och pommesen breder ut sig, skär in mot burgaren
            bb = a.getbbox(); bw = bb[2] - bb[0]
            a = a.crop((bb[0] + int(bw * 0.24), 0, bb[2] - int(bw * 0.24), a.height))
    if namn in BURGARE and namn not in ("tropical", "combo"):
        a = tona_sidor(a, 0.16)
    if namn in HANDTAG:
        bb = a.getbbox()
        if bb and bb[0] <= 2:
            a = tona_vanster(a, 0.10)
    # städa svagt alfaskräp
    al = a.split()[3].point(lambda v: 0 if v < 10 else v)
    a.putalpha(al)
    bb = a.getbbox(); a = a.crop(bb)
    if max(a.size) > maxsida:
        k = maxsida / max(a.size); a = a.resize((int(a.width * k), int(a.height * k)), Image.LANCZOS)
    a.save(f"assets/o-{namn}.webp", quality=90, method=6)
    return a.size

if __name__ == "__main__":
    namn = sys.argv[1:] or [os.path.basename(p)[:-4] for p in sorted(__import__("glob").glob("_frilagt/*.png"))]
    for n in namn:
        print(n, gor(n))
