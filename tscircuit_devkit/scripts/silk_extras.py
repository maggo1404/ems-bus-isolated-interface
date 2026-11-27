#!/usr/bin/env python3
"""Extra top-silkscreen artwork that tscircuit cannot draw natively (no filled silkscreen polygons): the JLCPCB 2D-barcode marker
(solid 8x8 mm square) and the black-swan logo (10 mm, from assets/blackswan.svg).  Shared by postprocess_gerbers.py (Gerber regions),
check_fab.py (clearance checks) and inject_svg.py (renders).  All coordinates mm, board centre = origin, +Y up (Gerber / circuit.json frame).

JLCPCB rule (https://jlcpcb.com/help/article/how-to-mark-on-pcb): 'Specify Position' + a SOLID square on the silkscreen layer of the
barcode size (5x5 / 8x8 / 10x10 mm); keep it away from traces, drills and other silkscreen, ideally on mask over large copper or bare substrate.
"""
import os, io, json, hashlib
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, box, Point
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, "..", "assets", "blackswan.svg")
CACHE = os.path.join(HERE, "..", "assets", "blackswan_silk.json")   # generated; keeps the exporter independent of cairosvg/skimage

# ---- placement (centre coordinates, mm) -------------------------------------------------------
BARCODE_C = (-50.0, 11.5)   # 8x8 mm solid square: x -54..-46, y 7.5..15.5 (left of P1 when the board is turned so 'EMS BUS' reads upright)
BARCODE_S = 8.0
LOGO_C = (46.0, -2.0)       # logo bounding-box centre (DevKitC variant: right of the DevKitC plate, x 41..51)
LOGO_W = 10.0               # logo width (height follows the aspect ratio, <= 10 mm)
SILK_CLEAR = 0.15           # silk-to-pad / via clearance applied to the logo
MIN_FEAT = 0.15             # JLC min silk line width / gap

def barcode_poly():
    cx, cy = BARCODE_C
    return box(cx - BARCODE_S / 2, cy - BARCODE_S / 2, cx + BARCODE_S / 2, cy + BARCODE_S / 2)

def _raster_logo():
    import cairosvg
    from PIL import Image
    from skimage import measure
    N = 3072
    png = cairosvg.svg2png(url=SVG, output_width=N, output_height=N, background_color="white")
    im = np.asarray(Image.open(io.BytesIO(png)).convert("L"), dtype=float) / 255.0   # painter's order resolved by the renderer
    dark = im < 0.5                                                                    # 50 % luminance threshold
    ys, xs = np.where(dark)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1                   # crop to the artwork (the SVG has wide margins)
    dark = np.pad(dark[y0:y1, x0:x1], 1)
    cs = measure.find_contours(dark.astype(float), 0.5)
    polys = []
    for c in cs:
        if len(c) < 4: continue
        p = Polygon([(x, -y) for y, x in c]).buffer(0)
        if p.area > 4: polys.append(p)
    # even-odd assembly (outer contours and holes alternate)
    polys.sort(key=lambda p: -p.area)
    g = Polygon()
    for p in polys:
        g = g.symmetric_difference(p)
    return g

def logo_local():
    """Printable swan in mm, centred on its bounding box, width LOGO_W, hole-aware shapely geometry."""
    if os.path.exists(CACHE):
        d = json.load(open(CACHE))
        return unary_union([Polygon(p["ext"], p["holes"]) for p in d])
    g = _raster_logo()
    minx, miny, maxx, maxy = g.bounds
    s = LOGO_W / (maxx - minx)
    g = affinity.scale(g, s, s, origin=(0, 0))
    minx, miny, maxx, maxy = g.bounds
    g = affinity.translate(g, -(minx + maxx) / 2, -(miny + maxy) / 2)
    r = MIN_FEAT / 2
    g = g.buffer(-r, join_style=1).buffer(r, join_style=1)      # opening: drop strokes < 0.15 mm
    g = g.buffer(r, join_style=1).buffer(-r, join_style=1)      # closing: fill gaps < 0.15 mm
    g = g.simplify(0.02)
    parts = list(g.geoms) if isinstance(g, MultiPolygon) else [g]
    parts = [p for p in parts if p.area > 0.02]
    json.dump([{"ext": [list(c) for c in p.exterior.coords], "holes": [[list(c) for c in h.coords] for h in p.interiors]} for p in parts], open(CACHE, "w"))
    return unary_union(parts)

def logo_poly():
    g = logo_local()
    return affinity.translate(g, LOGO_C[0], LOGO_C[1])

def copper_obstacles(CJ, pad_margin=SILK_CLEAR):
    """Exposed copper the logo must stay off: SMD pads, plated holes, vias, NPTH (top side), grown by pad_margin."""
    ob = []
    for e in CJ:
        t = e["type"]
        if t == "pcb_smtpad" and e.get("layer") == "top":
            if e["shape"] == "rect": ob.append(box(e["x"] - e["width"] / 2, e["y"] - e["height"] / 2, e["x"] + e["width"] / 2, e["y"] + e["height"] / 2))
            elif e["shape"] == "circle": ob.append(Point(e["x"], e["y"]).buffer(e["radius"]))
            elif e["shape"] == "rotated_rect":
                b = box(-e["width"] / 2, -e["height"] / 2, e["width"] / 2, e["height"] / 2)
                ob.append(affinity.translate(affinity.rotate(b, e.get("ccw_rotation", 0), origin=(0, 0)), e["x"], e["y"]))
            else:
                ob.append(Point(e["x"], e["y"]).buffer(max(e.get("width", 1), e.get("height", 1)) / 2))
        elif t == "pcb_via":
            ob.append(Point(e["x"], e["y"]).buffer(e.get("outer_diameter", 0.6) / 2))
        elif t == "pcb_plated_hole":
            d = e.get("outer_diameter") or max(e.get("outer_width", 1), e.get("outer_height", 1))
            ob.append(Point(e["x"], e["y"]).buffer(d / 2 + 0.1))
        elif t == "pcb_hole":
            ob.append(Point(e["x"], e["y"]).buffer(e.get("hole_diameter", 1) / 2))
    return unary_union(ob).buffer(pad_margin) if ob else Polygon()

def logo_printable(CJ):
    """Logo geometry clipped away from copper obstacles (>= SILK_CLEAR); sub-0.15 mm leftovers removed again."""
    g = logo_poly().difference(copper_obstacles(CJ))
    r = MIN_FEAT / 2
    g = g.buffer(-r, join_style=1).buffer(r, join_style=1)
    return g

def polys_of(g):
    return list(g.geoms) if hasattr(g, "geoms") else ([g] if not g.is_empty else [])

def gerber_regions(g):
    """Top-silk Gerber text (%LPD% filled outer rings, %LPC% holes, strictly alternating so each hole is cleared after its outer)."""
    out = []
    def ring(pts, pol):
        s = "%LP" + pol + "*%\nG36*\n"
        s += "X%dY%dD02*\nG01*\n" % (round(pts[0][0] * 1e6), round(pts[0][1] * 1e6))
        s += "".join("X%dY%dD01*\n" % (round(x * 1e6), round(y * 1e6)) for x, y in pts[1:]) + "G37*\n"
        return s
    for p in polys_of(g):
        out.append(ring(list(p.exterior.coords), "D"))
        for h in p.interiors:
            out.append(ring(list(h.coords), "C"))
    return "".join(out) + "%LPD*%\n"

def svg_path(g, fill, opacity=1.0):
    """SVG <path> (even-odd) in board mm with Y flipped (SVG frame y_down = -y)."""
    d = ""
    for p in polys_of(g):
        for r in [p.exterior] + list(p.interiors):
            c = list(r.coords)
            d += "M" + " L".join("%.3f,%.3f" % (x, -y) for x, y in c) + " Z "
    return d
