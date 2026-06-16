"""Assemble a 3-chamber serpentine slice (boxes + connecting stairs + a goblin in
each) and render it, to confirm the chamber style AND the connected layout before
building the whole map. No scene changes."""
import os
from PIL import Image
import maptools as mt
from chamber_preview import build_box, DARK, LIT, floor_cap, cell
from generate_map2 import stair_run_right

def merge(dst, src):
    for k in ("back", "frame", "ground"):
        dst[k] += src[k]

def main():
    world = {"back": [], "frame": [], "ground": []}
    goblins = []

    # Three boxes climbing up-right, connected by 8-row double stairs.
    # (ix, iy, iw, ih, entry_door, exit_door)
    boxes = [
        (4, 30, 12, 5, None, "right"),
        (33, 22, 12, 5, "left", "right"),
        (62, 14, 12, 5, "left", None),
    ]
    built = []
    for ix, iy, iw, ih, entry, exit_ in boxes:
        # build with the exit door; punch the entry door afterwards
        b = build_box(ix, iy, iw, ih, border=2, door=exit_ or "right")
        if exit_ is None:
            # rebuild without an exit gap (closed right) -> use a closed box
            b = build_box(ix, iy, iw, ih, border=2, door="none")
        built.append((b, ix, iy, iw, ih, entry, exit_))

    # punch entry doors (left) by removing dark border cells at floor level on the left
    def punch_left_door(b, ix, iy, ih):
        fy = iy + ih - 1
        keep = []
        for c in b["frame"]:
            x, y = c[0], c[1]
            if x < ix and (fy - 1 <= y <= fy):
                continue
            keep.append(c)
        b["frame"] = keep

    for b, ix, iy, iw, ih, entry, exit_ in built:
        if entry == "left":
            punch_left_door(b, ix, iy, ih)
        merge(world, b)
        gx = ix + iw // 2; gy = iy + ih - 1
        goblins.append((gx, gy))

    # connecting stairs: from each box's right door down-floor up to next box's left door
    # C1 floor y34 -> C2 floor y26 ; C2 floor y26 -> C3 floor y18  (8-row rises)
    world["ground"] += stair_run_right(33, 26)   # base ~x17 (C1 right) -> top x33 (C2 left)
    world["ground"] += stair_run_right(62, 18)   # base ~x46 (C2 right) -> top x62 (C3 left)
    # short floor bridges so the door openings meet the stair base cleanly
    for x in range(16, 18):
        world["ground"].append(cell(x, 34, *floor_cap(x)))
    for x in range(45, 47):
        world["ground"].append(cell(x, 26, *floor_cap(x)))

    layers = [("walls.png", world["back"]),
              ("walls.png", world["frame"]),      # dark border is also walls.png
              ("ground.png", world["ground"])]
    all_cells = [c for _, cs in layers for c in cs]
    xs = [c[0] for c in all_cells]; ys = [c[1] for c in all_cells]
    bnds = (min(xs), min(ys), max(xs), max(ys))
    out = "preview/slice.png"
    mt.composite(layers, out + ".tmp.png", bg=(16, 12, 18, 255), bounds=bnds)

    base = Image.open(out + ".tmp.png").convert("RGBA")
    gob = Image.open(os.path.join(mt.ROOT, "Assets", "Mobs", "Goblin", "Idle.png")).convert("RGBA")
    f0 = gob.crop((0, 0, 150, 150)); f0 = f0.crop(f0.getbbox())
    sc = (3 * 16) / f0.size[1]; f0 = f0.resize((int(f0.size[0] * sc), 3 * 16), Image.NEAREST)
    for gx, gy in goblins:
        px = (gx - bnds[0]) * 16 - f0.size[0] // 2
        py = (gy - bnds[1]) * 16 + 16 - f0.size[1]
        base.alpha_composite(f0, (px, py))
    base.save(out); os.remove(out + ".tmp.png")
    print("saved", out, "size", base.size)

if __name__ == "__main__":
    main()
