#!/usr/bin/env python3
"""CadQuery-Variante des Gehaeuses (echtes B-Rep -> STEP) mit denselben PARAMS wie enclosure.py.

Alle Masse/Positionen werden aus enclosure.py importiert (PARAMS, LEDS, BTN, HOLES, Z_*, CAV_*, ...),
auch die P_<NAME>-Umgebungsvariablen wirken.  Geometrie-Logik 1:1 zu enclosure.py, nur mit CadQuery/OCCT.

Aufruf:
  python3 enclosure_cq.py            STEP + 3MF + STL (aus derselben CadQuery-Geometrie) + Aequivalenz-/Passungspruefung
  python3 enclosure_cq.py --no-stl   STL nicht ueberschreiben
  python3 enclosure_cq.py --check    nur Pruefungen (nichts schreiben ausser data/*.json)
"""
import json, os, sys, math
import numpy as np
import cadquery as cq
import trimesh
import enclosure as E
from enclosure import P, LEDS, BTN, HOLES, HERE
from enclosure import (Z_PCB_B, Z_PCB_T, Z_LID_U, Z_LID_T, CAV_X0, CAV_X1, CAV_Y, OUT_X0, OUT_X1, OUT_Y,
                       led_geom, clear_height, parts_boxes, rod_len)

V = cq.Vector


# ----------------------------------------------------------------------------------------------
# Primitive
# ----------------------------------------------------------------------------------------------
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val()


def cyl(x, y, z0, z1, r, r2=None):
    if r2 is None or r2 == r:
        return cq.Solid.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))
    return cq.Solid.makeCone(r, r2, z1 - z0, V(x, y, z0), V(0, 0, 1))


def rrect(x0, x1, y0, y1, r, z0, z1):
    w = cq.Workplane("XY").workplane(offset=z0).center((x0 + x1) / 2, (y0 + y1) / 2).rect(x1 - x0, y1 - y0).extrude(z1 - z0)
    if r > 0:
        w = w.edges("|Z").fillet(r)
    return w.val()


def fuse(items):
    items = [i for i in items if i is not None]
    return items[0].fuse(*items[1:]).clean() if len(items) > 1 else items[0]


def cut(a, items):
    items = [i for i in items if i is not None]
    return a.cut(*items).clean() if items else a


def text_solid(s, cx, cy, z0, z1, h=None):
    h = h or P.label_h
    t = (cq.Workplane("XY").workplane(offset=z0).center(cx, cy)
         .text(s, h, z1 - z0, halign='center', valign='center', font="DejaVu Sans", kind='bold', combine=False))
    return t.val()


def prism_x(y, z, w, h, r, x0, x1):
    """Rundrechteck-Prisma entlang +X (Profil in der YZ-Ebene, Mitte (y,z))."""
    w_ = cq.Workplane("YZ").workplane(offset=x0).center(y, z).rect(w, h).extrude(x1 - x0).edges("|X").fillet(r)
    return w_.val()


def prism_y(x, z, w, h, r, y0, y1):
    """Rundrechteck-Prisma entlang +Y (Profil in der XZ-Ebene, Mitte (x,z))."""
    w_ = cq.Workplane("XZ").workplane(offset=-y0).center(x, z).rect(w, h).extrude(-(y1 - y0)).edges("|Y").fillet(r)
    return w_.val()


# ----------------------------------------------------------------------------------------------
# Unterteil
# ----------------------------------------------------------------------------------------------
def make_bottom(bosses=True):
    outer = rrect(OUT_X0, OUT_X1, -OUT_Y, OUT_Y, P.corner_r, 0, Z_LID_U)
    cav = rrect(CAV_X0, CAV_X1, -CAV_Y, CAV_Y, 1.0, P.floor_t, Z_LID_U + 1)
    b = outer.cut(cav)
    reb = rrect(CAV_X0 - P.rebate, CAV_X1, -CAV_Y - P.rebate, CAV_Y + P.rebate, 1.0, Z_LID_U - P.rebate_h, Z_LID_U + 1)
    b = b.cut(reb)
    if P.floor_ant_t < P.floor_t:
        b = b.cut(box(47.0, CAV_X1 - 0.01, -24.0, 24.0, P.floor_ant_t, P.floor_t + 0.01))
    adds, cuts = [], []
    for (x, y) in (HOLES if bosses else []):
        adds.append(cyl(x, y, 0.0, P.floor_t + 1.5, 4.6, 3.5))
        adds.append(cyl(x, y, P.floor_t + 1.0, Z_PCB_B, P.boss_d / 2))
        if P.insert:
            cuts.append(cyl(x, y, Z_PCB_B - P.insert_depth, Z_PCB_B + 0.1, P.insert_d / 2))
        else:
            cuts.append(cyl(x, y, Z_PCB_B - P.pilot_depth, Z_PCB_B + 0.1, P.pilot_d / 2))
    if P.rib:
        adds.append(box(-P.rib_t / 2, P.rib_t / 2, -CAV_Y - 0.1, CAV_Y + 0.1, P.floor_t - 0.1, Z_PCB_B - P.rib_gap_below))
        if P.rib_slot_tabs:
            for ys in (8.0, -8.0):
                adds.append(box(-P.tab_t / 2, P.tab_t / 2, ys - 5.7, ys + 5.7, Z_PCB_B - P.rib_gap_below - 0.1, Z_PCB_T - 0.4))
    # Wandmontage (Laschen: additiv, Loecher werden danach geschnitten)
    if P.mount in ('ears', 'both'):
        for xe in P.ear_x:
            for sgn in (1, -1):
                yc = sgn * (OUT_Y + P.ear_len - P.ear_w / 2)
                ya, yb = sorted((sgn * (OUT_Y - 1.0), yc))
                adds.append(box(xe - P.ear_w / 2, xe + P.ear_w / 2, ya, yb, 0, P.ear_t))
                adds.append(cyl(xe, yc, 0, P.ear_t, P.ear_w / 2))
                cuts.append(cyl(xe, yc, -0.1, P.ear_t + 0.1, P.ear_hole / 2))
    b = fuse([b] + adds)
    # Ausschnitte
    uz = Z_PCB_T + P.usb_z_mid_above_pcb
    cuts.append(prism_y(P.usb_x, uz, P.usb_w, P.usb_h, 1.0, CAV_Y - 1.0, CAV_Y + P.wall + 1.0))
    pz = Z_PCB_T + P.p1_slot_z_above_pcb
    cuts.append(prism_x(0.0, pz, P.p1_slot_w, P.p1_slot_h, 1.0, OUT_X0 - 0.5, OUT_X0 - 0.5 + P.wall + 2.0))
    if P.mount in ('keyholes', 'both'):
        for (kx, ky) in P.keyholes:
            kh = fuse([cyl(kx, ky, -0.1, P.floor_t + 0.1, P.key_big / 2),
                       box(kx - P.key_small / 2, kx + P.key_small / 2, ky, ky + P.key_slot, -0.1, P.floor_t + 0.1),
                       cyl(kx, ky + P.key_slot, -0.1, P.floor_t + 0.1, P.key_small / 2)])
            cuts.append(kh)
    return cut(b, cuts)


# ----------------------------------------------------------------------------------------------
# Deckel (Einbaulage)
# ----------------------------------------------------------------------------------------------
def make_lid(posts=True):
    lid = rrect(OUT_X0, OUT_X1, -OUT_Y, OUT_Y, P.corner_r, Z_LID_U, Z_LID_T)
    lip_out = rrect(CAV_X0 - P.rebate + P.lip_clr, CAV_X1, -CAV_Y - P.rebate + P.lip_clr, CAV_Y + P.rebate - P.lip_clr, 1.0,
                    Z_LID_U - P.rebate_h + P.lip_clr, Z_LID_U + 0.01)
    lip_in = rrect(CAV_X0, CAV_X1 + 1, -CAV_Y, CAV_Y, 1.0, Z_LID_U - P.rebate_h, Z_LID_U + 1)
    adds = [lip_out.cut(lip_in)]
    for (x, y) in (HOLES if posts else []):
        adds.append(cyl(x, y, Z_PCB_T + P.post_gap, Z_LID_U + 0.01, P.boss_d / 2))
    if P.rib_lid:
        adds.append(box(-P.rib_t / 2, P.rib_t / 2, -CAV_Y, CAV_Y, Z_PCB_T + P.rib_lid_bottom_above_pcb, Z_LID_U + 0.01))
    led_bottom = Z_PCB_T + P.led_h + P.led_gap + 0.2
    led_info = {}
    for n in LEDS:
        x, y, rd = led_geom(n)
        hole_d = rd + 0.2 if P.led_mode == 'pipe' else rd
        sod = hole_d + 1.6
        lb = max(led_bottom, Z_PCB_T + clear_height(x, y, sod / 2 + 0.3, skip=(n,)) + 0.4)
        led_info[n] = (x, y, hole_d, sod, lb)
        adds.append(cyl(x, y, lb, Z_LID_U + 0.01, sod / 2))
    btn_bottom = Z_PCB_T + P.btn_top_h + 0.8
    for n, (x, y, *_r) in BTN.items():
        adds.append(cyl(x, y, btn_bottom, Z_LID_U + 0.01, P.btn_sleeve_od / 2))
    lid = fuse([lid] + adds)
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
    x0, x1, y0, y1 = P.p1_win
    cuts.append(rrect(x0, x1, y0, y1, 1.0, Z_LID_U - 0.1, Z_LID_T + 1))
    x0, x1, y0, y1 = P.p2_win
    if P.p2_mode == 'open':
        cuts.append(rrect(x0, x1, y0, y1, 0.8, Z_LID_U - 0.1, Z_LID_T + 1))
    elif P.p2_mode == 'knockout':
        cuts.append(rrect(x0, x1, y0, y1, 0.8, Z_LID_U - 0.1, Z_LID_T - P.p2_membrane))
    if P.lid_ant_t < P.lid_t:
        cuts.append(box(47.0, CAV_X1 - 0.01, -24.0, 24.0, Z_LID_U - 0.1, Z_LID_T - P.lid_ant_t))
    if P.vent:
        for xs in np.arange(-30, -14, 3.0):
            cuts.append(rrect(float(xs) - 0.8, float(xs) + 0.8, -7, 7, 0.8, Z_LID_U - 0.1, Z_LID_T + 1))
    lid = cut(lid, cuts)
    if P.labels == 'engrave':
        z0, z1 = Z_LID_T - P.label_depth, Z_LID_T + 0.1
        tx = []
        for n, (x, y) in LEDS.items():
            t, dx, dy = E.LED_LABEL[n]
            tx.append(text_solid(t, x + dx + (len(t) * 0.9 if dx > 0 else 0), y + dy, z0, z1))
        for n, (x, y, t, dx, dy) in BTN.items():
            tx.append(text_solid(t, x + dx, y + dy, z0, z1))
        if P.p2_mode != 'closed':
            tx.append(text_solid('P2', 12.0, -22.0, z0, z1))
        tx.append(text_solid('EMS-BUS', -53.0, 12.0, z0, z1, 3.0))
        lid = cut(lid, tx)
    return lid


def make_rod(n='LD1'):
    zb = Z_PCB_T + P.led_h + P.led_gap
    d = led_geom(n)[2]
    return fuse([cyl(0, 0, zb, Z_LID_T - P.flange_t + 0.01, d / 2), cyl(0, 0, Z_LID_T - P.flange_t, Z_LID_T, d / 2 + 0.7)])


def make_plunger():
    zb = Z_PCB_T + P.btn_top_h + 0.2
    return fuse([cyl(0, 0, zb, Z_LID_T + 0.6 + 0.01, 1.0), cyl(0, 0, Z_LID_U - 1.4, Z_LID_U - 0.4, 1.8),
                 cyl(0, 0, Z_LID_T + 0.6, Z_LID_T + 1.6, 2.5)])


# ----------------------------------------------------------------------------------------------
# Platinen-Stand-in (Board + Bauteile als Quader/Zylinder)
# ----------------------------------------------------------------------------------------------
def pcb_board(d=None):
    d = d or json.load(open(os.path.join(HERE, 'data', 'pcb_parts.json')))
    pts = [(p['x'], p['y']) for p in d['board']['outline']]
    board = cq.Workplane("XY").workplane(offset=Z_PCB_B).polyline(pts).close().extrude(P.pcb_t).val()
    cuts = [cyl(x, y, Z_PCB_B - 1, Z_PCB_T + 1, 1.75) for x, y in HOLES]
    for c in d['cutouts']:
        cuts.append(box(c['x'] - c['w'] / 2, c['x'] + c['w'] / 2, c['y'] - c['h'] / 2, c['y'] + c['h'] / 2, Z_PCB_B - 1, Z_PCB_T + 1))
    return cut(board, cuts), d


def pcb_components(d):
    """Liste (name, Shape) der Bauteil-Quader (wie enclosure.pcb_model) und THT-Beinchen."""
    out = []
    for (n, x0, x1, y0, y1, h) in parts_boxes():
        out.append((n, box(x0, x1, y0, y1, Z_PCB_T, Z_PCB_T + h)))
    legs = [cyl(ph['x'], ph['y'], Z_PCB_B - 2.5, Z_PCB_B + 0.01, (ph['d'] or 1.5) / 2) for ph in d['plated_holes']]
    return out, legs


def pcb_model(with_parts=True):
    board, d = pcb_board()
    items = [board]
    if with_parts:
        comps, legs = pcb_components(d)
        items += [s for _, s in comps] + legs
    return fuse(items), d


def plug_model():
    return box(-67.0, -48.0, -6.3, 6.3, Z_PCB_T + 0.3, Z_PCB_T + 14.5)


def screws(length=22.0):
    zh = Z_LID_T - P.head_depth
    return [fuse([cyl(x, y, zh - length, zh, 1.5), cyl(x, y, zh, zh + 1.65, 2.85)]) for (x, y) in HOLES]


# ----------------------------------------------------------------------------------------------
# Druckausrichtung
# ----------------------------------------------------------------------------------------------
def lid_print(lid):
    s = lid.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    return s.translate(V(0, 0, -s.BoundingBox().zmin))


def rods_print():
    out = []
    for i, n in enumerate(LEDS):
        r = make_rod(n).translate(V(0, 0, -Z_LID_T)).rotate(V(0, 0, 0), V(1, 0, 0), 180).translate(V(i * 8.0, 0, 0))
        out.append(r)
    return cq.Compound.makeCompound(out)


def plungers_print():
    out = []
    for i in range(2):
        r = make_plunger().translate(V(0, 0, -Z_LID_T - 0.6)).rotate(V(0, 0, 0), V(1, 0, 0), 180).translate(V(i * 8.0, 0, 0))
        out.append(r)
    c = cq.Compound.makeCompound(out)
    return c.translate(V(0, 0, -c.BoundingBox().zmin))     # Kappe liegt auf dem Druckbett (z=0)


def build_parts():
    bottom, lid = make_bottom(), make_lid()
    return dict(bottom=bottom, lid=lid), dict(bottom=bottom, lid=lid_print(lid), light_pipes=rods_print(), buttons=plungers_print())


# ----------------------------------------------------------------------------------------------
# Tessellierung / Mesh-Hilfen
# ----------------------------------------------------------------------------------------------
TOL, ANG = 0.01, 0.1   # lineare Abweichung mm, Winkel rad


def to_tm(shape, tol=TOL, ang=ANG):
    v, f = shape.tessellate(tol, ang)
    t = trimesh.Trimesh(vertices=np.array([[p.x, p.y, p.z] for p in v]), faces=np.array(f), process=True)
    t.merge_vertices(digits_vertex=6)
    t.fix_normals()
    return t


def to_manifold(t):
    import manifold3d as m
    mesh = m.Mesh(vert_properties=np.asarray(t.vertices, dtype=np.float32), tri_verts=np.asarray(t.faces, dtype=np.uint32))
    return m.Manifold(mesh)


def mf(shape):
    return to_manifold(to_tm(shape))


# ----------------------------------------------------------------------------------------------
# Export
# ----------------------------------------------------------------------------------------------
def export_step(parts_inst, parts_print):
    os.makedirs(os.path.join(HERE, 'step'), exist_ok=True)
    for n, s in parts_print.items():
        cq.exporters.export(cq.Workplane("XY").add(s), os.path.join(HERE, 'step', n + '.step'))
    # Baugruppe
    board, d = pcb_board()
    comps, legs = pcb_components(d)
    asm = cq.Assembly(name="ems_bus_gehaeuse")
    C = cq.Color
    asm.add(parts_inst['bottom'], name="Unterteil", color=C(0.30, 0.32, 0.36, 1))
    asm.add(parts_inst['lid'], name="Deckel", color=C(0.85, 0.85, 0.82, 1))
    for n in LEDS:
        x, y, _ = led_geom(n)
        asm.add(make_rod(n).translate(V(x, y, 0)), name=f"Lichtleiter_{n}", color=C(0.80, 0.92, 1.0, 0.6))
    for n, (x, y, *_r) in BTN.items():
        asm.add(make_plunger().translate(V(x, y, 0)), name=f"Stoessel_{n}", color=C(0.9, 0.2, 0.2, 1))
    asm.add(board, name="Platine_PCB", color=C(0.05, 0.45, 0.15, 1))
    for n, s in comps:
        col = C(0.15, 0.15, 0.15, 1)
        if n in LEDS: col = C(1.0, 0.8, 0.1, 1)
        elif n in ('P1', 'P2', 'J2'): col = C(0.7, 0.7, 0.75, 1)
        elif n in ('C12', 'C14'): col = C(0.1, 0.2, 0.6, 1)
        asm.add(s, name=f"Bauteil_{n}", color=col)
    for i, s in enumerate(legs):
        asm.add(s, name=f"THT_Beinchen_{i + 1}", color=C(0.75, 0.75, 0.75, 1))
    asm.add(plug_model(), name="P1_Gegenstecker_Platzhalter", color=C(0.2, 0.6, 0.2, 0.5))
    for i, s in enumerate(screws()):
        asm.add(s, name=f"Schraube_M3x22_{i + 1}", color=C(0.6, 0.6, 0.65, 1))
    asm.export(os.path.join(HERE, 'step', 'assembly.step'))


def export_3mf(meshes):
    os.makedirs(os.path.join(HERE, '3mf'), exist_ok=True)
    for n, t in meshes.items():
        sc = trimesh.Scene()
        sc.add_geometry(t.copy(), node_name=n, geom_name=n)
        sc.export(os.path.join(HERE, '3mf', n + '.3mf'), file_type='3mf')
    # Druckplatte: Teile nebeneinander (Y gestapelt), links unten bei (5|5), 5 mm Abstand
    gap = 6.0
    sc = trimesh.Scene()
    y = 5.0
    for n in ('bottom', 'lid', 'light_pipes', 'buttons'):
        t = meshes[n].copy()
        b = t.bounds
        if n == 'buttons':       # neben die Lichtleiter, rechts davon
            off = [5.0 + 36.4 + 10.0 - b[0][0], plate_y_buttons - b[0][1], -b[0][2]]
            t.apply_translation(off)
            sc.add_geometry(t, node_name=n, geom_name=n)
            continue
        t.apply_translation([5.0 - b[0][0], y - b[0][1], -b[0][2]])
        sc.add_geometry(t, node_name=n, geom_name=n)
        if n == 'light_pipes':
            plate_y_buttons = y
        y += (b[1][1] - b[0][1]) + gap
    sc.export(os.path.join(HERE, '3mf', 'plate.3mf'), file_type='3mf')


def verify_3mf(meshes):
    res = {}
    for n in list(meshes) + ['plate']:
        sc = trimesh.load(os.path.join(HERE, '3mf', n + '.3mf'), force='scene')
        names = sorted(sc.geometry.keys())
        tot = sum(g.volume for g in sc.geometry.values())
        res[n] = dict(objects=names, volume_cm3=round(tot / 1000, 3), bounds=np.round(sc.bounds, 2).tolist(),
                      watertight=all(g.is_watertight for g in sc.geometry.values()))
    return res


# ----------------------------------------------------------------------------------------------
# Pruefungen
# ----------------------------------------------------------------------------------------------
def equivalence(parts_print, meshes):
    out = {}
    for n, s in parts_print.items():
        ref = trimesh.load(os.path.join(HERE, 'stl', n + '.stl'))
        ref.apply_translation([0, 0, -ref.bounds[0][2]])   # alte buttons.stl lag 1 mm unter z=0
        cqm = meshes[n]
        vr, vc = float(ref.volume), float(s.Volume())
        a, b = to_manifold(ref), to_manifold(cqm)
        sym = float((a - b).volume() + (b - a).volume())
        out[n] = dict(vol_stl_mm3=round(vr, 1), vol_cq_brep_mm3=round(vc, 1), vol_cq_mesh_mm3=round(float(cqm.volume), 1),
                      vol_diff_pct=round(100 * (vc - vr) / vr, 3),
                      bbox_max_dev_mm=round(float(np.abs(ref.bounds - cqm.bounds).max()), 4),
                      symdiff_mm3=round(sym, 1), symdiff_pct_of_stl=round(100 * sym / vr, 3),
                      cq_valid=bool(s.isValid()), cq_solids=len(s.Solids()), cq_faces=len(s.Faces()),
                      cq_planar_cyl_faces_pct=round(100 * sum(f.geomType() in ('PLANE', 'CYLINDER') for f in s.Faces()) / len(s.Faces()), 1))
    return out


def fit_check(parts_inst):
    bottom, lid = mf(parts_inst['bottom']), mf(parts_inst['lid'])
    pcb = mf(pcb_model()[0])
    plug = mf(plug_model())
    scr = [mf(s) for s in screws()]
    rods = [mf(make_rod(n).translate(V(*led_geom(n)[:2], 0))) for n in LEDS]
    pls = [mf(make_plunger().translate(V(x, y, 0))) for (x, y, *_r) in BTN.values()]

    def inter(a, b):
        return round(float((a ^ b).volume()), 3)

    chk = {
        'Unterteil x Platine+Bauteile': inter(bottom, pcb), 'Deckel x Platine+Bauteile': inter(lid, pcb),
        'Unterteil x Deckel': inter(bottom, lid), 'Unterteil x P1-Stecker': inter(bottom, plug), 'Deckel x P1-Stecker': inter(lid, plug),
        'Lichtleiter x Platine': max(inter(r, pcb) for r in rods), 'Lichtleiter x Deckel': max(inter(r, lid) for r in rods),
        'Lichtleiter x Unterteil': max(inter(r, bottom) for r in rods),
        'Stoessel x Deckel': max(inter(r, lid) for r in pls), 'Stoessel x Platine': max(inter(r, pcb) for r in pls),
        'Schrauben x Platine': max(inter(s, pcb) for s in scr), 'Schrauben x Deckel': max(inter(s, lid) for s in scr),
        'Schrauben x Unterteil (Kernloch/Einsatz, nur Info)': max(inter(s, bottom) for s in scr)}
    comps, _ = pcb_components(json.load(open(os.path.join(HERE, 'data', 'pcb_parts.json'))))
    pcb_parts = mf(fuse([s for n, s in comps if n != 'P1'] + [box(-55, -42.8, -5.88, 5.88, Z_PCB_T, Z_PCB_T + 10)]))
    b0, l0 = mf(make_bottom(bosses=False)), mf(make_lid(posts=False))
    bare = mf(pcb_model(with_parts=False)[0])
    gaps = {
        'Unterteil (ohne Posten)<->Platine inkl. THT-Beinchen (mm)': round(float(b0.min_gap(pcb, 5.0)), 3),
        'Deckel (ohne Huelsen)<->Bauteile (mm)': round(float(l0.min_gap(pcb_parts, 5.0)), 3),
        'Posten/Huelsen<->Platine (Auflage/Klemmung, mm)': round(float(bottom.min_gap(pcb, 5.0)), 3),
        'Unterteil (ohne Posten)<->nackte Platine (mm)': round(float(b0.min_gap(bare, 5.0)), 3)}
    return dict(collisions_mm3=chk, gaps=gaps)


def main():
    no_stl, only_check = '--no-stl' in sys.argv, '--check' in sys.argv
    parts_inst, parts_print = build_parts()
    meshes = {n: to_tm(s) for n, s in parts_print.items()}
    res = dict(equivalence=equivalence(parts_print, meshes))
    res['fit_check_cadquery'] = fit_check(parts_inst)
    if not only_check:
        export_step(parts_inst, parts_print)
        export_3mf(meshes)
        res['threemf_reload'] = verify_3mf(meshes)
        if not no_stl:
            for n, t in meshes.items():
                t.export(os.path.join(HERE, 'stl', n + '.stl'))
    print(json.dumps(res, indent=1, ensure_ascii=False))
    json.dump(res, open(os.path.join(HERE, 'data', 'cq_check.json'), 'w'), indent=1, ensure_ascii=False)
    return res


if __name__ == '__main__':
    main()
