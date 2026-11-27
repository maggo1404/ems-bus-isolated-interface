#!/usr/bin/env python3
"""JLCPCB CPL origin/rotation per part, derived from the EasyEDA footprints (scratch/easyeda/<LCSC>.json).

JLCPCB places a part with the origin and rotation of the EasyEDA library footprint.  Our tscircuit footprints are written
in their own frame, so for every part we match the pads (same pad number) of the EasyEDA footprint (origin = canvas origin
of the footprint, y flipped to y-up, 10 mil units) with the pads of our footprint and solve
    p_eda = R(theta) * p_ts + t
(theta in 0/90/180/270).  A tscircuit part at origin O with rotation phi then has
    CPL rotation = phi - theta,   CPL position = O - R(phi - theta) * t.
Parts without cached EasyEDA footprint (plain 0805/SOD-123 R/C ... from tscircuit's own footprinter) are assumed to
equal the EasyEDA footprint (theta = 0, t = 0); they are listed as 'assumed'.
Usage: python3 scripts/cpl_check.py [circuit.json]  -> prints the table; importable (cpl_rows)."""
import json, math, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from netlib import load

HERE = os.path.dirname(os.path.abspath(__file__))
EDA = os.path.join(HERE, "..", "scratch", "easyeda")


def rot(p, deg):
    a = math.radians(deg)
    return (p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a))


def eda_pads(lcsc):
    f = os.path.join(EDA, lcsc + ".json")
    if not os.path.exists(f):
        return None
    d = json.load(open(f))
    r = d.get("result", d)
    if "packageDetail" not in r:
        return None
    ds = r["packageDetail"]["dataStr"]
    hx, hy = float(ds["head"]["x"]), float(ds["head"]["y"])
    pads = {}
    for s in ds["shape"]:
        if s.startswith("PAD~"):
            f_ = s.split("~")
            x = (float(f_[2]) - hx) * 0.254
            y = -(float(f_[3]) - hy) * 0.254
            pads.setdefault(f_[8], []).append((x, y))
    return pads


def cpl_rows(cjp="dist/index/circuit.json"):
    cj = load(cjp)
    sc = {e["source_component_id"]: e for e in cj if e["type"] == "source_component"}
    sp = {e["source_port_id"]: e for e in cj if e["type"] == "source_port"}
    pp = {e["pcb_port_id"]: e for e in cj if e["type"] == "pcb_port"}
    pcomp = {e["source_component_id"]: e for e in cj if e["type"] == "pcb_component"}
    pads_of = {}
    for e in cj:
        if e["type"] in ("pcb_smtpad", "pcb_plated_hole") and e.get("pcb_port_id") in pp:
            port = sp[pp[e["pcb_port_id"]]["source_port_id"]]
            pads_of.setdefault(port["source_component_id"], {}).setdefault(str(port.get("pin_number")), []).append((e["x"], e["y"]))
    rows = []
    for sid, s in sc.items():
        name = s["name"]
        if sid not in pcomp:
            continue
        pc = pcomp[sid]
        O = pc.get("footprint_origin") or pc["center"]
        phi = pc["rotation"]
        lcsc = None
        for k in ("supplier_part_numbers", "supplier_part_number"):
            v = s.get(k)
            if isinstance(v, dict) and v.get("jlcpcb"):
                lcsc = v["jlcpcb"][0]
        if not lcsc:
            continue
        mine = {n: [((x - O["x"]), (y - O["y"])) for x, y in v] for n, v in pads_of.get(sid, {}).items()}
        mine = {n: [rot(p, -phi) for p in v] for n, v in mine.items()}
        eda = eda_pads(lcsc)
        theta, t, note, res = 0, (0.0, 0.0), "assumed equal to EasyEDA footprint (no cached EasyEDA data)", None
        if eda:
            common = [n for n in mine if n in eda and len(mine[n]) == 1 and len(eda[n]) == 1]
            best = None
            for th in (0, 90, 180, 270):
                if len(common) < 1:
                    break
                ts = [(eda[n][0][0] - rot(mine[n][0], th)[0], eda[n][0][1] - rot(mine[n][0], th)[1]) for n in common]
                tx, ty = sum(a for a, b in ts) / len(ts), sum(b for a, b in ts) / len(ts)
                err = max(math.hypot(a - tx, b - ty) for a, b in ts)
                if best is None or err < best[0] - 1e-6:
                    best = (err, th, (tx, ty))
            if not best or best[0] > 0.8:
                # pad numbers differ between the two libraries (e.g. USB-C): match the pad point sets geometrically
                A = [p for v in mine.values() for p in v]
                B = [p for v in eda.values() for p in v]
                bestg = None
                for th in (0, 90, 180, 270):
                    Ar = [rot(p, th) for p in A]
                    for a in Ar:
                        for b in B:
                            tx, ty = b[0] - a[0], b[1] - a[1]
                            err = max(min(math.hypot(a2[0] + tx - b2[0], a2[1] + ty - b2[1]) for b2 in B) for a2 in Ar)
                            err2 = max(min(math.hypot(a2[0] + tx - b2[0], a2[1] + ty - b2[1]) for a2 in Ar) for b2 in B)
                            e = max(err, err2)
                            if bestg is None or e < bestg[0] - 1e-6:
                                bestg = (e, th, (tx, ty))
                if bestg and (not best or bestg[0] < best[0]):
                    best = bestg
                    common = A
                    note_extra = " (geometric pad-set match)"
                else:
                    note_extra = ""
            else:
                note_extra = ""
            if best:
                res, theta, t = best[0], best[1], best[2]
                note = "EasyEDA match on %d pads, residual %.3f mm%s" % (len(common), res, note_extra)
                if res > 0.8:
                    note += "  ** POOR MATCH, check manually **"
        rho = (phi - theta) % 360
        rt = rot(t, rho)
        M = (O["x"] - rt[0], O["y"] - rt[1])
        rows.append(dict(ref=name, lcsc=lcsc, mid=M, rot=rho, origin=(O["x"], O["y"]), phi=phi, theta=theta, t=t, layer=pc["layer"], note=note, res=res))
    return rows


def key(d):
    m = re.match(r"([A-Za-z]+)(\d+)", d)
    return (m.group(1), int(m.group(2)))


if __name__ == "__main__":
    rows = cpl_rows(sys.argv[1] if len(sys.argv) > 1 else "dist/index/circuit.json")
    print("%-5s %-9s %-18s %-4s %-5s %-6s %-14s %s" % ("ref", "lcsc", "CPL mid x/y", "rot", "phi", "theta", "t(eda-ts)", "note"))
    for r in sorted(rows, key=lambda r: key(r["ref"])):
        print("%-5s %-9s %8.3f %8.3f  %-4d %-5d %-6d (%5.2f,%5.2f)  %s" % (r["ref"], r["lcsc"], r["mid"][0], r["mid"][1], r["rot"], r["phi"], r["theta"], r["t"][0], r["t"][1], r["note"]))
