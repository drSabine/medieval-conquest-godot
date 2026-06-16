import sys, os
from PIL import Image, ImageDraw
import maptools as mt
TILE=16
def crop(png, c0, r0, c1, r1, scale=12, out=None):
    im = Image.open(os.path.join(mt.SHEETS_DIR, png)).convert("RGBA")
    reg = im.crop((c0*TILE, r0*TILE, (c1+1)*TILE, (r1+1)*TILE))
    big = reg.resize((reg.size[0]*scale, reg.size[1]*scale), Image.NEAREST)
    pad=26
    cv = Image.new("RGBA",(big.size[0]+pad,big.size[1]+pad),(12,12,16,255))
    cv.alpha_composite(big,(pad,pad))
    d=ImageDraw.Draw(cv)
    for i,c in enumerate(range(c0,c1+2)):
        x=pad+i*TILE*scale
        d.line([(x,pad),(x,pad+big.size[1])],fill=(0,255,0,120))
        if c<=c1: d.text((x+3,6),str(c),fill=(0,255,120,255))
    for j,r in enumerate(range(r0,r1+2)):
        y=pad+j*TILE*scale
        d.line([(pad,y),(pad+big.size[0],y)],fill=(0,255,0,120))
        if r<=r1: d.text((4,y+3),str(r),fill=(0,255,120,255))
    out = out or f"preview/crop_{png.replace('.png','')}_{c0}_{r0}.png"
    cv.save(out); print("saved",out, f"cols {c0}-{c1} rows {r0}-{r1}")
crop("walls_side_top.png",17,2,27,14,out="preview/crop_frame.png")
