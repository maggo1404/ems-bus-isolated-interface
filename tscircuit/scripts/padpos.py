#!/usr/bin/env python3
"""Print pad centres (board coords) for Ref.pin items: python3 scripts/padpos.py U2.2 C10.1 ..."""
import sys, json
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from netlib import load, Conn
cj = load("dist/index/circuit.json")
c = Conn(cj)
pp = {p["pcb_port_id"]: p for p in cj if p["type"] == "pcb_port"}
want = set(sys.argv[1:])
for e in cj:
    if e["type"] in ("pcb_smtpad", "pcb_plated_hole") and e.get("pcb_port_id") in pp:
        r = c.ports.get(pp[e["pcb_port_id"]]["source_port_id"])
        if r and "%s.%s" % r in want:
            w = e.get("width") or e.get("outer_diameter"); h = e.get("height") or w
            print("%s.%s" % r, round(e["x"], 2), round(e["y"], 2), "size", w, h)
