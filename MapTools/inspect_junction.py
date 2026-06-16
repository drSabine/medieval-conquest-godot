import generate_boxes as gb
d = gb.generate()
# classify cells
mark = {}
for x,y,s,ax,ay,a in d["back"]:   mark[(x,y)]="."   # interior back wall
for x,y,s,ax,ay,a in d["walls"]:  mark[(x,y)]="#"   # dark border wall
for x,y,s,ax,ay,a in d["ground"]:
    mark[(x,y)] = "F" if ay==1 else "/"             # floor cap vs stair
xs=[k[0] for k in mark]; ys=[k[1] for k in mark]
# Inspect Start (right side) -> C1 junction region. Start floor y44.
# print a window around the first stair
def window(x0,x1,y0,y1,title):
    print(f"\n== {title}  x{x0}..{x1} y{y0}..{y1} (F=floor /=stair #=wall .=back ' '=open)")
    print("     "+"".join(str(x%10) for x in range(x0,x1+1)))
    for y in range(y0,y1+1):
        print(f"y{y:>4} "+"".join(mark.get((x,y)," ") for x in range(x0,x1+1)))
window(16,44,36,46,"Start->C1 (ascend-right)")
window(22,52,28,40,"C1->C2 (ascend-left)")
