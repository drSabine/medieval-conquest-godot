"""Render a tileset sheet magnified with a coordinate grid + rulers so we can
identify exactly which (col,row) atlas tiles form walls, edges, corners, doors."""
import sys, os
from PIL import Image, ImageDraw
import maptools as mt

TILE = 16

def view(png, scale=4, out=None):
    im = Image.open(os.path.join(mt.SHEETS_DIR, png)).convert("RGBA")
    cols, rows = im.size[0] // TILE, im.size[1] // TILE
    pad = 22
    big = im.resize((im.size[0] * scale, im.size[1] * scale), Image.NEAREST)
    canvas = Image.new("RGBA", (big.size[0] + pad, big.size[1] + pad), (12, 12, 16, 255))
    canvas.alpha_composite(big, (pad, pad))
    d = ImageDraw.Draw(canvas)
    for c in range(cols + 1):
        x = pad + c * TILE * scale
        d.line([(x, pad), (x, pad + big.size[1])], fill=(0, 255, 0, 90))
        if c < cols and c % 1 == 0:
            d.text((x + 2, 4), str(c), fill=(0, 255, 0, 255))
    for r in range(rows + 1):
        y = pad + r * TILE * scale
        d.line([(pad, y), (pad + big.size[0], y)], fill=(0, 255, 0, 90))
        if r < rows:
            d.text((2, y + 2), str(r), fill=(0, 255, 0, 255))
    out = out or os.path.join(mt.ROOT, "MapTools", "preview", "atlas_" + png.replace(".png", "") + ".png")
    canvas.save(out)
    print(f"{png}: {cols}x{rows} tiles -> {out}")

if __name__ == "__main__":
    for png in sys.argv[1:] or ["walls.png", "walls_side_top.png", "env_objects.png"]:
        view(png)
