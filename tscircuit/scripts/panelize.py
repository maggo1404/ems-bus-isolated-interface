#!/usr/bin/env python3
"""Second fab variant: breakaway panel with mouse bites (run by scripts/export_fab.sh AFTER postprocess_gerbers.py).

Reads the finished single-board zip (fab/EMSinterface_V2.0-gerbers.zip, left untouched) and writes fab/EMSinterface_V2.0-panel-gerbers.zip:
the board (110 x 70 mm, x -55..55, y -40..30) gets a 5 mm rail + 2 mm routed gap on the top and bottom long edges -> panel 110 x 84 mm
(y -47..37), joined by mouse-bite tabs.  The Gerber origin is NOT moved, so the same BOM/CPL apply to both variants.
Only two files differ from the single zip:
  * <proj>-Edge_Cuts.gm1: ONE closed outer contour (rails + board + tab bridges) + the routed gap slots between the tabs + the unchanged opto slots.
  * <proj>-NPTH.drl: + mouse-bite holes (0.6 mm, 5 per tab, pitch 0.95 = hole edge gap 0.35, centres on the board edge line) + 3 tooling holes 2.0 mm.
Copper / mask / paste / silk / PTH are byte-identical (nothing on the rails).
Rules: docs/JLC_ECONOMIC.md "Breakaway panel variant".  Usage: python3 scripts/panelize.py [single.zip] [circuit.json] [panel.zip]
"""
import json, re, sys, zipfile
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

RAIL = 5.0            # rail width (JLC: 5 mm tooling edges, minimum 3 mm)
GAP = 2.0             # routed gap board <-> rail (JLC: 1.6 or 2 mm, minimum 1.2 mm)
TAB_W = 5.0           # tab width (JLC: mouse-bite tab >= 5 mm)
BITE_D = 0.60         # mouse-bite hole diameter (JLC 0.5-0.8, recommended 0.6)
BITE_EDGE_GAP = 0.35  # hole edge to hole edge (JLC 0.35-0.4, min 0.3)
BITE_PITCH = BITE_D + BITE_EDGE_GAP
BITE_N = 5            # holes per tab (JLC 5-8)
TOOL_D = 2.0          # tooling holes in the rails
TOOL_X = 52.5         # |x| of the tooling holes, y = rail centre
# tab centres (x).  Top: J2 mouth x 26..40, antenna x >= 45, isolation line x = 0 (+-4) stay free.
TABS_TOP = [-40.0, -16.0, 12.0]
TABS_BOTTOM = [-38.0, -14.0, 14.0]
MIN_PANEL = 70.0
EDGE, NPTH = "Edge_Cuts.gm1", "NPTH.drl"


def board_outline(cj):
    b = next(e for e in cj if e["type"] == "pcb_board")
    return Polygon([(p["x"], p["y"]) for p in b["outline"]])


def geometry(cj):
    bo = board_outline(cj)
    minx, miny, maxx, maxy = bo.bounds
    parts, tabs, bites = [], [], []
    parts += [box(minx, maxy + GAP, maxx, maxy + GAP + RAIL), box(minx, miny - GAP - RAIL, maxx, miny - GAP)]
    for side, xs, ye, sg in (("top", TABS_TOP, maxy, 1), ("bottom", TABS_BOTTOM, miny, -1)):
        for xc in xs:
            tabs.append((side, xc))
            y0, y1 = sorted((ye - sg * 0.5, ye + sg * (GAP + 0.5)))      # overlap 0.5 mm into board and rail
            parts.append(box(xc - TAB_W / 2, y0, xc + TAB_W / 2, y1))
            for i in range(BITE_N):
                bites.append((round(xc + (i - (BITE_N - 1) / 2) * BITE_PITCH, 4), round(ye, 4)))
    pan = unary_union([bo] + parts)
    assert pan.geom_type == "Polygon"
    tools = [(-TOOL_X, maxy + GAP + RAIL / 2), (-TOOL_X, miny - GAP - RAIL / 2), (TOOL_X, miny - GAP - RAIL / 2)]
    return dict(board=bo, panel=pan, bites=bites, tools=tools, tabs=tabs, bounds=pan.bounds)


def _f(v):
    return str(int(round(v * 1e6)))


def edge_gerber(orig, pan):
    k = orig.index("D10*")
    head = orig[:k]
    blocks = [b for b in orig[k:].split("D10*") if b.strip()][1:]        # drop the plain board outline contour
    end = ""
    if "M02*" in blocks[-1]:
        blocks[-1] = blocks[-1][:blocks[-1].index("M02*")]
        end = "M02*\n"
    body = "".join("D10*" + b for b in blocks)
    body += "G04 PANEL: rails + board + mouse-bite tabs; outer contour, then the routed gap slots between the tabs (scripts/panelize.py)*\n"
    for ring in [pan.exterior] + list(pan.interiors):
        pts = list(ring.coords)
        body += "D10*\nX%sY%sD02*\n" % (_f(pts[0][0]), _f(pts[0][1]))
        for p in pts[1:]:
            body += "X%sY%sD01*\n" % (_f(p[0]), _f(p[1]))
    return head + body + end


def drill_file(txt, g):
    lines = txt.splitlines()
    k = lines.index("%")
    hdr, body = lines[:k], lines[k + 1:]
    tdefs = {m.group(1): float(m.group(2)) for m in (re.match(r"T(\d+)C([\d.]+)", l) for l in hdr) if m}
    holes, order, cur = {}, [], None
    for ln in body:
        s = ln.strip()
        m = re.fullmatch(r"T(\d+)", s)
        if m:
            cur = m.group(1)
            holes.setdefault(cur, [])
            if cur not in order:
                order.append(cur)
        elif re.fullmatch(r"X-?[\d.]+Y-?[\d.]+", s):
            holes[cur].append(s)
    out = list(hdr)
    for d, pts in ((BITE_D, g["bites"]), (TOOL_D, g["tools"])):
        t = next((t for t, dd in tdefs.items() if abs(dd - d) < 1e-6), None)
        if t is None:
            t = str(max(int(x) for x in tdefs) + 1)
            tdefs[t] = d
            holes[t] = []
            order.append(t)
            out += ["; #@! TA.AperFunction,NonPlated,NPTH,ComponentDrill", "T%sC%.6f" % (t, d)]
        holes[t] += ["X%.4fY%.4f" % p for p in pts]
    res = out + ["%", "G90", "G05"]
    for t in order:
        if holes[t]:
            res += ["T" + t] + holes[t]
    return "\n".join(res + ["M30"])


def main():
    zp = sys.argv[1] if len(sys.argv) > 1 else "fab/EMSinterface_V2.0-gerbers.zip"
    cj = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "dist/index/circuit.json"))
    out = sys.argv[3] if len(sys.argv) > 3 else zp.replace("-gerbers.zip", "-panel-gerbers.zip")
    g = geometry(cj)
    with zipfile.ZipFile(zp) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.endswith("-" + EDGE):
                data = edge_gerber(data.decode(), g["panel"]).encode()
            elif info.filename.endswith("-" + NPTH):
                data = drill_file(data.decode(), g).encode()
            zi = zipfile.ZipInfo(info.filename, info.date_time)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, data)
    x0, y0, x1, y1 = g["bounds"]
    print("panelize: %s: panel %.1f x %.1f mm (y %.1f..%.1f), rail %.1f + gap %.1f, tabs top x=%s bottom x=%s, %d bites %.2f mm pitch %.2f, %d tooling holes %.1f mm"
          % (out, x1 - x0, y1 - y0, y0, y1, RAIL, GAP, TABS_TOP, TABS_BOTTOM, len(g["bites"]), BITE_D, BITE_PITCH, len(g["tools"]), TOOL_D))


if __name__ == "__main__":
    main()
