#!/usr/bin/env python3
"""Post-process the tscircuit Gerber zip for JLCPCB (run by scripts/export_fab.sh after the BOM/CPL conversion).

1. Removes tscircuit's own bom.csv / pick_and_place.csv from the Gerber zip (untransformed rotations/centres: they must NOT be
   uploaded to the PCBA step; the JLC files are fab/*-BOM_JLCPCB.csv and *-CPL_JLCPCB.csv).
2. Silkscreen: tscircuit writes text strokes as 0.09 x font size (0.167 mm at 1.85 mm) and paths/circles as 0.1 mm; JLCPCB needs >= 0.153 mm
   (min line width).  Every round silkscreen aperture thinner than MIN_STROKE (0.16 mm) is widened to MIN_STROKE (glyph height, see check_fab.py G5, is measured from the Gerber).
3b. Copper pour slivers (< 0.15 mm wide fingers/tips between clearance zones, R7 m2) are cleared with %LPC regions after the pour (scripts/slivers.py).
4. Renames the files to the JLC/KiCad pattern <project>-F_Cu.gtl, -B_Cu.gbl, -F_Mask.gts, -B_Mask.gbs, -F_Paste.gtp, -B_Paste.gbp, -F_Silkscreen.gto, -B_Silkscreen.gbo,
   -Edge_Cuts.gm1, -PTH.drl (vias + plated holes + slots), -NPTH.drl (R7 m7).  Contents (X2 attributes) are unchanged.
3. Paste on plated through-holes: tscircuit also writes paste apertures for the plated slots (J2 shell legs, F_Paste/B_Paste); these are
   removed (needs dist/index/circuit.json for the hole positions).
Solder paste of the SMD pads needs no post-processing: the board sets defaultSolderPasteMargin="0mm" (index.circuit.tsx) = 100 % of the pad
(tscircuit's own default would be 70 % x 70 %); JP1/JP2/TP pads carry noSolderPaste.  check_fab.py G6 verifies this by parsing F_Paste/B_Paste.
Usage: python3 scripts/postprocess_gerbers.py [fab/EMSinterface_V2.0_DevKitC-gerbers.zip] [dist/index/circuit.json]
"""
import re, shutil, sys, zipfile, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slivers, silk_extras

MIN_STROKE = 0.16   # JLC min silk line width 0.153 mm (R7 M1)
# tscircuit file name -> JLC/KiCad-style name (<project>-<name>), R7 m7
RENAME = {
    "F_Cu.gbr": "F_Cu.gtl", "B_Cu.gbr": "B_Cu.gbl", "F_Mask.gbr": "F_Mask.gts", "B_Mask.gbr": "B_Mask.gbs",
    "F_Paste.gbr": "F_Paste.gtp", "B_Paste.gbr": "B_Paste.gbp", "F_SilkScreen.gbr": "F_Silkscreen.gto", "B_SilkScreen.gbr": "B_Silkscreen.gbo",
    "Edge_Cuts.gbr": "Edge_Cuts.gm1", "drill-L1-L2.drl": "PTH.drl", "drill_npth.drl": "NPTH.drl",
}
PREFIX = os.path.basename(sys.argv[1] if len(sys.argv) > 1 else "fab/EMSinterface_V2.0_DevKitC-gerbers.zip").rsplit("-gerbers", 1)[0]
zp = sys.argv[1] if len(sys.argv) > 1 else "fab/EMSinterface_V2.0_DevKitC-gerbers.zip"
cjp = sys.argv[2] if len(sys.argv) > 2 else "dist/index/circuit.json"
CJ = json.load(open(cjp))
thv = [(e["x"], e["y"]) for e in CJ if e["type"] == "pcb_plated_hole"]
sliver_n = 0
removed_paste = 0
tmp = zp + ".tmp"
changed = 0
dropped = []
with zipfile.ZipFile(zp) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        name = info.filename
        for old, new in RENAME.items():            # idempotent: an already renamed zip is accepted
            if name.endswith("-" + new):
                name = old
        if name in ("bom.csv", "pick_and_place.csv", "F_Fab.gbr", "B_Fab.gbr"):   # F_Fab = fabrication notes (DevKitC outline for the assembly drawing), not for the fab
            dropped.append(name)
            continue
        data = zin.read(info.filename)
        if name in ("F_SilkScreen.gbr", "B_SilkScreen.gbr"):
            def widen(m):
                global changed
                d = float(m.group(2))
                if d < MIN_STROKE:
                    changed += 1
                    return "%%ADD%sC,%.6f*%%" % (m.group(1), MIN_STROKE)
                return m.group(0)
            data = re.sub(r"%ADD(\d+)C,([\d.]+)\*%", widen, data.decode()).encode()
        if name == "F_SilkScreen.gbr":
            # 5. JLCPCB 2D-barcode marker (solid 8x8 mm square) + black-swan logo as filled G36/G37 regions (scripts/silk_extras.py);
            #    idempotent: a previous run's regions are not duplicated (the file is rebuilt from tscircuit's export each time)
            txt = data.decode()
            k = txt.rindex("M02*")
            art = "G04 JLCPCB 2D barcode marker (solid square) and swan logo*\n" + silk_extras.gerber_regions(silk_extras.barcode_poly()) + silk_extras.gerber_regions(silk_extras.logo_printable(CJ))
            data = (txt[:k] + art + txt[k:]).encode()
        if name in ("F_Cu.gbr", "B_Cu.gbr"):
            # R7 m2: remove copper pour slivers narrower than 0.15 mm by clear-polarity regions appended after the pour (scripts/slivers.py)
            clears, _necks, _ = slivers.sliver_clears(CJ, "top" if name == "F_Cu.gbr" else "bottom")
            txt = data.decode()
            k = txt.rindex("M02*")
            add = ""
            for pg in clears:
                pts = list(pg.exterior.coords)
                add += "%LPC*%\nG36*\n" + "X%dY%dD02*\nG01*\n" % (round(pts[0][0] * 1e6), round(pts[0][1] * 1e6))
                add += "".join("X%dY%dD01*\n" % (round(x * 1e6), round(y * 1e6)) for x, y in pts[1:]) + "G37*\n%LPD*%\n"
            data = (txt[:k] + add + txt[k:]).encode()
            sliver_n += len(clears)
        if name in ("F_Paste.gbr", "B_Paste.gbr"):
            keep = []
            for ln in data.decode().splitlines():
                m = re.match(r"X(-?\d+)Y(-?\d+)D03\*", ln.strip())
                if m and any(abs(int(m.group(1)) / 1e6 - x) < 0.01 and abs(int(m.group(2)) / 1e6 - y) < 0.01 for x, y in thv):
                    removed_paste += 1
                    continue
                keep.append(ln)
            data = ("\n".join(keep) + "\n").encode()
        zout.writestr(PREFIX + "-" + RENAME[name] if name in RENAME else name, data)
shutil.move(tmp, zp)
print("postprocess_gerbers: renamed %d files to %s-<layer>.<ext>; removed %s; silk barcode square + logo added; widened %d silkscreen apertures to %.2f mm; removed %d paste flashes on plated holes; cleared %d copper pour slivers < %.2f mm" % (len(RENAME), PREFIX, ", ".join(dropped) or "nothing", changed, MIN_STROKE, removed_paste, sliver_n, slivers.NECK))
