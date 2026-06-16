from PIL import Image, ImageDraw
import os, maptools as mt
TILE=16
def palette(png, coords, out, scale=4, cols=8):
    sh = Image.open(os.path.join(mt.SHEETS_DIR, png)).convert("RGBA")
    cw, chh = TILE*scale+8, TILE*scale+18
    rows=(len(coords)+cols-1)//cols
    cv=Image.new("RGBA",(cols*cw+6, rows*chh+6),(18,18,24,255))
    d=ImageDraw.Draw(cv)
    for i,(ax,ay) in enumerate(coords):
        r,c=divmod(i,cols)
        t=sh.crop((ax*TILE,ay*TILE,ax*TILE+TILE,ay*TILE+TILE)).resize((TILE*scale,TILE*scale),Image.NEAREST)
        x=6+c*cw; y=6+r*chh
        cv.alpha_composite(t,(x,y))
        d.text((x, y+TILE*scale+2), f"{ax},{ay}", fill=(0,255,120,255))
    cv.save(out); print("saved",out)

# candidate solid bricks across walls.png (dark vs lit)
cand=[(20,9),(21,10),(22,11),(20,12),(23,13),  # lit panel (interior candidates)
      (8,0),(9,1),(8,1),(0,1),(1,2),(2,1),       # upper-left darker bricks
      (14,9),(15,10),(16,11),(14,12),(15,8),(16,9), # mid darker region
      (19,3),(20,4),(21,5),(20,2),(24,6),(25,7),  # upper tower (medium)
      (8,9),(9,10),(8,11),(0,9),(1,10)]            # left-mid bricks
palette("walls.png",cand,"preview/pal_walls.png")
