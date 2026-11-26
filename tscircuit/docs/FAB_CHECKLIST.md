# Fab-Checkliste V2.0 (Skill `.claude/skills/tscircuit/CHECKLIST.md`) - Stand Layout AP7b

Reproduzierbar mit `scripts/export_fab.sh 120s` (Build + Autorouter ~35 s, Gerber-Export aus `dist/index/circuit.json`, BOM/CPL, Netlist-, Fab- und Isolationspruefung).

| Skill-Punkt | Ergebnis |
|---|---|
| `tsci check netlist` / `scripts/check_netlist.py` | OK, alle V1-Netze 1:1, EMS/MCU getrennt (`ALL OK`) |
| `tsci check shorts dist/index/circuit.json` | "No shorts detected" |
| `tsci check pcb-style` | 1 Hinweis: Netz source_net_5, ein 6,5-mm-Segment mit 8 Grad Abweichung von 0 deg (kosmetisch) |
| `tsci check placement` | 0 DRC-Fehler; Hinweise: 3 Courtyard-Ueberlappungen (C24/R26 0,26 mm, R9/C13 0,25 mm, R11/C13 0,09 mm; Pads ueberlappen nicht) und "Drehung 180 deg" Vorschlaege fuer 2-Pin-Teile (nur Kosmetik der Pfadfuehrung). `tsci build` laeuft deshalb mit `--ignore-placement-drc` (zusaetzlich die gewollte Meldung "OC1/OC2 overlap cutout") |
| Routing-DRC (`tsci build`, Autorouter) | 0 Fehler (`errors.json` leer) |
| Gerber (F_Cu 853 / B_Cu 266 Leiterbahnen, 116 Vias 0,3/0,6, Ringbreite 0,15) | `scripts/check_fab.py`: 0 FAIL |
| Isolation EMS <-> MCU | `scripts/check_isolation.py`: 7,085 mm (oben) / 7,400 mm (unten), Kupfer in Schlitzen 0, nichts ueber x = 0 |
| Footprints/Polaritaet | siehe docs/FOOTPRINT_CHECK.md; CPL-Drehungen/Ursprung je Teil in docs/CPL_CHECK.md |
| Bestueckungsdaten | `fab/EMSinterface_V2.0-BOM_JLCPCB.csv`, `-CPL_JLCPCB.csv`; TP1..TP3, JP1, JP2 unbestueckt |

## Layout-Regeln und wie sie erfuellt wurden
* #22 Umriss 110 x 60 mit 4 Eckausschnitten 5,5 x 8,0 (Innenecke R3,5), 4 x Ø3,5 NPTH, Sperrzone Ø8 um jede Bohrung (`<keepout>`; Pour-Abstand >= 2,25 mm), P1 links (Steckerrichtung nach aussen, Koerper endet bei x = -55), ESP32 rechts, USB-C oben (Oeffnung bei y = +30), LEDs siehe docs/ENCLOSURE.md.
* #12 Antennenzone x >= 48, |y| <= 24: kein Kupfer, keine Bauteile auf beiden Lagen (Keepout + Pour-Aussparung, von check_fab/check_isolation geprueft). 3V3-Kondensatoren C22/C23 sitzen direkt am Modul bei x = 46,9.
* #13 Schlitze 2 x 12 mm nur unter OC1/OC2; #14 Pour-Abstand zu Bohrungen/Schlitzen >= 0,55 mm (`cutoutMargin`), zur Kante >= 0,5 mm (Pour-Umriss um 0,5 mm eingezogen).
* #8 Leiterbahnbreiten (Prueflogik `check_fab.py`): VBUS/V3V3/V5_EMS/EMS_VIN >= 0,5 mm, Busweg + Buck-SW >= 0,4 mm, Signale >= 0,25 mm; Einschnuerung auf 0,25 mm nur <= 1,5 mm neben einem Pad mit Rastermass <= 1,27 mm (USB-C, ESP32, SOT-23-6, SOIC). **GND/GND_EMS-Leiterbahnen (Stitching) 0,25 mm**: die Rueckfuehrung liegt auf den durchgehenden Pours (beide Lagen); alle Netze sind zusaetzlich pro Pad per Via/Bahn angebunden.
  Technik: `lib/netdefs.tsx` (`<net nominalTraceWidth>`), `lib/netclass.ts`. Der Autorouter verengt einzelne Zweige von Mehrpin-Netzen auf 0,25 mm. Deshalb sind 9 Verbindungen des Busweges von Hand mit `<trace pcbPath>` (0,4 mm) verlegt: Bruecke D1..D4/C1 (N3, N4, N6), L1 -> D4, R1/D7 -> R2 (N6), R4 -> C4 -> Q1 (N13), C9/U2 -> L3 (N26) in `src/ems-side.tsx`.
* #9 Abstand >= 0,2 mm zwischen Netzen (0,15 mm nur an Feinraster-Pads/-Zonen; 4 Paare 0,15..0,2 mm an J2/U4, ausgewiesen als INFO). Numerische Toleranz 0,002 mm.
* #10 Entkopplung: C10 (Buck-Eingang) neben U2, C11 direkt an L3 (V5), C13 zwischen OC2-Pin 5/8, C7 zwischen OC1-Pin 5/8, 100 nF/10 uF an U3-Pin 2, AMS1117-Kondensatoren C24/C25/C29/C26/C27 an U5. GND_EMS-Vias (hand platziert) am Buck- und Rueckkopplungs-GND.
* #11 AMS1117 (U5): V3V3-Pour 16,5 x 10,5 mm auf Ober- UND Unterseite (je ~165 mm2, zusammen ~3,3 cm2) am Tab + 8 Thermovias (0,3/0,6).
* #19 Silkscreen-Text >= 0,8 mm (Platinen-Texte), Linienbreite tscircuit-Standard; Courtyard siehe oben.
* #20 USB D+/D-: U4 (ESD) 5 mm hinter J2, Leitungspaar fuehrt ca. 12 mm parallel zu den ESP32-Pins 13/14; beide D+ und beide D- Pads angebunden (`check_fab.py`, Abschnitt USB-C).

## Offene Punkte / Einschraenkungen
1. **Autorouter ist nicht stabil**: jede kleine Platzierungsaenderung (auch auf der anderen Platinenseite) kann das ganze Ergebnis veraendern (Kurzschluesse, 0,25-mm-Zweige). Mehrere `routingPhaseIndex`-Phasen erzeugten ueberlappende Leiterbahnen und wurden verworfen. Nach jeder Platzierungsaenderung `scripts/export_fab.sh` laufen lassen und `check_fab.py` ablesen; bei Fehlschlag Bauteile um 0,1..0,5 mm verschieben (so entstand die aktuelle Platzierung).
2. 3 Courtyard-Ueberlappungen (s. o.), 1 pcb-style-Hinweis, Rotationshinweise von `tsci check placement`.
3. CPL-Rotationsvorzeichen (CCW positiv) und die 90/270-Teile in der JLC-Vorschau pruefen (docs/CPL_CHECK.md).
4. 3D-Ansicht: `tsci build --3d` braucht die Modelle von modelcdn.tscircuit.com (im Sandbox-Proxy gesperrt); `docs/img/assembly.png` (Bestueckungsplan) ersetzt sie.
5. J2 benoetigt 0,15 mm zu den eigenen NPTH-Pegs (Ø0,6, Footprint); Montagebohrungen >= 0,25 mm.
