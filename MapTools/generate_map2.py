"""Serpentine generator v2 — clean boustrophedon.

Keeps the existing start (lower floor y47 + landing y43 + their stair) intact and
stacks chambers above, 8 rows apart (good headroom for the ~58px player), with
double-stair connectors at ALTERNATING ends so stairs never overlap.

Tile vocabulary + stamps reused from generate_map.py (all verified against the
hand-painted original).
"""
import sys, os
import maptools as mt
from generate_map import gcell, build_floor, build_backdrop, stair_right, stair_left

TIER = 8          # rows between chamber floors
STAMP = 4         # rows per stair stamp
RUN = 2           # stamps per connector (2 -> 8-row rise over 16 cols)

def stair_run_right(top_anchor_x, top_fy, run=RUN):
    """Climb up-right: high floor starts at (top_anchor_x, top_fy) extends right;
    low floor sits ~16 cols left at top_fy+4*run."""
    cells = []
    for i in range(run):
        cells += stair_right(top_anchor_x - 8 * i, top_fy + STAMP * i)
    return cells

def stair_run_left(top_anchor_x, top_fy, run=RUN):
    """Climb up-left: high floor ends at (top_anchor_x, top_fy) extends left;
    low floor sits ~16 cols right at top_fy+4*run."""
    cells = []
    for i in range(run):
        cells += stair_left(top_anchor_x + 8 * i, top_fy + STAMP * i)
    return cells


def generate():
    text, existing = mt.read_main_layers()
    walls = list(existing["Walls"])
    ground = list(existing["Ground"])
    new_ground, new_walls = [], []

    # Existing landing (C1 upper) is at y43, usable span ~x44..68.
    # Build C2..C6 above it. Each entry: (name, floor_y, xl, xr, climb_side, top_anchor)
    #   climb_side 'L' = ascend-left run leading UP to this chamber (it extends left,
    #              player walks left across it); base lands at top_anchor+16.
    #   climb_side 'R' = ascend-right run (extends right, walk right); base at top_anchor-16.
    chambers = [
        # name  fy  xl  xr  side anchor
        ("C2", 35, 24, 52, "L", 52),   # base @68 -> lands on landing(y43) right end
        ("C3", 27, 40, 68, "R", 40),   # base @24 -> lands on C2 left end
        ("C4", 19, 24, 52, "L", 52),   # base @68 -> lands on C3 right end
        ("C5", 11, 40, 68, "R", 40),   # base @24 -> lands on C4 left end
        ("WIN", 3, 22, 52, "L", 52),   # base @68 -> lands on C5 right end; ends top-LEFT
    ]

    prev_y = 43
    for name, fy, xl, xr, side, anchor in chambers:
        new_ground += build_floor(xl, xr, fy)
        if side == "L":
            new_ground += stair_run_left(anchor, fy)
        else:
            new_ground += stair_run_right(anchor, fy)
        prev_y = fy

    # Big brick backdrop behind the whole new stack. Span full map width (matching
    # the existing wall) so there's no void upper-left, like the reference art.
    all_new = new_ground
    nxs = [c[0] for c in all_new]; nys = [c[1] for c in all_new]
    bx0, bx1 = 0, max(max(nxs) + 2, 74)
    by0, by1 = min(nys) - 5, 42       # cap a few rows above top floor; meet existing (y36+)
    backdrop = build_backdrop(bx0, bx1, by0, by1)

    # dedup: existing wall cells win
    occupied = {(x, y) for x, y, *_ in walls}
    for c in backdrop:
        if (c[0], c[1]) not in occupied:
            new_walls.append(c); occupied.add((c[0], c[1]))

    ground += new_ground
    walls += new_walls
    return {"Walls": walls, "Ground": ground}


if __name__ == "__main__":
    layers = generate()
    out = os.path.join(mt.ROOT, "MapTools", "preview", "serpentine2.png")
    size, bnds = mt.composite(
        [("walls.png", layers["Walls"]), ("ground.png", layers["Ground"])], out,
        grid="--grid" in sys.argv)
    print("preview:", out, "size:", size, "bounds:", bnds)
    print("ground:", len(layers["Ground"]), "walls:", len(layers["Walls"]))
    if "--write" in sys.argv:
        mt.write_main_layers(layers)
        print("WROTE main.tscn")
