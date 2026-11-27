"""Copper-pour sliver detection / removal (R7 m2), shared by postprocess_gerbers.py (removes) and check_fab.py G8 (verifies).

Pour copper narrower than NECK (mm) -- fingers between two clearance zones, tips of the pour polygon -- can peel off during etching (acid traps) and is flagged
by JLC DFM.  The pour is "opened" (erode by NECK/2, dilate by NECK/2, mitre joins): everything that disappears is a sliver.  The removal polygons
(`sliver_clears`) are written to the copper Gerber as clear-polarity regions (%LPC) AFTER the pour; they never touch pads, vias, plated holes or traces
(those obstacles are subtracted with a 0.02 mm margin).  Features wider than NECK are unchanged.
"""
import math
from shapely.geometry import Point, LineString, Polygon, box
from shapely.affinity import rotate
from shapely.ops import unary_union

NECK = 0.15
SPLIT_AREA = 0.5     # mm2: pieces smaller than this do not count as pour pieces
MIN_AREA = 0.004     # mm2: smaller leftovers are ignored (numerical dust)


def pour_polys(cj, layer):
    out = []
    for e in cj:
        if e["type"] == "pcb_copper_pour" and e["layer"] == layer:
            b = e["brep_shape"]
            pg = Polygon([(v["x"], v["y"]) for v in b["outer_ring"]["vertices"]],
                         [[(v["x"], v["y"]) for v in r["vertices"]] for r in b.get("inner_rings", [])])
            out.append(pg if pg.is_valid else pg.buffer(0))
    return out


def obstacles(cj, layer):
    """pads, plated holes, vias and traces of a layer as one geometry"""
    gs = []
    for e in cj:
        t = e["type"]
        if t == "pcb_smtpad" and e["layer"] == layer:
            sh, x, y = e["shape"], e["x"], e["y"]
            if sh in ("rect", "rotated_rect"):
                g = box(x - e["width"] / 2, y - e["height"] / 2, x + e["width"] / 2, y + e["height"] / 2)
                if sh == "rotated_rect" and e.get("ccw_rotation"):
                    g = rotate(g, e["ccw_rotation"], origin=(x, y))
            elif sh == "circle":
                g = Point(x, y).buffer(e["radius"], 16)
            elif sh in ("pill", "rotated_pill"):
                w, h = e["width"], e["height"]
                r = min(w, h) / 2
                g = LineString([(x - (w - h) / 2, y), (x + (w - h) / 2, y)]).buffer(r, 8) if w >= h else LineString([(x, y - (h - w) / 2), (x, y + (h - w) / 2)]).buffer(r, 8)
                if sh == "rotated_pill" and e.get("ccw_rotation"):
                    g = rotate(g, e["ccw_rotation"], origin=(x, y))
            elif sh == "polygon":
                g = Polygon([(p["x"], p["y"]) for p in e["points"]])
            else:
                g = Point(x, y).buffer(0.6)
            gs.append(g)
        elif t == "pcb_plated_hole":
            x, y = e["x"], e["y"]
            d = max(e.get("outer_diameter", 0) or 0, e.get("outer_width", 0) or 0, e.get("outer_height", 0) or 0, e.get("rect_pad_width", 0) or 0, e.get("rect_pad_height", 0) or 0, 1.0)
            gs.append(Point(x, y).buffer(d / 2 + 0.1, 12))
        elif t == "pcb_via":
            gs.append(Point(e["x"], e["y"]).buffer(e["outer_diameter"] / 2, 12))
        elif t == "pcb_trace":
            pts = e["route"]
            for a, b in zip(pts, pts[1:]):
                if a["route_type"] == "wire" and b["route_type"] == "wire" and a["layer"] == layer == b["layer"]:
                    w = b.get("width", a["width"])
                    gs.append(LineString([(a["x"], a["y"]), (b["x"], b["y"])]).buffer(w / 2, 6) if (a["x"], a["y"]) != (b["x"], b["y"]) else Point(a["x"], a["y"]).buffer(w / 2, 6))
    return unary_union(gs) if gs else Polygon()


def sliver_clears(cj, layer, neck=NECK):
    """(polygons to clear, kept necks, pour geometry) of one layer"""
    pours = pour_polys(cj, layer)
    if not pours:
        return [], [], None
    allp = unary_union(pours)
    opened = allp.buffer(-neck / 2 + 0.0005, join_style=2).buffer(neck / 2 - 0.0005, join_style=2)
    lost = allp.difference(opened).difference(obstacles(cj, layer).buffer(0.02))
    polys = [p for p in (lost.geoms if hasattr(lost, "geoms") else [lost]) if p.area >= MIN_AREA and p.geom_type == "Polygon"]
    # A lost polygon that is a NECK (its removal splits the pour into pieces of >= SPLIT_AREA mm2) is removed only together with a DEAD LOBE: a piece that touches no pad,
    # via, hole or trace at all (other nets keep >= 0.2 mm clearance, so such a piece is pour copper without any connection of its own: it hangs on the neck only).
    # Necks between pieces that both carry pads/traces are kept (reported): removing them could cut a pour connection.
    obst = obstacles(cj, layer).buffer(0.02)
    obst_tight = obstacles(cj, layer)

    def comps(g):
        return [q for q in (g.geoms if hasattr(g, "geoms") else [g]) if q.area >= SPLIT_AREA]
    grown, necks = [], []
    cur = allp
    for p in sorted(polys, key=lambda q: q.area):
        g = p.buffer(0.01, join_style=2).difference(obst)
        gl = [q for q in (g.geoms if hasattr(g, "geoms") else [g]) if q.area > 0 and q.geom_type == "Polygon"]
        if not gl:
            continue
        nxt = cur.difference(unary_union(gl))
        before, after = comps(cur), comps(nxt)
        if len(after) <= len(before):
            cur = nxt
            grown += gl
            continue
        # split: dead lobes = new pieces without any obstacle
        dead = [q for q in after if not obst_tight.buffer(0.05).intersects(q)]
        live = [q for q in after if q not in dead]
        if dead and live:
            for d in dead:
                gl.append(d.buffer(0.01, join_style=2))
            cur = cur.difference(unary_union(gl))
            grown += gl
        else:
            necks.append(p)
    return grown, necks, allp
