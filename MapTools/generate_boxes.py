"""Full boxed-chamber serpentine generator.

A start chamber + dynamically-sized boxed chambers (small/medium/large) folding
up a 2-column zig-zag, connected by reused double-stair stamps, ending at a
WINNER chamber top-left. Emits tilemap cells + actor/decoration positions.

Coordinates in tiles (16px). y increases downward; "up" = smaller y.
"""
import os
import maptools as mt
from chamber_preview import DARK, LIT, floor_cap, cell
from generate_map2 import stair_run_right, stair_left, stair_right

SRC = 0
RISE = 8            # floor-to-floor vertical gap (one double stair)

DOOR_H = 4   # doorway opening height in tiles (player is ~3.6 tiles tall)

def build_box(ix, iy, iw, ih, border=2, doors=()):
    """Dark-brick walls (thickness `border`) around a lit interior.
    doors: subset of {'left','right'} -> DOOR_H-tall gap at floor level on that side.
    Returns (back_cells, wall_cells, ground_cells, info)."""
    back, walls, ground = [], [], []
    x0, y0 = ix - border, iy - border
    x1, y1 = ix + iw - 1 + border, iy + ih - 1 + border
    floor_y = iy + ih - 1
    door_top = floor_y - min(DOOR_H, ih) + 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            interior = ix <= x <= ix + iw - 1 and iy <= y <= iy + ih - 1
            if interior:
                if y == floor_y:
                    ground.append(cell(x, y, *floor_cap(x)))
                else:
                    back.append(cell(x, y, *LIT(x, y)))
            else:
                if "right" in doors and x > ix + iw - 1 and door_top <= y <= floor_y:
                    continue
                if "left" in doors and x < ix and door_top <= y <= floor_y:
                    continue
                walls.append(cell(x, y, *DARK(x, y)))
    info = dict(ix=ix, iy=iy, iw=iw, ih=ih, floor_y=floor_y,
                left_outer=x0, right_outer=x1, top_outer=y0,
                left_door=ix - 1, right_door=ix + iw)
    return back, walls, ground, info


# size presets (interior w,h) ---------------------------------------------------
SIZES = {"S": (12, 5), "M": (16, 6), "L": (22, 8), "XL": (26, 9)}

def generate(base_floor_y=44, start_ix=6):
    """Returns dict(layers, goblins, torches, candles, king, winner)."""
    back, walls, ground = [], [], []

    # chain: (name, size, dir_to_next)  dir is the stair direction LEAVING this room.
    # 'R' = ascend-right (next is up-right); 'L' = ascend-left (next is up-left).
    chain = [
        ("Start", "M", "R"),
        ("C1", "L", "L"),
        ("C2", "S", "R"),
        ("C3", "XL", "L"),
        ("C4", "M", "R"),
        ("C5", "S", "L"),
        ("WINNER", "L", None),
    ]

    goblins, torches, candles = [], [], []
    ramps = []   # each: (x0_px, y0_px, x1_px, y1_px) sloped walking line over a staircase

    # ---- pass 1: compute positions + connecting stairs ----
    pos = []   # each: dict(name, ix, iy, iw, ih, floor_y, left_door, right_door, entry, exit)
    iw, ih = SIZES[chain[0][1]]
    iy = base_floor_y - ih + 1
    pos.append(dict(name=chain[0][0], ix=start_ix, iy=iy, iw=iw, ih=ih,
                    floor_y=base_floor_y, left_door=start_ix - 1,
                    right_door=start_ix + iw, entry=None, exit=chain[0][2]))
    for i in range(len(chain) - 1):
        pdir = chain[i][2]
        nname, nsz, ndir = chain[i + 1]
        niw, nih = SIZES[nsz]
        prev = pos[i]
        floor_next = prev["floor_y"] - RISE
        if pdir == "R":     # next up-right, enter at its LEFT
            next_ix = prev["right_door"] + 17
            stair = stair_run_right(next_ix, floor_next)
            entry = "left"
        else:               # next up-left, enter at its RIGHT
            next_ix = prev["left_door"] - 16 - niw
            top_anchor = next_ix + niw - 1
            stair = stair_left(top_anchor, floor_next) + stair_left(top_anchor + 8, floor_next + 4)
            entry = "right"
        ground.extend(stair)
        # floor bridges: connect each room's doorway to the stair surface so the
        # walk is continuous (no gaps). Bottom step sits one row above floor_prev.
        floor_prev = prev["floor_y"]
        base_y = max(c[1] for c in stair)            # bottom step row (= floor_prev-1)
        base_xs = [c[0] for c in stair if c[1] == base_y]
        land_xs = [c[0] for c in stair if c[1] == floor_next]  # top stamp's floor row
        def frun(y, xa, xb):
            for x in range(min(xa, xb), max(xa, xb) + 1):
                ground.append(cell(x, y, *floor_cap(x)))
        if pdir == "R":
            frun(floor_prev, prev["right_door"], max(base_xs))      # exit ledge -> base
            if land_xs: frun(floor_next, min(land_xs), next_ix)     # top -> next floor
        else:
            frun(floor_prev, prev["left_door"], min(base_xs))       # exit ledge -> base
            if land_xs: frun(floor_next, next_ix + niw - 1, max(land_xs))
        # one sloped ramp per staircase: low end at the lower floor surface,
        # high end at the upper floor surface, spanning the stair footprint.
        sxs = [c[0] for c in stair]
        xmin, xmax = min(sxs), max(sxs)
        if pdir == "R":   # high on the right
            ramps.append((xmin * 16, floor_prev * 16, (xmax + 1) * 16, floor_next * 16))
        else:             # high on the left
            ramps.append((xmin * 16, floor_next * 16, (xmax + 1) * 16, floor_prev * 16))
        n_iy = floor_next - nih + 1
        pos.append(dict(name=nname, ix=next_ix, iy=n_iy, iw=niw, ih=nih,
                        floor_y=floor_next, left_door=next_ix - 1,
                        right_door=next_ix + niw, entry=entry, exit=ndir))

    # ---- pass 2: build each room with its entry+exit doors ----
    built = []
    for p in pos:
        doors = set()
        if p["exit"] == "R": doors.add("right")
        elif p["exit"] == "L": doors.add("left")
        if p["entry"]: doors.add(p["entry"])
        bk, wl, gr, info = build_box(p["ix"], p["iy"], p["iw"], p["ih"], doors=doors)
        back += bk; walls += wl; ground += gr
        built.append((p["name"], info))
        cx = p["ix"] + p["iw"] // 2
        if p["name"] != "Start":
            goblins.append((cx, info["floor_y"]))
        ty = p["iy"] + max(1, p["ih"] // 3)
        torches.append((p["ix"], ty)); torches.append((p["ix"] + p["iw"] - 1, ty))
        candles.append((p["ix"] + 1, info["floor_y"]))
        candles.append((p["ix"] + p["iw"] - 2, info["floor_y"]))

    king = None
    winner = None
    for name, info in built:
        if name == "Start":
            king = (info["ix"] + info["iw"] // 2, info["floor_y"])   # centre of Start room
        if name == "WINNER":
            winner = dict(ix=info["ix"], iy=info["iy"], iw=info["iw"], ih=info["ih"],
                          floor_y=info["floor_y"])

    return dict(back=back, walls=walls, ground=ground, goblins=goblins,
                torches=torches, candles=candles, king=king, winner=winner,
                ramps=ramps, rooms=built)


if __name__ == "__main__":
    d = generate()
    layers = [("walls.png", d["back"]), ("walls.png", d["walls"]),
              ("ground.png", d["ground"])]
    out = os.path.join(mt.ROOT, "MapTools", "preview", "boxes.png")
    size, bnds = mt.composite(layers, out, bg=(14, 11, 16, 255))
    print("preview:", out, "size:", size, "bounds:", bnds)
    print("rooms:", [n for n, _ in d["rooms"]])
    print("goblins:", len(d["goblins"]), "torches:", len(d["torches"]),
          "candles:", len(d["candles"]), "king:", d["king"], "winner:", d["winner"])
