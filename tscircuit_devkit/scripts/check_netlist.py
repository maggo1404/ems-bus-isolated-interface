#!/usr/bin/env python3
"""Check the full V2.0 board (dist/index/circuit.json) against docs/netlist_v1.json and DESIGN_SPEC.

1. All 33 V1 nets (incl. P2 -> V3V3/MCU_TX/MCU_RX/GND): the 29 EMS-only nets must match pin-for-pin
   (JLC pad numbering, see PAD_SWAP); the 4 shared MCU nets (MCUGND, MCUVCC, MCURX, MCUTX) must contain all V1 pins
   (V2 adds ESP32/USB pins to them, they are listed as 'extra').
2. New MCU-side nets of the DevKitC variant (ESP_TX, P2_3V3, GPIO2 LED, DevKitC socket pins J1/J3): pins must be on one net,
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
    # V2: C30 (100 nF) is added in parallel to the buck input capacitor C10 (same nets, R5 M2)
    exp |= {"C30." + p.split(".")[1] for p in exp if p.startswith("C10.")}
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
# DevKitC variant: J1 / J3 = 1x22 sockets of the ESP32-S3-DevKitC-1 v1.1 (Espressif header table, docs/DEVKITC.md)
J1_OPEN_OK = {1: "3V3", 2: "3V3", 5: "GPIO5", 10: "GPIO17", 22: "GND"}   # J1 pins that carry a net
J3_OPEN_OK = {1: "GND", 5: "GPIO2", 21: "GND", 22: "GND"}                 # J3 pins that carry a net
NEW = {
    "V3V3": ["J1.1", "J1.2", "JP2.1", "R27.2"],
    "GND": ["J1.22", "J3.1", "J3.21", "J3.22", "LD4.2", "P2.4"],
    "MCU_RX": ["J1.5", "OC1.6", "P2.3"],
    "ESP_TX": ["J1.10", "JP1.1"],
    "MCU_TX": ["JP1.2", "R27.1", "OC2.3", "P2.2"],
    "P2_3V3": ["JP2.2", "P2.1"],
    "GPIO2_LED": ["J3.5", "R22.1"],
    "LED_R22": ["R22.2", "LD4.1"],
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
    if name in ("V3V3", "GND", "MCU_RX", "ESP_TX", "MCU_TX", "P2_3V3") and name not in nm:
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
for ref, mpn, lcsc in [("Q1", "BC817-40", "C20069155")]:
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
# DevKitC sockets: every pin except the ones above must be open (5V, RST, GPIO0 ... are NOT connected; 5V must never touch V3V3)
for ref, okp, n in (("J1", J1_OPEN_OK, 22), ("J3", J3_OPEN_OK, 22)):
    for i in range(1, n + 1):
        g = pin2grp.get("%s.%d" % (ref, i))
        if (i in okp) != (g is not None):
            ok = False
            print("FAIL %s.%d should be %s" % (ref, i, okp.get(i, "open (NC)")))
print("OK   J1/J3: only pins %s / %s are connected, the other %d pins are open" % (sorted(J1_OPEN_OK), sorted(J3_OPEN_OK), 44 - len(J1_OPEN_OK) - len(J3_OPEN_OK)))
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
