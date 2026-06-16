"""Core helpers for reading/writing Medieval-Conquest tilemap layers and
rendering a faithful pixel preview from the real tileset PNGs.

Godot 4 TileMapLayer.tile_map_data format (little-endian):
  [uint16 format=0][ per cell: int16 x, int16 y, uint16 src, uint16 atlas_x,
                    uint16 atlas_y, uint16 alt ]  (12 bytes/cell)
Cell tuple used here: (x, y, src, ax, ay, alt)
"""
import base64, struct, re, os
from PIL import Image

ROOT = r"C:\Users\ninomarcos\Documents\gamedev\Medieval-Conquest"
MAIN = os.path.join(ROOT, "Scenes", "Main", "main.tscn")
SHEETS_DIR = os.path.join(ROOT, "TileSetCastle")
TILE = 16

# Which source PNG each layer's TileSetAtlasSource points at, by layer name.
LAYER_SHEET = {"Walls": "walls.png", "Ground": "ground.png"}


def decode_layer(b64):
    raw = base64.b64decode(b64)
    cells = []
    off = 2
    while off + 12 <= len(raw):
        x, y = struct.unpack_from("<hh", raw, off)
        src, ax, ay, alt = struct.unpack_from("<HHHH", raw, off + 4)
        cells.append((x, y, src, ax, ay, alt))
        off += 12
    return cells


def encode_layer(cells):
    out = bytearray(struct.pack("<H", 0))
    # Godot writes cells sorted; sort by (y, x) for stable, clean diffs.
    for x, y, src, ax, ay, alt in sorted(cells, key=lambda c: (c[1], c[0])):
        out += struct.pack("<hh", x, y)
        out += struct.pack("<HHHH", src, ax, ay, alt)
    return base64.b64encode(bytes(out)).decode("ascii")


def read_main_layers(path=MAIN):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    layers = {}
    for name in LAYER_SHEET:
        m = re.search(
            r'\[node name="%s".*?tile_map_data = PackedByteArray\("([^"]+)"\)' % name,
            text, re.S)
        layers[name] = decode_layer(m.group(1)) if m else []
    return text, layers


def write_main_layers(layers, path=MAIN):
    """Replace the tile_map_data PackedByteArray for each named layer in-place."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for name, cells in layers.items():
        b64 = encode_layer(cells)
        text = re.sub(
            r'(\[node name="%s".*?tile_map_data = PackedByteArray\(")[^"]+("\))' % name,
            lambda m: m.group(1) + b64 + m.group(2),
            text, count=1, flags=re.S)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


_sheet_cache = {}
def sheet(png):
    if png not in _sheet_cache:
        _sheet_cache[png] = Image.open(os.path.join(SHEETS_DIR, png)).convert("RGBA")
    return _sheet_cache[png]


def composite(layers_in_order, out_path, bg=(20, 16, 22, 255), grid=False,
              bounds=None):
    """layers_in_order: list of (sheet_png, cells) drawn back-to-front."""
    all_cells = [c for _, cells in layers_in_order for c in cells]
    if not all_cells:
        raise ValueError("no cells")
    if bounds is None:
        xs = [c[0] for c in all_cells]; ys = [c[1] for c in all_cells]
        minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    else:
        minx, miny, maxx, maxy = bounds
    W = (maxx - minx + 1) * TILE
    H = (maxy - miny + 1) * TILE
    img = Image.new("RGBA", (W, H), bg)
    for png, cells in layers_in_order:
        sh = sheet(png)
        for x, y, src, ax, ay, alt in cells:
            tile = sh.crop((ax * TILE, ay * TILE, ax * TILE + TILE, ay * TILE + TILE))
            img.alpha_composite(tile, ((x - minx) * TILE, (y - miny) * TILE))
    if grid:
        from PIL import ImageDraw
        d = ImageDraw.Draw(img)
        for gx in range(0, W, TILE):
            d.line([(gx, 0), (gx, H)], fill=(255, 255, 255, 30))
        for gy in range(0, H, TILE):
            d.line([(0, gy), (W, gy)], fill=(255, 255, 255, 30))
    img.save(out_path)
    return img.size, (minx, miny, maxx, maxy)


if __name__ == "__main__":
    text, layers = read_main_layers()
    out = os.path.join(ROOT, "MapTools", "preview", "current_map.png")
    size, bnds = composite(
        [("walls.png", layers["Walls"]), ("ground.png", layers["Ground"])], out)
    print("Walls cells:", len(layers["Walls"]), " Ground cells:", len(layers["Ground"]))
    print("preview size px:", size, " tile-bounds (minx,miny,maxx,maxy):", bnds)
    print("saved:", out)
