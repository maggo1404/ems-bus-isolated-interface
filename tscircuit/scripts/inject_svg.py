#!/usr/bin/env python3
"""Add the 2D-barcode square and the swan logo (silk_extras.py; not native tscircuit elements) to dist/index/pcb.svg so that the PNG renders
(scripts/render_png.cjs -> docs/img/pcb.png) show them.  The SVG<->board transform is fitted on the through-hole pads (same order in
circuit.json and svg).  Idempotent.  Usage: python3 scripts/inject_svg.py [dist/index/pcb.svg] [dist/index/circuit.json]"""
import json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import silk_extras as SX

svgp = sys.argv[1] if len(sys.argv) > 1 else "dist/index/pcb.svg"
cjp = sys.argv[2] if len(sys.argv) > 2 else "dist/index/circuit.json"
CJ = json.load(open(cjp))
svg = re.sub(r'<g id="silk-extras">.*?</g>', "", open(svgp).read(), flags=re.S)
ph = [(e["x"], e["y"]) for e in CJ if e["type"] == "pcb_plated_hole"]
sv = [(float(a), float(b)) for a, b in re.findall(r'class="pcb-hole-outer"[^>]*? cx="([-\d.e]+)" cy="([-\d.e]+)"', svg)][:len(ph)]
# scale / offset from the first two plated holes (P1, distinct y), verified against ALL plated holes (nearest svg circle)
s = (sv[1][1] - sv[0][1]) / (ph[1][1] - ph[0][1])
sx, sy = s, -abs(s) if s < 0 else -s
sy = -abs(s)
sx = abs(s)
ox, oy = sv[0][0] - sx * ph[0][0], sv[0][1] - sy * ph[0][1]
allsv = np.array([(float(a), float(b)) for a, b in re.findall(r'class="pcb-hole-outer"[^>]*? cx="([-\d.e]+)" cy="([-\d.e]+)"', svg)])
dist = sorted(np.min(np.hypot(allsv[:, 0] - (sx * x + ox), allsv[:, 1] - (sy * y + oy))) for x, y in ph)
res = dist[4]    # holes inside rotated groups (J2 shell) are drawn in local coordinates: the majority must match
assert res < 0.1, "svg transform fit failed (residual %.3f)" % res
col = (re.search(r'pcb-silkscreen-top"[^>]*?\sstroke="(#[0-9a-fA-F]+)"', svg) or [None, "#f2eda1"])[1]
def path(g):
    d = ""
    for p in SX.polys_of(g):
        for r in [p.exterior] + list(p.interiors):
            c = list(r.coords)
            d += "M" + " L".join("%.2f,%.2f" % (sx * x + ox, sy * y + oy) for x, y in c) + " Z "
    return d
logo = SX.logo_printable(CJ)
g = '<g id="silk-extras"><path d="%s" fill="%s" fill-rule="evenodd" stroke="none"/><path d="%s" fill="%s" fill-rule="evenodd" stroke="none"/></g>' % (
    path(SX.barcode_poly()), col, path(logo), col)
k = svg.rindex("</svg>")
open(svgp, "w").write(svg[:k] + g + svg[k:])
print("inject_svg: barcode square + logo added to %s (silk colour %s, fit residual %.3f px)" % (svgp, col, res))
