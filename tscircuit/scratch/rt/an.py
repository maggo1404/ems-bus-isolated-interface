import json,sys,collections
cj=json.load(open(sys.argv[1]))
w=collections.Counter(); vias=[]; types=collections.Counter()
for e in cj:
    if e["type"]=="pcb_trace":
        for r in e["route"]:
            if r["route_type"]=="wire": w[r["width"]]+=1
            elif r["route_type"]=="via": vias.append(r)
    if e["type"]=="pcb_via": types[(e.get("hole_diameter"),e.get("outer_diameter"))]+=1
print("wire widths:",dict(w)); print("via route pts:",len(vias),"pcb_via dims:",dict(types))
print("errs:",[ (e["type"],e.get("message","")[:90]) for e in cj if "error" in e["type"]][:5])
