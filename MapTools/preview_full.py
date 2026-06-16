"""Full preview: tilemap + goblins + torches + candles + king, drawn with the real
sprites, so we can sign off the whole map before touching the scene."""
import os
from PIL import Image
import maptools as mt
import generate_boxes as gb

A = mt.ROOT
def sprite(path, region=None, target_h=None):
    im = Image.open(os.path.join(A, path)).convert("RGBA")
    if region: im = im.crop(region)
    bb = im.getbbox()
    if bb: im = im.crop(bb)
    if target_h:
        sc = target_h / im.size[1]
        im = im.resize((max(1, int(im.size[0] * sc)), target_h), Image.NEAREST)
    return im

def main():
    d = gb.generate()
    layers = [("walls.png", d["back"]), ("walls.png", d["walls"]),
              ("ground.png", d["ground"])]
    all_cells = [c for _, cs in layers for c in cs]
    xs = [c[0] for c in all_cells]; ys = [c[1] for c in all_cells]
    bnds = (min(xs), min(ys), max(xs), max(ys))
    mt.composite(layers, "preview/full.tmp.png", bg=(14, 11, 16, 255), bounds=bnds)
    img = Image.open("preview/full.tmp.png").convert("RGBA")
    minx, miny = bnds[0], bnds[1]
    def place(im, tx, ty, anchor="feet"):
        px = (tx - minx) * 16 + 8 - im.size[0] // 2
        if anchor == "feet":   # bottom of sprite on bottom of tile ty
            py = (ty - miny) * 16 + 16 - im.size[1]
        else:                  # centered on tile
            py = (ty - miny) * 16 + 8 - im.size[1] // 2
        img.alpha_composite(im, (px, py))

    torch = sprite("TileSetCastle/anim_light1.png", (0, 0, 48, 32), target_h=26)
    candle = sprite("TileSetCastle/environment.png", (13 * 16, 12 * 16, 14 * 16, 16 * 16), target_h=40)
    goblin = sprite("Assets/Mobs/Goblin/Idle.png", (0, 0, 150, 150), target_h=46)
    king = sprite("Assets/PlayerAssets/Medieval King Pack 2/Sprites/Idle.png", (0, 0, 160, 111), target_h=58)

    for tx, ty in d["torches"]:
        place(torch, tx, ty, anchor="center")
    for tx, ty in d["candles"]:
        place(candle, tx, ty, anchor="feet")
    for tx, ty in d["goblins"]:
        place(goblin, tx, ty, anchor="feet")
    if d["king"]:
        place(king, d["king"][0], d["king"][1], anchor="feet")

    img.save("preview/full.png"); os.remove("preview/full.tmp.png")
    print("saved preview/full.png size", img.size)

if __name__ == "__main__":
    main()
