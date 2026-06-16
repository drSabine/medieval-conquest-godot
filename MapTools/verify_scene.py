import re, maptools as mt
text, layers = mt.read_main_layers()
# 1) re-composite from saved scene
mt.composite([("walls.png",layers["Walls"]),("ground.png",layers["Ground"])],
             "preview/from_scene.png", bg=(14,11,16,255))
print("Walls cells:", len(layers["Walls"]), " Ground cells:", len(layers["Ground"]))

# 2) registration check
blocks = re.split(r'\[sub_resource type="TileSetAtlasSource"', text)
reg = {}
for blk in blocks[1:]:
    coords=set((int(a),int(b)) for a,b in re.findall(r'^(\d+):(\d+)/0 = 0', blk, re.M))
    tag = "walls.png" if (20,9) in coords else ("ground.png" if (12,1) in coords else "?")
    reg[tag]=coords
prob=0
for layer,png in [("Walls","walls.png"),("Ground","ground.png")]:
    used=set((c[3],c[4]) for c in layers[layer]); miss=used-reg.get(png,set())
    print(f"{layer}: missing={sorted(miss)}"); prob+=len(miss)
print("ALL TILES REGISTERED" if prob==0 else "!!! UNREGISTERED TILES")

# 3) structure checks
import collections
checks = {
 "torch ext_resource": 'torches.tscn' in text,
 "Decor node": '[node name="Decor"' in text,
 "King moved": 'position = Vector2(136, 653)' in text,
 "template Goblin removed": text.count('position = Vector2(896, 586)')==0,
 "Huntress kept": '[node name="Huntress"' in text,
}
print("Goblin instances:", len(re.findall(r'\[node name="Goblin\d+" parent="Actors"', text)))
print("Torch instances:", len(re.findall(r'\[node name="Torch\d+"', text)))
print("Candle instances:", len(re.findall(r'\[node name="Candle\d+"', text)))
for k,v in checks.items(): print(("OK  " if v else "FAIL ")+k)
# 4) sanity: every [node ... parent=...] parent exists / no obvious dup ext id
ids = re.findall(r'id="([^"]+)"', text)
dups = [i for i,c in collections.Counter(ids).items() if c>1]
print("duplicate resource ids:", dups or "none")
