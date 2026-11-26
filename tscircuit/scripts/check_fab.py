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
 G5 Silkscreen: glyph height/stroke MEASURED in the silk Gerber (>= 1.0 mm / 0.16 mm), texts vs pads/vias/holes/slots/edge/other texts, pin-1 + polarity marks.
 G8 Pour slivers < 0.15 mm cleared in the copper Gerbers (scripts/slivers.py), no island created; G9 C23 within 2 mm of the ESP32 3V3 pad; Gerber file names (JLC/KiCad).
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
CLEAR_TOL = 0.0005      # mm numeric tolerance of the router geometry (gap 0.198 counts as 0.2)
MIN_W_POWER = 0.50      # VBUS, VBUS_F (behind PTC F3), V3V3, V5_EMS, EMS_VIN
MIN_W_BUS = 0.40        # bus path, buck SW node
MIN_W_GND = 0.25        # GND / GND_EMS stitching traces: the solid pours on both layers carry the return current
MIN_W_SIGNAL = 0.25
MIN_W_NECK = 0.25       # power/bus segments may neck down to this ...
NECK_DIST = 1.5         # ... within this distance of a pad of a fine-pitch part (pad pitch <= FINE_PITCH)
FINE_PITCH = 1.27
MIN_CLEARANCE_HARD = 0.15  # allowed instead of MIN_CLEARANCE only at fine-pitch pads
STUB_LEN = 0.5          # mm; narrower wire segments shorter than this are warnings only
MIN_EDGE = 0.30         # copper to board edge
MIN_POUR_EDGE = 0.50    # pour to board edge / slots / NPTH
MIN_HOLE = 0.25         # copper to the NPTH mounting holes
MIN_HOLE_DIFF = 0.50    # hole edge to hole edge, different nets (JLC hole-to-hole)
MIN_HOLE_SAME = 0.50    # hole edge to hole edge, same net (R7 m3: JLC recommends 0.5 mm for all pairs; router param minViaHoleEdgeToViaHoleEdgeClearance=0.5mm)
MIN_SILK_W = 0.16       # JLC silkscreen line width (min 0.153; R7 M1)
MIN_SILK_EDGE = 0.30    # silk text envelope to the board edge
MIN_SILK_H = 1.0        # JLC silkscreen character height
MAX_SILK_PAD = 0.30     # mm2 of silkscreen of ONE item over exposed pads (JLC clips silk on pads, but keep it off; the 0805 outlines of tightly packed neighbours may touch)
MIN_PASTE = 0.90        # paste aperture / pad area, smallest allowed (largest allowed 1.0 + tolerance)
MIN_PEG = 0.15          # copper to the 0.6 mm NPTH positioning pegs inside a part footprint (J2)
TOL = 1e-3
POWER_NETS = {"VBUS", "VBUS_F", "V3V3", "V5_EMS", "EMS_VIN"}
GND_NETS = {"GND", "GND_EMS"}
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
        zip_names = z.namelist()
    # the zip carries JLC/KiCad-style names (<proj>-F_Cu.gtl ...); the parsers below use the tscircuit names -> copy under the old names
    JLC_NAMES = {"F_Cu.gbr": "F_Cu.gtl", "B_Cu.gbr": "B_Cu.gbl", "F_Mask.gbr": "F_Mask.gts", "B_Mask.gbr": "B_Mask.gbs",
                 "F_Paste.gbr": "F_Paste.gtp", "B_Paste.gbr": "B_Paste.gbp", "F_SilkScreen.gbr": "F_Silkscreen.gto",
                 "B_SilkScreen.gbr": "B_Silkscreen.gbo", "Edge_Cuts.gbr": "Edge_Cuts.gm1", "drill-L1-L2.drl": "PTH.drl", "drill_npth.drl": "NPTH.drl"}
    SILK_FILE = {}
    for old, new in JLC_NAMES.items():
        hit = [n for n in zip_names if n.endswith("-" + new)]
        if hit:
            import shutil
            shutil.copy(os.path.join(tmp, hit[0]), os.path.join(tmp, old))
        elif old not in zip_names:
            pass
print("== Gerber / drill (%s) ==" % gz)
if not NOGERBER:
    miss = [new for old, new in JLC_NAMES.items() if not any(n.endswith("-" + new) for n in zip_names)]
    bad_names = [n for n in zip_names if not any(n.endswith("-" + new) for new in JLC_NAMES.values())]
    (FAIL if miss or bad_names else OK)("Gerber file names follow the JLC/KiCad pattern <project>-F_Cu.gtl ... -PTH.drl, -NPTH.drl%s" % (
        " (missing %s, unexpected %s)" % (miss, bad_names) if miss or bad_names else " (%d files)" % len(zip_names)))


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
    if nm & POWER_NETS:
        return MIN_W_POWER
    if nm & GND_NETS:
        return MIN_W_GND
    if root in bus_roots:
        return MIN_W_BUS
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
drill_holes = []     # (x, y, hole diameter, net, label) of vias and round plated holes (hole-to-hole check G4)
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
        if e.get("hole_diameter"):
            drill_holes.append((x, y, e["hole_diameter"], pad_net(e), "PTH " + lbl))

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
    if root is None and e.get("source_trace_id") in conn.trace_root:
        root = conn.trace_root[e["source_trace_id"]]
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
        net = trace_net.get(e.get("pcb_trace_id"))
        if net is None and e.get("source_net_id"):
            net = conn.root_of_net(e["source_net_id"])
        if net is None:
            net = ("via", e["pcb_via_id"])
        add("via", net, ["top", "bottom"], Point(e["x"], e["y"]).buffer(e["outer_diameter"] / 2, 16), None, "via")
        drill_holes.append((e["x"], e["y"], e["hole_diameter"], net, "via"))
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

# ---- fine-pitch pads (pad centre pitch <= FINE_PITCH to another pad of the same part): USB-C, ESP32, SOIC, SOT-23 ... ----
by_comp = collections.defaultdict(list)
for it in items:
    if it.kind == "pad" and it.comp:
        by_comp[it.comp].append(it)
fine_ids = set()
for comp, its in by_comp.items():
    for a in its:
        ca = a.geom.centroid
        for b in its:
            if b.id != a.id and b.layer == a.layer and math.hypot(ca.x - b.geom.centroid.x, ca.y - b.geom.centroid.y) <= FINE_PITCH + 1e-6:
                fine_ids.add(a.id)
                break
fine_geoms = [it.geom for it in items if it.id in fine_ids]
fine_tree = STRtree(fine_geoms) if fine_geoms else None
print("fine-pitch pads (pitch <= %.2f mm): %d" % (FINE_PITCH, len(fine_ids)))


def near_fine_pad(geom, dist):
    return bool(fine_tree is not None and len(fine_tree.query(geom, predicate="dwithin", distance=dist)))


# ---- trace widths per net class ----
viol = collections.defaultdict(list)
necks = collections.defaultdict(list)
for root, layer, w, ln, seg in wire_segments:
    need = min_width_of(root if not isinstance(root, tuple) else None)
    if w < need - TOL:
        # power/bus nets may neck down to MIN_W_NECK only within NECK_DIST of a fine-pitch pad
        sg = LineString([(seg[0], seg[1]), (seg[2], seg[3])]) if ln > 1e-9 else Point(seg[0], seg[1])
        if w >= MIN_W_NECK - TOL and need > MIN_W_NECK and near_fine_pad(sg, NECK_DIST):
            necks[(root, need)].append((w, ln, layer))
        else:
            viol[(root, need)].append((w, ln, layer, seg))
nm = lambda r: net_name.get(r, str(r)) if not isinstance(r, tuple) else str(r)
if viol:
    FAIL("trace width: %d segments too narrow (power >= %.2f, bus/SW >= %.2f, GND pours/signals >= %.2f; neck to %.2f only <= %.1f mm from a fine-pitch pad) on %d nets; widths used: %s" % (
        sum(len(l) for l in viol.values()), MIN_W_POWER, MIN_W_BUS, MIN_W_SIGNAL, MIN_W_NECK, NECK_DIST, len(viol),
        dict(sorted(collections.Counter(round(s[2], 3) for s in wire_segments).items()))))
    for (root, need), l in sorted(viol.items(), key=lambda kv: -len(kv[1]))[:12]:
        print("       %-28s need %.2f, got min %.3f in %d segments (%.1f mm total)" % (
            nm(root), need, min(x[0] for x in l), len(l), sum(x[1] for x in l)))
        for x in l[:4]:
            print("           %s w=%.3f len=%.2f at (%.2f,%.2f)-(%.2f,%.2f)" % (x[2], x[0], x[1], *x[3][:4]))
else:
    OK("trace widths ok (power >= %.2f, bus/SW >= %.2f, others >= %.2f)" % (MIN_W_POWER, MIN_W_BUS, MIN_W_SIGNAL))
if necks:
    print("INFO %d power/bus segments necked to >= %.2f mm within %.1f mm of a fine-pitch pad (allowed): %s" % (
        sum(len(l) for l in necks.values()), MIN_W_NECK, NECK_DIST, sorted({nm(r) for (r, _) in necks})))

# ---- clearance (per layer) ----
print()
geoms_by_layer = collections.defaultdict(list)
for it in items:
    geoms_by_layer[it.layer].append(it)
clear_viol = {}
fine_clear = [0]
fine_list = []
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
            if d < MIN_CLEARANCE - CLEAR_TOL and d >= MIN_CLEARANCE_HARD - TOL and (
                    a.id in fine_ids or b.id in fine_ids or near_fine_pad(a.geom, NECK_DIST) or near_fine_pad(b.geom, NECK_DIST)):
                fine_clear[0] += 1
                fine_list.append((d, a.kind + "/" + b.kind, nm(a.net), nm(b.net), a.geom.centroid))
                continue
            if d < MIN_CLEARANCE - CLEAR_TOL:
                key = (layer, a.kind + "/" + b.kind, nm(a.net), nm(b.net))
                cv = clear_viol.setdefault(key, [d, 0, a.geom.centroid])
                cv[1] += 1
                if d < cv[0]:
                    cv[0], cv[2] = d, a.geom.centroid
if fine_clear[0]:
    print("INFO %d clearance pairs between %.2f and %.2f mm at fine-pitch pads (allowed down to %.2f)" % (fine_clear[0], MIN_CLEARANCE_HARD, MIN_CLEARANCE, MIN_CLEARANCE_HARD))
for d_, k_, n1_, n2_, c_ in sorted(fine_list, key=lambda t: t[0])[:8]:
    print("       fine-pitch pair %s %s <-> %s: %.3f mm near (%.1f,%.1f)" % (k_, n1_, n2_, d_, c_.x, c_.y))
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
        if it.layer in k["layers"] and it.geom.intersects(kg.buffer(-0.1 if it.kind == "pour" else 0)) and not (it.comp and it.comp == k.get("pcb_component_id")):
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
# pours: >= 0.5 mm from the board edge, the NPTH holes and the slots
bad = []
for it in items:
    if it.kind != "pour":
        continue
    de = outline.exterior.distance(it.geom)
    if de < MIN_POUR_EDGE - TOL:
        bad.append("pour %.2f mm from board edge on %s" % (de, it.layer))
    for cid, cg in cut:
        if it.geom.distance(cg) < MIN_POUR_EDGE - TOL:
            bad.append("pour %.2f mm from %s on %s" % (it.geom.distance(cg), cid, it.layer))
    for h in [e for e in cj if e["type"] == "pcb_hole"]:
        dh = it.geom.distance(Point(h["x"], h["y"]).buffer(h.get("hole_diameter", 0.6) / 2))
        if dh < MIN_POUR_EDGE - TOL:
            bad.append("pour %.2f mm from hole (%.1f,%.1f) on %s" % (dh, h["x"], h["y"], it.layer))
(FAIL if bad else OK)("pour >= %.1f mm from board edge, slots and NPTH holes%s" % (MIN_POUR_EDGE, ": " + "; ".join(sorted(set(bad))[:5]) if bad else ""))
holes = [e for e in cj if e["type"] == "pcb_hole"]
bad = []
for h in holes:
    hg = Point(h["x"], h["y"]).buffer(h.get("hole_diameter", 0.6) / 2, 24)
    # board mounting holes (no component): MIN_HOLE; the 0.6 mm positioning pegs of a part (J2): MIN_PEG for other copper of the board
    lim = MIN_HOLE if not h.get("pcb_component_id") else MIN_PEG
    for it in items:
        if it.geom.distance(hg) < lim - TOL and not (it.comp and it.comp == h.get("pcb_component_id")):
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


# =====================================================================
# G4: hole-to-hole spacing (vias and round plated drill_holes), JLC drill spacing
# =====================================================================
print()
hv = collections.Counter()
worst = {}
htree = STRtree([Point(h[0], h[1]) for h in drill_holes])
for i, a in enumerate(drill_holes):
    for j in htree.query(Point(a[0], a[1]), predicate="dwithin", distance=2.0):
        if j <= i:
            continue
        b = drill_holes[j]
        gap = math.hypot(a[0] - b[0], a[1] - b[1]) - (a[2] + b[2]) / 2
        same = a[3] == b[3]
        need = MIN_HOLE_SAME if same else MIN_HOLE_DIFF
        if gap < need - TOL:
            k = ("same net" if same else "different nets", nm(a[3]) if same else "%s/%s" % (nm(a[3]), nm(b[3])))
            hv[k] += 1
            worst.setdefault(k, []).append((gap, a, b))
if hv:
    FAIL("hole-to-hole spacing: %d pairs below %.2f (same net) / %.2f mm (different nets), edge to edge" % (sum(hv.values()), MIN_HOLE_SAME, MIN_HOLE_DIFF))
    for k, l in worst.items():
        for gap, a, b in sorted(l)[:4]:
            print("       %s %s: gap %.3f mm  (%.2f,%.2f) %s <-> (%.2f,%.2f) %s" % (k[0], k[1], gap, a[0], a[1], a[4], b[0], b[1], b[4]))
else:
    mg = min(math.hypot(a[0] - b[0], a[1] - b[1]) - (a[2] + b[2]) / 2 for i, a in enumerate(drill_holes) for b in drill_holes[i + 1:] if math.hypot(a[0] - b[0], a[1] - b[1]) < 3)
    OK("hole-to-hole spacing of %d vias/round plated drill_holes: smallest edge-to-edge gap %.3f mm (need >= %.2f same net, >= %.2f different nets)" % (len(drill_holes), mg, MIN_HOLE_SAME, MIN_HOLE_DIFF))

# =====================================================================
# G5: silkscreen. Glyph height and stroke are MEASURED in the silk Gerber (not taken from fontSize), R7 M1:
#     per text the Gerber strokes inside the text's box are collected (strokes of circuit.json silk paths/circles are excluded),
#     height = extent along the text's up axis + stroke width.  Texts must not touch pads/vias/holes, the board edge, other texts.
# =====================================================================
print()
from shapely.ops import unary_union
from shapely.affinity import translate
silk_by_layer = collections.defaultdict(list)    # layer -> [(ref/label, geom)]   (paths/circles only, texts are handled exactly below)
_src = {e["source_component_id"]: e["name"] for e in cj if e["type"] == "source_component"}
comp_name = {e["pcb_component_id"]: _src.get(e.get("source_component_id"), e["pcb_component_id"]) for e in cj if e["type"] == "pcb_component"}
silk_texts = [e for e in cj if e["type"] == "pcb_silkscreen_text"]
silk_circles = {"top": [], "bottom": []}
silk_pathsegs = {"top": set(), "bottom": set()}
for e in cj:
    t = e["type"]
    if t == "pcb_silkscreen_path":
        rt = e["route"]
        for a_, b_ in zip(rt, rt[1:]):
            silk_pathsegs[e["layer"]].add(frozenset({(round(a_["x"], 3), round(a_["y"], 3)), (round(b_["x"], 3), round(b_["y"], 3))}))
        if len(rt) >= 2:
            silk_by_layer[e["layer"]].append(("path of %s" % comp_name.get(e.get("pcb_component_id"), e.get("pcb_component_id")), LineString([(p["x"], p["y"]) for p in rt]).buffer(max(e.get("stroke_width", 0.1), MIN_SILK_W) / 2, 4)))
    elif t == "pcb_silkscreen_circle":
        c = e["center"]
        silk_circles[e["layer"]].append((c["x"], c["y"], e["radius"] + max(e.get("stroke_width", 0.1), MIN_SILK_W)))
        silk_by_layer[e["layer"]].append(("circle", Point(c["x"], c["y"]).buffer(e["radius"] + max(e.get("stroke_width", 0.1), MIN_SILK_W) / 2, 12).difference(Point(c["x"], c["y"]).buffer(max(e["radius"] - max(e.get("stroke_width", 0.1), MIN_SILK_W) / 2, 0), 12))))


def silk_segments(path):
    """dark draws with round apertures of a Gerber file: [(x1, y1, x2, y2, width)]"""
    ap, cur, pol, x, y, out = {}, None, "D", 0.0, 0.0, []
    in_reg = False
    for ln in open(path):
        ln = ln.strip()
        m = re.match(r"%ADD(\d+)C,([\d.]+)\*%", ln)
        if m:
            ap[m.group(1)] = float(m.group(2))
            continue
        if ln.startswith("%LP"):
            pol = ln[3]
        if ln.startswith("G36"):
            in_reg = True
        elif ln.startswith("G37"):
            in_reg = False
            continue
        if in_reg:
            continue            # filled regions (barcode square, logo) are no strokes
        m = re.match(r"D(\d+)\*$", ln)
        if m and int(m.group(1)) >= 10:
            cur = m.group(1)
            continue
        m = re.match(r"(?:X(-?\d+))?(?:Y(-?\d+))?D0([123])\*", ln)
        if m:
            nx = int(m.group(1)) / 1e6 if m.group(1) else x
            ny = int(m.group(2)) / 1e6 if m.group(2) else y
            if m.group(3) == "1" and pol == "D" and cur in ap:
                out.append((x, y, nx, ny, ap[cur]))
            x, y = nx, ny
    return out


text_env = []     # (e, envelope geometry or None, height, stroke)
small_h, thin_w, missing = [], [], []
if not NOGERBER:
    silk_segs = {"top": silk_segments(os.path.join(tmp, "F_SilkScreen.gbr")), "bottom": silk_segments(os.path.join(tmp, "B_SilkScreen.gbr"))}
    for e in silk_texts:
        lay = e["layer"]
        ax, ay, fs = e["anchor_position"]["x"], e["anchor_position"]["y"], e["font_size"]
        rot = math.radians(e.get("ccw_rotation", 0) or 0)
        hw, hh = max(len(e["text"]), 1) * 0.9 * fs / 2 + 0.3, fs * 0.7
        loc, ws, geoms = [], [], []
        for (x1, y1, x2, y2, w) in silk_segs[lay]:
            if frozenset({(round(x1, 3), round(y1, 3)), (round(x2, 3), round(y2, 3))}) in silk_pathsegs[lay]:
                continue
            if any(math.hypot(x1 - cx, y1 - cy) <= r_ and math.hypot(x2 - cx, y2 - cy) <= r_ for cx, cy, r_ in silk_circles[lay]):
                continue
            pl = []
            for (px, py) in ((x1, y1), (x2, y2)):
                dx, dy = px - ax, py - ay
                pl.append((dx * math.cos(rot) + dy * math.sin(rot), -dx * math.sin(rot) + dy * math.cos(rot)))
            if all(abs(q[0]) <= hw and abs(q[1]) <= hh for q in pl):
                loc += pl
                ws.append(w)
                geoms.append(LineString([(x1, y1), (x2, y2)]).buffer(w / 2, 4) if (x1, y1) != (x2, y2) else Point(x1, y1).buffer(w / 2, 4))
        if not loc:
            missing.append(e["text"])
            text_env.append((e, None, 0.0, 0.0))
            continue
        stroke = min(ws)
        height = max(q[1] for q in loc) - min(q[1] for q in loc) + stroke
        text_env.append((e, unary_union(geoms), height, stroke))
        if height < MIN_SILK_H - 0.01:
            small_h.append("%s %.2f" % (e["text"], height))
        if stroke < MIN_SILK_W - TOL:
            thin_w.append("%s %.3f" % (e["text"], stroke))
    if missing:
        FAIL("silkscreen texts without strokes in the Gerber (dropped by the exporter?): %s" % sorted(set(missing)))
    if small_h:
        FAIL("silkscreen glyph height measured in the Gerber below %.1f mm (JLC minimum): %s" % (MIN_SILK_H, sorted(set(small_h))[:10]))
    else:
        hs = [h for _, g, h, _ in text_env if g is not None]
        OK("silkscreen glyph height measured in the Gerber >= %.1f mm for all %d texts (smallest %.3f mm, largest %.3f mm)" % (MIN_SILK_H, len(hs), min(hs), max(hs)))
    if thin_w:
        FAIL("silkscreen text stroke below %.2f mm: %s" % (MIN_SILK_W, sorted(set(thin_w))[:10]))
    else:
        OK("silkscreen text strokes measured in the Gerber >= %.2f mm (smallest %.3f mm)" % (MIN_SILK_W, min(st for _, g, _, st in text_env if g is not None)))
    thin = {}
    for lay in ("F_SilkScreen", "B_SilkScreen"):
        for ln in open(os.path.join(tmp, lay + ".gbr")):
            m = re.match(r"%ADD\d+C,([\d.]+)\*%", ln.strip())
            if m and float(m.group(1)) < MIN_SILK_W - TOL:
                thin[(lay, float(m.group(1)))] = 1
    if thin:
        FAIL("silkscreen Gerber stroke widths below %.2f mm: %s (run scripts/postprocess_gerbers.py)" % (MIN_SILK_W, sorted(thin)))
    else:
        OK("silkscreen Gerber stroke widths (all apertures: text, outlines, marks) >= %.2f mm" % MIN_SILK_W)
else:
    for e in silk_texts:
        if e["font_size"] < 1.8:
            FAIL("silkscreen text '%s' fontSize %.2f too small (geometry-only mode: needs >= 1.8 mm)" % (e["text"], e["font_size"]))
# texts vs pads / vias / holes / board edge / other texts
board_ = next(e for e in cj if e["type"] == "pcb_board")
outline_ = Polygon([(p["x"], p["y"]) for p in board_["outline"]]) if board_.get("outline") else rect_poly(board_["center"]["x"], board_["center"]["y"], board_["width"], board_["height"])
bad_t = []
for e, env, h, st in text_env:
    if env is None:
        continue
    lay = e["layer"]
    for it in items:
        if it.kind in ("pad", "pth", "via") and (it.layer == lay or it.kind == "pth" or it.kind == "via") and it.geom.intersects(env):
            bad_t.append("'%s' on %s %s" % (e["text"], it.kind, it.label))
    for h_ in (x for x in cj if x["type"] == "pcb_hole"):
        if Point(h_["x"], h_["y"]).buffer(h_.get("hole_diameter", 0.6) / 2).intersects(env):
            bad_t.append("'%s' on NPTH (%.1f,%.1f)" % (e["text"], h_["x"], h_["y"]))
    for cid, cg in cut:
        if cg.intersects(env):
            bad_t.append("'%s' over cutout %s" % (e["text"], cid))
    if not outline_.contains(env) or outline_.exterior.distance(env) < MIN_SILK_EDGE:
        bad_t.append("'%s' %.2f mm from the board edge" % (e["text"], 0.0 if not outline_.contains(env) else outline_.exterior.distance(env)))
envs = [(e, env) for e, env, h, st in text_env if env is not None]
for i, (e1, g1) in enumerate(envs):
    for e2, g2 in envs[i + 1:]:
        if e1["layer"] == e2["layer"] and g1.distance(g2) < 0.1:
            bad_t.append("'%s' touches text '%s'" % (e1["text"], e2["text"]))
if NOGERBER:
    pass
elif bad_t:
    FAIL("silkscreen text overlaps pads/vias/holes/edge (>= %.2f mm)/other text: %s" % (MIN_SILK_EDGE, sorted(set(bad_t))[:12]))
else:
    OK("silkscreen texts (measured glyph envelopes): no overlap with pads, vias, holes, slots or other texts, >= %.2f mm from the board edge" % MIN_SILK_EDGE)
# ---- G5b: JLCPCB 2D-barcode marker (solid 8x8 mm silk square) + black-swan logo (filled silk regions, scripts/silk_extras.py) ----
def silk_regions(path):
    """filled G36/G37 regions of a Gerber: [shapely geometry], each dark region with the clear-polarity regions that follow it subtracted"""
    out, pol, ring, reg, x, y = [], "D", [], False, 0.0, 0.0
    for ln in open(path):
        ln = ln.strip()
        if ln.startswith("%LP"):
            pol = ln[3]
        elif ln.startswith("G36"):
            reg, ring = True, []
        elif ln.startswith("G37"):
            reg = False
            if len(ring) >= 3:
                pg = Polygon(ring).buffer(0)
                if pol == "D":
                    out.append(pg)
                elif out:
                    out[-1] = out[-1].difference(pg)
        elif reg:
            m = re.match(r"(?:X(-?\d+))?(?:Y(-?\d+))?D0([123])\*", ln)
            if m:
                x = int(m.group(1)) / 1e6 if m.group(1) else x
                y = int(m.group(2)) / 1e6 if m.group(2) else y
                ring.append((x, y))
    return out


if not NOGERBER:
    import silk_extras as SX
    regs = silk_regions(os.path.join(tmp, "F_SilkScreen.gbr"))
    bc_box = SX.barcode_poly()
    bc = [g for g in regs if g.centroid.distance(bc_box.centroid) < 0.5 and abs(g.area - SX.BARCODE_S ** 2) < 0.05]
    logo_g = unary_union([g for g in regs if not any(g is b for b in bc)])
    # (a) barcode: exactly one solid square of the barcode size (JLCPCB 'Specify Position' needs a solid square in the silkscreen layer)
    if len(bc) != 1 or abs(bc[0].area - SX.BARCODE_S ** 2) > 0.05 or not bc[0].equals_exact(bc_box, 0.01) and bc[0].symmetric_difference(bc_box).area > 0.05:
        FAIL("2D-barcode marker: no solid %.0fx%.0f mm square in F_Silkscreen at (%.2f, %.2f) (run scripts/postprocess_gerbers.py)" % (SX.BARCODE_S, SX.BARCODE_S, *SX.BARCODE_C))
    else:
        bz = bc[0]
        sil_bad = []
        for it in items:
            if it.kind in ("pad", "pth", "via", "trace", "pour_x") and (it.layer == "top" or it.kind in ("pth", "via")) and it.geom.distance(bz) < 0.5:
                sil_bad.append("%s %s" % (it.kind, it.label))
        for h_ in (x for x in cj if x["type"] == "pcb_hole"):
            if Point(h_["x"], h_["y"]).buffer(h_.get("hole_diameter", 0.6) / 2).distance(bz) < 0.5:
                sil_bad.append("NPTH (%.1f,%.1f)" % (h_["x"], h_["y"]))
        for cid, cg in cut:
            if cg.distance(bz) < 0.5:
                sil_bad.append("cutout %s" % cid)
        for k in keeps:
            kg = rect_poly(k["center"]["x"], k["center"]["y"], k["width"], k["height"]) if k["shape"] == "rect" else Point(k["center"]["x"], k["center"]["y"]).buffer(k["radius"])
            if "top" in k["layers"] and kg.intersects(bz):
                sil_bad.append("keepout (%.1f,%.1f)" % (k["center"]["x"], k["center"]["y"]))
        for lbl, g in silk_by_layer["top"]:
            if g.distance(bz) < 0.5:
                sil_bad.append("silk " + lbl)
        for e, env, h, st in text_env:
            if env is not None and e["layer"] == "top" and env.distance(bz) < 0.5:
                sil_bad.append("silk text '%s'" % e["text"])
        if not outline_.contains(bz) or outline_.exterior.distance(bz) < 0.5:
            sil_bad.append("board edge/notch %.2f mm" % (0.0 if not outline_.contains(bz) else outline_.exterior.distance(bz)))
        if logo_g.distance(bz) < 0.5:
            sil_bad.append("logo")
        if sil_bad:
            FAIL("2D-barcode field (%.0fx%.0f mm at %.1f, %.1f) not free (0.5 mm): %s" % (SX.BARCODE_S, SX.BARCODE_S, SX.BARCODE_C[0], SX.BARCODE_C[1], sorted(set(sil_bad))[:10]))
        else:
            under = [it for it in items if it.kind == "pour" and it.layer == "top" and it.geom.intersects(bz)]
            OK("2D-barcode field: solid %.0fx%.0f mm silk square at (%.1f, %.1f), no pads/vias/holes/slots/traces/keepouts/other silk within 0.5 mm, >= 0.5 mm from the board edge%s" % (
                SX.BARCODE_S, SX.BARCODE_S, SX.BARCODE_C[0], SX.BARCODE_C[1], " (on %d top pour polygon(s): plain mask over copper, allowed by JLC)" % len(under) if under else ""))
    # (b) logo: filled, clear of exposed copper / holes / other silk / edge, printable feature size
    if logo_g.is_empty or logo_g.area < 20:
        FAIL("logo: no filled swan regions in F_Silkscreen (area %.1f mm2)" % logo_g.area)
    else:
        lb, lg_bad = logo_g.bounds, []
        for it in items:
            if it.kind in ("pad", "pth", "via") and (it.layer == "top" or it.kind in ("pth", "via")) and it.geom.distance(logo_g) < SX.SILK_CLEAR - 0.005:
                lg_bad.append("%s %s" % (it.kind, it.label))
        for h_ in (x for x in cj if x["type"] == "pcb_hole"):
            if Point(h_["x"], h_["y"]).buffer(h_.get("hole_diameter", 0.6) / 2).distance(logo_g) < SX.SILK_CLEAR:
                lg_bad.append("NPTH")
        for cid, cg in cut:
            if cg.distance(logo_g) < 0.3:
                lg_bad.append("cutout %s" % cid)
        for lbl, g in silk_by_layer["top"]:
            if g.distance(logo_g) < 0.15:
                lg_bad.append("silk " + lbl)
        for e, env, h, st in text_env:
            if env is not None and e["layer"] == "top" and env.distance(logo_g) < 0.15:
                lg_bad.append("silk text '%s'" % e["text"])
        if not outline_.contains(logo_g) or outline_.exterior.distance(logo_g) < MIN_SILK_EDGE:
            lg_bad.append("board edge")
        thin_ = logo_g.difference(logo_g.buffer(-(SX.MIN_FEAT - 0.01) / 2).buffer((SX.MIN_FEAT - 0.01) / 2))
        gap_ = logo_g.buffer((SX.MIN_FEAT - 0.01) / 2).buffer(-(SX.MIN_FEAT - 0.01) / 2).difference(logo_g)
        if thin_.area > 0.05:
            lg_bad.append("strokes < %.2f mm (%.3f mm2)" % (SX.MIN_FEAT, thin_.area))
        if gap_.area > 0.05:
            lg_bad.append("gaps < %.2f mm (%.3f mm2)" % (SX.MIN_FEAT, gap_.area))
        if lg_bad:
            FAIL("swan logo: %s" % sorted(set(lg_bad))[:10])
        else:
            OK("swan logo: %.2f x %.2f mm filled silk at (%.1f, %.1f), %.1f mm2, clear (>= %.2f mm) of pads/vias/holes/other silk, features/gaps >= %.2f mm" % (
                lb[2] - lb[0], lb[3] - lb[1], (lb[0] + lb[2]) / 2, (lb[1] + lb[3]) / 2, logo_g.area, SX.SILK_CLEAR, SX.MIN_FEAT))
# texts over component outlines (warning only)
tp_warn = []
for e, env in envs:
    for lbl, g in silk_by_layer[e["layer"]]:
        if g.intersects(env) and g.intersection(env).area > 0.02:
            tp_warn.append("'%s' over %s" % (e["text"], lbl))
if tp_warn:
    WARN("silkscreen text crosses component outlines: %s" % sorted(set(tp_warn))[:8])
# silk paths / circles over exposed pads (JLC clips the silk, keep it small)
tot = 0.0
bad_silk = collections.defaultdict(float)
for layer, sl in silk_by_layer.items():
    pads = [(it.label, it.geom) for it in items if it.kind in ("pad", "pth") and it.layer == layer]
    ptree = STRtree([g for _, g in pads])
    for lbl, g in sl:
        for j in ptree.query(g, predicate="intersects"):
            a = g.intersection(pads[j][1]).area
            if a > 1e-6:
                tot += a
                bad_silk[(layer, lbl, pads[j][0])] += a
agg = collections.defaultdict(float)
for k, a_ in bad_silk.items():
    agg[(k[0], k[1])] += a_
worst_items = {k: a_ for k, a_ in agg.items() if a_ > MAX_SILK_PAD}
if worst_items:
    FAIL("silkscreen outlines over exposed pads: %d items above %.2f mm2 (total %.2f mm2)" % (len(worst_items), MAX_SILK_PAD, tot))
else:
    OK("silkscreen outlines/marks over exposed pads: largest item %.3f mm2 (limit %.2f per item), total %.3f mm2" % (max(agg.values()) if agg else 0.0, MAX_SILK_PAD, tot))
for k, a_ in sorted(agg.items(), key=lambda kv: -kv[1])[:10]:
    print("       %s %s: %.3f mm2 over pads %s" % (k[0], k[1], a_, sorted({kk[2] for kk in bad_silk if (kk[0], kk[1]) == k})[:6]))
# silk path/circle closer than MIN_SILK_EDGE to the board edge (JLC clips silk at the edge)
edge_silk = []
for layer, sl in silk_by_layer.items():
    for lbl, g in sl:
        if not outline_.contains(g) or outline_.exterior.distance(g) < 0.15:
            edge_silk.append("%s (%s)" % (lbl, layer))
(WARN if edge_silk else OK)("silkscreen outlines %s" % ("within 0.15 mm of / outside the board edge: %s" % sorted(set(edge_silk))[:6] if edge_silk else ">= 0.15 mm from the board edge"))

# ---- pin-1 / polarity marks (R7 m6): a silk dot/bar/'+' must sit next to the marked pad and nearer to it than to the part's other pads ----
MARK_REFS = {"U1": 1, "U2": 1, "U3": 1, "U4": 1, "U5": 1, "Q1": 1, "OC1": 1, "OC2": 1,     # ref -> pad number to mark (IC pin 1, cathode, '+')
             "D1": 2, "D2": 2, "D3": 2, "D4": 2, "D5": 2, "D6": 1, "D7": 1,                   # BAT42W pad 2 = K; 1N4148W/B5819W pad 1 = K
             "LD1": 1, "LD2": 2, "LD3": 2, "LD4": 2, "LD5": 2, "C12": 1, "C14": 1, "C29": 1}  # NCD0805R1 pad 1 = K; KT-0805Y pad 2 = K; '+' = pad 1
marks_missing = []
for ref, pn in MARK_REFS.items():
    pads_ = [it for it in items if it.kind in ("pad", "pth") and it.label.startswith(ref + ".") and it.label.split(".")[1] != ""]
    mine = [it for it in pads_ if it.label == "%s.%d" % (ref, pn) or it.label == "%s.pin%d" % (ref, pn)]
    if not mine:
        marks_missing.append("%s (no pad %d)" % (ref, pn))
        continue
    tgt = mine[0]
    oth = [it for it in pads_ if it.comp == tgt.comp and it.layer == tgt.layer and it.label not in (tgt.label,) and not it.label.endswith(("_internal_1",))
           and it.geom.distance(tgt.geom) > 0.01]
    # exclude the other pad of a pin shared by several pads (EPAD, shell legs): only the pads of OTHER pins matter
    ok_ = False
    for lbl, g in silk_by_layer[tgt.layer]:
        d_t = g.distance(tgt.geom)
        if d_t > 1.6:
            continue
        if all(g.distance(o.geom) > d_t + 0.3 for o in oth):
            ok_ = True
            break
    if not ok_:
        marks_missing.append(ref)
(FAIL if marks_missing else OK)("pin-1 / polarity silk marks next to the marked pad (%d parts: ICs pin 1, diode/LED cathodes, polarised caps)%s" % (len(MARK_REFS), ": missing " + ", ".join(marks_missing) if marks_missing else ""))

# =====================================================================
# G8 (R7 m2): copper pour slivers. Morphological opening of every pour polygon: anything narrower than MIN_NECK is a sliver / neck that can peel off
# (acid trap) and is flagged by JLC DFM. G9 (R7 m4): decoupling cap of the ESP32 3V3 pin within MAX_DECOUP mm.
# =====================================================================
print()
import slivers as _sl


def gerber_clear_regions(path):
    """clear-polarity (%LPC) G36 regions of a Gerber file as polygons"""
    pol, reg, cur, x, y, out = "D", False, [], 0.0, 0.0, []
    for ln in open(path):
        ln = ln.strip()
        if ln.startswith("%LP"):
            pol = ln[3]
        elif ln.startswith("G36"):
            reg, cur = True, []
        elif ln.startswith("G37"):
            if reg and pol == "C" and len(cur) >= 3:
                pg = Polygon(cur)
                out.append(pg if pg.is_valid else pg.buffer(0))
            reg = False
        elif reg:
            m = re.match(r"(?:X(-?\d+))?(?:Y(-?\d+))?D0([12])\*", ln)
            if m:
                x = int(m.group(1)) / 1e6 if m.group(1) else x
                y = int(m.group(2)) / 1e6 if m.group(2) else y
                cur.append((x, y))
    return out


n_sl, n_unclear, removed_area, islands, kept_necks = 0, 0, 0.0, [], []
for lay, gfile in (("top", "F_Cu.gbr"), ("bottom", "B_Cu.gbr")):
    clears, necks_, allp = _sl.sliver_clears(cj, lay)
    for nk in necks_:
        kept_necks.append((lay, nk.centroid.x, nk.centroid.y, nk.area))
    n_sl += len(clears)
    removed_area += sum(c.area for c in clears)
    if NOGERBER:
        continue
    gclear = unary_union(gerber_clear_regions(os.path.join(tmp, gfile)))
    for c in clears:
        if c.intersection(gclear).area < 0.95 * c.area:
            n_unclear += 1
            print("       sliver left in %s copper near (%.2f,%.2f) %.3f mm2" % (lay, c.centroid.x, c.centroid.y, c.area))
    # no pour island may be created by the removal (every remaining piece must touch a pad/via/trace of its own net)
    if clears:
        cu = unary_union(clears)
        for it in items:
            if it.kind == "pour" and it.layer == lay:
                rest = it.geom.difference(cu)
                for piece in (rest.geoms if hasattr(rest, "geoms") else [rest]):
                    if piece.area < 0.5:
                        continue
                    if not any(o.net == it.net and o.kind != "pour" and o.layer == lay and o.geom.intersects(piece) for o in items):
                        islands.append("%s pour piece %.1f mm2 near (%.1f,%.1f)" % (lay, piece.area, piece.centroid.x, piece.centroid.y))
if NOGERBER:
    print("INFO %d pour slivers < %.2f mm found (geometry-only mode: not checked in the Gerber)" % (n_sl, _sl.NECK))
elif n_unclear:
    FAIL("%d copper pour slivers/necks narrower than %.2f mm remain in the copper Gerbers (run scripts/postprocess_gerbers.py)" % (n_unclear, _sl.NECK))
elif islands:
    FAIL("sliver removal isolates pour copper: %s" % islands[:4])
else:
    OK("copper pour slivers narrower than %.2f mm: %d found in the routed pours (total %.2f mm2), all cleared in the Gerbers, no pour island created" % (_sl.NECK, n_sl, removed_area))
if kept_necks:
    WARN("%d copper pour necks narrower than %.2f mm kept (removing them would split the pour): %s" % (len(kept_necks), _sl.NECK, "; ".join("%s (%.1f,%.1f) %.2f mm2" % k for k in kept_necks[:6])))
MAX_DECOUP = 2.0
u3p2 = [it for it in items if it.kind == "pad" and it.label in ("U3.2", "U3.pin2")]
dec = {}
for it in items:
    if it.kind == "pad" and it.label.startswith("C23.") and u3p2:
        dec[it.label] = min(it.geom.distance(u.geom) for u in u3p2)
if dec:
    (FAIL if min(dec.values()) > MAX_DECOUP else OK)("C23 (100 nF) pad is %.2f mm from the ESP32 3V3 pin (U3.2) pad, limit %.1f mm (R7 m4)" % (min(dec.values()), MAX_DECOUP))
else:
    FAIL("C23 / U3 pin 2 pads not found for the decoupling distance check")

# =====================================================================
# G6: solder paste apertures (Gerber) vs. the pads of circuit.json
# =====================================================================
print()
if not NOGERBER:
    def paste_flashes(fn):
        ap, cur, out = {}, None, []
        for ln in open(os.path.join(tmp, fn)):
            ln = ln.strip()
            m = re.match(r"%ADD(\d+)R,([\d.]+)X([\d.]+)\*%", ln)
            if m:
                ap[m.group(1)] = ("R", float(m.group(2)), float(m.group(3)))
                continue
            m = re.match(r"%ADD(\d+)C,([\d.]+)\*%", ln)
            if m:
                ap[m.group(1)] = ("C", float(m.group(2)), float(m.group(2)))
                continue
            m = re.match(r"%ADD(\d+)(\w+),", ln)
            if m and m.group(1) not in ap:
                ap[m.group(1)] = ("?", 0, 0)
                continue
            m = re.match(r"D(\d+)\*$", ln)
            if m and int(m.group(1)) >= 10:
                cur = m.group(1)
                continue
            m = re.match(r"X(-?\d+)Y(-?\d+)D03\*", ln)
            if m and cur in ap:
                out.append((int(m.group(1)) / 1e6, int(m.group(2)) / 1e6) + ap[cur])
        return out
    ratios, nopaste, extra = [], [], 0
    for lay, gf in (("top", "F_Paste.gbr"), ("bottom", "B_Paste.gbr")):
        fl = paste_flashes(gf)
        used = set()
        for e in cj:
            if e["type"] != "pcb_smtpad" or e["layer"] != lay:
                continue
            best = None
            for k, f in enumerate(fl):
                if k not in used and abs(f[0] - e["x"]) < 0.01 and abs(f[1] - e["y"]) < 0.01:
                    best = k
                    break
            lbl = pin_str(e.get("pcb_port_id")) or e["pcb_smtpad_id"]
            if best is None:
                nopaste.append(lbl)
                continue
            used.add(best)
            f = fl[best]
            if e["shape"] in ("rect", "rotated_rect") and f[2] == "R":
                pa, fa = e["width"] * e["height"], f[3] * f[4]
                ratios.append((fa / pa, lbl))
            elif e["shape"] == "circle" and f[2] == "C":
                ratios.append((f[3] ** 2 / (2 * e["radius"]) ** 2, lbl))
        extra += len(fl) - len(used)
    if ratios:
        lo = min(ratios)
        hi = max(ratios)
        if lo[0] < MIN_PASTE - 1e-3 or hi[0] > 1.0 + 1e-3:
            FAIL("paste aperture / pad area outside %.0f..100 %%: smallest %.0f %% (%s), largest %.0f %% (%s)" % (MIN_PASTE * 100, lo[0] * 100, lo[1], hi[0] * 100, hi[1]))
        else:
            OK("paste apertures: %d pads compared, aperture/pad area %.0f..%.0f %%" % (len(ratios), lo[0] * 100, hi[0] * 100))
    bad_np = sorted(set(x for x in nopaste if not re.match(r"(JP\d|TP\d)", x)))
    jp_np = sorted(set(x for x in nopaste if re.match(r"JP\d", x)))
    print("       pads without paste: %d (JP1/JP2 pads must have none: %s; test pads TP: %s)" % (len(nopaste), jp_np, sorted(set(x for x in nopaste if x.startswith("TP")))))
    if bad_np:
        WARN("SMD pads without paste aperture: %s" % bad_np[:12])
    if any(not (x.startswith("JP1") or x.startswith("JP2")) for x in []):
        pass
    for jp in ("JP1", "JP2"):
        if sum(1 for x in nopaste if x.startswith(jp + ".")) < 2:
            FAIL("%s pads have paste (must stay open without paste)" % jp)
    if extra:
        FAIL("%d paste flashes without a matching SMD pad (paste on plated holes? run scripts/postprocess_gerbers.py)" % extra)

    # G7: JP1/JP2 mask openings must merge into one opening (R5 m3/m7)
    mk = paste_flashes("F_Mask.gbr")
    for jp in ("JP1", "JP2"):
        pads_ = [e for e in cj if e["type"] == "pcb_smtpad" and (pin_str(e.get("pcb_port_id")) or "").startswith(jp + ".")]
        ops = []
        for e in pads_:
            for f in mk:
                if abs(f[0] - e["x"]) < 0.01 and abs(f[1] - e["y"]) < 0.01 and f[2] == "R":
                    ops.append((e, f))
        if len(ops) != 2:
            FAIL("%s: %d mask openings found for 2 pads" % (jp, len(ops)))
            continue
        (e1, f1), (e2, f2) = ops
        dx, dy = abs(e1["x"] - e2["x"]), abs(e1["y"] - e2["y"])
        merged = (dx < (f1[3] + f2[3]) / 2 - 1e-6 and dy < (f1[4] + f2[4]) / 2 + 1e-6) or (dy < (f1[4] + f2[4]) / 2 - 1e-6 and dx < (f1[3] + f2[3]) / 2 + 1e-6)
        (OK if merged else FAIL)("%s mask openings %.2fx%.2f mm each, centre distance %.2f/%.2f mm: %s" % (jp, f1[3], f1[4], dx, dy, "one common opening (merged)" if merged else "NOT merged (mask web between the pads)"))

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

# =====================================================================
# P1: breakaway panel (rails + mouse-bite tabs) for the >= 70 mm delivery size (scripts/panelize.py, docs/JLC_ECONOMIC.md)
# =====================================================================
print("\n-- Breakaway panel (rails + mouse bites) --")
PANEL = None            # shapely polygon of the panel material (None = Gerber without panel)
if not NOGERBER:
    import panelize as PZ
    from gerbonara import GerberFile
    import gerbonara.utils as _gu
    _board_p = [e for e in cj if e["type"] == "pcb_board"][0]
    _bo = Polygon([(p["x"], p["y"]) for p in _board_p["outline"]])
    # ---- Edge_Cuts contours ----
    _rings, _cur, _open = [], [], 0
    for ln in open(os.path.join(tmp, "Edge_Cuts.gbr")):
        m = re.match(r"X(-?\d+)Y(-?\d+)D0([12])\*", ln.strip())
        if not m:
            continue
        pt = (int(m.group(1)) / 1e6, int(m.group(2)) / 1e6)
        if m.group(3) == "2":
            if _cur:
                _rings.append(_cur)
            _cur = [pt]
        else:
            _cur.append(pt)
    if _cur:
        _rings.append(_cur)
    _unclosed = [i for i, r in enumerate(_rings) if len(r) < 4 or math.hypot(r[0][0] - r[-1][0], r[0][1] - r[-1][1]) > 1e-6]
    _polys = sorted((Polygon(r) for r in _rings if len(r) >= 4), key=lambda p: -p.area)
    _is_panel = _polys and _polys[0].bounds[3] - _polys[0].bounds[1] > _board_p["height"] + 1
    (FAIL if _unclosed else OK)("panel: Edge_Cuts has %d closed contours%s" % (len(_rings), "" if not _unclosed else " (UNCLOSED: %s)" % _unclosed))
    if not _is_panel:
        FAIL("panel: Edge_Cuts holds only the bare board outline (%.1f mm high): run scripts/panelize.py; JLC Economic delivery needs >= 70 mm in each direction" % (_polys[0].bounds[3] - _polys[0].bounds[1] if _polys else 0))
    else:
        _outer = _polys[0]
        PANEL = Polygon(_outer.exterior, [p.exterior for p in _polys[1:] if _outer.contains(p)])
        _x0, _y0, _x1, _y1 = _outer.bounds
        _W, _H = _x1 - _x0, _y1 - _y0
        (OK if min(_W, _H) >= PZ.MIN_PANEL - TOL and max(_W, _H) <= 250 else FAIL)(
            "panel: size %.2f x %.2f mm (delivered PCB >= 70 x 70 mm, panel <= 250 x 250 mm)" % (_W, _H))
        (OK if abs((_x0 + _x1) / 2) < TOL and abs((_y0 + _y1) / 2) < TOL else FAIL)(
            "panel: centred on the Gerber origin (%.3f, %.3f), so the board origin and the CPL coordinates are unchanged" % ((_x0 + _x1) / 2, (_y0 + _y1) / 2))
        # the board outline is contained in the panel material; what is left after break-off is exactly rails/tabs outside the board
        _oc = [p for p in _polys[1:] if _bo.contains(p)]          # OC1/OC2 slots of the board
        _miss = _bo.difference(PANEL.buffer(1e-4)).difference(unary_union(_oc).buffer(1e-4)).area
        (OK if _miss < 1e-6 else FAIL)("panel: board outline (110 x 60, 4 notches) lies completely inside the panel material apart from its own %d slots (missing %.6f mm2)" % (len(_oc), _miss))
        _rest = PANEL.difference(_bo.buffer(1e-4))
        _pieces = [g_ for g_ in (_rest.geoms if hasattr(_rest, "geoms") else [_rest]) if g_.area > 1.0]
        (OK if len(_pieces) == 2 else FAIL)("panel: after break-off exactly two pieces are removed (top and bottom rail with their tab stubs): %d pieces" % len(_pieces))
        _gaps, _rw = [], []
        _probe = PANEL.intersection(LineString([(_x0 + 0.5, -100), (_x0 + 0.5, 100)]))        # column through the rails at the panel end (outside any tab)
        for sg_ in (1, -1):
            segs_ = [g_ for g_ in (_probe.geoms if hasattr(_probe, "geoms") else [_probe]) if g_.length > 0.1 and g_.centroid.y * sg_ > _bo.bounds[3] - 1]
            if segs_:
                sg0 = max(segs_, key=lambda g_: g_.centroid.y * sg_)
                _rw.append(sg0.length)
                _gaps.append(abs(sg0.bounds[1] if sg_ > 0 else sg0.bounds[3]) - _bo.bounds[3])
        (OK if _rw and min(_rw) >= PZ.RAIL - 0.06 else FAIL)("panel: rail width %s mm (JLC: 5 mm tooling edge, minimum 3 mm); no copper/silk/mask on the rails (see below)" % ", ".join("%.2f" % r for r in _rw))
        (OK if _gaps and min(_gaps) >= 1.6 - 0.06 else FAIL)("panel: routed gap board-rail %s mm (JLC: 1.6 or 2 mm, minimum 1.2 mm)" % ", ".join("%.2f" % r for r in _gaps))
        _slots = [p for p in _polys[1:] if _outer.contains(p) and p.bounds[2] - p.bounds[0] > 5 and p.bounds[3] - p.bounds[1] < 3]
        _sw = [p.bounds[3] - p.bounds[1] for p in _slots]
        (OK if not _sw or min(_sw) >= 1.2 else FAIL)("panel: %d closed routed slots between the tabs, narrowest %.2f mm (JLC min routed gap 1.2 mm)" % (len(_slots), min(_sw) if _sw else 0))
        # ---- tabs: material bridging the gap ----
        _tabs = []
        for sg, ye in ((1, _bo.bounds[3]), (-1, _bo.bounds[1])):
            band = box(_x0, min(ye + sg * 0.3, ye + sg * 1.7), _x1, max(ye + sg * 0.3, ye + sg * 1.7))
            cut_ = PANEL.intersection(band)
            for g_ in (cut_.geoms if hasattr(cut_, "geoms") else [cut_]):
                if g_.area > 0.01:
                    _tabs.append((sg, g_.bounds[0], g_.bounds[2]))
        _top = [t for t in _tabs if t[0] > 0]
        _bot = [t for t in _tabs if t[0] < 0]
        # the open end pieces of the gap are not material: tabs are the pieces inside the board edge span
        _bad = []
        _j2 = [e for e in cj if e["type"] == "pcb_component" and e.get("center") and abs(e["center"]["x"] - 33) < 1 and abs(e["center"]["y"] - 25) < 2][0]
        _j2x0, _j2x1 = _j2["center"]["x"] - _j2["width"] / 2, _j2["center"]["x"] + _j2["width"] / 2
        _ant = [k for k in keeps if k.get("width") and k["center"]["x"] - k["width"] / 2 > 40 and k["width"] > 5]
        _ax0 = min([k["center"]["x"] - k["width"] / 2 for k in _ant], default=45.0)
        for sg, a0, a1 in _tabs:
            if a1 - a0 < PZ.TAB_W - 0.05:
                _bad.append("tab %+.1f..%+.1f narrower than %.1f mm" % (a0, a1, PZ.TAB_W))
            if sg > 0 and not (a1 < _j2x0 - 3 or a0 > _j2x1 + 3):
                _bad.append("tab %.1f..%.1f within 3 mm of J2 (%.1f..%.1f)" % (a0, a1, _j2x0, _j2x1))
            if a1 > _ax0 - 3:
                _bad.append("tab %.1f..%.1f within 3 mm of the antenna region (x >= %.1f)" % (a0, a1, _ax0))
            if a0 < -46.5 or a1 > 46.5:
                _bad.append("tab %.1f..%.1f too close to the corner notches (straight edge |x| <= 49.5)" % (a0, a1))
        (OK if len(_top) >= 3 and len(_bot) >= 3 and not _bad else FAIL)(
            "panel: %d tabs top (x centres %s) / %d bottom (%s), width %.1f mm (JLC: >= 5 mm; one set every 50-60 mm), clear of J2 mouth, antenna region, corner notches%s" % (
                len(_top), [round((t[1] + t[2]) / 2, 1) for t in _top], len(_bot), [round((t[1] + t[2]) / 2, 1) for t in _bot],
                min([t[2] - t[1] for t in _tabs], default=0), "" if not _bad else ": " + "; ".join(_bad)))
        # ---- NPTH drill: mouse bites + tooling holes ----
        _dr = {}
        _cd, _tdia = None, {}
        for ln in open(os.path.join(tmp, "drill_npth.drl")):
            ln = ln.strip()
            m = re.match(r"T(\d+)C([\d.]+)", ln)
            if m:
                _tdia[m.group(1)] = float(m.group(2))
            m = re.fullmatch(r"T(\d+)", ln)
            if m:
                _cd = m.group(1)
            m = re.fullmatch(r"X(-?[\d.]+)Y(-?[\d.]+)", ln)
            if m:
                _dr.setdefault(_tdia[_cd], []).append((float(m.group(1)), float(m.group(2))))
        _yb = _bo.bounds[3]
        _bites = [(d, p) for d, ps in _dr.items() for p in ps if abs(abs(p[1]) - _yb) < 0.5 and d < 1.0]
        _tool = [(d, p) for d, ps in _dr.items() for p in ps if abs(p[1]) > _yb + 1 and d >= 1.5]
        _badb = []
        for sg, a0, a1 in _tabs:
            hs = sorted(p[0] for d, p in _bites if a0 - 0.01 <= p[0] <= a1 + 0.01 and p[1] * sg > 0)
            if len(hs) < 5:
                _badb.append("tab %.1f..%.1f has %d holes (JLC: 5-8 per set)" % (a0, a1, len(hs)))
            else:
                eg = min(b - a for a, b in zip(hs, hs[1:])) - _bites[0][0]
                if eg < 0.3 - 1e-3:
                    _badb.append("tab %.1f..%.1f hole edge gap %.2f < 0.3" % (a0, a1, eg))
                if hs[0] - _bites[0][0] / 2 < a0 + 0.2 or hs[-1] + _bites[0][0] / 2 > a1 - 0.2:
                    _badb.append("tab %.1f..%.1f holes too close to the tab ends" % (a0, a1))
        _offs = [abs(p[1]) - _yb for d, p in _bites]
        _dd = sorted({d for d, p in _bites})
        if not _bites or not all(0.5 <= d <= 0.8 for d in _dd):
            _badb.append("mouse-bite hole diameters %s outside 0.5-0.8 mm" % _dd)
        if _offs and (max(_offs) > 0.2 or min(_offs) < -PZ.BITE_D / 3 - 1e-6):
            _badb.append("hole centres %.2f..%.2f mm from the board edge (limit: on the line .. 1/3 hole inside)" % (min(_offs), max(_offs)))
        (FAIL if _badb else OK)("panel: %d mouse-bite holes (NPTH.drl) d=%s mm, %d per tab, hole edge gap %.2f mm (JLC min 0.3), centres on the board edge line%s" % (
            len(_bites), _dd, PZ.BITE_N, PZ.BITE_EDGE_GAP, "" if not _badb else ": " + "; ".join(_badb)))
        _badt = [p for d, p in _tool if not PANEL.contains(Point(p).buffer(d / 2 + 0.5)) or abs(abs(p[1]) - _yb - PZ.GAP - PZ.RAIL / 2) > 0.01]
        _corn = {(p[0] > 0, p[1] > 0) for d, p in _tool}
        (OK if len(_tool) >= 3 and len(_corn) >= 3 and not _badt and all(abs(d - 2.0) < 1e-6 for d, p in _tool) else FAIL)(
            "panel: %d tooling holes 2.0 mm in the rails on %d different corners (JLC: 2 mm tooling holes, at least 3 corners)" % (len(_tool), len(_corn)))
        # ---- nothing on the rails; nothing close to the tabs on the board side ----
        _rail_geom = PANEL.difference(_bo.buffer(0.001))
        _onrail = []
        for nm_, fn_ in (("F_Cu.gtl", "copper top"), ("B_Cu.gbl", "copper bottom"), ("F_Mask.gts", "mask top"), ("B_Mask.gbs", "mask bottom"),
                         ("F_Paste.gtp", "paste top"), ("F_Silkscreen.gto", "silk top"), ("B_Silkscreen.gbo", "silk bottom")):
            hit = [n for n in zip_names if n.endswith("-" + nm_)]
            if not hit:
                continue
            gf = GerberFile.open(os.path.join(tmp, hit[0]))
            bb = gf.bounding_box(unit=_gu.MM)
            if bb and (bb[0][1] < -_yb - 1e-6 or bb[1][1] > _yb + 1e-6):
                _onrail.append("%s (y %.2f..%.2f)" % (fn_, bb[0][1], bb[1][1]))
        (FAIL if _onrail else OK)("panel: no copper, mask, paste or silkscreen outside the board (nothing on the rails; Gerber bounding boxes inside y = +-%.1f)%s" % (_yb, "" if not _onrail else ": " + ", ".join(_onrail)))
        _bg = unary_union([Point(p).buffer(d / 2, 16) for d, p in _bites])
        _near = []
        for it in items:
            lim = 0.2 if it.kind == "pour" else 0.5     # JLC: copper >= 0.2 mm from routed edges; pours here are 0.5 mm back from the board edge already
            if it.geom.distance(_bg) < lim - TOL:
                _near.append("%s %s %s %.2f mm" % (it.kind, it.label, it.layer, it.geom.distance(_bg)))
        for hit in [n for n in zip_names if n.endswith("-F_Silkscreen.gto") or n.endswith("-B_Silkscreen.gbo")]:
            for ob in GerberFile.open(os.path.join(tmp, hit)).objects:
                bb = ob.bounding_box(_gu.MM)
                if bb and box(bb[0][0], bb[0][1], bb[1][0], bb[1][1]).distance(_bg) < 0.5 - TOL:
                    _near.append("silk %s %.2f mm" % (hit.split("-")[-1], box(bb[0][0], bb[0][1], bb[1][0], bb[1][1]).distance(_bg)))
        for e in cj:
            if e["type"] == "pcb_component" and e.get("width") and e["center"]:
                c_ = e["center"]
                if box(c_["x"] - e["width"] / 2, c_["y"] - e["height"] / 2, c_["x"] + e["width"] / 2, c_["y"] + e["height"] / 2).distance(_bg) < 0.5 - TOL:
                    _near.append("component %s %.2f mm" % (e.get("pcb_component_id"), box(c_["x"] - e["width"] / 2, c_["y"] - e["height"] / 2, c_["x"] + e["width"] / 2, c_["y"] + e["height"] / 2).distance(_bg)))
        (FAIL if _near else OK)("panel: on the board side nothing (pads, traces, vias, silk, component bodies) within 0.5 mm of a mouse-bite hole, pours >= 0.2 mm%s" % ("" if not _near else ": " + "; ".join(sorted(set(_near))[:6])))
        # ---- J2 vs the top rail ----
        _j2y = _j2["center"]["y"] + _j2["height"] / 2
        _j2pads = [e for e in cj if e["type"] == "pcb_smtpad" and e.get("x") is not None and _j2x0 - 1 < e["x"] < _j2x1 + 1 and e["y"] > 20]
        _ov = max(_j2y, max([e["y"] + e.get("height", 0) / 2 for e in _j2pads], default=0)) - _yb
        (OK if _ov < PZ.GAP - 0.3 else FAIL)("panel: J2 USB-C footprint/pads end at y %.2f = %.2f mm inside the board edge (silk %.2f); the %.1f mm gap clears the mouth even if the metal shell overhangs by up to %.1f mm in 3D" % (_yb + _ov, -_ov, 29.73, PZ.GAP, PZ.GAP - 0.3))
        print("       info: JLC capabilities 'Mouse bites Panel': tab >= 5 mm, hole 0.5-0.8 mm; blog 'mouse-bite-panelization-guide': 5-8 holes of 0.6 mm, edge gap 0.35-0.4 (min 0.3), spacing 1.6/2 mm; a customer Gerber panel gets no extra tooling data from JLC")

# =====================================================================
# E1: JLCPCB Economic PCBA compliance (rules + sources: docs/JLC_ECONOMIC.md, data: scripts/jlc_economic.py)
# =====================================================================
print("\n-- Economic PCBA compliance --")
import jlc_economic as JE
_pre = os.path.join(os.path.dirname(os.path.abspath(gz)), "EMSinterface_V2.0")
_bomf, _cplf = _pre + "-BOM_JLCPCB.csv", _pre + "-CPL_JLCPCB.csv"
if not (os.path.exists(_bomf) and os.path.exists(_cplf)):
    FAIL("Economic: BOM/CPL csv not found next to the gerber zip (%s)" % _bomf)
else:
    _bom = list(csv.DictReader(open(_bomf)))
    _cpl = list(csv.DictReader(open(_cplf)))
    _bomrefs = {d.strip() for r in _bom for d in r["Designator"].split(",")}
    _cplrefs = {r["Designator"] for r in _cpl}
    _board = [e for e in cj if e["type"] == "pcb_board"][0]
    _dnp = {s["name"] for e in cj if e["type"] == "pcb_component" and e.get("do_not_place")
            for s in cj if s["type"] == "source_component" and s["source_component_id"] == e["source_component_id"]}
    # board: layers, thickness, size, single side
    (OK if _board.get("num_layers") in JE.ECON["layers"] else FAIL)("Economic: %s copper layers (allowed 2/4/6)" % _board.get("num_layers"))
    (OK if JE.ECON["thick"][0] <= _board.get("thickness", 1.6) <= JE.ECON["thick"][1] else FAIL)("Economic: board thickness %.1f mm (0.8..1.6)" % _board.get("thickness", 0))
    _bw, _bh = _board["width"], _board["height"]
    (OK if _bw >= 10 and _bh >= 10 and max(_bw, _bh) <= 500 and min(_bw, _bh) <= 470 else FAIL)("Economic: board %.0f x %.0f mm (10x10 .. 470x500)" % (_bw, _bh))
    _layers = {r["Layer"] for r in _cpl}
    (OK if _layers <= {"Top"} else FAIL)("Economic: single-sided placement, CPL layers = %s (must be Top only)" % sorted(_layers))
    (OK if _bomrefs == _cplrefs else FAIL)("Economic: BOM and CPL list the same %d designators%s" % (len(_cplrefs), "" if _bomrefs == _cplrefs else " (diff %s)" % sorted(_bomrefs ^ _cplrefs)))
    _both = sorted(_dnp & _bomrefs)
    (OK if not _both else FAIL)("Economic: DNP parts %s are not in BOM/CPL%s" % (sorted(_dnp), "" if not _both else " (STILL IN BOM: %s)" % _both))
    # every assembled part: has an LCSC number and PCBA Type "Economic and Standard"
    _badp, _wave = [], []
    for r in _bom:
        c = r["LCSC Part #"].strip()
        t = JE.PARTS.get(c)
        if not re.fullmatch(r"C\d+", c):
            _badp.append("%s (no LCSC number)" % r["Designator"])
        elif t is None:
            _badp.append("%s %s (not in scripts/jlc_economic.py: look up jlcpcb.com/partdetail/%s 'PCBA Type', or run jlc_economic.py --live)" % (r["Designator"], c, c))
        elif t[1] != JE.ES:
            _badp.append("%s %s is '%s'" % (r["Designator"], c, t[1]))
        elif t[0] == "Wave Soldering":
            _wave.append(r["Designator"])
    (FAIL if _badp else OK)("Economic: all %d BOM lines are 'Economic and Standard' parts%s" % (len(_bom), "" if not _badp else ": " + "; ".join(_badp)))
    if _wave:
        print("       info: THT parts assembled by wave soldering (allowed in Economic, 'Single sided placement (SMT/Thru-hole)'): %s" % ", ".join(_wave))
    # smallest package 0402 / IC pitch >= 0.4 mm among assembled parts (pad pitch of every assembled part's smt pads)
    _sc = {s["source_component_id"]: s["name"] for s in cj if s["type"] == "source_component"}
    _pitch = []
    _pads = collections.defaultdict(list)
    for e in cj:
        if e["type"] == "pcb_smtpad" and e.get("shape") == "rect":
            pr = pin_str(e.get("pcb_port_id"))
            if pr and pr.split(".")[0] in _bomrefs and pr.split(".")[0][0] in "UO":
                _pads[pr.split(".")[0]].append((e["x"], e["y"]))
    for ref, ps in _pads.items():
        m = min((math.hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(ps) for b in ps[i + 1:] if abs(a[0] - b[0]) < 0.01 or abs(a[1] - b[1]) < 0.01), default=9)
        if m < JE.ECON["min_ic_pitch"] - 1e-6:
            _pitch.append("%s %.2f mm" % (ref, m))
    (FAIL if _pitch else OK)("Economic: IC pad pitch of assembled ICs >= 0.4 mm%s" % ("" if not _pitch else ": " + ", ".join(_pitch)))
    _pk = [r["Designator"] for r in _bom if r["Footprint"].strip() in ("0201", "01005")]
    (FAIL if _pk else OK)("Economic: smallest package 0402 (no 0201/01005 in BOM)%s" % ("" if not _pk else ": " + ", ".join(_pk)))
    # body-to-board-edge >= 2.5 mm (JLC terms 'Notes on DFM' no. 3; pad bbox is a conservative proxy, connectors at the edge are exempt)
    _poly = Polygon([(p["x"], p["y"]) for p in _board["outline"]]) if _board.get("outline") else box(-_bw / 2, -_bh / 2, _bw / 2, _bh / 2)
    _edge = []
    for e in cj:
        if e["type"] == "pcb_component" and e["source_component_id"] in _sc and _sc[e["source_component_id"]] in _bomrefs:
            n = _sc[e["source_component_id"]]
            c_, w_, h_ = e["center"], e["width"], e["height"]
            bx_ = box(c_["x"] - w_ / 2, c_["y"] - h_ / 2, c_["x"] + w_ / 2, c_["y"] + h_ / 2)
            if PANEL is not None:
                # delivered panel: the conveyor/clamp edges are the rails (top/bottom panel edge); the board edge is a mouse-bite break line, not a transport edge
                d = min(abs(PANEL.bounds[3] - bx_.bounds[3]), abs(bx_.bounds[1] - PANEL.bounds[1]))
            else:
                d = _poly.exterior.distance(bx_)
            if d < JE.ECON["edge_body_mm"] and n not in ("J2",):
                _edge.append("%s %.2f mm" % (n, d))
    if PANEL is not None:
        OK("Economic: all assembled parts >= 2.5 mm from the panel edges that carry the board through SMT (top/bottom rails: nearest part %.1f mm from the panel edge); the breakaway board edge is no transport edge" % (
            min(min(PANEL.bounds[3] - e["center"]["y"] - e["height"] / 2, e["center"]["y"] - e["height"] / 2 - PANEL.bounds[1]) for e in cj if e["type"] == "pcb_component" and e["source_component_id"] in _sc and _sc[e["source_component_id"]] in _bomrefs)))
    elif _edge:
        WARN("Economic/JLC DFM: part pads closer than 2.5 mm to the board edge (body distance is larger; JLC terms 'body to edge >= 2.5 mm', verify in the order DFM preview): " + ", ".join(_edge))
    else:
        OK("Economic: all assembled parts >= 2.5 mm from the board edge (J2 USB-C edge connector exempt)")
    print("       info: Economic needs no edge rails/fiducials; this panel is customer-made (rails + mouse bites, tooling holes 2 mm); order: 2-50 pcs, 1.6 mm, HASL or ENIG, standard stack-up")

print("\n%d FAIL, %d WARN" % (len(fails), len(warns)))
print("ALL FAB CHECKS OK" if not fails else "FAB CHECKS FAILED")
sys.exit(1 if fails else 0)
