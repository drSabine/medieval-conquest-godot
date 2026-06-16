"""Compose ONE simple chamber box as a preview image (no scene changes yet).

Layers back-to-front: back wall (walls.png brick) -> frame border
(walls_side_top.png) -> floor (ground.png) -> goblin sprite pasted in.
Frame tile coords are at the top so they're easy to tweak while iterating.
"""
import os
from PIL import Image
import maptools as mt

TILE = 16
SRC = 0
def cell(x, y, ax, ay): return (x, y, SRC, ax, ay, 0)

# ---- frame tiles from walls_side_top.png (clean room template cols18-25 rows3-13) ----
F = {
    "top_cap": (21, 3),                      # bright brick top surface (ceiling cap)
    "top_in": (21, 4), "tl": (18, 4), "tr": (25, 4),   # dark top inner + X-brace corners
    "left": (18, 6), "right": (25, 6),       # vertical side walls
    "bot_in": (21, 11), "bl": (18, 11), "br": (25, 11),  # bottom inner + X-brace corners
    "bottom": (21, 12), "base": (21, 13),    # bottom border + base
}
BACK = lambda x, y: (20 + (x % 6), 10 + (y % 6))   # lit brick interior fill (walls.png)
def floor_cap(x): return (12, 1) if x % 2 == 0 else (13, 1)

def build_chamber(ix, iy, iw, ih, door="right"):
    """ix,iy = top-left of the INTERIOR; iw,ih = interior size in tiles.
    Frame wraps the interior: 2-row top (cap+inner), 1-col sides, 2-row bottom.
    Floor (player standing surface) is the bottom interior row."""
    back, frame, ground = [], [], []
    xl, xr = ix - 1, ix + iw            # side-wall columns
    y_cap, y_topin = iy - 2, iy - 1     # ceiling rows
    y_botin, y_bottom, y_base = iy + ih, iy + ih + 1, iy + ih + 2
    floor_y = iy + ih - 1               # player floor (bottom interior row)

    # ceiling: bright cap + dark inner (with X-brace corners)
    for x in range(xl, xr + 1):
        frame.append(cell(x, y_cap, *F["top_cap"]))
        frame.append(cell(x, y_topin, F["tl"][0] if x == xl else F["tr"][0] if x == xr else F["top_in"][0],
                          F["tl"][1] if x in (xl, xr) else F["top_in"][1]))
    # bottom: inner (with braces) + border + base
    for x in range(xl, xr + 1):
        frame.append(cell(x, y_botin, F["bl"][0] if x == xl else F["br"][0] if x == xr else F["bot_in"][0],
                          F["bl"][1] if x in (xl, xr) else F["bot_in"][1]))
        frame.append(cell(x, y_bottom, *F["bottom"]))
        frame.append(cell(x, y_base, *F["base"]))
    # side walls + interior back wall + floor
    for y in range(iy, iy + ih):
        # doorway gap (2 tiles tall at floor level) on chosen side
        door_rows = floor_y - 1 <= y <= floor_y
        if not (door == "left" and door_rows):
            frame.append(cell(xl, y, *F["left"]))
        if not (door == "right" and door_rows):
            frame.append(cell(xr, y, *F["right"]))
        for x in range(ix, ix + iw):
            if y == floor_y:
                ground.append(cell(x, y, *floor_cap(x)))
            else:
                back.append(cell(x, y, *BACK(x, y)))
    return {"back": back, "frame": frame, "ground": ground, "floor_y": floor_y,
            "interior": (ix, ix + iw - 1, floor_y)}

DARK = lambda x, y: (14 + (x % 3), 9 + (y % 3))   # dark solid brick (border)
LIT = lambda x, y: (20 + (x % 6), 9 + (y % 6))    # lit brick (interior back)

def build_box(ix, iy, iw, ih, border=2, door="right"):
    """High-contrast box: `border`-thick DARK brick walls around a LIT interior.
    ix,iy,iw,ih describe the interior. Floor = bottom interior row."""
    back, frame, ground = [], [], []
    x0, y0 = ix - border, iy - border
    x1, y1 = ix + iw - 1 + border, iy + ih - 1 + border
    floor_y = iy + ih - 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            in_interior = ix <= x <= ix + iw - 1 and iy <= y <= iy + ih - 1
            if in_interior:
                if y == floor_y:
                    ground.append(cell(x, y, *floor_cap(x)))
                else:
                    back.append(cell(x, y, *LIT(x, y)))
            else:
                # doorway: 2-tall gap at floor level on the chosen side
                if door == "right" and x > ix + iw - 1 and floor_y - 1 <= y <= floor_y:
                    continue
                if door == "left" and x < ix and floor_y - 1 <= y <= floor_y:
                    continue
                frame.append(cell(x, y, *DARK(x, y)))   # dark border wall
    return {"back": back, "frame": frame, "ground": ground, "floor_y": floor_y,
            "interior": (ix, ix + iw - 1, floor_y), "frame_sheet": "walls.png"}

def render(ch, out, goblin_at=None):
    layers = [("walls.png", ch["back"]),
              (ch.get("frame_sheet", "walls_side_top.png"), ch["frame"]),
              ("ground.png", ch["ground"])]
    all_cells = [c for _, cs in layers for c in cs]
    xs = [c[0] for c in all_cells]; ys = [c[1] for c in all_cells]
    minx, miny, maxx, maxy = min(xs), min(ys), max(xs), max(ys)
    img = mt.composite(layers, out + ".tmp.png", bg=(18, 14, 20, 255),
                       bounds=(minx, miny, maxx, maxy))
    # paste goblin idle frame so "a goblin in there" is visible
    base = Image.open(out + ".tmp.png").convert("RGBA")
    if goblin_at:
        gob = Image.open(os.path.join(mt.ROOT, "Assets", "Mobs", "Goblin", "Idle.png")).convert("RGBA")
        frame0 = gob.crop((0, 0, 150, 150))
        # trim transparent, scale to ~3 tiles tall
        bbox = frame0.getbbox(); frame0 = frame0.crop(bbox)
        target_h = 3 * TILE
        sc = target_h / frame0.size[1]
        frame0 = frame0.resize((int(frame0.size[0] * sc), target_h), Image.NEAREST)
        gx, gy = goblin_at
        px = (gx - minx) * TILE - frame0.size[0] // 2
        py = (gy - miny) * TILE + TILE - frame0.size[1]
        base.alpha_composite(frame0, (px, py))
    base.save(out)
    os.remove(out + ".tmp.png")
    print("saved", out, "size", base.size)

if __name__ == "__main__":
    a = build_chamber(4, 4, 16, 6, door="right")          # frame (walls_side_top)
    ax = a["interior"]; render(a, "preview/chamber_A_frame.png", goblin_at=((ax[0]+ax[1])//2, ax[2]))
    b = build_box(4, 4, 16, 6, border=2, door="right")    # high-contrast dark border
    bx = b["interior"]; render(b, "preview/chamber_B_box.png", goblin_at=((bx[0]+bx[1])//2, bx[2]))
    # stitch side by side for comparison
    from PIL import Image
    A = Image.open("preview/chamber_A_frame.png"); B = Image.open("preview/chamber_B_box.png")
    W = max(A.width, B.width); gap = 16
    cmp = Image.new("RGBA", (W, A.height + gap + B.height), (10, 10, 14, 255))
    cmp.paste(A, (0, 0)); cmp.paste(B, (0, A.height + gap))
    cmp.save("preview/chamber_compare.png"); print("saved preview/chamber_compare.png  (A=frame top, B=box bottom)")
