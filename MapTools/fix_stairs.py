"""Replace the 3 tangled stair systems with one clean ramp body.

  - strip solid tile collision from stair tiles (keep it only on floor caps, ay==1)
  - delete the legacy StairCollisions / StairZones / WorldBounds nodes
  - delete the now-unused stair_zone ext_resource
  - add a StairRamps StaticBody2D (layer 1) with one sloped CollisionPolygon2D per
    staircase, generated to match the real stairs (see preview/ramps.png)
"""
import re
import maptools as mt
import generate_boxes as gb

GROUND_ATLAS = "TileSetAtlasSource_2a143"
THICK = 140  # ramp body thickness (px) below the walking line

def main():
    d = gb.generate()
    with open(mt.MAIN, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")

    # 1) strip collision polygons from ground tiles that are NOT floor caps (ay != 1)
    out = []
    cur_atlas = None
    poly_re = re.compile(r"^(\d+):(\d+)/0/physics_layer_0/polygon_0/points")
    head_re = re.compile(r'^\[sub_resource type="(\w+)" id="([^"]+)"\]$')
    removed = 0
    for ln in lines:
        h = head_re.match(ln)
        if h:
            cur_atlas = h.group(2) if h.group(1) == "TileSetAtlasSource" else None
        if cur_atlas == GROUND_ATLAS:
            p = poly_re.match(ln)
            if p and int(p.group(2)) != 1:
                removed += 1
                continue
        out.append(ln)
    text = "\n".join(out)

    # 2) delete legacy stair/bounds nodes (contiguous block before Decor)
    text = re.sub(
        r'\[node name="StairCollisions".*?(?=\[node name="Decor")',
        "", text, count=1, flags=re.S)

    # 3) drop the stair_zone ext_resource
    text = re.sub(r'^\[ext_resource[^\n]*stair_zone\.gd"[^\n]*\]\n', "", text, flags=re.M)

    # 4) build StairRamps node block
    blk = ['[node name="StairRamps" type="StaticBody2D" parent="TileLayers"]\n']
    for i, (x0, y0, x1, y1) in enumerate(d["ramps"], 1):
        poly = f"PackedVector2Array({x0}, {y0}, {x1}, {y1}, {x1}, {y1 + THICK}, {x0}, {y0 + THICK})"
        blk.append(f'\n[node name="Ramp{i}" type="CollisionPolygon2D" parent="TileLayers/StairRamps"]\n'
                   f'polygon = {poly}\n')
    ramps_block = "".join(blk) + "\n"
    # insert right before Decor
    text = text.replace('[node name="Decor"', ramps_block + '[node name="Decor"', 1)

    with open(mt.MAIN, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"stripped {removed} stair-tile collisions; added {len(d['ramps'])} ramps")

if __name__ == "__main__":
    main()
