#!/usr/bin/env python3
"""Fabrication check of the routed board: Gerber zip + drill + dist/index/circuit.json (geometry).

Usage: python3 scripts/check_fab.py [fab/EMSinterface_V2.0-gerbers.zip] [dist/index/circuit.json]
Exit code 0 = all checks pass, 1 = at least one FAIL.  Needs shapely.

Checks
 G1 Gerber: trace draws (D01 outside regions, polarity dark) present on F_Cu and B_Cu; draw widths listed,
    smallest draw >= MIN_W_SIGNAL; pours (G36 regions) present.
 G2 Drill: via tools (ViaDrill) >= MIN_VIA_DRILL, hit count == pcb_via count of circuit.json.
 C1 Annular ring of vias and plated holes >= MIN_ANNULAR (circuit.json).
 C2 Trace width per net class: power/bus/SW nets >= MIN_W_POWER, all others >= MIN_W_SIGNAL (wire segments
    shorter than STUB_LEN that are narrower are only warned: they are pad-entry stubs of the autorouter).
 C3 Copper clearance between different nets (traces, pads, vias, plated holes, pours; per layer) >= MIN_CLEARANCE.
    Pad-to-pad inside one component is a library property and is not reported.
 C4 No copper inside <cutout>s (slots), no copper inside <keepout>s (antenna) except the keepout's own component,
    copper-to-NPTH-hole and copper-to-board-edge distance.
 C5 Every net is physically connected by copper (traces/vias/pours) = no open/unrouted connection; the USB-C pads
    are listed one by one (both D+ pads, both D- pads, all VBUS/GND pads, CC1/CC2, shell legs).
"""
import csv, collections, io, math, os, re, sys, tempfile, zipfile, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from netlib import load, Conn
from shapely.geometry import Point, LineString, Polygon, box, MultiPolygon
from shapely.affinity import rotate
from shapely.strtree import STRtree

# ---------------- rules ----------------
MIN_VIA_DRILL = 0.30
MIN_ANNULAR = 0.13
MIN_CLEARANCE = 0.20
MIN_W_POWER = 0.40
MIN_W_SIGNAL = 0.20
STUB_LEN = 0.5          # mm; narrower wire segments shorter than this are warnings only
MIN_EDGE = 0.30         # copper to board edge
MIN_HOLE = 0.25         # copper to NPTH hole edge (other components)
TOL = 1e-3
POWER_NETS = {"VBUS", "V3V3", "GND", "GND_EMS", "V5_EMS", "EMS_VIN"}
# nets that contain one of these pins are "bus/SW" nets (width >= MIN_W_POWER): buck SW node U2.6, bus path
BUS_PINS = ["U2.6", "F1.1", "F1.2", "F2.1", "F2.2", "L1.1", "L1.2", "L2.1", "L2.2", "D1.1", "D1.2", "D2.1", "D2.2",
            "D3.1", "D3.2", "D4.1", "D4.2", "R2.1", "R2.2", "R3.1", "R3.2", "R4.1", "R4.2", "Q1.3", "P1.1", "P1.2"]
USB_REF = "J2"

gz = sys.argv[1] if len(sys.argv) > 1 else "fab/EMSinterface_V2.0-gerbers.zip"
cjp = sys.argv[2] if len(sys.argv) > 2 else "dist/index/circuit.json"
fails, warns = [], []


def FAIL(msg):
    fails.append(msg)
    print("FAIL", msg)


def WARN(msg):
    warns.append(msg)
    print("WARN", msg)


def OK(msg):
    print("OK  ", msg)


# =====================================================================
# G1/G2: Gerber + drill
# =====================================================================
NOGERBER = gz in ("-", "none")   # geometry-only mode (e.g. for tscircuit setting experiments)
tmp = tempfile.mkdtemp(prefix="checkfab_")
if not NOGERBER:
    with zipfile.ZipFile(gz) as z:
        z.extractall(tmp)
print("== Gerber / drill (%s) ==" % gz)


def parse_gerber(path):
    ap, cur, pol, reg = {}, None, "D", False
    draws, flashes, regions = collections.Counter(), 0, 0
    for ln in open(path):
        ln = ln.strip()
        m = re.match(r"%ADD(\d+)(\w+),([^*]*)\*%", ln)
        if m:
            ap[m.group(1)] = (m.group(2), m.group(3))
            continue
        if ln.startswith("%LPD"):
            pol = "D"
        elif ln.startswith("%LPC"):
            pol = "C"
        if ln.startswith("G36"):
            reg = True
            if pol == "D":
                regions += 1
        elif ln.startswith("G37"):
            reg = False
        m = re.match(r"D(\d+)\*$", ln)
        if m and int(m.group(1)) >= 10:
            cur = m.group(1)
            continue
        if reg:
            continue
        if ln.endswith("D01*") and pol == "D" and cur in ap:
            kind, par = ap[cur]
            if kind == "C":
                draws[float(par.split("X")[0])] += 1
        elif ln.endswith("D03*") and pol == "D":
            flashes += 1
    return draws, flashes, regions


for layer in (() if NOGERBER else ("F_Cu", "B_Cu")):
    d, fl, rg = parse_gerber(os.path.join(tmp, layer + ".gbr"))
    n = sum(d.values())
    if n == 0:
        FAIL("%s.gbr has NO trace draws (export from the routed circuit.json!)" % layer)
    else:
        mw = min(d)
        msg = "%s: %d trace draws, widths %s, %d flashes, %d pour regions" % (
            layer, n, {k: v for k, v in sorted(d.items())}, fl, rg)
        if mw < MIN_W_SIGNAL - TOL:
            FAIL(msg + "  smallest draw %.3f < %.2f" % (mw, MIN_W_SIGNAL))
        else:
            OK(msg)

# drill files
via_tools, via_hits = {}, 0
cur, tools, kinds = None, {}, {}
drl = os.path.join(tmp, "drill-L1-L2.drl")
lastfn = None
for ln in (open(drl) if not NOGERBER else []):
    ln = ln.strip()
    m = re.search(r"TA\.AperFunction,(\S+)", ln)
    if m:
        lastfn = m.group(1)
    m = re.match(r"T(\d+)C([\d.]+)", ln)
    if m:
        tools[m.group(1)] = float(m.group(2))
        kinds[m.group(1)] = lastfn
        continue
    m = re.match(r"T(\d+)$", ln)
    if m:
        cur = m.group(1)
        continue
    if re.match(r"X", ln) and cur:
        if "ViaDrill" in (kinds.get(cur) or ""):
            via_tools[tools[cur]] = via_tools.get(tools[cur], 0) + 1
            via_hits += 1
if NOGERBER:
    via_hits = None
elif not via_hits:
    FAIL("drill-L1-L2.drl has no via drills (ViaDrill)")
else:
    bad = {d: n for d, n in via_tools.items() if d < MIN_VIA_DRILL - TOL}
    (FAIL if bad else OK)("via drills: %s (min %.2f)%s" % (via_tools, MIN_VIA_DRILL, "  TOO SMALL: %s" % bad if bad else ""))

# =====================================================================
# circuit.json geometry
# =====================================================================
print("\n== circuit.json geometry (%s) ==" % cjp)
cj = load(cjp)
conn = Conn(cj)
pcb_port = {e["pcb_port_id"]: e for e in cj if e["type"] == "pcb_port"}
net_name = {}   # root -> display name


def root_of_pcbport(pid):
    p = pcb_port.get(pid)
    if not p:
        return None
    return conn.root_of_port(p.get("source_port_id"))


pin_of_root = collections.defaultdict(set)
for g, d in conn.groups.items():
    net_name[g] = "/".join(sorted(d["names"])) or ("net(" + ",".join(sorted(d["pins"]))[:30] + ")")


def pin_str(pid):
    p = pcb_port.get(pid)
    if not p:
        return None
    r = conn.ports.get(p.get("source_port_id"))
    return "%s.%s" % r if r else None


# net classes
bus_roots = set()
pin2root = {}
for g, d in conn.groups.items():
    for p in d["pins"]:
        pin2root[p] = g
for p in BUS_PINS:
    if p in pin2root:
        bus_roots.add(pin2root[p])


def min_width_of(root):
    if root is None:
        return MIN_W_SIGNAL
    nm = conn.groups[root]["names"] if root in conn.groups else set()
    if nm & POWER_NETS or root in bus_roots:
        return MIN_W_POWER
    return MIN_W_SIGNAL


def rect_poly(cx, cy, w, h, rot=0):
    p = box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    return rotate(p, rot, origin=(cx, cy)) if rot else p


class Item:
    __slots__ = ("id", "kind", "net", "layer", "geom", "comp", "label")

    def __init__(self, id, kind, net, layer, geom, comp=None, label=""):
        self.id, self.kind, self.net, self.layer, self.geom, self.comp, self.label = id, kind, net, layer, geom, comp, label


items = []        # Item per layer (a via/PTH contributes one item per layer, same id)
annular = []      # (label, ring)
nid = [0]


def add(kind, net, layers, geom_fn, comp=None, label=""):
    nid[0] += 1
    for l in layers:
        items.append(Item(nid[0], kind, net, l, geom_fn, comp, label))
    return nid[0]


unconn = [0]


def pad_net(e):
    r = root_of_pcbport(e.get("pcb_port_id"))
    if r is None:
        unconn[0] += 1
        return ("unconn", e.get("pcb_smtpad_id") or e.get("pcb_plated_hole_id"))
    return r


pad_pin = {}   # item id -> "Ref.pin"
for e in cj:
    t = e["type"]
    if t == "pcb_smtpad":
        sh = e["shape"]
        x, y = e["x"], e["y"]
        if sh == "rect":
            g = rect_poly(x, y, e["width"], e["height"])
        elif sh == "rotated_rect":
            g = rect_poly(x, y, e["width"], e["height"], e.get("ccw_rotation", 0))
        elif sh == "circle":
            g = Point(x, y).buffer(e["radius"], 24)
        elif sh in ("pill", "rotated_pill"):
            w, h = e["width"], e["height"]
            r = min(w, h) / 2
            if w >= h:
                g = LineString([(x - (w - h) / 2, y), (x + (w - h) / 2, y)]).buffer(r, 12)
            else:
                g = LineString([(x, y - (h - w) / 2), (x, y + (h - w) / 2)]).buffer(r, 12)
            if sh == "rotated_pill" and e.get("ccw_rotation"):
                g = rotate(g, e["ccw_rotation"], origin=(x, y))
        elif sh == "polygon":
            g = Polygon([(p["x"], p["y"]) for p in e["points"]])
        else:
            g = Point(x, y).buffer(0.5)
        i = add("pad", pad_net(e), [e["layer"]], g, e.get("pcb_component_id"), pin_str(e.get("pcb_port_id")) or "")
        pad_pin[i] = pin_str(e.get("pcb_port_id"))
    elif t == "pcb_plated_hole":
        sh, x, y = e["shape"], e["x"], e["y"]
        lbl = pin_str(e.get("pcb_port_id")) or ""
        if sh == "circle":
            g = Point(x, y).buffer(e["outer_diameter"] / 2, 24)
            ring = (e["outer_diameter"] - e["hole_diameter"]) / 2
        elif sh in ("pill", "rotated_pill"):
            w, h = e["outer_width"], e["outer_height"]
            r = min(w, h) / 2
            if w >= h:
                g = LineString([(x - (w - h) / 2, y), (x + (w - h) / 2, y)]).buffer(r, 12)
            else:
                g = LineString([(x, y - (h - w) / 2), (x, y + (h - w) / 2)]).buffer(r, 12)
            if e.get("ccw_rotation"):
                g = rotate(g, e["ccw_rotation"], origin=(x, y))
            ring = min((w - e["hole_width"]) / 2, (h - e["hole_height"]) / 2)
        elif "rect_pad_width" in e:
            g = rect_poly(x + e.get("hole_offset_x", 0) * 0, y, e["rect_pad_width"], e["rect_pad_height"], e.get("rect_ccw_rotation", 0))
            hd = e.get("hole_diameter") or min(e.get("hole_width", 0), e.get("hole_height", 0))
            ring = (min(e["rect_pad_width"], e["rect_pad_height"]) - hd) / 2
        else:
            g = Point(x, y).buffer(max(e.get("outer_diameter", 1.0), 1.0) / 2)
            ring = 9
        i = add("pth", pad_net(e), ["top", "bottom"], g, e.get("pcb_component_id"), lbl)
        pad_pin[i] = pin_str(e.get("pcb_port_id"))
        annular.append(("plated hole %s @(%.2f,%.2f)" % (lbl, x, y), ring))

# traces: net from connected ports, fallback connection_name
trace_net = {}
wire_segments = []   # (root, layer, width, length, (x1,y1,x2,y2))
for e in cj:
    if e["type"] != "pcb_trace":
        continue
    root = None
    for pid in e.get("connectsTo", []) or []:
        root = root_of_pcbport(pid)
        if root is not None:
            break
    if root is None:
        cn = e.get("connection_name", "")
        if cn in conn.nets:
            root = conn.root_of_net(cn)
    trace_net[e["pcb_trace_id"]] = root if root is not None else ("trace", e["pcb_trace_id"])
    pts = e["route"]
    for a, b in zip(pts, pts[1:]):
        if a["route_type"] == "wire" and b["route_type"] == "wire" and a["layer"] == b["layer"]:
            ln = math.hypot(b["x"] - a["x"], b["y"] - a["y"])
            w = b.get("width", a["width"])
            wire_segments.append((trace_net[e["pcb_trace_id"]], a["layer"], w, ln, (a["x"], a["y"], b["x"], b["y"])))
            if ln > 1e-9:
                add("trace", trace_net[e["pcb_trace_id"]], [a["layer"]],
                    LineString([(a["x"], a["y"]), (b["x"], b["y"])]).buffer(w / 2, 8), None, "trace")
            else:
                add("trace", trace_net[e["pcb_trace_id"]], [a["layer"]], Point(a["x"], a["y"]).buffer(w / 2, 8), None, "trace")
n_via = 0
for e in cj:
    if e["type"] == "pcb_via":
        n_via += 1
        net = trace_net.get(e.get("pcb_trace_id"), ("via", e["pcb_via_id"]))
        add("via", net, ["top", "bottom"], Point(e["x"], e["y"]).buffer(e["outer_diameter"] / 2, 16), None, "via")
        annular.append(("via @(%.2f,%.2f) %.2f/%.2f" % (e["x"], e["y"], e["hole_diameter"], e["outer_diameter"]),
                        (e["outer_diameter"] - e["hole_diameter"]) / 2))
        if e["hole_diameter"] < MIN_VIA_DRILL - TOL:
            pass  # reported below with the other via checks
pour_geoms = []
for e in cj:
    if e["type"] == "pcb_copper_pour":
        b = e["brep_shape"]
        pg = Polygon([(v["x"], v["y"]) for v in b["outer_ring"]["vertices"]],
                     [[(v["x"], v["y"]) for v in r["vertices"]] for r in b.get("inner_rings", [])])
        if not pg.is_valid:
            pg = pg.buffer(0)
        net = conn.root_of_net(e["source_net_id"]) if e.get("source_net_id") else None
        add("pour", net if net is not None else ("pour", e["pcb_copper_pour_id"]), [e["layer"]], pg, None, "pour")
        pour_geoms.append(pg)

# convert geometry (we stored geometry objects directly)
for it in items:
    pass

# ---- via checks ----
vias = [e for e in cj if e["type"] == "pcb_via"]
print("vias: %d in circuit.json, %s in drill file" % (len(vias), via_hits))
if via_hits is not None and len(vias) != via_hits:
    FAIL("via count mismatch circuit.json %d vs drill %d" % (len(vias), via_hits))
sv = {(e["hole_diameter"], e["outer_diameter"]) for e in vias}
bad = [s for s in sv if s[0] < MIN_VIA_DRILL - TOL]
(FAIL if bad else OK)("via drill/pad sizes in circuit.json: %s (need drill >= %.2f)" % (sorted(sv), MIN_VIA_DRILL))
badr = [(l, r) for l, r in annular if r < MIN_ANNULAR - TOL]
if badr:
    agg = collections.Counter(l.split(" @")[0] + " " + (l.split(" ")[-1] if l.startswith("via") else "") for l, r in badr)
    FAIL("annular ring < %.2f mm on %d holes, worst %.3f: %s" % (MIN_ANNULAR, len(badr), min(r for _, r in badr), dict(agg)))
else:
    OK("annular ring of %d vias/plated holes >= %.2f (min %.3f)" % (len(annular), MIN_ANNULAR, min(r for _, r in annular)))

# ---- trace widths per net class ----
viol = collections.defaultdict(list)
stubs = collections.defaultdict(list)
for root, layer, w, ln, seg in wire_segments:
    need = min_width_of(root if not isinstance(root, tuple) else None)
    if w < need - TOL:
        (viol if ln >= STUB_LEN else stubs)[(root, need)].append((w, ln, layer))
tot = collections.Counter()
for (root, need), l in viol.items():
    tot[need] += len(l)
nm = lambda r: net_name.get(r, str(r)) if not isinstance(r, tuple) else str(r)
if viol:
    FAIL("trace width: %d segments too narrow (power/bus/SW >= %.2f, others >= %.2f) on %d nets; widths used: %s" % (
        sum(len(l) for l in viol.values()), MIN_W_POWER, MIN_W_SIGNAL, len(viol),
        dict(sorted(collections.Counter(round(s[2], 3) for s in wire_segments).items()))))
    for (root, need), l in sorted(viol.items(), key=lambda kv: -len(kv[1]))[:12]:
        print("       %-28s need %.2f, got min %.3f in %d segments (%.1f mm total)" % (
            nm(root), need, min(x[0] for x in l), len(l), sum(x[1] for x in l)))
else:
    OK("trace widths ok")
if stubs:
    WARN("%d short pad-entry stubs (< %.1f mm) narrower than the class minimum (autorouter shrinks the wire at narrow pads)" % (
        sum(len(l) for l in stubs.values()), STUB_LEN))

# ---- clearance (per layer) ----
print()
geoms_by_layer = collections.defaultdict(list)
for it in items:
    geoms_by_layer[it.layer].append(it)
clear_viol = {}
for layer, its in geoms_by_layer.items():
    tree = STRtree([i.geom for i in its])
    for ia, a in enumerate(its):
        for ib in tree.query(a.geom, predicate="dwithin", distance=MIN_CLEARANCE):
            if ib <= ia:
                continue
            b = its[ib]
            if a.net == b.net:
                continue
            if a.kind in ("pad", "pth") and b.kind in ("pad", "pth") and a.comp == b.comp:
                continue
            if a.id == b.id:
                continue
            d = a.geom.distance(b.geom)
            if d < MIN_CLEARANCE - TOL:
                key = (layer, a.kind + "/" + b.kind, nm(a.net), nm(b.net))
                cv = clear_viol.setdefault(key, [d, 0, a.geom.centroid])
                cv[1] += 1
                if d < cv[0]:
                    cv[0], cv[2] = d, a.geom.centroid
if clear_viol:
    FAIL("copper clearance < %.2f mm: %d net/kind pairs, worst %.3f mm" % (
        MIN_CLEARANCE, len(clear_viol), min(v[0] for v in clear_viol.values())))
    for k, v in sorted(clear_viol.items(), key=lambda kv: kv[1][0])[:12]:
        print("       %s %-10s %s <-> %s: min %.3f mm (%d pairs) near (%.1f,%.1f)" % (k[0], k[1], k[2], k[3], v[0], v[1], v[2].x, v[2].y))
else:
    OK("copper clearance >= %.2f mm between all different nets (traces, pads, vias, pours)" % MIN_CLEARANCE)

# ---- cutouts / keepouts / holes / board edge ----
cut = []
for e in cj:
    if e["type"] == "pcb_cutout":
        if e["shape"] == "rect":
            cut.append((e.get("pcb_cutout_id"), rect_poly(e["center"]["x"], e["center"]["y"], e["width"], e["height"], e.get("rotation", 0))))
        elif e["shape"] == "circle":
            cut.append((e.get("pcb_cutout_id"), Point(e["center"]["x"], e["center"]["y"]).buffer(e["radius"], 24)))
        elif e["shape"] == "polygon":
            cut.append((e.get("pcb_cutout_id"), Polygon([(p["x"], p["y"]) for p in e["points"]])))
bad = []
for cid, cg in cut:
    for it in items:
        if it.geom.intersects(cg):
            bad.append("%s %s on %s" % (cid, it.kind + (" " + it.label if it.label else ""), it.layer))
(FAIL if bad else OK)("no copper in %d cutout(s)%s" % (len(cut), ": " + "; ".join(sorted(set(bad))[:8]) if bad else ""))
keeps = [e for e in cj if e["type"] == "pcb_keepout"]
bad = []
for k in keeps:
    kg = rect_poly(k["center"]["x"], k["center"]["y"], k["width"], k["height"]) if k["shape"] == "rect" else \
        Point(k["center"]["x"], k["center"]["y"]).buffer(k["radius"])
    for it in items:
        if it.layer in k["layers"] and it.geom.intersects(kg) and not (it.comp and it.comp == k.get("pcb_component_id")):
            bad.append("%s on %s (%s)" % (it.kind, it.layer, nm(it.net)))
(FAIL if bad else OK)("no copper in %d keepout(s)/antenna area%s" % (len(keeps), ": " + "; ".join(sorted(set(bad))[:8]) if bad else ""))
board = next(e for e in cj if e["type"] == "pcb_board")
outline = Polygon([(p["x"], p["y"]) for p in board["outline"]]) if board.get("outline") else rect_poly(
    board["center"]["x"], board["center"]["y"], board["width"], board["height"])
bad = []
for it in items:
    if not outline.contains(it.geom):
        bad.append("%s %s outside board" % (it.kind, it.label))
    elif outline.exterior.distance(it.geom) < MIN_EDGE - TOL:
        bad.append("%s %s edge distance %.2f on %s" % (it.kind, it.label, outline.exterior.distance(it.geom), it.layer))
if bad:
    c = collections.Counter(b.split(" ")[0] for b in bad)
    (WARN if all(b.startswith("pad") or b.startswith("pth") for b in bad) else FAIL)(
        "copper closer than %.2f mm to board edge: %s e.g. %s" % (MIN_EDGE, dict(c), "; ".join(sorted(set(bad))[:5])))
else:
    OK("copper >= %.2f mm from board edge" % MIN_EDGE)
holes = [e for e in cj if e["type"] == "pcb_hole"]
bad = []
for h in holes:
    hg = Point(h["x"], h["y"]).buffer(h.get("hole_diameter", 0.6) / 2, 24)
    for it in items:
        if it.geom.distance(hg) < MIN_HOLE - TOL and not (it.comp and it.comp == h.get("pcb_component_id")):
            bad.append("%s %s %s near NPTH (%.1f,%.1f) d=%.2f" % (it.kind, it.label, it.layer, h["x"], h["y"], it.geom.distance(hg)))
(FAIL if bad else OK)("copper >= %.2f mm from %d NPTH holes%s" % (MIN_HOLE, len(holes), ": " + "; ".join(sorted(set(bad))[:5]) if bad else ""))

# ---- physical connectivity ----
print()
par = {}


def find(x):
    par.setdefault(x, x)
    while par[x] != x:
        par[x] = par[par[x]]
        x = par[x]
    return x


def union(a, b):
    par[find(a)] = find(b)


for layer, its in geoms_by_layer.items():
    tree = STRtree([i.geom for i in its])
    for ia, a in enumerate(its):
        find(a.id)
        for ib in tree.query(a.geom, predicate="intersects"):
            b = its[ib]
            if b.id != a.id and (a.net == b.net or isinstance(a.net, tuple) or isinstance(b.net, tuple)):
                union(a.id, b.id)
# pad items: pin string -> item ids
pin_items = collections.defaultdict(list)
for i, p in pad_pin.items():
    if p:
        pin_items[p].append(i)
opens = []
for g, d in conn.groups.items():
    pins = [p for p in d["pins"] if p in pin_items]
    if len(pins) < 2:
        continue
    comps = collections.defaultdict(list)
    for p in pins:
        comps[find(pin_items[p][0])].append(p)
    if len(comps) > 1:
        opens.append((net_name[g], sorted(comps.values(), key=len)))
if opens:
    FAIL("%d net(s) not fully connected by copper (unrouted / islands)" % len(opens))
    for n, cs in opens[:15]:
        print("       %-28s %d islands, smallest: %s" % (n, len(cs), cs[0][:6]))
else:
    OK("all %d nets are physically connected by copper" % sum(1 for g, d in conn.groups.items() if len(d["pins"]) > 1))

# ---- USB-C pads ----
usb = {}
for e in cj:
    if e["type"] in ("pcb_smtpad", "pcb_plated_hole"):
        p = pin_str(e.get("pcb_port_id"))
        if p and p.startswith(USB_REF + "."):
            usb[int(p.split(".")[1])] = e
LABEL = {1: "GND_L", 2: "VBUS_L", 3: "CC2", 4: "SBU1", 5: "DP_L", 6: "DN_L", 7: "DP_R", 8: "DN_R", 9: "CC1", 10: "SBU2",
         11: "VBUS_R", 12: "GND_R", 13: "SH1", 14: "SH2", 15: "SH3", 16: "SH4"}
EXPECT = {1: "GND", 2: "VBUS", 3: "CC2", 5: "USB_DP", 6: "USB_DN", 7: "USB_DP", 8: "USB_DN", 9: "CC1", 11: "VBUS", 12: "GND",
          13: "SHELL", 14: "SHELL", 15: "SHELL", 16: "SHELL"}
if not usb:
    WARN("no %s pads found" % USB_REF)
else:
    bad = []
    for n in sorted(usb):
        p = "%s.%d" % (USB_REF, n)
        root = pin2root.get(p)
        grp_pins = [q for q in conn.groups[root]["pins"] if q != p] if root is not None else []
        names = sorted(conn.groups[root]["names"]) if root is not None else []
        ids = pin_items.get(p, [])
        iid = ids[0] if ids else None
        reach = 0
        if iid is not None:
            r = find(iid)
            reach = sum(1 for q in grp_pins if q in pin_items and find(pin_items[q][0]) == r)
        status = "connected to %d other pad(s)" % reach if reach else ("NC (intentional)" if n in (4, 10) else "NOT CONNECTED")
        exp = EXPECT.get(n)
        netok = (exp is None and root is None) or (exp is not None and exp in names) or (exp in ("CC1", "CC2", "SHELL") and root is not None)
        if n not in (4, 10) and (not reach or not netok):
            bad.append("%s %s" % (LABEL[n], "net %s (expected %s), %s" % (names or "-", exp, status)))
        print("       %s.%-2d %-7s net=%-8s %s" % (USB_REF, n, LABEL[n], "/".join(names) or "-", status))
    (FAIL if bad else OK)("USB-C pads%s" % (": " + "; ".join(bad) if bad else " all on the right nets and connected by copper"))

print("\n%d FAIL, %d WARN" % (len(fails), len(warns)))
print("ALL FAB CHECKS OK" if not fails else "FAB CHECKS FAILED")
sys.exit(1 if fails else 0)
