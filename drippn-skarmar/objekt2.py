#!/usr/bin/env python3
"""Version 2 (Emanuel 21/9: ljus beige bakgrund, AI-bilder med riktiga skuggor).

Varje rätt är genererad på vit yta med hård blixt och en riktig skugga.
  _ai/vit/<namn>.png   bilden på vitt
  _ai/mask/<namn>.png  samma bild frilagd av Higgsfield (alfat = själva rätten)
Ut: assets/a-<namn>.webp där rätten är helt täckande och skuggan ligger kvar som
halvgenomskinligt mörker. Då faller skuggan rätt på vilken ljus yta som helst,
utan CSS-filter och utan blandningslägen (Tizen).
"""
import sys, os, glob
import numpy as np
from PIL import Image, ImageFilter

SKUGGFARG = (38, 24, 10)   # varm mörkbrun, inte ren svart, så den gifter sig med beige

def gor(namn, maxsida=1400):
    vit = Image.open(f"_ai/vit/{namn}.png").convert("RGB")
    mask = Image.open(f"_ai/mask/{namn}.png").convert("RGBA").split()[3]
    if mask.size != vit.size: mask = mask.resize(vit.size, Image.LANCZOS)
    m = np.asarray(mask, dtype=np.float32) / 255.0
    rgb = np.asarray(vit, dtype=np.float32)
    lum = rgb.min(axis=2)                                   # mörkaste kanalen: vitt = 255
    sk = np.clip((246.0 - lum) / 246.0, 0, 1)               # 0 på vitt, upp mot 1 i kärnskuggan
    sk = np.clip(sk * 1.05, 0, 0.62)                        # skuggan får aldrig bli kolsvart
    sk = np.asarray(Image.fromarray((sk * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), dtype=np.float32) / 255.0
    sk = sk * (1 - m)                                       # bara utanför rätten
    a = m + sk * (1 - m)
    ut = np.zeros(rgb.shape[:2] + (4,), dtype=np.float32)
    for c in range(3):
        ut[..., c] = (rgb[..., c] * m + SKUGGFARG[c] * sk * (1 - m)) / np.maximum(a, 1e-4)
    ut[..., 3] = a * 255
    bild = Image.fromarray(np.clip(ut, 0, 255).astype(np.uint8), "RGBA")
    al = bild.split()[3].point(lambda v: 0 if v < 8 else v); bild.putalpha(al)
    bild = bild.crop(bild.getbbox())
    if max(bild.size) > maxsida:
        k = maxsida / max(bild.size); bild = bild.resize((int(bild.width * k), int(bild.height * k)), Image.LANCZOS)
    bild.save(f"assets/a-{namn}.webp", quality=90, method=6)
    # var ligger själva rätten i den beskurna bilden? behövs för att centrera på rätten, inte på rätt+skugga
    mm = Image.fromarray((m * 255).astype(np.uint8)).crop(Image.fromarray((ut[..., 3]).astype(np.uint8)).point(lambda v: 0 if v < 8 else v).getbbox())
    bb = mm.point(lambda v: 255 if v > 128 else 0).getbbox(); W, H = mm.size
    return bild.size, [round(bb[0] / W, 4), round(bb[1] / H, 4), round(bb[2] / W, 4), round(bb[3] / H, 4)]

if __name__ == "__main__":
    import json
    namn = sys.argv[1:] or [os.path.basename(p)[:-4] for p in sorted(glob.glob("_ai/mask/*.png"))]
    fil = "assets/a-matt.json"; matt = json.load(open(fil)) if os.path.exists(fil) else {}
    for n in namn:
        s, bb = gor(n); matt[n] = {"w": s[0], "h": s[1], "ratt": bb}; print(n, s, bb)
    json.dump(matt, open(fil, "w"), indent=1)
