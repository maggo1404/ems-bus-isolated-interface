#!/usr/bin/env python3
"""Erzeugt data/pcb_parts.json (Traegerplatine, Bauteil-Footprints, THT-Loecher) aus ../tscircuit_devkit/dist/index/circuit.json
(nur lesen).  Aufruf:  python3 extract_pcb_parts.py   (circuit.json ggf. mit `cd ../tscircuit_devkit && bash scripts/export_fab.sh` neu bauen)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'tscircuit_devkit', 'dist', 'index', 'circuit.json')
c = json.load(open(SRC))
sc = {e['source_component_id']: e for e in c if e['type'] == 'source_component'}
r = lambda v: round(float(v), 3)
b = [e for e in c if e['type'] == 'pcb_board'][0]
parts = []
for e in c:
    if e['type'] != 'pcb_component':
        continue
    s = sc.get(e['source_component_id'])
    if not s or not s.get('name'):
        continue                                   # namenlose 0,6-mm-Hilfsobjekte (keine Bauteile)
    parts.append(dict(name=s['name'], x=r(e['center']['x']), y=r(e['center']['y']), w=r(e['width']), h=r(e['height']),
                      rot=int(e.get('rotation') or 0)))
ph = []
for e in c:
    if e['type'] == 'pcb_plated_hole':
        d = e.get('outer_diameter') or e.get('rect_pad_width') or 1.6
        ph.append(dict(x=r(e['x']), y=r(e['y']), d=r(d)))
out = dict(source='tscircuit_devkit/dist/index/circuit.json (read-only extract)',
           board=dict(thickness=b['thickness'], width=b['width'], height=b['height'],
                      outline=[dict(x=r(p['x']), y=r(p['y'])) for p in b['outline']]),
           parts=parts, plated_holes=ph,
           mount_holes=[dict(x=r(e['x']), y=r(e['y']), d=e['hole_diameter']) for e in c if e['type'] == 'pcb_hole'],
           cutouts=[dict(x=r(e['center']['x']), y=r(e['center']['y']), w=r(e['width']), h=r(e['height'])) for e in c if e['type'] == 'pcb_cutout'])
json.dump(out, open(os.path.join(HERE, 'data', 'pcb_parts.json'), 'w'), indent=1)
print(len(parts), 'Bauteile,', len(ph), 'THT-Loecher,', len(out['board']['outline']), 'Umrisspunkte')
