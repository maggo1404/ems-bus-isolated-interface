#!/usr/bin/env python3
"""Minimum copper distance EMS nets vs MCU nets per layer (pads, plated holes, traces, vias, pours).
Reads dist/index/circuit.json. Requires shapely (pip install shapely).
Side of a net: by net name (EMS_*, GND_EMS, V5_EMS = EMS; any other named net = MCU); unnamed nets by pad x (<0 EMS).
Limit: >= 6.0 mm excluding the pads of the optocouplers OC1/OC2 (which bridge the barrier by design).
Also reports: distance incl. opto pads, copper inside the isolation slots / across x=0, copper in the antenna keepout.
Usage: python3 scripts/check_isolation.py [circuit.json] [limit_mm]
"""
import sys, math
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from netlib import load, Conn
from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union
from shapely import affinity

cjp = sys.argv[1] if len(sys.argv) > 1 else "dist/index/circuit.json"
LIMIT = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
cj = load(cjp)
c = Conn(cj)
OPTOS = {"OC1", "OC2"}
EMS_NAMES = lambda n: n.startswith("EMS_") or n in ("GND_EMS", "V5_EMS")

pcb_port = {p["pcb_port_id"]: p for p in cj if p["type"] == "pcb_port"}
pcb_comp = {p["pcb_component_id"]: p for p in cj if p["type"] == "pcb_component"}
src_comp = {p["source_component_id"]: p["name"] for p in cj if p["type"] == "source_component"}
pcbc2ref = {}
for p in cj:
    if p["type"] == "pcb_component":
        pcbc2ref[p["pcb_component_id"]] = src_comp.get(p.get("source_component_id"), "?")

# ---- side per connectivity root ----
root_xs = {}
for pid, pp in pcb_port.items():
    r = c.root_of_port(pp["source_port_id"])
    if r is not None:
        root_xs.setdefault(r, []).append(pp["x"])


def side_of_root(r):
    if r is None:
        return None
    names = c.groups.get(r, {}).get("names", set())
    if names:
        return "EMS" if any(EMS_NAMES(n) for n in names) else "MCU"
    xs = root_xs.get(r, [0])
    return "EMS" if sum(xs) / len(xs) < 0 else "MCU"


# items: (side, layer, geom, tag)
items = []


def add(side, layers, geom, tag):
    for l in layers:
        items.append((side, l, geom, tag))


def pad_geom(p):
    if p["shape"] == "circle":
        return Point(p["x"], p["y"]).buffer(p["radius"])
    if p["shape"] in ("rect", "rotated_rect"):
        g = box(p["x"] - p["width"] / 2, p["y"] - p["height"] / 2, p["x"] + p["width"] / 2, p["y"] + p["height"] / 2)
        if p.get("ccw_rotation"):
            g = affinity.rotate(g, p["ccw_rotation"], origin=(p["x"], p["y"]))
        return g
    if p["shape"] == "pill":
        w, h = p["width"], p["height"]
        r = min(w, h) / 2
        return Point(p["x"], p["y"]).buffer(r) if w == h else box(p["x"] - w / 2, p["y"] - h / 2, p["x"] + w / 2, p["y"] + h / 2)
    raise ValueError(p["shape"])


for p in cj:
    t = p["type"]
    if t == "pcb_smtpad":
        pp = pcb_port.get(p.get("pcb_port_id"))
        r = c.root_of_port(pp["source_port_id"]) if pp else None
        ref = pcbc2ref.get(p["pcb_component_id"], "?")
        side = side_of_root(r)
        if side is None:  # unconnected pad: use position
            side = "EMS" if p["x"] < 0 else "MCU"
        add(side, [p["layer"]], pad_geom(p), "opto" if ref in OPTOS else "pad:" + ref)
    elif t == "pcb_plated_hole":
        pp = pcb_port.get(p.get("pcb_port_id"))
        r = c.root_of_port(pp["source_port_id"]) if pp else None
        side = side_of_root(r) or ("EMS" if p["x"] < 0 else "MCU")
        if p["shape"] == "circle":
            g = Point(p["x"], p["y"]).buffer(p["outer_diameter"] / 2)
        else:
            w, h = p.get("outer_width", 1), p.get("outer_height", 1)
            g = box(p["x"] - w / 2, p["y"] - h / 2, p["x"] + w / 2, p["y"] + h / 2)
        add(side, ["top", "bottom"], g, "pth:" + pcbc2ref.get(p["pcb_component_id"], "?"))

traces = {p["pcb_trace_id"]: p for p in cj if p["type"] == "pcb_trace"}


def trace_side(t):
    cn = t.get("connection_name", "")
    st = t.get("source_trace_id")
    r = None
    if st and st in c.trace_root:
        r = c.trace_root[st]
    elif cn in c.nets:
        r = c.root_of_net(cn)
    elif cn in c.trace_root:
        r = c.trace_root[cn]
    else:
        pts = [(pt["x"]) for pt in t["route"]]
        return "EMS" if sum(pts) / len(pts) < 0 else "MCU"
    return side_of_root(r)


for t in traces.values():
    side = trace_side(t)
    rt = t["route"]
    for a, b in zip(rt, rt[1:]):
        if a.get("route_type") == "wire" and b.get("route_type") == "wire" and a["layer"] == b["layer"]:
            w = a.get("width", 0.15)
            if (a["x"], a["y"]) == (b["x"], b["y"]):
                g = Point(a["x"], a["y"]).buffer(w / 2)
            else:
                g = LineString([(a["x"], a["y"]), (b["x"], b["y"])]).buffer(w / 2)
            add(side, [a["layer"]], g, "trace")
for v in (p for p in cj if p["type"] == "pcb_via"):
    t = traces.get(v["pcb_trace_id"])
    side = trace_side(t) if t else ("EMS" if v["x"] < 0 else "MCU")
    add(side, ["top", "bottom"], Point(v["x"], v["y"]).buffer(v["outer_diameter"] / 2), "via")
for p in (p for p in cj if p["type"] == "pcb_copper_pour"):
    r = c.root_of_net(p["source_net_id"])
    side = side_of_root(r)
    b = p["brep_shape"]
    g = Polygon([(v["x"], v["y"]) for v in b["outer_ring"]["vertices"]],
                [[(v["x"], v["y"]) for v in ring["vertices"]] for ring in b.get("inner_rings", [])])
    if not g.is_valid:
        g = g.buffer(0)
    add(side, [p["layer"]], g, "pour")

print("copper items:", len(items), "(EMS %d, MCU %d)" % (sum(1 for i in items if i[0] == "EMS"), sum(1 for i in items if i[0] == "MCU")))
ok = True


def mind(layer, skip_opto):
    E = [g for s, l, g, tg in items if s == "EMS" and l == layer and not (skip_opto and tg == "opto")]
    M = [g for s, l, g, tg in items if s == "MCU" and l == layer and not (skip_opto and tg == "opto")]
    ue, um = unary_union(E), unary_union(M)
    d = ue.distance(um)
    # nearest points
    from shapely.ops import nearest_points
    pa, pb = nearest_points(ue, um)
    return d, pa, pb


for layer in ("top", "bottom"):
    d, pa, pb = mind(layer, True)
    d2, pa2, pb2 = mind(layer, False)
    st = "OK  " if d >= LIMIT - 1e-6 else "FAIL"
    if st == "FAIL":
        ok = False
    print("%s %-6s min EMS-MCU copper distance (excl. opto pads): %.3f mm  at (%.2f,%.2f)-(%.2f,%.2f)" % (st, layer, d, pa.x, pa.y, pb.x, pb.y))
    print("     %-6s incl. opto pads (OC1/OC2 pad rows): %.3f mm  at (%.2f,%.2f)-(%.2f,%.2f)" % (layer, d2, pa2.x, pa2.y, pb2.x, pb2.y))

optoE = unary_union([g for s, l, g, tg in items if s == "EMS" and tg == "opto" and l == "top"])
optoM = unary_union([g for s, l, g, tg in items if s == "MCU" and tg == "opto" and l == "top"])
print("     opto pad rows: EMS pads vs MCU pads distance %.3f mm (by design, bridged by the opto body)" % optoE.distance(optoM))
# copper vs isolation slots and barrier
slots = [Polygon(box(p["center"]["x"] - p["width"] / 2, p["center"]["y"] - p["height"] / 2, p["center"]["x"] + p["width"] / 2, p["center"]["y"] + p["height"] / 2)) for p in cj if p["type"] == "pcb_cutout"]
bad = [(s, l, tg) for s, l, g, tg in items for sl in slots if g.intersects(sl)]
print("%s copper inside isolation slots: %d" % ("OK  " if not bad else "FAIL", len(bad)))
ok &= not bad
# copper of a side across the barrier line x=0 (other than opto pads are nowhere near x=0)
cross = [(s, l, tg) for s, l, g, tg in items if (s == "EMS" and g.bounds[2] > 0) or (s == "MCU" and g.bounds[0] < 0)]
print("%s copper objects crossing x=0 into the other side: %d %s" % ("OK  " if not cross else "FAIL", len(cross), cross[:5]))
ok &= not cross
# pours near barrier
for s in ("EMS", "MCU"):
    for layer in ("top", "bottom"):
        pg = unary_union([g for ss, l, g, tg in items if ss == s and l == layer and tg == "pour"])
        b = pg.bounds
        print("     pour %s %-6s x-range [%.2f, %.2f]" % (s, layer, b[0], b[2]))
# antenna keepout
for k in (p for p in cj if p["type"] == "pcb_keepout"):
    kg = box(k["center"]["x"] - k["width"] / 2, k["center"]["y"] - k["height"] / 2, k["center"]["x"] + k["width"] / 2, k["center"]["y"] + k["height"] / 2)
    inside = [(s, l, tg) for s, l, g, tg in items if g.intersects(kg) and l in k["layers"]]
    print("%s copper in keepout (%.1f x %.1f at %.1f,%.1f): %d %s" % ("OK  " if not inside else "FAIL", k["width"], k["height"], k["center"]["x"], k["center"]["y"], len(inside), sorted({i[2] for i in inside})))
    ok &= not inside
# mounting holes vs other side copper (>= 6 mm)
for h in (p for p in cj if p["type"] == "pcb_hole" and p.get("hole_diameter", 0) > 3):
    side = "EMS" if h["x"] < 0 else "MCU"
    other = unary_union([g for s, l, g, tg in items if s != side and tg != "pour"])
    d = Point(h["x"], h["y"]).buffer(h["hole_diameter"] / 2).distance(other)
    st = "OK  " if d >= LIMIT - 1e-6 else "FAIL"
    ok &= st == "OK  "
    print("%s mounting hole (%.1f,%.1f) %s side: %.2f mm to other side's copper (non-pour)" % (st, h["x"], h["y"], side, d))
print("ISOLATION OK" if ok else "ISOLATION FAILED")
sys.exit(0 if ok else 1)
