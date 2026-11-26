import sys,json
from shapely.geometry import Polygon, LineString, Point
cj=json.load(open(sys.argv[1]))
pg={}
for e in cj:
    if e["type"]=="pcb_copper_pour":
        b=e["brep_shape"]; pg[e["layer"]]=Polygon([(v["x"],v["y"]) for v in b["outer_ring"]["vertices"]],[[(v["x"],v["y"]) for v in r["vertices"]] for r in b.get("inner_rings",[])]).buffer(0)
pads=[(e["layer"],e["x"],e["y"],e["width"],e["height"]) for e in cj if e["type"]=="pcb_smtpad"]
# min distance between any non-GND trace edge and the pour polygon
src={e["source_trace_id"]:e for e in cj if e["type"]=="source_trace"}
out=[]
for e in cj:
    if e["type"]=="pcb_trace" and "GND" not in e.get("connection_name","") :
        pts=e["route"]
        for a,b in zip(pts,pts[1:]):
            if a["route_type"]=="wire" and b["route_type"]=="wire" and a["layer"]==b["layer"] and a["layer"] in pg:
                ls=LineString([(a["x"],a["y"]),(b["x"],b["y"])]).buffer(b["width"]/2)
                out.append((pg[a["layer"]].distance(ls),b["width"]))
out.sort()
print("non-GND traces vs pour: n=%d min gap %.3f; sample (gap,width): %s"%(len(out),out[0][0] if out else -1,out[:3]))
print("pours:",[(l,round(p.area,1)) for l,p in pg.items()])
