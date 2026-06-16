"""Isolated test: connect two floors 8 rows apart with stairs, render zoomed,
so we can confirm the stair geometry/orientation before building the full map."""
import maptools as mt
from generate_map import (gcell, build_floor, build_backdrop,
                          stair_right, stair_left)

def scene(stair_cells, label, low=(0, 24), high=(0, 16), low_xr=26, high_xl=0, high_xr=26):
    walls = build_backdrop(-2, 30, high[1] - 4, low[1])
    ground = build_floor(low[0], low_xr, low[1]) + build_floor(high_xl, high_xr, high[1]) + stair_cells
    out = f"preview/stair_{label}.png"
    mt.composite([("walls.png", walls), ("ground.png", ground)], out, grid=False)
    # also a zoomed crop printed as ascii of ground rows
    xs=[c[0] for c in ground]; ys=[c[1] for c in ground]
    g={(x,y):("F" if ay==1 else "/") for x,y,_,ax,ay,_ in ground}
    print(f"--- {label} ---")
    for y in range(min(ys), max(ys)+1):
        print(f"y{y:>3} "+"".join(g.get((x,y),".") for x in range(min(xs),max(xs)+1)))
    print("saved", out)

if __name__ == "__main__":
    # Test A: single ascend-right stamp (4 rows): high floor at y20 (4 above low y24)
    scene(stair_right(18, 20), "A_single_right", low=(0,24), high=(0,20),
          low_xr=26, high_xl=18, high_xr=30)
    # Test B: double ascend-right stamp (8 rows): low y24 -> high y16
    dbl = stair_right(26, 16) + stair_right(18, 20)
    scene(dbl, "B_double_right", low=(0,24), high=(0,16),
          low_xr=20, high_xl=26, high_xr=40)
