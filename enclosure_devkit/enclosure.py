#!/usr/bin/env python3
"""Parametrisches Gehaeuse fuer das EMS-Bus-Interface, DevKitC-Variante (ESP32-S3-DevKitC-1 mit 2 x USB-C, gesteckt).

Quelle der Wahrheit fuer alle Masse = PARAMS unten.  Koordinaten wie in tscircuit_devkit/: Platinenmitte = (0|0), X nach rechts
(EMS-Klemme P1 bei -X, DevKitC bei x 11 .. 36,4), Y nach oben (Antenne +Y, USB-C-Enden -Y), Z = 0 ist die Aussenseite des
Gehaeuseunterteils.  Python + manifold3d + trimesh (Netz-Variante); die B-Rep-Variante (STEP) ist enclosure_cq.py.

Aufruf:  python3 enclosure.py            (STL + Pruefungen + Bilder)
         python3 enclosure.py --check    (nur Pruefungen)
Optionen ueber Umgebungsvariable P_<NAME>=wert (nur skalare Parameter), z.B.  P_INSERT=0 P_USB_MODE=separate python3 enclosure.py
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
    wall_ant=1.2,              # Wand der Antennentasche (duenn, <= 1,5)
    floor_t=2.0,               # Bodenstaerke
    floor_ant_t=1.2,           # Boden unter der Antennentasche (von innen abgeduennt)
    lid_t=2.8,                 # Deckelstaerke
    lid_ant_t=1.2,             # Deckelstaerke ueber der Antennentasche (von innen abgeduennt, <= 1,5)
    corner_r=3.0,              # Aussen-Eckenradius
    standoff=4.5,              # Abstand Boden-Innenflaeche -> Platinenunterseite (THT-Beinchen)
    h_above=21.0,              # Innenhoehe ueber Platinenoberseite (DevKitC-Stapel 15,8 + Luft; USB-Schlitz muss unter dem Falz enden)
    ext_left=12.0,             # Zusatzraum links neben der Platine fuer den P1-Gegenstecker
    # Schrauben / Posten
    insert=1,                  # 1 = M3-Gewindeeinsatz (Heat-Set), 0 = M3 selbstschneidend
    insert_d=4.2, insert_depth=5.0,     # Bohrung fuer Heat-Set (M3 x 4, aussen ~4,6 -> Bohrung 4,2)
    pilot_d=2.6, pilot_depth=5.0,       # Kernloch fuer selbstschneidende M3 (PLA 2,6 / PETG 2,7)
    boss_d=7.0,                # Aussendurchmesser Posten und Deckelhuelse (Platine: Sperrzone O8)
    screw_clear_d=3.5,         # Durchgangsloch Deckel
    head_d=6.4, head_depth=1.8,         # Senkung fuer M3-Linsenkopf (ISO 7380: O5,7 x 1,65)
    screw_len=28.0,            # M3 x 28 (Kopfauflage ... Einsatz)
    post_gap=0.0,              # Luft zwischen Deckelhuelse und Platinenoberseite
    # Deckelfuehrung (Falz, rundum)
    rebate=1.0, rebate_h=2.0, lip_clr=0.2,
    # --- DevKitC (ESP32-S3-DevKitC-1, N16R8-Klon mit 2 x USB-C), Masse: tscircuit_devkit/docs/DEVKITC.md ---
    dk_x0=11.0, dk_x1=36.4, dk_y0=-32.9, dk_y1=29.96, dk_ant_tip=36.26,   # Platine (USB-Ende unten), Antennenspitze
    dk_pcb_t=1.6, dk_socket_h=8.5, dk_hdr_h=2.5, dk_module_h=3.2,        # Buchsenleiste 8,5 + Stiftleistenkoerper 2,5 + Platine 1,6 + Modul 3,2
    dk_module_y0=10.76,        # Modul (18 x 25,5) beginnt hier; Antennenueberstand dk_y1 .. dk_ant_tip
    dk_ant_x0=14.75, dk_ant_x1=32.75, dk_ant_t=1.2,                       # Antennen-Leiterplatte (Dicke konservativ)
    dk_row_x=(12.27, 35.13), dk_pin_y0=-26.21, dk_pin_y1=29.67,           # Buchsenleisten J1/J3 (Koerper 2,54 breit)
    # USB-C (zwei Buchsen am -Y-Ende, Mitten x laut Zeichnung; Klone weichen +-1..2 mm ab -> PARAMS anpassen)
    usb_x=(17.0, 30.4), usb_rc_w=8.94, usb_rc_d=7.35, usb_rc_h=3.26, usb_z_mid_above_dk=1.63,
    usb_mode='combined',       # 'combined' = ein Schlitz ueber beide Buchsen, 'separate' = zwei Schlitze (usb_w breit)
    usb_h=8.0, usb_pad=7.5, usb_w=12.0,   # Schlitzhoehe; combined: Ueberstand je Seite ueber die aeusseren Buchsenmitten; separate: Breite
    plug_w=11.0, plug_h=6.4,   # Stecker-Overmould (nur Pruefkoerper)
    usb_clr_y=0.5,             # Luft zwischen DevKitC-Ende (y = -32,9) und Innenseite der -Y-Wand
    ant_air=5.0,               # Luft Antenne <-> Taschenwand (Seiten und Ende)
    # Niederhalter: Rippen im Deckel auf dem Modulschirmblech
    hold=1, hold_gap=0.0, hold_pads=((17.0, 30.5, 13.5, 16.5), (17.0, 30.5, 21.5, 24.5)),
    # Unterstuetzung der Traegerplatine beim Aufstecken des DevKitC (Rippen im Boden, kontaktlos mit Luft hold_sup_gap)
    sup=1, sup_gap=0.25, sup_pads=((17.5, 29.5, -16.5, -13.5), (17.5, 29.5, 12.0, 15.0)),
    # DevKitC-Taster (RST/BOOT): Stoessel durch den Deckel; Positionen NICHT aus der Zeichnung ableitbar -> Standard 'none'
    btn_mode='none', btn_top_above_dk=2.0, dk_btn=(('RST', 20.5, -20.0), ('BOOT', 26.9, -20.0)),
    # P1 Klemme
    p1_slot_w=12.0, p1_slot_h=8.0, p1_slot_z_above_pcb=5.5,        # Leitungsaustritt linke Wand
    p1_win=(-64.0, -42.0, -7.0, 7.0),                              # Deckelfenster Schraubzugang (x0,x1,y0,y1)
    # P2 (jetzt senkrecht bei x = 8,6): 'knockout' (Deckel innen ausgenommen, Reststaerke 0,6), 'open', 'closed'
    p2_mode='knockout', p2_win=(6.4, 10.8, -30.2, -18.0), p2_membrane=0.6,
    # LEDs: 'pipe' = Lichtleiter-Stab (light_pipes.stl), 'hole' = nur Loch
    led_mode='pipe', led_hole_pipe=3.2, led_hole_open=3.0, rod_d=3.0, flange_d=4.4, flange_t=0.8,
    led_h=0.9, sleeve_od=4.6, led_gap=0.3,
    # Taster (nur btn_mode='plunger')
    btn_hole=2.4, btn_sleeve_od=6.0, btn_bore=4.0, btn_top_h=1.5,
    # Gravur
    labels='engrave', label_depth=0.4, label_h=2.6,
    # Isolationsrippe
    rib=1, rib_t=1.2, rib_gap_below=0.3, rib_lid=1, rib_lid_bottom_above_pcb=5.5, rib_slot_tabs=1, tab_t=1.2,
    # Wandmontage: 'ears' | 'keyholes' | 'both' | 'none'  (Laschen links und rechts der Antennentasche)
    mount='ears', ear_x=(-40.0, 46.0), ear_len=8.0, ear_w=10.0, ear_hole=4.5, ear_t=3.0,
    keyholes=((-25.0, 0.0), (45.0, 0.0)), key_big=7.0, key_small=3.8, key_slot=7.0,
    # Lueftung (Deckel, klein) 0/1
    vent=0,
)
for k, v in list(PARAMS.items()):
    e = os.environ.get('P_' + k.upper())
    if e is not None:
        PARAMS[k] = type(v)(float(e)) if isinstance(v, (int, float)) and not isinstance(v, bool) else e
P = type('P', (), PARAMS)

# LED-Positionen (Platinenmitte = 0|0, aus tscircuit_devkit/dist/index/circuit.json; LD5 entfaellt) und Gravurtexte (Text, dx, dy relativ zur LED)
LEDS = dict(LD1=(-8.0, 24.0), LD3=(9.6, 15.5), LD2=(9.9, -13.5), LD4=(38.4, 7.4))
LED_LABEL = dict(LD1=('EMS', -6.0, 0.0), LD3=('RX', -4.6, 0.0), LD2=('TX', -4.6, 0.0), LD4=('STATUS', 0.0, 4.5))
# Lichtleiter-Achse seitlich versetzt / duenner, weil LD2/LD3 (x ~9,7) nur 1,1..1,4 mm neben dem DevKitC-Rand (x 11,0) liegen
LED_OPT = {'LD2': dict(dx=-0.7, d=1.8, wall=0.6), 'LD3': dict(dx=-0.7, d=1.8, wall=0.6), 'LD4': dict(dx=1.0)}
HOLES = [(-42.25, 19.75), (-42.25, -19.75), (42.25, 19.75), (42.25, -19.75)]

# ----------------------------------------------------------------------------------------------
# Abgeleitete Masse
# ----------------------------------------------------------------------------------------------
Z_PCB_B = P.floor_t + P.standoff                  # Platinenunterseite
Z_PCB_T = Z_PCB_B + P.pcb_t                       # Platinenoberseite
Z_LID_U = Z_PCB_T + P.h_above                     # Deckelunterseite = Oberkante Unterteil
Z_LID_T = Z_LID_U + P.lid_t                       # Deckeloberseite
Z_DK_B = Z_PCB_T + P.dk_socket_h + P.dk_hdr_h     # DevKitC-Unterseite
Z_DK_T = Z_DK_B + P.dk_pcb_t                      # DevKitC-Oberseite
Z_MOD_T = Z_DK_T + P.dk_module_h                  # Modul-Oberkante
Z_USB_C = Z_DK_T + P.usb_z_mid_above_dk           # Mitte der USB-C-Buchsen / Stecker
CAV_X0 = -P.pcb_w / 2 - P.clr - P.ext_left
CAV_X1 = P.pcb_w / 2 + P.clr
CAV_Y0 = min(-P.pcb_h / 2 - P.clr, P.dk_y0 - P.usb_clr_y)      # -Y-Wand sitzt direkt hinter dem DevKitC-USB-Ende
CAV_Y1 = P.pcb_h / 2 + P.clr
PK_X0, PK_X1 = P.dk_ant_x0 - P.ant_air, P.dk_ant_x1 + P.ant_air  # Antennentasche (+Y), Innenmasse
PK_Y1 = P.dk_ant_tip + P.ant_air
OUT_X0, OUT_X1 = CAV_X0 - P.wall, CAV_X1 + P.wall
OUT_Y0, OUT_Y1 = CAV_Y0 - P.wall, CAV_Y1 + P.wall
POUT_X0, POUT_X1, POUT_Y1 = PK_X0 - P.wall_ant, PK_X1 + P.wall_ant, PK_Y1 + P.wall_ant
ANT_Y0 = 27.0                                     # Beginn des abgeduennten Deckel-/Bodenbereichs der Tasche
SEG = 48

BTN = {}
if P.btn_mode == 'plunger':
    BTN = {n: (x, y, n, 0.0, -6.0) for (n, x, y) in P.dk_btn}
BTN_TOP = Z_DK_T + P.btn_top_above_dk             # Oberkante DevKitC-Taster


# ----------------------------------------------------------------------------------------------
# Hilfsfunktionen
# ----------------------------------------------------------------------------------------------
def led_geom(n):
    """(x, y, Stabdurchmesser) der Lichtleiter-Achse; Abweichung von der LED-Mitte nur wo noetig."""
    x, y = LEDS[n]
    o = LED_OPT.get(n, {})
    return x + o.get('dx', 0.0), y + o.get('dy', 0.0), o.get('d', P.rod_d)


def led_sleeve_wall(n):
    """Wandstaerke der Deckelhuelse um das Lichtleiterloch (duenner bei LD2/LD3: nur 0,2 mm Luft zum DevKitC-Rand)."""
    return LED_OPT.get(n, {}).get('wall', 0.8)


# Bauteilhoehen ueber der Platinenoberseite (mm, Planungswerte)
HEIGHT = dict(C12=12.5, C14=12.5, P1=10.0, P2=11.5, OC1=4.0, OC2=4.0, L3=2.1, L1=2.0, L2=2.0, J1=P.dk_socket_h, J3=P.dk_socket_h,
              U1=1.8, Q1=1.3, U2=1.3, C11=1.8, JP1=0.1, JP2=0.1)
BODY = dict(C12=(10.4, 10.4), C14=(10.4, 10.4), P1=(12.2, 11.76), P2=(2.54, 10.16),
            J1=(2.54, P.dk_pin_y1 - P.dk_pin_y0), J3=(2.54, P.dk_pin_y1 - P.dk_pin_y0))

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


def dk_boxes():
    """DevKitC-Koerper als Quader {name: (x0,x1,y0,y1,z0,z1)}: Platine, Stiftleistenkoerper, Modul, Antennenueberstand, USB-C-Buchsen."""
    b = {'DK_PCB': (P.dk_x0, P.dk_x1, P.dk_y0, P.dk_y1, Z_DK_B, Z_DK_T)}
    for i, xr in enumerate(P.dk_row_x):
        b[f'DK_HDR_J{1 + 2 * i}'] = (xr - 1.27, xr + 1.27, P.dk_pin_y0, P.dk_pin_y1, Z_PCB_T + P.dk_socket_h, Z_DK_B)
    b['DK_MODULE'] = (P.dk_ant_x0, P.dk_ant_x1, P.dk_module_y0, P.dk_y1, Z_DK_T, Z_MOD_T)
    b['DK_ANTENNA'] = (P.dk_ant_x0, P.dk_ant_x1, P.dk_y1, P.dk_ant_tip, Z_DK_T, Z_DK_T + P.dk_ant_t)
    for i, x in enumerate(P.usb_x):
        b[f'DK_USB{i + 1}'] = (x - P.usb_rc_w / 2, x + P.usb_rc_w / 2, P.dk_y0, P.dk_y0 + P.usb_rc_d, Z_DK_T, Z_DK_T + P.usb_rc_h)
    return b


def plug_boxes(dx=0.0, dz=0.0, length=30.0):
    """USB-C-Stecker-Overmould (Pruefkoerper) vor den Buchsen, optional seitlich/hoehenmaessig versetzt."""
    return {f'PLUG{i + 1}': (x + dx - P.plug_w / 2, x + dx + P.plug_w / 2, P.dk_y0 - length, P.dk_y0,
                             Z_USB_C + dz - P.plug_h / 2, Z_USB_C + dz + P.plug_h / 2) for i, x in enumerate(P.usb_x)}


def usb_slots():
    """[(x_mitte, breite)] der USB-Oeffnungen in der -Y-Wand."""
    if P.usb_mode == 'combined':
        x0, x1 = min(P.usb_x) - P.usb_pad, max(P.usb_x) + P.usb_pad
        return [((x0 + x1) / 2, x1 - x0)]
    return [(x, P.usb_w) for x in P.usb_x]


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


def outer_shape(z0, z1):
    """Aussenkontur: Hauptkasten + Antennentasche (+Y)."""
    return rrect(OUT_X0, OUT_X1, OUT_Y0, OUT_Y1, P.corner_r, z0, z1) + rrect(POUT_X0, POUT_X1, OUT_Y1 - 4.0, POUT_Y1, 2.0, z0, z1)


def cav_shape(z0, z1):
    """Innenkontur: Hauptraum + Antennentasche."""
    return rrect(CAV_X0, CAV_X1, CAV_Y0, CAV_Y1, 1.0, z0, z1) + rrect(PK_X0, PK_X1, CAV_Y1 - 3.0, PK_Y1, 1.0, z0, z1)


def prism_y(x, z, w, h, r, y0, y1):
    """Rundrechteck-Prisma entlang +Y (Profil in der XZ-Ebene, Mitte (x,z))."""
    cs = CS.square([w - 2 * r, h - 2 * r]).translate([-(w - 2 * r) / 2, -(h - 2 * r) / 2]).offset(r, m.JoinType.Round, 2.0, 24)
    return M.extrude(cs, y1 - y0).rotate([-90, 0, 0]).translate([x, y0, z])


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
    b = outer_shape(0, Z_LID_U) - cav_shape(P.floor_t, Z_LID_U + 1)
    # Falz rundum (nur um den Hauptraum; die duenne Antennentasche hat keinen Falz)
    b = b - rrect(CAV_X0 - P.rebate, CAV_X1 + P.rebate, CAV_Y0 - P.rebate, CAV_Y1 + P.rebate, 1.0, Z_LID_U - P.rebate_h, Z_LID_U + 1)
    # Antennentasche: Boden von innen auf floor_ant_t abduennen
    if P.floor_ant_t < P.floor_t:
        b = b - box(PK_X0, PK_X1, ANT_Y0, PK_Y1, P.floor_ant_t, P.floor_t + 0.01)
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
        b = b + box(-P.rib_t / 2, P.rib_t / 2, CAV_Y0 - 0.1, CAV_Y1 + 0.1, P.floor_t - 0.1, Z_PCB_B - P.rib_gap_below)
        if P.rib_slot_tabs:
            for ys in (8.0, -8.0):
                b = b + box(-P.tab_t / 2, P.tab_t / 2, ys - 5.7, ys + 5.7, Z_PCB_B - P.rib_gap_below - 0.1, Z_PCB_T - 0.4)
    # Auflagerippen unter den DevKitC-Buchsenleisten (Platine beim Aufstecken stuetzen, kontaktlos)
    if P.sup:
        for (x0, x1, y0, y1) in P.sup_pads:
            b = b + box(x0, x1, y0, y1, P.floor_t - 0.1, Z_PCB_B - P.sup_gap)
    # USB-C-Oeffnung(en) in der -Y-Wand
    for (xc, w) in usb_slots():
        b = b - prism_y(xc, Z_USB_C, w, P.usb_h, 1.0, OUT_Y0 - 1.0, CAV_Y0 + 1.0)
    # P1 Leitungsaustritt (linke Wand)
    pz = Z_PCB_T + P.p1_slot_z_above_pcb
    s = M.extrude(CS.square([P.p1_slot_w - 2, P.p1_slot_h - 2]).translate([-(P.p1_slot_w - 2) / 2, -(P.p1_slot_h - 2) / 2])
                  .offset(1.0, m.JoinType.Round, 2.0, 24), P.wall + 2.0)
    s = s.rotate([90, 0, 90]).translate([OUT_X0 - 0.5, 0, pz])
    b = b - s
    # Wandmontage
    if P.mount in ('ears', 'both'):
        for xe in P.ear_x:
            for sgn, yo in ((1, OUT_Y1), (-1, OUT_Y0)):
                yc = yo + sgn * (P.ear_len - P.ear_w / 2)
                ya, yb = sorted((yo - sgn * 1.0, yc))
                ear = box(xe - P.ear_w / 2, xe + P.ear_w / 2, ya, yb, 0, P.ear_t)
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
    lid = outer_shape(Z_LID_U, Z_LID_T)
    # Falz-Lippe (innen, rundum um den Hauptraum; vor der Antennentasche unterbrochen)
    lip_out = rrect(CAV_X0 - P.rebate + P.lip_clr, CAV_X1 + P.rebate - P.lip_clr, CAV_Y0 - P.rebate + P.lip_clr,
                    CAV_Y1 + P.rebate - P.lip_clr, 1.0, Z_LID_U - P.rebate_h + P.lip_clr, Z_LID_U + 0.01)
    lid = lid + (lip_out - cav_shape(Z_LID_U - P.rebate_h, Z_LID_U + 1))
    # Schraubhuelsen
    for (x, y) in (HOLES if posts else []):
        lid = lid + cyl(x, y, Z_PCB_T + P.post_gap, Z_LID_U + 0.01, P.boss_d / 2)
    # Rippe oben (Isolation, beruehrt das DevKitC nicht: x = 0, DevKitC ab x = 11)
    if P.rib_lid:
        lid = lid + box(-P.rib_t / 2, P.rib_t / 2, CAV_Y0, CAV_Y1, Z_PCB_T + P.rib_lid_bottom_above_pcb, Z_LID_U + 0.01)
    # Niederhalter auf dem Modul-Schirmblech
    if P.hold:
        for (x0, x1, y0, y1) in P.hold_pads:
            lid = lid + box(x0, x1, y0, y1, Z_MOD_T + P.hold_gap, Z_LID_U + 0.01)
    # LED-Huelsen
    led_bottom = Z_PCB_T + P.led_h + P.led_gap + 0.2
    led_info = {}
    for n in LEDS:
        x, y, rd = led_geom(n)
        hole_d = rd + 0.2 if P.led_mode == 'pipe' else rd
        sod = hole_d + 2 * led_sleeve_wall(n)
        lb = max(led_bottom, Z_PCB_T + clear_height(x, y, sod / 2 + 0.3, skip=(n,)) + 0.4)
        led_info[n] = (x, y, hole_d, sod, lb)
        lid = lid + cyl(x, y, lb, Z_LID_U + 0.01, sod / 2)
    # Tasterhuelsen (Bohrung 4,0 unter dem Deckel, 2,4 durch die Platte)
    btn_bottom = BTN_TOP + 0.8
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
    # Antennentasche: Deckel duenner (von innen)
    if P.lid_ant_t < P.lid_t:
        cuts.append(box(PK_X0, PK_X1, ANT_Y0, PK_Y1, Z_LID_U - 0.1, Z_LID_T - P.lid_ant_t))
    # Lueftungsschlitze
    if P.vent:
        for xs in np.arange(-30, -14, 3.0):
            cuts.append(rrect(xs - 0.8, xs + 0.8, -7, 7, 0.8, Z_LID_U - 0.1, Z_LID_T + 1))
    lid = lid - union(cuts)
    # Gravuren
    if P.labels == 'engrave':
        z0, z1 = Z_LID_T - P.label_depth, Z_LID_T + 0.1
        tx = []
        for n, (x, y) in LEDS.items():
            t, dx, dy = LED_LABEL[n]
            tx.append(text_solid(t, x + dx + (len(t) * 0.9 if dx > 0 else 0), y + dy, z0, z1))
        for n, (x, y, t, dx, dy) in BTN.items():
            tx.append(text_solid(t, x + dx, y + dy, z0, z1))
        if P.p2_mode != 'closed':
            tx.append(text_solid('P2', 3.6, -24.1, z0, z1))
        tx.append(text_solid('EMS-BUS', -53.0, 12.0, z0, z1, 3.0))
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
    """Taster-Stoessel in Einbaulage (nur btn_mode='plunger')."""
    zb = BTN_TOP + 0.2
    shaft = cyl(0, 0, zb, Z_LID_T + 0.6 + 0.01, 1.0)
    collar = cyl(0, 0, Z_LID_U - 1.4, Z_LID_U - 0.4, 1.8)
    cap = cyl(0, 0, Z_LID_T + 0.6, Z_LID_T + 1.6, 2.5)
    return shaft + collar + cap


# ----------------------------------------------------------------------------------------------
# Platinenmodell (Pruefkoerper) + DevKitC
# ----------------------------------------------------------------------------------------------
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
    if with_parts:
        for (n, x0, x1, y0, y1, h) in parts_boxes():
            items.append(box(x0, x1, y0, y1, Z_PCB_T, Z_PCB_T + h))
        for ph in d['plated_holes']:
            items.append(cyl(ph['x'], ph['y'], Z_PCB_B - 2.5, Z_PCB_B + 0.01, (ph['d'] or 1.5) / 2))
    return union(items), d


def dk_model():
    return union([box(*v) for v in dk_boxes().values()])


def plug_model():
    """P1-Gegenstecker (Zubehoer, 14,5 mm hoch) im Zusatzraum; Schraubfenster darueber."""
    return box(-67.0, -48.0, -6.3, 6.3, Z_PCB_T + 0.3, Z_PCB_T + 14.5)


def usb_plugs(dx=0.0, dz=0.0):
    return union([box(*v) for v in plug_boxes(dx, dz).values()])


def screws(length=None):
    """M3 Linsenkopf (ISO 7380) als Pruefkoerper."""
    length = length or P.screw_len
    zh = Z_LID_T - P.head_depth
    return [cyl(x, y, zh - length, zh, 1.5) + cyl(x, y, zh, zh + 1.65, 2.85) for (x, y) in HOLES]


# ----------------------------------------------------------------------------------------------
def to_tm(mf):
    mesh = mf.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts), process=True)


def vol(mf):
    return mf.volume()


def fit_check_manifold(bottom, lid, pcb, dk, plug, scr, rods_in, pl_in):
    """Kollisionen (mm3) und Luftspalte (mm); gemeinsam fuer enclosure.py und (mit Netzen aus B-Rep) enclosure_cq.py nutzbar."""
    def inter(a, b):
        return abs(round(float((a ^ b).volume()), 3))

    chk = {}
    chk['Unterteil x Platine+Bauteile'] = inter(bottom, pcb)
    chk['Deckel x Platine+Bauteile'] = inter(lid, pcb)
    chk['Unterteil x DevKitC (Platine, Leisten, Modul, Antenne, USB-C)'] = inter(bottom, dk)
    chk['Deckel x DevKitC (inkl. Niederhalter)'] = inter(lid, dk)
    chk['Unterteil x Deckel'] = inter(bottom, lid)
    chk['Unterteil x P1-Stecker'] = inter(bottom, plug)
    chk['Deckel x P1-Stecker'] = inter(lid, plug)
    chk['Platine x DevKitC'] = inter(pcb, dk)
    for dx, dz in ((0, 0), (-1.5, 0), (1.5, 0), (0, 0.7), (0, -0.7)):
        pl = usb_plugs(dx, dz)
        chk[f'USB-C-Stecker-Overmould (dx {dx:+.1f}, dz {dz:+.1f}) x Unterteil'] = inter(bottom, pl)
        if (dx, dz) == (0, 0):
            chk['USB-C-Stecker-Overmould x Deckel'] = inter(lid, pl)
    if rods_in:
        chk['Lichtleiter x Platine+DevKitC'] = max(max(inter(r, pcb), inter(r, dk)) for r in rods_in)
        chk['Lichtleiter x Deckel'] = max(inter(r, lid) for r in rods_in)
        chk['Lichtleiter x Unterteil'] = max(inter(r, bottom) for r in rods_in)
    if pl_in:
        chk['Stoessel x Deckel'] = max(inter(r, lid) for r in pl_in)
        chk['Stoessel x Platine+DevKitC'] = max(max(inter(r, pcb), inter(r, dk)) for r in pl_in)
    chk['Schrauben x Platine+DevKitC'] = max(max(inter(s, pcb), inter(s, dk)) for s in scr)
    chk['Schrauben x Deckel'] = max(inter(s, lid) for s in scr)
    chk['Schrauben x Unterteil (Kernloch/Einsatz, nur Info)'] = max(inter(s, bottom) for s in scr)
    return chk


def gaps_manifold(bottom, lid, b0, l0, pcb, bare, parts, dk, dk_nohold_lid, ant):
    g = {}
    g['Unterteil (ohne Posten)<->Platine inkl. THT-Beinchen (mm)'] = round(float(b0.min_gap(pcb, 5.0)), 3)
    g['Deckel (ohne Huelsen, ohne Niederhalter)<->Bauteile (mm)'] = round(float(l0.min_gap(parts, 5.0)), 3)
    g['Posten/Huelsen<->Platine (Auflage/Klemmung, mm)'] = round(float(bottom.min_gap(pcb, 5.0)), 3)
    g['Unterteil (ohne Posten)<->nackte Platine (mm)'] = round(float(b0.min_gap(bare, 5.0)), 3)
    g['Unterteil (ohne Posten)<->DevKitC (mm)'] = round(float(b0.min_gap(dk, 6.0)), 3)
    g['Deckel (ohne Huelsen, ohne Niederhalter)<->DevKitC (mm)'] = round(float(dk_nohold_lid.min_gap(dk, 8.0)), 3)
    g['Niederhalter-Rippen<->Modul-Schirmblech (mm; 0 = Beruehrung)'] = round(float(P.hold_gap), 3)
    g['Antenne<->naechstes Gehaeuseteil (Taschenwand/Deckel/Boden, mm, Suche bis 8)'] = round(float(min(b0.min_gap(ant, 8.0), dk_nohold_lid.min_gap(ant, 8.0))), 3)
    g['Deckel<->Modul-Oberkante (Luft, mm)'] = round(Z_LID_U - Z_MOD_T, 2)
    g['Deckel<->hoechstes Bauteil C12/C14 (mm)'] = round(Z_LID_U - (Z_PCB_T + 12.5), 2)
    g['Deckel<->P1-Stecker (mm)'] = round(Z_LID_U - (Z_PCB_T + 14.5), 2)
    return g


def main():
    only_check = '--check' in sys.argv
    bottom, lid = make_bottom(), make_lid()
    rod, plunger = make_rod(), make_plunger()
    pcb, data = pcb_model()
    dk = dk_model()
    plug = plug_model()
    scr = screws()
    res = {}
    # --- Export (Druckausrichtung) ---
    os.makedirs(os.path.join(HERE, 'stl'), exist_ok=True)
    lid_print = lid.rotate([180, 0, 0])
    lid_print = lid_print.translate([0, 0, -lid_print.bounding_box()[2]])
    # Lichtleiter nebeneinander, Flansch unten (Druckausrichtung)
    L = rod_len()
    rods = []
    for i, n in enumerate(LEDS):
        r = make_rod(n).translate([0, 0, -Z_LID_T])      # Flanschoberseite bei z=0
        r = r.rotate([180, 0, 0])                          # Flansch unten
        r = r.translate([i * 8.0, 0, 0])
        rods.append(r)
    rods = union(rods)
    parts = dict(bottom=bottom, lid=lid_print, light_pipes=rods)
    if BTN:
        parts['buttons'] = union([make_plunger().translate([0, 0, -Z_LID_T - 0.6]).rotate([180, 0, 0]).translate([i * 8.0, 0, 0]) for i in range(len(BTN))])
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
    rods_in = [make_rod(n).translate(list(led_geom(n)[:2]) + [0]) for n in LEDS]
    pl_in = [plunger.translate([x, y, 0]) for (x, y, *_r) in BTN.values()]
    chk = fit_check_manifold(bottom, lid, pcb, dk, plug, scr, rods_in, pl_in)
    pcb_parts = union([box(x0, x1, y0, y1, Z_PCB_T, Z_PCB_T + h) for (n, x0, x1, y0, y1, h) in parts_boxes() if n != 'P1'] +
                      [box(-55, -42.8, -5.88, 5.88, Z_PCB_T, Z_PCB_T + 10)])
    b0, l0 = make_bottom(bosses=False), make_lid(posts=False)
    bare, _ = pcb_model(with_parts=False)
    ant = box(*dk_boxes()['DK_ANTENNA'])
    # Deckel ohne Niederhalter fuer die Luftspalt-Messung zum DevKitC
    saved, P.hold = P.hold, 0              # P ist eine Klasse: Attribut zeitweise umsetzen
    l_nh = make_lid(posts=False)
    P.hold = saved
    gaps = gaps_manifold(bottom, lid, b0, l0, pcb, bare, pcb_parts, dk, l_nh, ant)
    res['collisions_mm3'] = chk
    res['gaps'] = gaps
    res['dims'] = dict(outer_xyz=[round(OUT_X1 - OUT_X0, 2), round(POUT_Y1 - OUT_Y0, 2), round(Z_LID_T, 2)],
                       outer_main_xy=[round(OUT_X1 - OUT_X0, 2), round(OUT_Y1 - OUT_Y0, 2)],
                       outer_x_range=[round(OUT_X0, 2), round(OUT_X1, 2)], outer_y_range=[round(OUT_Y0, 2), round(POUT_Y1, 2)],
                       inner_cavity=[round(CAV_X1 - CAV_X0, 2), round(CAV_Y1 - CAV_Y0, 2)],
                       antenna_pocket_inner=dict(x=[PK_X0, PK_X1], y_to=round(PK_Y1, 2)),
                       z=dict(pcb_bottom=Z_PCB_B, pcb_top=Z_PCB_T, devkit_bottom=round(Z_DK_B, 2), devkit_top=round(Z_DK_T, 2),
                              module_top=round(Z_MOD_T, 2), lid_underside=Z_LID_U, lid_top=Z_LID_T),
                       rod_length=round(L, 2), usb_centre_z=round(Z_USB_C, 2),
                       usb_slots=[dict(x_mid=round(xc, 2), w=round(w, 2), h=P.usb_h, x0=round(xc - w / 2, 2), x1=round(xc + w / 2, 2))
                                  for xc, w in usb_slots()],
                       usb_slot_z=[round(Z_USB_C - P.usb_h / 2, 2), round(Z_USB_C + P.usb_h / 2, 2)], rebate_start_z=round(Z_LID_U - P.rebate_h, 2))
    print(json.dumps(res, indent=1, ensure_ascii=False))
    json.dump(res, open(os.path.join(HERE, 'data', 'fit_check.json'), 'w'), indent=1, ensure_ascii=False)
    if not only_check:
        import render
        render.render_all(dict(bottom=bottom, lid=lid, pcb=pcb, dk=dk, plug=plug, plugs=usb_plugs(), rods=rods_in, rodsm=rods_in, plungers=pl_in, scr=scr,
                               cut=box(-90, 70, -50, 24.0, -5, 80)), to_tm, globals())
    return res


if __name__ == '__main__':
    main()
