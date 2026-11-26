#!/usr/bin/env python3
"""Parametrisches Gehaeuse fuer das EMS-Bus-Interface (FDM, PLA/PETG, 0,4 mm Duese).

Quelle der Wahrheit fuer alle Masse = PARAMS unten.  Koordinaten: Platinenmitte = (0|0),
X nach rechts (Antenne bei +X, EMS-Klemme P1 bei -X), Y nach oben (USB-C an +Y), Z = 0 ist
die Aussenseite des Gehaeuseunterteils.  OpenSCAD war in der Umgebung nicht installierbar
(apt ohne Paket), daher Python + manifold3d + trimesh.

Aufruf:  python3 enclosure.py            (STL + Pruefungen)
         python3 enclosure.py --check    (nur Pruefungen)
Optionen ueber Umgebungsvariable P_<NAME>=wert, z.B.  P_INSERT=0 P_MOUNT=keyholes python3 enclosure.py
"""
import json, os, sys, math
import numpy as np
import manifold3d as m
from manifold3d import Manifold as M, CrossSection as CS
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------------------------
# Parameter
# ----------------------------------------------------------------------------------------------
PARAMS = dict(
    # Platine
    pcb_t=1.6,                 # Platinendicke
    pcb_w=110.0, pcb_h=60.0,   # Platine X x Y
    clr=0.4,                   # Luft Platine <-> Innenwand (je Seite)
    # Huelle
    wall=2.0,                  # Wandstaerke
    wall_ant=1.2,              # Wand am Antennenende (+X), duenn
    floor_t=2.0,               # Bodenstaerke
    floor_ant_t=1.2,           # Boden unter dem Antennenbereich (Tasche von innen)
    lid_t=2.8,                 # Deckelstaerke
    lid_ant_t=1.6,             # Deckelstaerke ueber der Antenne (Tasche von innen)
    corner_r=3.0,              # Aussen-Eckenradius
    standoff=4.5,              # Abstand Boden-Innenflaeche -> Platinenunterseite (THT-Beinchen)
    h_above=16.0,              # Innenhoehe ueber Platinenoberseite (hoechstes Teil: P1 mit Stecker 15)
    ext_left=12.0,             # Zusatzraum links neben der Platine fuer den P1-Gegenstecker
    # Schrauben / Posten
    insert=1,                  # 1 = M3-Gewindeeinsatz (Heat-Set), 0 = M3 selbstschneidend
    insert_d=4.2, insert_depth=5.0,     # Bohrung fuer Heat-Set (M3 x 4, aussen ~4,6 -> Bohrung 4,2)
    pilot_d=2.6, pilot_depth=5.0,       # Kernloch fuer selbstschneidende M3 (PLA 2,6 / PETG 2,7)
    boss_d=7.0,                # Aussendurchmesser Posten und Deckelhuelse (Platine: Sperrzone O8)
    screw_clear_d=3.5,         # Durchgangsloch Deckel
    head_d=6.4, head_depth=1.8,         # Senkung fuer M3-Linsenkopf (ISO 7380: O5,7 x 1,65); Schraube M3x22
    post_gap=0.0,              # Luft zwischen Deckelhuelse und Platinenoberseite
    # Deckelfuehrung (Falz)
    rebate=1.0, rebate_h=2.0, lip_clr=0.2,
    # USB-C (J2)
    usb_w=12.0, usb_h=7.0, usb_x=33.0, usb_z_mid_above_pcb=1.63,   # Buchse 3,26 hoch -> Mitte 1,63
    # P1 Klemme
    p1_slot_w=12.0, p1_slot_h=8.0, p1_slot_z_above_pcb=5.5,        # Leitungsaustritt linke Wand
    p1_win=(-64.0, -42.0, -7.0, 7.0),                              # Deckelfenster Schraubzugang (x0,x1,y0,y1)
    # P2 Stiftleiste: 'knockout' (Deckel innen ausgenommen, Reststaerke 0,6), 'open', 'closed'
    p2_mode='knockout', p2_win=(5.5, 18.5, -29.0, -24.0), p2_membrane=0.6,
    # LEDs: 'pipe' = Lichtleiter-Stab (light_pipes.stl), 'hole' = nur Loch
    led_mode='pipe', led_hole_pipe=3.2, led_hole_open=3.0, rod_d=3.0, flange_d=4.4, flange_t=0.8,
    led_h=0.9, sleeve_od=4.6, led_gap=0.3,
    # Taster
    btn_hole=2.4, btn_sleeve_od=6.0, btn_bore=4.0, btn_top_h=1.5,
    # Gravur
    labels='engrave', label_depth=0.4, label_h=2.6,
    # Isolationsrippe
    rib=1, rib_t=1.2, rib_gap_below=0.3, rib_lid=1, rib_lid_bottom_above_pcb=5.5, rib_slot_tabs=1, tab_t=1.2,
    # Wandmontage: 'ears' | 'keyholes' | 'both' | 'none'
    mount='ears', ear_x=(-40.0, 20.0), ear_len=8.0, ear_w=10.0, ear_hole=4.5, ear_t=3.0,
    keyholes=((-25.0, 0.0), (25.0, 0.0)), key_big=7.0, key_small=3.8, key_slot=7.0,
    # Lueftung (Deckel, klein) 0/1
    vent=0,
)
for k, v in list(PARAMS.items()):
    e = os.environ.get('P_' + k.upper())
    if e is not None:
        PARAMS[k] = type(v)(float(e)) if isinstance(v, (int, float)) and not isinstance(v, bool) else e
P = type('P', (), PARAMS)

# LED-Positionen (Platinenmitte = 0|0) und Gravurtexte (Text, dx, dy relativ zur LED)
LEDS = dict(LD1=(-8.0, 24.0), LD3=(16.0, 13.6), LD2=(12.5, -13.8), LD5=(28.0, 9.3), LD4=(47.0, -16.5))
LED_LABEL = dict(LD1=('EMS', 4.0, 0.0), LD3=('RX', 3.8, 0.0), LD2=('TX', 3.8, 0.0), LD5=('3V3', 4.2, 0.0),
                 LD4=('STATUS', 0.0, 4.0))
BTN = dict(SW1=(33.5, -23.5, 'RESET', -9.5, 0.0), SW2=(34.0, -14.8, 'BOOT', -8.5, 0.0))
LED_OPT = {'LD5': dict(dx=-0.8, d=2.4)}   # LD5 liegt 1,2 mm neben dem ESP32-Modul -> duenner, versetzter Stab
HOLES = [(-42.25, 19.75), (-42.25, -19.75), (42.25, 19.75), (42.25, -19.75)]

# ----------------------------------------------------------------------------------------------
# Abgeleitete Masse
# ----------------------------------------------------------------------------------------------
Z_PCB_B = P.floor_t + P.standoff                  # Platinenunterseite
Z_PCB_T = Z_PCB_B + P.pcb_t                       # Platinenoberseite
Z_LID_U = Z_PCB_T + P.h_above                     # Deckelunterseite = Oberkante Unterteil
Z_LID_T = Z_LID_U + P.lid_t                       # Deckeloberseite
CAV_X0 = -P.pcb_w / 2 - P.clr - P.ext_left
CAV_X1 = P.pcb_w / 2 + P.clr
CAV_Y = P.pcb_h / 2 + P.clr
OUT_X0, OUT_X1 = CAV_X0 - P.wall, CAV_X1 + P.wall_ant
OUT_Y = CAV_Y + P.wall
SEG = 48


# ----------------------------------------------------------------------------------------------
# Hilfsfunktionen
# ----------------------------------------------------------------------------------------------
def led_geom(n):
    """(x, y, Stabdurchmesser) der Lichtleiter-Achse; Abweichung von der LED-Mitte nur wo noetig."""
    x, y = LEDS[n]
    o = LED_OPT.get(n, {})
    return x + o.get('dx', 0.0), y + o.get('dy', 0.0), o.get('d', P.rod_d)


_PARTS = None


def parts_boxes():
    global _PARTS
    if _PARTS is None:
        d = json.load(open(os.path.join(HERE, 'data', 'pcb_parts.json')))
        out = []
        for p in d['parts']:
            n = p['name']
            h = HEIGHT.get(n, 0.9 if n in LEDS else (1.3 if n[0] in 'RCDF' else 1.5))
            w, hh = BODY.get(n, (p['w'], p['h']))
            if n == 'P1':
                out.append((n, -55.0, -42.8, -5.88, 5.88, h)); continue
            out.append((n, p['x'] - w / 2, p['x'] + w / 2, p['y'] - hh / 2, p['y'] + hh / 2, h))
        _PARTS = out
    return _PARTS


def clear_height(x, y, r, skip=()):
    """hoechste Bauteilhoehe (ueber Platinenoberseite) im Kreis r um (x,y)."""
    hmax = 0.0
    for (n, x0, x1, y0, y1, h) in parts_boxes():
        if n in skip:
            continue
        dx = max(x0 - x, 0, x - x1); dy = max(y0 - y, 0, y - y1)
        if math.hypot(dx, dy) < r:
            hmax = max(hmax, h)
    return hmax


def box(x0, x1, y0, y1, z0, z1):
    return M.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cyl(x, y, z0, z1, r, r2=None):
    return M.cylinder(z1 - z0, r, r if r2 is None else r2, SEG).translate([x, y, z0])


def rrect(x0, x1, y0, y1, r, z0, z1):
    sq = CS.square([x1 - x0 - 2 * r, y1 - y0 - 2 * r]).translate([x0 + r, y0 + r])
    sq = sq.offset(r, m.JoinType.Round, 2.0, SEG) if r > 0 else sq
    return M.extrude(sq, z1 - z0).translate([0, 0, z0])


def union(items):
    items = [i for i in items if i is not None]
    return M.batch_boolean(items, m.OpType.Add)


def text_solid(s, cx, cy, z0, z1, h=None):
    """Text als Extrusion (zentriert um cx,cy)."""
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    h = h or P.label_h
    tp = TextPath((0, 0), s, size=h, prop=FontProperties(family='DejaVu Sans', weight='bold'))
    polys = [np.asarray(p) for p in tp.to_polygons() if len(p) > 2]
    cs = CS(polys, m.FillRule.EvenOdd)
    b = cs.bounds()
    cs = cs.translate([cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2])
    return M.extrude(cs, z1 - z0).translate([0, 0, z0])


# ----------------------------------------------------------------------------------------------
# Unterteil
# ----------------------------------------------------------------------------------------------
def make_bottom(bosses=True):
    outer = rrect(OUT_X0, OUT_X1, -OUT_Y, OUT_Y, P.corner_r, 0, Z_LID_U)
    cav = rrect(CAV_X0, CAV_X1, -CAV_Y, CAV_Y, 1.0, P.floor_t, Z_LID_U + 1)
    b = outer - cav
    # Falz (nur links/oben/unten; rechts duenne Wand ohne Falz)
    reb = rrect(CAV_X0 - P.rebate, CAV_X1, -CAV_Y - P.rebate, CAV_Y + P.rebate, 1.0, Z_LID_U - P.rebate_h, Z_LID_U + 1)
    b = b - reb
    # Antennenbereich: Boden von innen auf floor_ant_t abduennen
    if P.floor_ant_t < P.floor_t:
        b = b - box(47.0, CAV_X1 - 0.01, -24.0, 24.0, P.floor_ant_t, P.floor_t + 0.01)
    # Posten
    for (x, y) in (HOLES if bosses else []):
        boss = cyl(x, y, 0.0, P.floor_t + 1.5, 4.6, 3.5) + cyl(x, y, P.floor_t + 1.0, Z_PCB_B, P.boss_d / 2)
        b = b + boss
        if P.insert:
            b = b - cyl(x, y, Z_PCB_B - P.insert_depth, Z_PCB_B + 0.1, P.insert_d / 2)
        else:
            b = b - cyl(x, y, Z_PCB_B - P.pilot_depth, Z_PCB_B + 0.1, P.pilot_d / 2)
    # Isolationsrippe unter der Platine (x=0) + Zungen durch die Optokoppler-Schlitze
    if P.rib:
        rib = box(-P.rib_t / 2, P.rib_t / 2, -CAV_Y - 0.1, CAV_Y + 0.1, P.floor_t - 0.1, Z_PCB_B - P.rib_gap_below)
        b = b + rib
        if P.rib_slot_tabs:
            for ys in (8.0, -8.0):
                b = b + box(-P.tab_t / 2, P.tab_t / 2, ys - 5.7, ys + 5.7, Z_PCB_B - P.rib_gap_below - 0.1, Z_PCB_T - 0.4)
    # USB-C Ausschnitt (+Y Wand)
    uz = Z_PCB_T + P.usb_z_mid_above_pcb
    cut = M.extrude(CS.square([P.usb_w - 2, P.usb_h - 2]).translate([-(P.usb_w - 2) / 2, -(P.usb_h - 2) / 2])
                    .offset(1.0, m.JoinType.Round, 2.0, 24), CAV_Y + P.wall + 1.0 - (CAV_Y - 1.0))
    # Extrusion laeuft in +Z; auf +Y drehen: (x,y,z)->(x,z,y)
    cut = cut.rotate([-90, 0, 0]).translate([P.usb_x, CAV_Y - 1.0, uz])
    b = b - cut
    # P1 Leitungsaustritt (linke Wand)
    pz = Z_PCB_T + P.p1_slot_z_above_pcb
    s = M.extrude(CS.square([P.p1_slot_w - 2, P.p1_slot_h - 2]).translate([-(P.p1_slot_w - 2) / 2, -(P.p1_slot_h - 2) / 2])
                  .offset(1.0, m.JoinType.Round, 2.0, 24), P.wall + 2.0)
    s = s.rotate([90, 0, 90]).translate([OUT_X0 - 0.5, 0, pz])
    b = b - s
    # Wandmontage
    if P.mount in ('ears', 'both'):
        for xe in P.ear_x:
            for sgn in (1, -1):
                yc = sgn * (OUT_Y + P.ear_len - P.ear_w / 2 + 0.0)
                ear = box(xe - P.ear_w / 2, xe + P.ear_w / 2, min(sgn * (OUT_Y - 1.0), sgn * (OUT_Y + P.ear_len - P.ear_w / 2)),
                          max(sgn * (OUT_Y - 1.0), sgn * (OUT_Y + P.ear_len - P.ear_w / 2)), 0, P.ear_t)
                ear = ear + cyl(xe, yc, 0, P.ear_t, P.ear_w / 2)
                ear = ear - cyl(xe, yc, -0.1, P.ear_t + 0.1, P.ear_hole / 2)
                b = b + ear
    if P.mount in ('keyholes', 'both'):
        for (kx, ky) in P.keyholes:
            kh = cyl(kx, ky, -0.1, P.floor_t + 0.1, P.key_big / 2)
            kh = kh + box(kx - P.key_small / 2, kx + P.key_small / 2, ky, ky + P.key_slot, -0.1, P.floor_t + 0.1)
            kh = kh + cyl(kx, ky + P.key_slot, -0.1, P.floor_t + 0.1, P.key_small / 2)
            b = b - kh
    return b


# ----------------------------------------------------------------------------------------------
# Deckel (in Einbaulage, Oberseite = +Z)
# ----------------------------------------------------------------------------------------------
def make_lid(posts=True):
    plate = rrect(OUT_X0, OUT_X1, -OUT_Y, OUT_Y, P.corner_r, Z_LID_U, Z_LID_T)
    lid = plate
    # Falz-Lippe (innen, nur links/oben/unten)
    lip_out = rrect(CAV_X0 - P.rebate + P.lip_clr, CAV_X1, -CAV_Y - P.rebate + P.lip_clr, CAV_Y + P.rebate - P.lip_clr, 1.0,
                    Z_LID_U - P.rebate_h + P.lip_clr, Z_LID_U + 0.01)
    lip_in = rrect(CAV_X0, CAV_X1 + 1, -CAV_Y, CAV_Y, 1.0, Z_LID_U - P.rebate_h, Z_LID_U + 1)
    lid = lid + (lip_out - lip_in)
    # Schraubhuelsen
    for (x, y) in (HOLES if posts else []):
        lid = lid + cyl(x, y, Z_PCB_T + P.post_gap, Z_LID_U + 0.01, P.boss_d / 2)
    # Rippe oben
    if P.rib_lid:
        lid = lid + box(-P.rib_t / 2, P.rib_t / 2, -CAV_Y, CAV_Y, Z_PCB_T + P.rib_lid_bottom_above_pcb, Z_LID_U + 0.01)
    # LED-Huelsen
    led_bottom = Z_PCB_T + P.led_h + P.led_gap + 0.2
    led_info = {}
    for n in LEDS:
        x, y, rd = led_geom(n)
        hole_d = rd + 0.2 if P.led_mode == 'pipe' else rd
        sod = hole_d + 1.6
        lb = max(led_bottom, Z_PCB_T + clear_height(x, y, sod / 2 + 0.3, skip=(n,)) + 0.4)
        led_info[n] = (x, y, hole_d, sod, lb)
        lid = lid + cyl(x, y, lb, Z_LID_U + 0.01, sod / 2)
    # Tasterhuelsen (Bohrung 4,0 unter dem Deckel, 2,4 durch die Platte)
    btn_bottom = Z_PCB_T + P.btn_top_h + 0.8
    for n, (x, y, *_r) in BTN.items():
        lid = lid + cyl(x, y, btn_bottom, Z_LID_U + 0.01, P.btn_sleeve_od / 2)
    # --- Abzuege ---
    cuts = []
    for (x, y) in HOLES:
        cuts.append(cyl(x, y, Z_PCB_T, Z_LID_T + 1, P.screw_clear_d / 2))
        cuts.append(cyl(x, y, Z_LID_T - P.head_depth, Z_LID_T + 1, P.head_d / 2))
    for n, (x, y, hole_d, sod, lb) in led_info.items():
        cuts.append(cyl(x, y, lb - 0.1, Z_LID_T + 1, hole_d / 2))
        if P.led_mode == 'pipe':
            cuts.append(cyl(x, y, Z_LID_T - P.flange_t, Z_LID_T + 1, (hole_d + 1.4 + 0.4) / 2))
    for n, (x, y, *_r) in BTN.items():
        cuts.append(cyl(x, y, Z_LID_U + 0.0, Z_LID_T + 1, P.btn_hole / 2))
        cuts.append(cyl(x, y, btn_bottom - 0.1, Z_LID_U, P.btn_bore / 2))
    # P1 Fenster
    x0, x1, y0, y1 = P.p1_win
    cuts.append(rrect(x0, x1, y0, y1, 1.0, Z_LID_U - 0.1, Z_LID_T + 1))
    # P2
    x0, x1, y0, y1 = P.p2_win
    if P.p2_mode == 'open':
        cuts.append(rrect(x0, x1, y0, y1, 0.8, Z_LID_U - 0.1, Z_LID_T + 1))
    elif P.p2_mode == 'knockout':
        cuts.append(rrect(x0, x1, y0, y1, 0.8, Z_LID_U - 0.1, Z_LID_T - P.p2_membrane))
    # Antennenbereich: Deckel duenner (Tasche von innen)
    if P.lid_ant_t < P.lid_t:
        cuts.append(box(47.0, CAV_X1 - 0.01, -24.0, 24.0, Z_LID_U - 0.1, Z_LID_T - P.lid_ant_t))
    # Lueftungsschlitze
    if P.vent:
        for xs in np.arange(-30, -14, 3.0):
            cuts.append(rrect(xs - 0.8, xs + 0.8, -7, 7, 0.8, Z_LID_U - 0.1, Z_LID_T + 1))
    lid = lid - union(cuts)
    # Gravuren
    if P.labels == 'engrave':
        tx = []
        for n, (x, y) in LEDS.items():
            t, dx, dy = LED_LABEL[n]
            tx.append(text_solid(t, x + dx + (len(t) * 0.9 if dx > 0 else 0), y + dy, Z_LID_T - P.label_depth, Z_LID_T + 0.1))
        for n, (x, y, t, dx, dy) in BTN.items():
            tx.append(text_solid(t, x + dx, y + dy, Z_LID_T - P.label_depth, Z_LID_T + 0.1))
        tx.append(text_solid('P2', 12.0, -22.0, Z_LID_T - P.label_depth, Z_LID_T + 0.1)) if P.p2_mode != 'closed' else None
        tx.append(text_solid('EMS-BUS', -53.0, 12.0, Z_LID_T - P.label_depth, Z_LID_T + 0.1, 3.0))
        lid = lid - union(tx)
    return lid


def rod_len():
    return Z_LID_T - (Z_PCB_T + P.led_h + P.led_gap)


def make_rod(n='LD1'):
    """Lichtleiter-Stab in Einbaulage um (0,0) (Flansch oben)."""
    zb = Z_PCB_T + P.led_h + P.led_gap
    d = led_geom(n)[2]
    return cyl(0, 0, zb, Z_LID_T - P.flange_t + 0.01, d / 2) + cyl(0, 0, Z_LID_T - P.flange_t, Z_LID_T, d / 2 + 0.7)


def make_plunger():
    """Taster-Stoessel in Einbaulage."""
    zb = Z_PCB_T + P.btn_top_h + 0.2
    shaft = cyl(0, 0, zb, Z_LID_T + 0.6 + 0.01, 1.0)
    collar = cyl(0, 0, Z_LID_U - 1.4, Z_LID_U - 0.4, 1.8)
    cap = cyl(0, 0, Z_LID_T + 0.6, Z_LID_T + 1.6, 2.5)
    return shaft + collar + cap


# ----------------------------------------------------------------------------------------------
# Platinenmodell (Pruefkoerper)
# ----------------------------------------------------------------------------------------------
HEIGHT = dict(C12=12.5, C14=12.5, P1=10.0, P2=11.5, J2=3.3, U3=3.3, OC1=4.0, OC2=4.0, L3=2.1, L1=2.0, L2=2.0,
              SW1=1.5, SW2=1.5, U1=1.8, U5=1.8, U2=1.3, U4=1.3, Q1=1.3, C11=1.8, C26=1.8, JP1=0.1, JP2=0.1,
              TP1=0.1, TP2=0.1, TP3=0.1, R2=0.9, R3=0.9, R4=0.9)
BODY = dict(C12=(10.4, 10.4), C14=(10.4, 10.4), P1=(12.2, 11.76), P2=(10.2, 2.5))


def pcb_model(with_parts=True):
    d = json.load(open(os.path.join(HERE, 'data', 'pcb_parts.json')))
    outline = [(p['x'], p['y']) for p in d['board']['outline']]
    cs = CS([np.array(outline)])
    board = M.extrude(cs, P.pcb_t).translate([0, 0, Z_PCB_B])
    cuts = [cyl(x, y, Z_PCB_B - 1, Z_PCB_T + 1, 1.75) for x, y in HOLES]
    for c in d['cutouts']:
        cuts.append(box(c['x'] - c['w'] / 2, c['x'] + c['w'] / 2, c['y'] - c['h'] / 2, c['y'] + c['h'] / 2, Z_PCB_B - 1, Z_PCB_T + 1))
    board = board - union(cuts)
    items = [board]
    leds = {k for k in LEDS}
    if with_parts:
        for p in d['parts']:
            n = p['name']
            h = HEIGHT.get(n, 0.9 if n in leds else (1.3 if n[0] in 'RCDF' else 1.5))
            w, hh = BODY.get(n, (p['w'], p['h']))
            if n == 'P1':
                x0, x1 = -55.0, -42.8
                items.append(box(x0, x1, -w / 2 if False else -5.88, 5.88, Z_PCB_T, Z_PCB_T + h))
                continue
            items.append(box(p['x'] - w / 2, p['x'] + w / 2, p['y'] - hh / 2, p['y'] + hh / 2, Z_PCB_T, Z_PCB_T + h))
        for ph in d['plated_holes']:
            items.append(cyl(ph['x'], ph['y'], Z_PCB_B - 2.5, Z_PCB_B + 0.01, (ph['d'] or 1.5) / 2))
    return union(items), d


def plug_model():
    """P1-Gegenstecker (Zubehoer, 14,5 mm hoch) im Zusatzraum; Schraubfenster darueber."""
    return box(-67.0, -48.0, -6.3, 6.3, Z_PCB_T + 0.3, Z_PCB_T + 14.5)


def screws(length=22.0):
    """M3x22 Linsenkopf (ISO 7380) als Pruefkoerper."""
    zh = Z_LID_T - P.head_depth
    return [cyl(x, y, zh - length, zh, 1.5) + cyl(x, y, zh, zh + 1.65, 2.85) for (x, y) in HOLES]


# ----------------------------------------------------------------------------------------------
def to_tm(mf):
    mesh = mf.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts), process=True)


def vol(mf):
    return mf.volume()


def main():
    only_check = '--check' in sys.argv
    bottom, lid = make_bottom(), make_lid()
    rod, plunger = make_rod(), make_plunger()
    pcb, data = pcb_model()
    plug = plug_model()
    scr = screws()
    res = {}
    # --- Export (Druckausrichtung) ---
    os.makedirs(os.path.join(HERE, 'stl'), exist_ok=True)
    lid_print = lid.rotate([180, 0, 0])
    lid_print = lid_print.translate([0, 0, -lid_print.bounding_box()[2]])
    # Lichtleiter: 5 Stk. nebeneinander, Flansch unten (Druckausrichtung)
    L = rod_len()
    rods = []
    for i, n in enumerate(LEDS):
        r = make_rod(n).translate([0, 0, -Z_LID_T])      # Flanschoberseite bei z=0
        r = r.rotate([180, 0, 0])                          # Flansch unten
        r = r.translate([i * 8.0, 0, 0])
        rods.append(r)
    rods = union(rods)
    pls = union([make_plunger().translate([0, 0, -Z_LID_T - 0.6]).rotate([180, 0, 0]).translate([i * 8.0, 0, 0]) for i in range(2)])
    parts = dict(bottom=bottom, lid=lid_print, light_pipes=rods, buttons=pls)
    meshes = {}
    for n, mf in parts.items():
        t = to_tm(mf)
        meshes[n] = t
        if not only_check:
            t.export(os.path.join(HERE, 'stl', n + '.stl'))
        bb = t.bounds
        res[n] = dict(size=[round(float(v), 2) for v in (bb[1] - bb[0])], watertight=bool(t.is_watertight),
                      winding=bool(t.is_winding_consistent), volume_cm3=round(float(t.volume) / 1000, 2),
                      manifold_status=str(mf.status()), euler=int(t.euler_number))
    # --- Kollisionspruefung (Einbaulage) ---
    def inter(a, b):
        return round(float((a ^ b).volume()), 3)

    chk = {}
    chk['Unterteil x Platine+Bauteile'] = inter(bottom, pcb)
    chk['Deckel x Platine+Bauteile'] = inter(lid, pcb)
    chk['Unterteil x Deckel'] = inter(bottom, lid)
    chk['Unterteil x P1-Stecker'] = inter(bottom, plug)
    chk['Deckel x P1-Stecker'] = inter(lid, plug)
    rods_in = [make_rod(n).translate(list(led_geom(n)[:2]) + [0]) for n in LEDS]
    chk['Lichtleiter x Platine'] = max(inter(r, pcb) for r in rods_in)
    chk['Lichtleiter x Deckel'] = max(inter(r, lid) for r in rods_in)
    chk['Lichtleiter x Unterteil'] = max(inter(r, bottom) for r in rods_in)
    pl_in = [plunger.translate([x, y, 0]) for (x, y, *_r) in BTN.values()]
    chk['Stoessel x Deckel'] = max(inter(r, lid) for r in pl_in)
    chk['Stoessel x Platine'] = max(inter(r, pcb) for r in pl_in)
    chk['Schrauben x Platine'] = max(inter(s, pcb) for s in scr)
    chk['Schrauben x Deckel'] = max(inter(s, lid) for s in scr)
    chk['Schrauben x Unterteil (Kernloch/Einsatz, nur Info)'] = max(inter(s, bottom) for s in scr)
    gaps = {}
    pcb_parts = union([box(x0, x1, y0, y1, Z_PCB_T, Z_PCB_T + h) for (n, x0, x1, y0, y1, h) in parts_boxes() if n != 'P1'] +
                      [box(-55, -42.8, -5.88, 5.88, Z_PCB_T, Z_PCB_T + 10)])
    b0, l0 = make_bottom(bosses=False), make_lid(posts=False)
    gaps['Unterteil (ohne Posten)<->Platine inkl. THT-Beinchen (mm)'] = round(float(b0.min_gap(pcb, 5.0)), 3)
    gaps['Deckel (ohne Huelsen)<->Bauteile (mm)'] = round(float(l0.min_gap(pcb_parts, 5.0)), 3)
    gaps['Posten/Huelsen<->Platine (Auflage/Klemmung, mm)'] = round(float(bottom.min_gap(pcb, 5.0)), 3)
    gaps['Deckel<->hoechstes Bauteil C12/C14 (mm)'] = round(Z_LID_U - (Z_PCB_T + 12.5), 2)
    gaps['Deckel<->P1-Stecker (mm)'] = round(Z_LID_U - (Z_PCB_T + 14.5), 2)
    # Platine <-> Innenwand ohne Bauteile
    bare, _ = pcb_model(with_parts=False)
    gaps['Unterteil (ohne Posten)<->nackte Platine (mm)'] = round(float(b0.min_gap(bare, 5.0)), 3)
    res['collisions_mm3'] = chk
    res['gaps'] = gaps
    res['dims'] = dict(outer_xyz=[round(OUT_X1 - OUT_X0, 2), round(2 * OUT_Y, 2), round(Z_LID_T, 2)],
                       inner_cavity=[round(CAV_X1 - CAV_X0, 2), round(2 * CAV_Y, 2)],
                       z=dict(pcb_bottom=Z_PCB_B, pcb_top=Z_PCB_T, lid_underside=Z_LID_U, lid_top=Z_LID_T),
                       rod_length=round(L, 2), usb_centre_z=round(Z_PCB_T + P.usb_z_mid_above_pcb, 2))
    print(json.dumps(res, indent=1, ensure_ascii=False))
    json.dump(res, open(os.path.join(HERE, 'data', 'fit_check.json'), 'w'), indent=1, ensure_ascii=False)
    if not only_check:
        import render
        render.render_all(dict(bottom=bottom, lid=lid, pcb=pcb, plug=plug, rods=rods_in, rodsm=rods_in, plungers=pl_in, scr=scr, cut=box(-80, 70, -40, 6, -5, 60)),
                          to_tm, globals())
    return res


if __name__ == '__main__':
    main()
