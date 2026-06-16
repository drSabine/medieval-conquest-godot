"""Single source of truth for main.tscn collision. Idempotent - run any time.

Design:
  - FLOORS : ground-atlas floor caps (ay==1) get a solid 16x16 box.
  - WALLS  : the dark chamber-border tiles (ax 14-16, ay 9-11) get a solid box.
  - STAIRS : one physical ramp per staircase. Ramps are one-way collision so an
             upper staircase cannot block the player while climbing below it.
  - GATES  : none. The old hidden trigger/barrier setup could trap the player.
"""
import re
import maptools as mt
import generate_boxes as gb

WALLS_ATLAS = "TileSetAtlasSource_y3v7k"
GROUND_ATLAS = "TileSetAtlasSource_2a143"
TILESETS = ("TileSet_hryqi", "TileSet_xlvfx")
BOX = "PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)"
SIBS = "StairRamps|StairZones|Gates|Decor"
RAMP_THICKNESS = 72


def is_dark_wall(ax, ay):
    return ax in (14, 15, 16) and ay in (9, 10, 11)


def strip_block(text, name):
    """Remove a node and its descendants, stopping at the next sibling block."""
    pat = r'\[node name="%s"[^\n]*\n.*?(?=\[node name="(?:%s)")' % (name, SIBS)
    return re.sub(pat, "", text, flags=re.S)


def strip_subresource(text, resource_id):
    pat = r'\n?\[sub_resource[^\n]*id="%s"[^\n]*\]\n.*?(?=\n\[)' % re.escape(resource_id)
    return re.sub(pat, "\n", text, flags=re.S)


def main():
    d = gb.generate()
    text = open(mt.MAIN, encoding="utf-8").read()

    # 1) per-tile collision: drop every existing physics polygon, re-add wanted ones.
    out, cur = [], None
    reg = re.compile(r"^(\d+):(\d+)/0 = 0$")
    old_poly = re.compile(r"^\d+:\d+/0/physics_layer_0/")
    head = re.compile(r'^\[sub_resource type="(\w+)" id="([^"]+)"\]$')
    for ln in text.split("\n"):
        if old_poly.match(ln):
            continue
        h = head.match(ln)
        if h:
            cur = h.group(2) if h.group(1) == "TileSetAtlasSource" else None
        out.append(ln)
        if cur in (WALLS_ATLAS, GROUND_ATLAS):
            m = reg.match(ln)
            if m:
                ax, ay = int(m.group(1)), int(m.group(2))
                want = (cur == GROUND_ATLAS and ay == 1) or (
                    cur == WALLS_ATLAS and is_dark_wall(ax, ay)
                )
                if want:
                    out.append(f"{ax}:{ay}/0/physics_layer_0/polygon_0/points = {BOX}")
    text = "\n".join(out)

    # 2) ensure each TileSet declares the physics layer.
    for ts in TILESETS:
        text = re.sub(
            r'(\[sub_resource type="TileSet" id="%s"\]\n)(?!physics_layer)' % ts,
            r"\1physics_layer_0/collision_layer = 1\n",
            text,
        )

    # 3) remove legacy stair-zone/gate resources and gate signal connections.
    text = re.sub(r'^\[ext_resource[^\n]*stair_zone\.gd"[^\n]*\]\n+', "", text, flags=re.M)
    text = strip_subresource(text, "RectangleShape2D_gate")
    text = strip_subresource(text, "RectangleShape2D_gatetrig")
    text = re.sub(
        r'^\[connection signal="body_exited" from="Gates/GateTrigger\d+".*\]\n',
        "",
        text,
        flags=re.M,
    )

    # 4) rebuild the generated collision block.
    for nm in ("StairRamps", "StairZones", "Gates"):
        text = strip_block(text, nm)

    ramps = ['[node name="StairRamps" type="StaticBody2D" parent="TileLayers"]\n']
    for i, (x0, y0, x1, y1) in enumerate(d["ramps"], 1):
        poly = (
            f"PackedVector2Array({x0}, {y0}, {x1}, {y1}, "
            f"{x1}, {y1 + RAMP_THICKNESS}, {x0}, {y0 + RAMP_THICKNESS})"
        )
        ramps.append(
            f'\n[node name="Ramp{i}" type="CollisionPolygon2D" parent="TileLayers/StairRamps"]\n'
            f"polygon = {poly}\n"
            "one_way_collision = true\n"
            "one_way_collision_margin = 8.0\n"
        )
    text = text.replace('[node name="Decor"', "".join(ramps) + "\n" + '[node name="Decor"', 1)

    open(mt.MAIN, "w", encoding="utf-8").write(text)
    print(f"collision rebuilt: floors + walls + {len(d['ramps'])} one-way stair ramps; gates removed")


if __name__ == "__main__":
    main()
