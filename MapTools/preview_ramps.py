"""Overlay the generated stair ramps (+ king spawn / winner zone) on the real map
so we can confirm alignment before writing collision into the scene."""
import os
from PIL import Image, ImageDraw
import maptools as mt
import generate_boxes as gb

def main():
    d = gb.generate()
    layers = [("walls.png", d["back"]), ("walls.png", d["walls"]),
              ("ground.png", d["ground"])]
    cells = [c for _, cs in layers for c in cs]
    xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    bnds = (min(xs), min(ys), max(xs), max(ys))
    mt.composite(layers, "preview/ramps.tmp.png", bg=(14, 11, 16, 255), bounds=bnds)
    img = Image.open("preview/ramps.tmp.png").convert("RGBA")
    dr = ImageDraw.Draw(img)
    ox, oy = bnds[0] * 16, bnds[1] * 16
    for (x0, y0, x1, y1) in d["ramps"]:
        dr.line([(x0 - ox, y0 - oy), (x1 - ox, y1 - oy)], fill=(0, 255, 80, 255), width=3)
        dr.ellipse([x0 - ox - 4, y0 - oy - 4, x0 - ox + 4, y0 - oy + 4], outline=(0, 255, 80))
        dr.ellipse([x1 - ox - 4, y1 - oy - 4, x1 - ox + 4, y1 - oy + 4], outline=(0, 255, 80))
    # king spawn
    kx, kfy = d["king"]
    px, py = kx * 16 + 8 - ox, kfy * 16 - oy
    dr.ellipse([px - 6, py - 6, px + 6, py + 6], outline=(80, 160, 255), width=3)
    # winner zone
    w = d["winner"]
    dr.rectangle([w["ix"] * 16 - ox, w["iy"] * 16 - oy,
                  (w["ix"] + w["iw"]) * 16 - ox, (w["iy"] + w["ih"]) * 16 - oy],
                 outline=(255, 80, 220), width=3)
    img.convert("RGB").save("preview/ramps.png")
    os.remove("preview/ramps.tmp.png")
    print("ramps:", d["ramps"])
    print("king:", d["king"], "winner:", d["winner"])
    print("map tile bounds:", bnds, "-> px width", (bnds[2] - bnds[0] + 1) * 16)
    print("saved preview/ramps.png", img.size)

if __name__ == "__main__":
    main()
