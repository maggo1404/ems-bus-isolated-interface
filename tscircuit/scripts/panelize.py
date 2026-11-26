#!/usr/bin/env python3
"""Customer-made breakaway panel for JLCPCB Economic PCBA (run by scripts/export_fab.sh AFTER postprocess_gerbers.py).

The delivered PCB must be >= 70 mm in each direction; the board is 110 x 60 mm.  This adds two breakaway rails (top and bottom, along the
110 mm edges) joined by mouse-bite tabs:  panel = 110 x 74 mm = 5 mm rail + 2 mm routed gap + 60 mm board + 2 mm gap + 5 mm rail.
After break-off the board is the unchanged 110 x 60 mm outline (the board itself - placement, copper, silk, mask, paste - is NOT touched;
the Gerber origin stays the board centre, so the CPL stays valid).

What is changed in the Gerber zip (idempotent, always rebuilt from dist/index/circuit.json):
  * <proj>-Edge_Cuts.gm1: ONE closed contour = rails + board outline + tab bridges (the 2 mm gaps between the tabs are the routed slots, open at the
    panel ends / corner notches), followed by the unchanged OC1/OC2 slot contours.
  * <proj>-NPTH.drl: mouse-bite holes (0.6 mm, 5 per tab, hole edge to hole edge 0.35 mm = pitch 0.95 mm, centre on the board edge line, i.e. the
    hole row runs along the break line) + 3 tooling holes 2.0 mm in the rails.  Existing holes are untouched.
Rules: docs/JLC_ECONOMIC.md section "Breakaway rails / panel".
Usage: python3 scripts/panelize.py [fab/EMSinterface_V2.0-gerbers.zip] [dist/index/circuit.json]
"""
import json, os, re, shutil, sys, zipfile
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

# ---------------- panel parameters (checked by scripts/check_fab.py "Panel" section) ----------------
RAIL = 5.0            # rail width (JLC: 'use 5 mm tooling edges', minimum 3 mm)
GAP = 2.0             # routed gap board <-> rail (JLC: 1.6 or 2 mm, minimum 1.2 mm)
TAB_W = 5.0           # breakaway tab width (JLC: 'For breakaway with mouse-bites, the minimum width is 5 mm')
BITE_D = 0.60         # mouse-bite hole diameter (JLC: 0.6 mm; capabilities page 0.5-0.8 mm)
BITE_EDGE_GAP = 0.35  # hole edge to hole edge (JLC blog: 0.35-0.4, minimum 0.3 mm)
BITE_PITCH = BITE_D + BITE_EDGE_GAP
BITE_N = 5            # holes per tab (JLC: 5 to 8 per set)
BITE_INSET = 0.0      # hole centre distance from the board edge line into the board (JLC: on the frame centre line or <= 1/3 hole into the board)
TOOL_D = 2.0          # tooling holes in the rails (JLC: 2 mm)
TOOL_X = 52.5         # |x| of the tooling holes (2.5 mm from the panel end), y = centre of the rail
# tab centres along X (board edge y = +-30 is straight for |x| <= 49.5).  Excluded: USB-C J2 mouth x 27..39 (tab zone must stay >= 3 mm away),
# antenna region x >= 45, corner notches (|x| > 49.5), isolation slot silk line at x = 0.
TABS_TOP = [-40.0, -14.0, 12.0]
TABS_BOTTOM = [-38.0, 10.0, 34.0]
MIN_PANEL = 70.0

NPTH = "NPTH.drl"
EDGE = "Edge_Cuts.gm1"


def board_outline(cj):
    b = next(e for e in cj if e["type"] == "pcb_board")
    if b.get("outline"):
        return Polygon([(p["x"], p["y"]) for p in b["outline"]]), b
    w, h, c = b["width"], b["height"], b["center"]
    return box(c["x"] - w / 2, c["y"] - h / 2, c["x"] + w / 2, c["y"] + h / 2), b


def geometry(cj):
    """-> dict(board, panel (single polygon), bites [(x,y)], tools [(x,y)], tabs [(side, xc)], yb (board half height), ytop, ybot)"""
    bo, b = board_outline(cj)
    minx, miny, maxx, maxy = bo.bounds
    rails = [box(minx, maxy + GAP, maxx, maxy + GAP + RAIL), box(minx, miny - GAP - RAIL, maxx, miny - GAP)]
    tabs = []
    bites = []
    for side, xs, ye, sg in (("top", TABS_TOP, maxy, 1), ("bottom", TABS_BOTTOM, miny, -1)):
        for xc in xs:
            tabs.append((side, xc))
            y0, y1 = sorted((ye - sg * 0.5, ye + sg * (GAP + 0.5)))   # overlap 0.5 mm into board and rail
            tabs_poly = box(xc - TAB_W / 2, y0, xc + TAB_W / 2, y1)
            rails.append(tabs_poly)
            for i in range(BITE_N):
                bites.append((round(xc + (i - (BITE_N - 1) / 2) * BITE_PITCH, 4), round(ye - sg * BITE_INSET, 4)))
    pan = unary_union([bo] + rails)
    assert pan.geom_type == "Polygon", "panel must be one connected piece"
    tools = [(-TOOL_X, maxy + GAP + RAIL / 2), (-TOOL_X, miny - GAP - RAIL / 2), (TOOL_X, miny - GAP - RAIL / 2)]
    return dict(board=bo, panel=pan, bites=bites, tools=tools, tabs=tabs, ytop=maxy, ybot=miny, bounds=pan.bounds)


def _fmt(v):
    return str(int(round(v * 1e6)))


def edge_gerber(orig, pan):
    """Edge_Cuts: the tscircuit file = board outline contour + OC1/OC2 slot contours.  The board outline contour is replaced by the panel contours
    (outer contour + the closed routed slots between the tabs); the slot contours stay.  Idempotent (an earlier panel section is cut off first)."""
    if "G04 PANEL" in orig:
        cut = orig.index("G04 PANEL")
        k = orig.rindex("M02*")
        orig = orig[:cut] + orig[k:]                      # earlier panel section removed ...
        k = orig.index("D10*")
        head, rest = orig[:k], orig[k:]
        blocks = [b for b in rest.split("D10*") if b.strip()]
    else:
        k = orig.index("D10*")
        head = orig[:k]
        blocks = [b for b in orig[k:].split("D10*") if b.strip()][1:]   # ... or the plain board outline dropped
    end = ""
    if "M02*" in blocks[-1]:
        blocks[-1] = blocks[-1][:blocks[-1].index("M02*")]
        end = "M02*\n"
    body = "".join("D10*" + blk for blk in blocks)
    body += "G04 PANEL: rails + board outline + mouse-bite tabs; outer contour, then the routed slots between the tabs (scripts/panelize.py)*\n"
    for ring in [pan.exterior] + list(pan.interiors):
        pts = list(ring.coords)
        body += "D10*\nX%sY%sD02*\n" % (_fmt(pts[0][0]), _fmt(pts[0][1]))
        for p in pts[1:]:
            body += "X%sY%sD01*\n" % (_fmt(p[0]), _fmt(p[1]))
    return head + body + end


def drill_file(txt, g):
    """add mouse-bite holes (0.6 mm tool) + tooling holes (2.0 mm tool) to the NPTH drill file.
    Holes of an earlier panelize run are dropped first (board holes all lie > 2 mm inside the board edge), so the step is idempotent."""
    lines = txt.splitlines()
    k = lines.index("%")
    hdr, body = lines[:k], lines[k + 1:]
    tdefs = {}                                   # tool number -> diameter
    for ln in hdr:
        m = re.match(r"T(\d+)C([\d.]+)", ln)
        if m:
            tdefs[m.group(1)] = float(m.group(2))
    holes, order, cur = {}, [], None
    for ln in body:
        s = ln.strip()
        m = re.fullmatch(r"T(\d+)", s)
        if m:
            cur = m.group(1)
            holes.setdefault(cur, [])
            order.append(cur) if cur not in order else None
        elif re.fullmatch(r"X-?[\d.]+Y-?[\d.]+", s):
            if abs(float(re.search(r"Y(-?[\d.]+)", s).group(1))) < g["ytop"] - 2.0:
                holes[cur].append(s)
    def tool_for(d):
        for t, dd in tdefs.items():
            if abs(dd - d) < 1e-6:
                return t
        t = str(max(int(x) for x in tdefs) + 1)
        tdefs[t] = d
        holes[t] = []
        order.append(t)
        return t
    newtools = []
    for d, pts in ((BITE_D, g["bites"]), (TOOL_D, g["tools"])):
        t = tool_for(d)
        holes[t] += ["X%.4fY%.4f" % p for p in pts]
    out = [ln for ln in hdr if not re.match(r"T(\d+)C", ln) or True]
    have = {m.group(1) for m in (re.match(r"T(\d+)C", ln) for ln in hdr) if m}
    # drop an old tooling-hole tool definition that has no holes any more is not needed: tool 2.0 is always re-added
    for t, d in tdefs.items():
        if t not in have:
            out += ["; #@! TA.AperFunction,NonPlated,NPTH,ComponentDrill", "T%sC%.6f" % (t, d)]
    res = out + ["%", "G90", "G05"]
    for t in order:
        if holes[t]:
            res.append("T" + t)
            res += holes[t]
    res.append("M30")
    return "\n".join(res)


def main():
    zp = sys.argv[1] if len(sys.argv) > 1 else "fab/EMSinterface_V2.0-gerbers.zip"
    cjp = sys.argv[2] if len(sys.argv) > 2 else "dist/index/circuit.json"
    cj = json.load(open(cjp))
    g = geometry(cj)
    tmp = zp + ".tmp"
    with zipfile.ZipFile(zp) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.endswith("-" + EDGE):
                data = edge_gerber(data.decode(), g["panel"]).encode()
            elif info.filename.endswith("-" + NPTH):
                data = drill_file(data.decode(), g).encode()
            zout.writestr(info.filename, data)
    shutil.move(tmp, zp)
    x0, y0, x1, y1 = g["bounds"]
    print("panelize: panel %.1f x %.1f mm (rail %.1f + gap %.1f), %d tabs (top x=%s, bottom x=%s), %d mouse-bite holes %.2f mm @ pitch %.2f, %d tooling holes %.1f mm"
          % (x1 - x0, y1 - y0, RAIL, GAP, len(g["tabs"]), TABS_TOP, TABS_BOTTOM, len(g["bites"]), BITE_D, BITE_PITCH, len(g["tools"]), TOOL_D))


if __name__ == "__main__":
    main()
