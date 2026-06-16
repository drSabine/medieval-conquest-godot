"""Write the boxed-chamber serpentine into main.tscn:
  - Walls layer  = back (lit brick) + walls (dark border)
  - Ground layer = floors + stairs + bridges
  - King repositioned into the Start chamber
  - 6 goblins (one per chamber), torches (Burn1) on walls, candles (Burn2) on floors
Everything is reversible via main.tscn.bak.
"""
import re
import maptools as mt
import generate_boxes as gb

TILE = 16
def px(tx): return tx * TILE + TILE // 2

def main():
    d = gb.generate()
    # layer cells (dedup by coord; last wins)
    def dedup(cells):
        m = {}
        for c in cells:
            m[(c[0], c[1])] = c
        return list(m.values())
    walls_cells = dedup(d["back"] + d["walls"])
    ground_cells = dedup(d["ground"])

    with open(mt.MAIN, encoding="utf-8") as f:
        text = f.read()

    # 1) add torches.tscn ext_resource (after the goblin ext_resource line)
    if "Scenes/Environment/torches.tscn" not in text:
        text = re.sub(
            r'(\[ext_resource type="PackedScene"[^\n]*goblin\.tscn"[^\n]*\]\n)',
            r'\1[ext_resource type="PackedScene" uid="uid://c122p0phwexc3" path="res://Scenes/Environment/torches.tscn" id="6_torch"]\n',
            text, count=1)

    # 2) replace tile_map_data for Walls and Ground
    for name, cells in [("Walls", walls_cells), ("Ground", ground_cells)]:
        b64 = mt.encode_layer(cells)
        text = re.sub(
            r'(\[node name="%s".*?tile_map_data = PackedByteArray\(")[^"]+("\))' % name,
            lambda m: m.group(1) + b64 + m.group(2), text, count=1, flags=re.S)

    # 3) reposition the King into the Start chamber (feet on the floor)
    kx, kfy = d["king"]
    text = re.sub(
        r'(\[node name="MedievalKing"[^\]]*\]\nposition = Vector2\()[^)]+(\))',
        lambda m: m.group(1) + f"{px(kx)}, {kfy*TILE - 51}" + m.group(2), text, count=1)

    # 4) remove the invisible template Goblin node (avoid a phantom enemy)
    text = re.sub(
        r'\n\[node name="Goblin" parent="Actors"[^\]]*\]\nvisible = false\nposition = Vector2\([^)]+\)\n',
        "\n", text, count=1)

    # 5) build Decor (torches+candles) inserted before Actors, and goblins appended
    decor = ['[node name="Decor" type="Node2D" parent="."]\n']
    ti = 0
    for tx, ty in d["torches"]:
        ti += 1
        decor.append(
            f'\n[node name="Torch{ti}" parent="Decor" instance=ExtResource("6_torch")]\n'
            f'position = Vector2({px(tx)}, {ty*TILE + 8})\n'
            f'animation_name = "Burn1"\n')
    ci = 0
    for cx, cy in d["candles"]:
        ci += 1
        decor.append(
            f'\n[node name="Candle{ci}" parent="Decor" instance=ExtResource("6_torch")]\n'
            f'position = Vector2({px(cx)}, {cy*TILE + 4})\n'
            f'scale = Vector2(0.7, 0.7)\n'
            f'animation_name = "Burn2"\n')
    decor_block = "".join(decor) + "\n"
    text = text.replace('[node name="Actors"', decor_block + '[node name="Actors"', 1)

    goblins = []
    for gi, (gx, gfy) in enumerate(d["goblins"], 1):
        goblins.append(
            f'\n[node name="Goblin{gi}" parent="Actors" instance=ExtResource("5_goblin")]\n'
            f'position = Vector2({px(gx)}, {gfy*TILE - 35})\n')
    text = text.rstrip() + "\n" + "".join(goblins)

    with open(mt.MAIN, "w", encoding="utf-8") as f:
        f.write(text)
    print("WROTE main.tscn")
    print(f"  walls cells={len(walls_cells)} ground cells={len(ground_cells)}")
    print(f"  king@{(px(kx), kfy*TILE-51)}  goblins={len(d['goblins'])} "
          f"torches={ti} candles={ci}")

if __name__ == "__main__":
    main()
