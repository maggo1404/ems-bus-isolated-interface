#!/usr/bin/env python3
"""Post-process the tscircuit Gerber zip for JLCPCB (run by scripts/export_fab.sh after the BOM/CPL conversion).

1. Removes tscircuit's own bom.csv / pick_and_place.csv from the Gerber zip (untransformed rotations/centres: they must NOT be
   uploaded to the PCBA step; the JLC files are fab/*-BOM_JLCPCB.csv and *-CPL_JLCPCB.csv).
2. Silkscreen: tscircuit writes text strokes as 0.09 x font size (0.072 mm at 0.8 mm) and paths as 0.1 mm; JLCPCB needs >= 0.153 mm
   (min line width).  Every round silkscreen aperture thinner than MIN_STROKE is widened to MIN_STROKE (text height stays 1.0 mm, see check_fab.py G5).
3. Paste on plated through-holes: tscircuit also writes paste apertures for the plated slots (J2 shell legs, F_Paste/B_Paste); these are
   removed (needs dist/index/circuit.json for the hole positions).
Solder paste of the SMD pads needs no post-processing: the board sets defaultSolderPasteMargin="0mm" (index.circuit.tsx) = 100 % of the pad
(tscircuit's own default would be 70 % x 70 %); JP1/JP2/TP pads carry noSolderPaste.  check_fab.py G6 verifies this by parsing F_Paste/B_Paste.
Usage: python3 scripts/postprocess_gerbers.py [fab/EMSinterface_V2.0-gerbers.zip] [dist/index/circuit.json]
"""
import re, shutil, sys, zipfile, os, json

MIN_STROKE = 0.15
zp = sys.argv[1] if len(sys.argv) > 1 else "fab/EMSinterface_V2.0-gerbers.zip"
cjp = sys.argv[2] if len(sys.argv) > 2 else "dist/index/circuit.json"
thv = [(e["x"], e["y"]) for e in json.load(open(cjp)) if e["type"] == "pcb_plated_hole"]
removed_paste = 0
tmp = zp + ".tmp"
changed = 0
dropped = []
with zipfile.ZipFile(zp) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        name = info.filename
        if name in ("bom.csv", "pick_and_place.csv"):
            dropped.append(name)
            continue
        data = zin.read(name)
        if name in ("F_SilkScreen.gbr", "B_SilkScreen.gbr"):
            def widen(m):
                global changed
                d = float(m.group(2))
                if d < MIN_STROKE:
                    changed += 1
                    return "%%ADD%sC,%.6f*%%" % (m.group(1), MIN_STROKE)
                return m.group(0)
            data = re.sub(r"%ADD(\d+)C,([\d.]+)\*%", widen, data.decode()).encode()
        if name in ("F_Paste.gbr", "B_Paste.gbr"):
            keep = []
            for ln in data.decode().splitlines():
                m = re.match(r"X(-?\d+)Y(-?\d+)D03\*", ln.strip())
                if m and any(abs(int(m.group(1)) / 1e6 - x) < 0.01 and abs(int(m.group(2)) / 1e6 - y) < 0.01 for x, y in thv):
                    removed_paste += 1
                    continue
                keep.append(ln)
            data = ("\n".join(keep) + "\n").encode()
        zout.writestr(info, data)
shutil.move(tmp, zp)
print("postprocess_gerbers: removed %s; widened %d silkscreen apertures to %.2f mm; removed %d paste flashes on plated holes" % (", ".join(dropped) or "nothing", changed, MIN_STROKE, removed_paste))
