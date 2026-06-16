import re, maptools as mt

with open(mt.MAIN, encoding="utf-8") as f:
    text = f.read()

# Parse registered atlas coords from each TileSetAtlasSource block (lines like "20:9/0 = 0")
def registered_coords(block):
    return set((int(a), int(b)) for a, b in re.findall(r'^(\d+):(\d+)/0 = 0', block, re.M))

# Walls source uses walls.png; Ground source uses ground.png. Split blocks by SubResource.
blocks = re.split(r'\[sub_resource type="TileSetAtlasSource"', text)
reg = {}
for blk in blocks[1:]:
    tex = re.search(r'texture = ExtResource\("([^"]+)"\)', blk)
    coords = registered_coords(blk)
    # map ext resource id to png
    if tex:
        rid = tex.group(1)
        png = "walls.png" if "xlvfx" in rid or "2_xlvfx" == rid else ("ground.png" if "2a143" in rid else rid)
        reg[png] = coords

# Identify which png each registered set belongs to by checking known tiles
# walls backdrop uses (20,9); ground floor uses (12,1)
for png, coords in list(reg.items()):
    tag = "walls.png" if (20,9) in coords else ("ground.png" if (12,1) in coords else png)
    reg[tag] = coords

text2, layers = mt.read_main_layers()
problems = 0
for layer, png in [("Walls","walls.png"), ("Ground","ground.png")]:
    used = set((c[3], c[4]) for c in layers[layer])
    rset = reg.get(png, set())
    missing = used - rset
    print(f"{layer}: {len(used)} distinct atlas tiles used, {len(rset)} registered, missing={sorted(missing)}")
    problems += len(missing)
print("ALL TILES REGISTERED" if problems==0 else f"!!! {problems} UNREGISTERED TILE TYPES")

# structure check: actors & key nodes still present
for needle in ['name="MedievalKing"','name="Huntress"','name="Goblin"','name="Background"',
               'name="Walls"','name="Ground"','run/main_scene', 'name="Actors"']:
    print(("OK " if needle in text else "MISSING ") + needle)
