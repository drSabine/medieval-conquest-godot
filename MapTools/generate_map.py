"""Generate the serpentine chamber map for Medieval-Conquest.

Keeps the existing start (C1 floor y47 + C2 landing y43 + their stair) fully
intact and stacks new chambers above, connected by reused staircase stamps.

Run with --write to apply to main.tscn; otherwise only renders a preview.
"""
import sys, os
import maptools as mt

# ---- tile vocabulary (learned from the existing map) ----
def floor_cap(x):
    # alternating 2-tile floor surface; even x -> 12,1  odd x -> 13,1
    return (12, 1) if x % 2 == 0 else (13, 1)

# Staircase stamp that ASCENDS RIGHTWARD (low-left, high-right).
# (dx, dy, ax, ay) relative to anchor = leftmost tile of the UPPER floor.
ASCEND_RIGHT = [
    (-1, -1, 13, 3),
    (-3, 0, 11, 4), (-2, 0, 12, 4), (-1, 0, 13, 4),
    (-5, 1, 13, 3),
    (-4, 1, 10, 5), (-3, 1, 11, 5), (-2, 1, 12, 5), (-1, 1, 13, 5),
    (-7, 2, 11, 4), (-6, 2, 12, 4), (-5, 2, 13, 4),
    (-4, 2, 10, 6), (-3, 2, 11, 6),
    (-8, 3, 10, 5), (-7, 3, 11, 5), (-6, 3, 12, 5), (-5, 3, 13, 5),
]
# Mirror -> ASCENDS LEFTWARD (high-left, low-right). Anchor = rightmost tile of UPPER floor.
ASCEND_LEFT = [(-dx, dy, 28 - ax, ay) for (dx, dy, ax, ay) in ASCEND_RIGHT]

SRC = 0  # source_id for both tilesets in main.tscn

def gcell(x, y, ax, ay):
    return (x, y, SRC, ax, ay, 0)

# ---- builders ----
def build_floor(xl, xr, fy):
    return [gcell(x, fy, *floor_cap(x)) for x in range(xl, xr + 1)]

def build_backdrop(xl, xr, ytop, ybot):
    """Seamless brick panel (cols 20-25 x rows 9-15); row 9 cap sits at ytop."""
    cells = []
    for y in range(ytop, ybot + 1):
        ay = 9 + ((y - ytop) % 7)
        for x in range(xl, xr + 1):
            ax = 20 + (x % 6)
            cells.append(gcell(x, y, ax, ay))
    return cells

def stair_right(anchor_x, upper_fy):
    return [gcell(anchor_x + dx, upper_fy + dy, ax, ay) for (dx, dy, ax, ay) in ASCEND_RIGHT]

def stair_left(anchor_x, upper_fy):
    return [gcell(anchor_x + dx, upper_fy + dy, ax, ay) for (dx, dy, ax, ay) in ASCEND_LEFT]


def generate():
    text, existing = mt.read_main_layers()
    walls = list(existing["Walls"])    # keep everything already painted
    ground = list(existing["Ground"])

    new_ground = []
    new_walls = []

    # Existing: C1 floor y47, C2 landing y43 (reached by existing ascend-right stair).
    # Continue the serpentine UP from the C2 landing (spans ~x44..60).
    #
    # Each chamber: flat floor [xl..xr] at fy, plus a stair UP to the next.
    # side 'L' = ascend-left stair on this chamber's left, next chamber up-left.
    # side 'R' = ascend-right stair on this chamber's right, next chamber up-right.
    #
    # Walk the path (zig-zag, climbing). Coordinates chosen to stay compact and
    # alternate sides so it reads as the serpentine in the sketch.
    chambers = [
        # name      xl   xr   fy   up_side  (stair to next chamber)
        ("C3", 22, 42, 39, "R"),   # from C2(y43) we climbed left->C3; C3 exits up-right
        ("C4", 50, 70, 35, "L"),   # C4 exits up-left
        ("C5", 22, 46, 31, "R"),
        ("C6", 54, 74, 27, "L"),
        ("C7", 22, 46, 23, "R"),
        ("WIN", 54, 78, 19, None),  # final chamber (top)
    ]

    # Connect C2 landing (y43) up to C3 (y39) with an ascend-LEFT stair:
    # C3 is upper/left, C2 lower/right. Anchor = C3 rightmost floor tile.
    new_ground += stair_left(42, 39)

    for i, (name, xl, xr, fy, side) in enumerate(chambers):
        new_ground += build_floor(xl, xr, fy)
        # backdrop behind this chamber: cap row 6 above the floor down to the floor row
        new_walls += build_backdrop(xl - 2, xr + 2, fy - 6, fy)
        if side == "R":
            # next chamber up-right; ascend-right stair, anchor = next floor leftmost
            nxt = chambers[i + 1]
            new_ground += stair_right(nxt[1], nxt[3])
        elif side == "L":
            nxt = chambers[i + 1]
            new_ground += stair_left(nxt[2], nxt[3])

    ground += new_ground
    walls += new_walls
    return {"Walls": walls, "Ground": ground}


def ascii_schematic(layers):
    """Print ground layer as F=floor, /=stair step, .=empty for path inspection."""
    g = layers["Ground"]
    xs = [c[0] for c in g]; ys = [c[1] for c in g]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    grid = {}
    for x, y, src, ax, ay, alt in g:
        # floor caps are row 1; stairs use rows 3-6
        grid[(x, y)] = "F" if ay == 1 else "/"
    lines = []
    for y in range(miny, maxy + 1):
        row = "".join(grid.get((x, y), ".") for x in range(minx, maxx + 1))
        lines.append(f"y{y:>3} |{row}")
    header = "      " + "".join(str((minx + i) // 10 % 10) if (minx + i) % 10 == 0 else " "
                                for i in range(maxx - minx + 1))
    print(header)
    print("\n".join(lines))


if __name__ == "__main__":
    layers = generate()
    grid = "--grid" in sys.argv
    out = os.path.join(mt.ROOT, "MapTools", "preview", "serpentine.png")
    size, bnds = mt.composite(
        [("walls.png", layers["Walls"]), ("ground.png", layers["Ground"])],
        out, grid=grid)
    print("preview:", out, "size:", size, "bounds:", bnds)
    print("ground cells:", len(layers["Ground"]), " walls cells:", len(layers["Walls"]))
    if "--ascii" in sys.argv:
        ascii_schematic(layers)
    if "--write" in sys.argv:
        mt.write_main_layers(layers)
        print("WROTE main.tscn")
