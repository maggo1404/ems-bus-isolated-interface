#!/usr/bin/env python3
"""JLCPCB Economic-PCBA rules + per-part "PCBA Type" (data for check_fab.py) and an optional live re-check.

Sources (fetched 2026-11-26, quotes in docs/JLC_ECONOMIC.md):
  https://jlcpcb.com/capabilities/pcb-assembly-capabilities   (Economic vs Standard table)
  https://jlcpcb.com/partdetail/<LCSC>                          (field "PCBA Type": "Economic and Standard" | "Standard Only";
                                                                 field "Assembly Type": "SMT Assembly" | "Wave Soldering")
Usage: python3 scripts/jlc_economic.py [--live] [BOM.csv]   (--live re-reads every BOM part from jlcpcb.com/partdetail)"""
import csv, html, re, subprocess, sys

# LCSC -> (Assembly Type, PCBA Type) as shown on jlcpcb.com/partdetail on 2026-11-26
ES, SO = "Economic and Standard", "Standard Only"
PARTS = {
    "C107120": ("SMT Assembly", ES), "C15850": ("SMT Assembly", ES), "C46653": ("SMT Assembly", ES), "C1717": ("SMT Assembly", ES),
    "C1744": ("SMT Assembly", ES), "C49678": ("SMT Assembly", ES), "C12891": ("SMT Assembly", ES), "C49256851": ("SMT Assembly", ES),
    "C28323": ("SMT Assembly", ES), "C16133": ("SMT Assembly", ES), "C22466362": ("SMT Assembly", ES), "C81598": ("SMT Assembly", ES),
    "C8598": ("SMT Assembly", ES), "C910822": ("SMT Assembly", ES), "C269119": ("SMT Assembly", ES), "C165948": ("SMT Assembly", ES),
    "C98021": ("SMT Assembly", ES), "C43183": ("SMT Assembly", ES), "C84256": ("SMT Assembly", ES), "C2296": ("SMT Assembly", ES),
    "C92651": ("SMT Assembly", ES), "C336082": ("SMT Assembly", ES), "C441236": ("Wave Soldering", ES), "C20071202": ("Wave Soldering", ES), "C32713270": ("Wave Soldering", ES),
    "C20069155": ("SMT Assembly", ES), "C17414": ("SMT Assembly", ES), "C53284030": ("SMT Assembly", ES), "C17655": ("SMT Assembly", ES),
    "C17713": ("SMT Assembly", ES), "C149504": ("SMT Assembly", ES), "C17673": ("SMT Assembly", ES), "C17710": ("SMT Assembly", ES),
    "C17772": ("SMT Assembly", ES), "C26010": ("SMT Assembly", ES), "C17471": ("SMT Assembly", ES), "C17384": ("SMT Assembly", ES),
    "C17379": ("SMT Assembly", ES), "C17630": ("SMT Assembly", ES), "C27834": ("SMT Assembly", ES), "C17514": ("SMT Assembly", ES),
    "C318884": ("SMT Assembly", ES), "C7955": ("SMT Assembly", ES), "C371172": ("SMT Assembly", ES), "C7519": ("SMT Assembly", ES),
    "C6186": ("SMT Assembly", ES),
    # not assembled (DNP, hand-soldered): every ESP32-S3 module (WROOM-1/-1U/MINI-1, all flash/PSRAM variants) is "Standard Only"
    "C2913202": ("SMT Assembly", SO),
}
# Economic limits (capabilities table)
ECON = dict(layers=(2, 4, 6), thick=(0.8, 1.6), single_min=(10, 10), single_max=(470, 500), min_package="0402", min_ic_pitch=0.4,
            min_bga_pitch=0.5, qty=(2, 50), sides=1, edge_body_mm=2.5)


def live(code):
    t = subprocess.run(["curl", "-sL", "-m", "40", "-A", "Mozilla/5.0", "https://jlcpcb.com/partdetail/" + code], capture_output=True, text=True).stdout
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"</(dd|dt|div|p|span)>", "|", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    g = lambda k: (re.search(k + r"\|+\s*([^|]{1,60})", t) or [0, "?"])[1].strip()
    return g("Assembly Type"), g("PCBA Type")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--live"]
    bom = list(csv.DictReader(open(args[0] if args else "fab/EMSinterface_V2.0_DevKitC-BOM_JLCPCB.csv")))
    bad = 0
    for r in bom:
        c = r["LCSC Part #"]
        got = live(c) if "--live" in sys.argv else PARTS.get(c, ("?", "?"))
        flag = "" if got[1] == ES else "   <-- NOT ECONOMIC"
        bad += bool(flag)
        print("%-10s %-16s %-16s %s%s" % (c, r["Designator"][:16], got[0], got[1], flag))
    print("Economic-compatible" if not bad else "%d part(s) block Economic PCBA" % bad)
    sys.exit(1 if bad else 0)
