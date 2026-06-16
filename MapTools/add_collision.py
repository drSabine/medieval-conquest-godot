"""Add physics collision to the chamber tiles in main.tscn (idempotent).

What gets a solid 16x16 collision box:
  - Ground atlas (floors / stairs / bridges)  -> ALL registered tiles (walkable, solid)
  - Walls atlas, DARK border tiles only        -> ax in {14,15,16}, ay in {9,10,11}
The LIT interior tiles (ax 20-25, ay 9-14) stay collision-free so the player can
stand inside each room. Both TileSets get physics_layer_0 on collision_layer 1
(matches the actors' default layer/mask).

Re-run after build_scene.py if the TileSet sub-resources are ever regenerated.
"""
import re
import maptools as mt

BOX = "PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)"

# which atlas SubResource id maps to which collision rule
WALLS_ATLAS = "TileSetAtlasSource_y3v7k"   # walls.png  -> only dark border
GROUND_ATLAS = "TileSetAtlasSource_2a143"  # ground.png -> everything
TILESETS = ("TileSet_hryqi", "TileSet_xlvfx")

def dark(ax, ay):
    return ax in (14, 15, 16) and ay in (9, 10, 11)

def main():
    with open(mt.MAIN, encoding="utf-8") as f:
        lines = f.read().split("\n")

    out = []
    cur_atlas = None          # which atlas block we're inside
    tile_re = re.compile(r"^(\d+):(\d+)/0 = 0$")
    added = 0
    for ln in lines:
        m = re.match(r'^\[sub_resource type="(\w+)" id="([^"]+)"\]$', ln)
        if m:
            cur_atlas = m.group(2) if m.group(1) == "TileSetAtlasSource" else None
            out.append(ln)
            # give each TileSet a physics layer (idempotent)
            if m.group(1) == "TileSet" and m.group(2) in TILESETS:
                # peek: only add if not already present later in this block
                out.append("physics_layer_0/collision_layer = 1")
            continue

        out.append(ln)
        tm = tile_re.match(ln)
        if tm and cur_atlas in (WALLS_ATLAS, GROUND_ATLAS):
            ax, ay = int(tm.group(1)), int(tm.group(2))
            want = (cur_atlas == GROUND_ATLAS) or (cur_atlas == WALLS_ATLAS and dark(ax, ay))
            if want:
                out.append(f"{ax}:{ay}/0/physics_layer_0/polygon_0/points = {BOX}")
                added += 1

    text = "\n".join(out)
    # idempotency: collapse any duplicate physics_layer / polygon lines created by a re-run
    text = re.sub(r"(physics_layer_0/collision_layer = 1\n)(?:physics_layer_0/collision_layer = 1\n)+",
                  r"\1", text)
    text = re.sub(r"(/0/physics_layer_0/polygon_0/points = [^\n]+\n)(?:\1)+", r"\1", text)

    with open(mt.MAIN, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"added {added} tile collision polygons; physics_layer_0 on {TILESETS}")

if __name__ == "__main__":
    main()
