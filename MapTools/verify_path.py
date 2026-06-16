import maptools as mt, generate_map2 as g2
L = g2.generate()
gnd = L["Ground"]
xs=[c[0] for c in gnd]; ys=[c[1] for c in gnd]
minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
grid={}
for x,y,src,ax,ay,alt in gnd:
    grid[(x,y)] = "F" if ay==1 else ("c" if (ax,ay)in[(13,3),(15,3)] else "/")
print(f"x {minx}..{maxx}  y {miny}..{maxy}   (F=floor cap, /=stair, c=cap-nub)")
# column ruler
ruler="     "
for x in range(minx,maxx+1):
    ruler += (str(x%10) if x%5==0 else " ")
print(ruler)
for y in range(miny,maxy+1):
    row="".join(grid.get((x,y)," ") for x in range(minx,maxx+1))
    print(f"y{y:>3} |{row}")
