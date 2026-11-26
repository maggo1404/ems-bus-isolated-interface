#!/usr/bin/env python3
"""Check the full V2.0 board (dist/index/circuit.json) against docs/netlist_v1.json and DESIGN_SPEC.

1. All 33 V1 nets (incl. P2 -> V3V3/MCU_TX/MCU_RX/GND): the 29 EMS-only nets must match pin-for-pin
   (JLC pad numbering, see PAD_SWAP); the 4 shared MCU nets (MCUGND, MCUVCC, MCURX, MCUTX) must contain all V1 pins
   (V2 adds ESP32/USB pins to them, they are listed as 'extra').
2. New MCU-side nets from DESIGN_SPEC (VBUS, EN, BOOT, USB_DP/DN, ESP_TX, CC1/CC2 ...): pins must be on one net,
   different nets must not be shorted, EMS and MCU nets must not be shorted.
Usage: python3 scripts/check_netlist.py [circuit.json] [docs/netlist_v1.json]
"""
import json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from netlib import load, Conn

cjp = sys.argv[1] if len(sys.argv) > 1 else "dist/index/circuit.json"
refp = sys.argv[2] if len(sys.argv) > 2 else "docs/netlist_v1.json"
c = Conn(load(cjp))
ref = json.load(open(refp))
NAME = {"+5V": "V5_EMS", "GND": "GND_EMS", "VIN": "EMS_VIN", "MCUGND": "GND", "MCUVCC": "V3V3", "MCURX": "MCU_RX", "MCUTX": "MCU_TX"}
SHARED = {"MCUGND", "MCUVCC", "MCURX", "MCUTX"}
# JLC pad numbering: BAT42W (D1-D5) and green LEDs (LD2, LD3): pad1 = anode; D6, D7, LD1: pad1 = cathode
ANODE_FIRST = {"D1", "D2", "D3", "D4", "D5", "LD2", "LD3"}


def cvt(pin):
    r, pad = pin.split(".")
    if r.startswith("D") or r.startswith("LD"):
        pad = {"A": "1", "C": "2"}[pad] if r in ANODE_FIRST else {"C": "1", "A": "2"}[pad]
    elif r == "C12":
        pad = {"+": "1", "-": "2"}.get(pad, pad)
    else:
        pad = {"+": "1", "-": "2"}.get(pad, pad)
    return "%s.%s" % (r, pad)


pin2grp = {}
for g, d in c.groups.items():
    for p in d["pins"]:
        pin2grp[p] = g
ok = True
print("== V1 nets (%d) ==" % len(ref["nets"]))
for n in ref["nets"]:
    exp = {cvt(p) for p in n["pins"]}
    # V2: the single 2200uF C12 is replaced by C12 + C14 (2 x 1000uF SMD in parallel, same nets)
    exp |= {"C14." + p.split(".")[1] for p in exp if p.startswith("C12.")}
    name = NAME.get(n["name"], n["name"])
    if n["name"] == "MCUVCC":  # V2: P2 pin 1 hangs on net P2_3V3 behind the open solder jumper JP2
        exp.discard("P2.1")
    gs = {pin2grp.get(p) for p in exp}
    if len(gs) != 1 or None in gs:
        ok = False
        missing = sorted(p for p in exp if pin2grp.get(p) is None)
        print("FAIL %-8s (%s) pins not on one net; unconnected=%s groups=%d" % (n["name"], name, missing, len(gs)))
        continue
    g = gs.pop()
    got = c.groups[g]["pins"]
    extra = sorted(got - exp)
    names = sorted(c.groups[g]["names"])
    if n["name"] in SHARED:
        status = "OK  " if name in names else "FAIL"
        if status == "FAIL":
            ok = False
        print("%s %-8s -> %s  (+%d V2 pins: %s)" % (status, n["name"], names, len(extra), ",".join(extra[:40])))
    else:
        if extra:
            ok = False
            print("FAIL %-8s extra pins %s" % (n["name"], extra))
        else:
            print("OK   %-8s -> %s" % (n["name"], names))

# ---- new MCU nets (DESIGN_SPEC / src/mcu-side.tsx).  pins as Ref.pin number ----
NEW = {
    "VBUS": ["J2.2", "J2.11", "U5.3", "C24.1", "C25.1", "U4.5"],
    "V3V3": ["U3.2", "U5.2", "U5.4", "C29.1", "JP2.1", "C22.1", "C23.1", "C26.1", "C27.1", "C28.1", "R20.1", "R21.1", "R26.1", "R27.2"],
    "GND": ["U3.1", "U3.40"] + ["U3.%d" % i for i in range(41, 50)] + ["J2.1", "J2.12", "U4.2", "U5.1", "C29.2", "C20.2", "C22.2", "SW1.3", "SW1.4", "SW2.3", "SW2.4", "LD4.2", "LD5.2", "R23.2", "R24.2", "R25.2", "C21.2", "P2.4"],
    "MCU_RX": ["U3.5", "OC1.6", "P2.3"],
    "ESP_TX": ["U3.10", "JP1.1"],
    "MCU_TX": ["JP1.2", "R27.1", "OC2.3", "P2.2"],
    "USB_DP": ["J2.5", "J2.7", "U4.1", "U4.6", "U3.14"],
    "USB_DN": ["J2.6", "J2.8", "U4.3", "U4.4", "U3.13"],
    "EN": ["U3.3", "R20.2", "C20.1", "SW1.1", "SW1.2"],
    "BOOT": ["U3.27", "R21.2", "SW2.1", "SW2.2"],
    "CC1": ["J2.9", "R23.1"],
    "CC2": ["J2.3", "R24.1"],
    "SHELL": ["J2.13", "J2.14", "J2.15", "J2.16", "R25.1", "C21.1"],
    "P2_3V3": ["JP2.2", "P2.1"],
    "SBU1": [], "SBU2": [],
    "GPIO2_LED": ["U3.38", "R22.1"],
    "LED_R22": ["R22.2", "LD4.1"],
    "PWR_LED": ["R26.2", "LD5.1"],
    "UART0_TX": ["U3.37", "TP1.1"], "UART0_RX": ["U3.36", "TP2.1"], "UART0_GND": ["TP3.1", "GND_ANCHOR"],
}
print("\n== new MCU nets ==")
roots = {}
for name, pins in NEW.items():
    pins = [p for p in pins if p != "GND_ANCHOR"]
    if not pins:  # SBU1/SBU2 (J2.4, J2.10) are intentionally unconnected
        continue
    gs = {pin2grp.get(p) for p in pins}
    if len(gs) != 1 or None in gs:
        ok = False
        print("FAIL %-10s not one net: unconnected=%s" % (name, [p for p in pins if pin2grp.get(p) is None]))
        continue
    g = gs.pop()
    if name in ("UART0_GND",):
        continue
    nm = sorted(c.groups[g]["names"])
    if name in ("VBUS", "V3V3", "GND", "MCU_RX", "ESP_TX", "MCU_TX", "USB_DP", "USB_DN", "EN", "BOOT", "P2_3V3", "SHELL") and name not in nm:
        ok = False
        print("FAIL %-10s net names %s" % (name, nm))
        continue
    if g in roots:
        ok = False
        print("FAIL %-10s shorted with %s" % (name, roots[g]))
        continue
    roots[g] = name
    print("OK   %-10s -> %s (%d pins in net)" % (name, nm, len(c.groups[g]["pins"])))
# parts: LCSC numbers / values of the changed parts, every pad of USB-C / EPAD / tactile / shell on the right net
src = {x["name"]: x for x in c.cj if x["type"] == "source_component"}
for ref, mpn, lcsc in [("Q1", "BC817-40", "C20069155"), ("C29", "TAJB107K006RNJ", "C16133")]:
    comp = src.get(ref)
    got_l = (comp or {}).get("supplier_part_numbers", {}).get("jlcpcb", [])
    if not comp or comp.get("manufacturer_part_number") != mpn or lcsc not in got_l:
        ok = False
        print("FAIL part %s expected %s %s got %s" % (ref, mpn, lcsc, comp and (comp.get("manufacturer_part_number"), got_l)))
    else:
        print("OK   part %s = %s %s" % (ref, mpn, lcsc))
# JP2: V3V3 <-> P2_3V3 only through the (open) jumper: pins must be on DIFFERENT nets
if pin2grp.get("JP2.1") == pin2grp.get("JP2.2") or pin2grp.get("JP1.1") == pin2grp.get("JP1.2"):
    ok = False
    print("FAIL JP1/JP2 pins on one net (jumper not open)")
# Q1 pin order B/E/C = 1/2/3 on the V1 nets (checked above via V1 nets EMS_N14=Q1.1 base ... ) ; GND of TP3 must be on GND
if pin2grp.get("TP3.1") != pin2grp.get("U3.1"):
    ok = False
    print("FAIL TP3 not on GND")
# EMS/MCU separation by net names
EMS = lambda n: n.startswith("EMS_") or n in ("GND_EMS", "V5_EMS")
print("\n== EMS/MCU separation ==")
for g, d in c.groups.items():
    nms = d["names"]
    if any(EMS(n) for n in nms) and any(not EMS(n) for n in nms):
        ok = False
        print("FAIL net group mixes EMS and MCU names:", nms)
    if len(nms) > 1:
        ok = False
        print("FAIL net group has several names (short):", nms)
print("ALL OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
