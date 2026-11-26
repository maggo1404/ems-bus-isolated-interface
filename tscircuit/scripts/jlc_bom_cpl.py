#!/usr/bin/env python3
"""Convert the tsci gerber-zip bom.csv / pick_and_place.csv into JLCPCB upload format.

JLCPCB BOM:  Comment, Designator, Footprint, LCSC Part #   (grouped by LCSC number, designators comma-separated)
JLCPCB CPL:  Designator, Mid X, Mid Y, Layer, Rotation       (only parts that are in the BOM)
Parts without LCSC number (test pads TP1-3, solder jumper JP1) are not assembled and are dropped.
Usage: python3 scripts/jlc_bom_cpl.py [fab/EMSinterface_V2.0-gerbers.zip] [outprefix]
CPL origin/rotation are NOT those of tscircuit: scripts/cpl_check.py derives, per part, the EasyEDA footprint origin and rotation
(JLCPCB convention) by matching the EasyEDA pads to our footprint pads (details/table: docs/CPL_CHECK.md).
Usage: python3 scripts/jlc_bom_cpl.py [gerbers.zip] [outprefix] [dist/index/circuit.json]
"""
import csv, io, os, sys, zipfile, collections, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cpl_check

zp = sys.argv[1] if len(sys.argv) > 1 else "fab/EMSinterface_V2.0-gerbers.zip"
prefix = sys.argv[2] if len(sys.argv) > 2 else "fab/EMSinterface_V2.0"
z = zipfile.ZipFile(zp)
bom = list(csv.DictReader(io.StringIO(z.read("bom.csv").decode())))
cpl = list(csv.DictReader(io.StringIO(z.read("pick_and_place.csv").decode())))
# LCSC -> (comment, package)
INFO = {
    "C441236": ("2-pin 5.08mm header KF2EDGRC-5.08-2P", "THT P5.08"), "C910822": ("PTC 0.5A 24V BSMD0805-050-24V", "0805"),
    "C98021": ("4.7uH LQH32PN4R7NN0L", "1210"), "C107120": ("68pF C0G 50V", "0805"), "C22466362": ("BAT42W Schottky", "SOD-123"),
    "C8598": ("B5819W Schottky", "SOD-123"), "C81598": ("1N4148W", "SOD-123"), "C15850": ("10uF 25V X5R", "0805"),
    "C12891": ("22uF 25V X5R", "1206"), "C49256851": ("1000uF 25V JVJ25V1000M10X12", "SMD D10xL12"), "C17414": ("10k 1%", "0805"),
    "C53284030": ("68R 1% CL2010FN68RB", "2010"), "C46653": ("1nF 50V X7R", "0805"), "C1717": ("1.5nF 50V X7R", "0805"),
    "C1710": ("10nF 50V X7R", "0805"), "C49678": ("100nF 50V X7R", "0805"), "C17655": ("390R 1%", "0805"),
    "C17713": ("47k 1%", "0805"), "C149504": ("100k 1%", "0805"), "C17673": ("4.7k 1%", "0805"), "C17710": ("470R 1%", "0805"),
    "C7955": ("LM393DR2G", "SOIC-8"), "C20069155": ("BC817-40", "SOT-23"), "C16133": ("100uF 6.3V tantalum TAJB107K006RNJ", "case B 3528"), "C371172": ("JW5017S buck", "SOT-23-6"),
    "C43183": ("4.7uH SWPA5020S4R7MT", "5x5x2"), "C17772": ("6.8k 1%", "0805"), "C17384": ("1.3k 1%", "0805"),
    "C17379": ("1.2k 1%", "0805"), "C84256": ("LED red NCD0805R1", "0805"), "C92651": ("6N137S-TA1-L", "SOP-8 gull-wing"),
    "C336082": ("6N136S-TA1-L", "SOP-8 gull-wing"), "C2297": ("LED green KT-0805G", "0805"), "C17590": ("270R 1%", "0805"),
    "C2913202": ("ESP32-S3-WROOM-1-N16R8", "module 18x25.5"), "C318884": ("Tactile switch TS-1187A-B-A-B", "SMD 5.1x5.1"),
    "C28323": ("1uF 50V X7R", "0805"), "C165948": ("USB-C TYPE-C-31-M-12", "SMD+THT"), "C27834": ("5.1k 1%", "0805"),
    "C17514": ("1M 1%", "0805"), "C1744": ("4.7nF 50V X7R", "0805"), "C7519": ("USBLC6-2SC6", "SOT-23-6"),
    "C6186": ("AMS1117-3.3", "SOT-223"), "C17513": ("1k 1%", "0805"), "C32713270": ("1x4 header 2.54mm", "THT P2.54"),
}
groups = collections.OrderedDict()
for r in bom:
    lc = r["JLCPCB Part #"].strip()
    if not re.fullmatch(r"C\d+", lc):
        continue
    groups.setdefault(lc, []).append(r["Designator"])


def key(d):
    m = re.match(r"([A-Za-z]+)(\d+)", d)
    return (m.group(1), int(m.group(2)))


with open(prefix + "-BOM_JLCPCB.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for lc, ds in sorted(groups.items(), key=lambda kv: key(sorted(kv[1], key=key)[0])):
        cm, pk = INFO.get(lc, (lc, ""))
        w.writerow([cm, ",".join(sorted(ds, key=key)), pk, lc])
keep = {d for ds in groups.values() for d in ds}
with open(prefix + "-CPL_JLCPCB.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    cjp = sys.argv[3] if len(sys.argv) > 3 else "dist/index/circuit.json"
    for r in sorted(cpl_check.cpl_rows(cjp), key=lambda r: cpl_check.key(r["ref"])):
        if r["ref"] in keep:
            w.writerow([r["ref"], "%.3fmm" % r["mid"][0], "%.3fmm" % r["mid"][1], r["layer"].capitalize(), int(round(r["rot"])) % 360])
print("BOM lines:", len(groups), "parts:", len(keep), "CPL rows:", len(keep), "dropped (no LCSC):", sorted({r["Designator"] for r in bom} - keep))
missing = [lc for lc in groups if lc not in INFO]
print("no INFO for:", missing)
