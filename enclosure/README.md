# 3D-gedrucktes Gehäuse für das EMS-Bus-Interface (ESP32-S3, galvanisch getrennt)

Zweiteiliges Gehäuse für die Platine aus `tscircuit/` (110 x 60 x 1,6 mm, 4 Eckausschnitte, 4 x Ø3,5 Montagebohrungen
bei (±42,25 | ±19,75)). FDM, PLA oder PETG, 0,4-mm-Düse, **ohne Stützstrukturen** druckbar.
Die ursprüngliche Hammond-Variante (1591XXCFLBK, Reichelt) bleibt unverändert in `tscircuit/docs/ENCLOSURE.md` dokumentiert;
dieses Gehäuse ist die 3D-Druck-Alternative aus Abschnitt "3D-Druck-Alternative" dort.

## Dateien

| Datei | Inhalt |
|---|---|
| `enclosure.py` | parametrische Quelle (Python + manifold3d + trimesh; OpenSCAD war in der Umgebung nicht installierbar). Alle Maße in `PARAMS` am Dateianfang. |
| `enclosure_cq.py` | gleiche Geometrie mit CadQuery (echtes B-Rep): erzeugt STEP, 3MF und die STL; importiert `PARAMS` aus `enclosure.py` (eine Parameterquelle) und prüft Äquivalenz und Passung |
| `render.py` | Vorschaubilder |
| `data/pcb_parts.json` | Auszug aus `tscircuit/dist/index/circuit.json` (Bauteilpositionen, Umriss, Löcher, Schlitze; tscircuit/ wurde nur gelesen) |
| `data/fit_check.json` | Ergebnis der Mesh- und Kollisionsprüfung (`enclosure.py`) |
| `data/cq_check.json` | Äquivalenz STL-alt gegen CadQuery und Kollisions-/Abstandsprüfung mit den CadQuery-Teilen, 3MF-Reload |
| `step/bottom.step`, `lid.step`, `light_pipes.step`, `buttons.step` | Einzelteile als B-Rep (Ebenen/Zylinder), gleiche Lage wie die STL (Deckel mit Außenseite unten, Lichtleiter/Stößel in Druckausrichtung) |
| `step/assembly.step` | Baugruppe in Einbaulage mit Namen und Farben: Unterteil, Deckel, 5 Lichtleiter, 2 Stößel, Platine (Umriss, Ausschnitte, Löcher, Optokoppler-Schlitze), Bauteile als Quader, THT-Beinchen, P1-Gegenstecker-Platzhalter, 4 Schrauben |
| `3mf/bottom.3mf`, `lid.3mf`, `light_pipes.3mf`, `buttons.3mf` | je ein Druckteil, Einheit mm, Druckausrichtung |
| `3mf/plate.3mf` | Druckplatte: Unterteil, Deckel (Außenseite unten), Lichtleiter und Stößel nebeneinander, ca. 131 x 168 mm Belegung, passt auf 180 x 180 mm und größer |
| `stl/bottom.stl` | Unterteil, Druckausrichtung (offene Seite oben) |
| `stl/lid.stl` | Deckel, **Druckausrichtung = Oberseite auf dem Druckbett** (Pfosten zeigen nach oben) |
| `stl/light_pipes.stl` | 5 Lichtleiter-Stäbe (klares PETG), Druckausrichtung: Flansch unten, stehend |
| `stl/buttons.stl` | 2 optionale Taster-Stößel (RESET, BOOT) |
| `img/` | `assembly_exploded.png`, `assembly_fit.png`, `assembly_cutaway.png`, `sections.png`, `plan_lid.png`, `plan_bottom.png` |

## Welches Format wofür

- **STEP** (`step/`): zum Weiterkonstruieren in Fusion, FreeCAD, Onshape usw. Echte Flächen (Ebenen, Zylinder, Gravurtext als Kantenzüge), keine Dreiecke. `assembly.step` zeigt alles in Einbaulage; die Platine ist nur ein Platzhalter.
- **3MF** (`3mf/`): zum Slicen in PrusaSlicer, Bambu Studio, Cura. Objekte tragen Namen, Einheit mm. `plate.3mf` ist die fertige Plattenbelegung, die Einzeldateien sind für eigene Anordnung.
- **STL** (`stl/`): Dreiecksnetz, wird aus derselben CadQuery-Geometrie erzeugt (Auflösung 0,01 mm Sehnenabweichung, Kreise echt rund statt 48-Eck).

## Neu erzeugen

- Alles (STEP, 3MF, STL, Prüfungen, ca. 1 min): `pip install cadquery manifold3d trimesh numpy matplotlib scipy networkx shapely lxml`, dann `python3 enclosure_cq.py`. Ohne STL zu überschreiben: `python3 enclosure_cq.py --no-stl`; nur Prüfungen: `python3 enclosure_cq.py --check`.
- Parameter weiterhin in `PARAMS` in `enclosure.py` oder per Umgebungsvariable, z. B. `P_INSERT=0 P_MOUNT=keyholes python3 enclosure_cq.py`.
- Der ursprüngliche Manifold-Pfad bleibt lauffähig: `python3 enclosure.py` (schreibt STL aus manifold3d, überschreibt dann die CadQuery-STL; danach `enclosure_cq.py` erneut laufen lassen, damit STL, STEP und 3MF dieselbe Quelle haben).

Neu erzeugen (alter Pfad): `python3 enclosure.py` (Abhängigkeiten: `pip install manifold3d trimesh numpy matplotlib scipy networkx shapely`).
Parameter ohne Dateiänderung per Umgebungsvariable, z. B. `P_INSERT=0 P_MOUNT=keyholes P_P2_MODE=open python3 enclosure.py`.

## Maße (Standardparameter)

- Außen **126,0 x 64,8 x 26,9 mm** (Unterteil 24,1 hoch, Deckel 2,8 Platte + 16 mm Hülsen; mit Wandlaschen 80,8 mm breit)
- Innenraum 122,8 x 60,8 mm; die Platine liegt 12 mm vom linken Innenrand entfernt (Platz für den P1-Gegenstecker), 0,4 mm Luft zu den anderen Wänden
- Wand 2,0 mm, **Antennenseite (+X) 1,2 mm**, Boden 2,0 mm (unter der Antenne 1,2 mm), Deckel 2,8 mm (über der Antenne 1,6 mm)
- Platinenunterseite 4,5 mm über der Bodeninnenfläche (THT-Beinchen von P1, P2, J2), Platinenoberseite bei z = 8,1 mm, Deckelunterseite z = 24,1 mm (16 mm Luft über der Platine)

## Teileliste

| Menge | Teil | Hinweis |
|---|---|---|
| 1 | `bottom.stl` | |
| 1 | `lid.stl` | |
| 5 | Lichtleiter aus `light_pipes.stl` | klares PETG; oder Parameter `led_mode=hole` (nur Löcher Ø3) |
| 4 | **M3 x 22** Linsenkopfschraube (ISO 7380, Kopf Ø5,7) oder Zylinderkopf (Senkung Ø6,4 x 1,8) | Edelstahl ist unkritisch: die Schrauben liegen in den Montagelöchern und berühren nur Kunststoff und die (kupferfreien, Sperrzone Ø8) Bohrungsränder |
| 4 | **M3-Gewindeeinsatz (Heat-Set) M3 x 4, Außen ca. Ø4,6**, Bohrung Ø4,2 x 5 | Standard (`insert=1`) |
| (4) | alternativ: kein Einsatz, M3-Schrauben selbstschneidend in Kernloch Ø2,6 (`P_INSERT=0`; PETG ggf. 2,7) | nur 2-3 Montagezyklen empfohlen |
| 2-4 | Schrauben für die Wandlaschen (Ø4,5-Loch, Kopf bis Ø8) | nach Wand/Dübel |
| 1 | P1-Gegenstecker 2-polig, 5,08 mm, Leitungsaustritt parallel zur Platine (KF2EDGK-5.08-2P / Phoenix-MSTB-Klasse) | nicht in der BOM |
| optional | Büroklammer/Stift zum Drücken von RESET/BOOT | oder gedruckte Stößel `buttons.stl` |

## Druckeinstellungen

- Material: PETG (oder PLA; Heizungskeller, Dauer < 50 °C: PETG/ASA bevorzugt). Düse 0,4, Schichthöhe 0,2 mm, 3 Wandlinien (die 1,2-mm-Antennenwand = 3 Linien), Boden/Deckel 4-5 Schichten, Infill 20 %.
- **Keine Stützen.** Überbrückungen: USB-C-Ausschnitt (12 mm) und P1-Leitungsschlitz (12 mm) haben abgerundete Ecken, Brücke mit Lüfter 100 %, ca. 30-40 mm/s. Im Deckel (Oberseite unten gedruckt) werden Senkungen, Gravuren und Flanschsitze über ca. 0,4-1,8 mm Höhe überbrückt (alle Spannweiten <= 6,4 mm).
- Deckel `lid.stl` liegt bereits mit der Außenseite unten; die Gravur (0,4 mm tief, 2,6 mm Schrifthöhe) ist lesbar, wenn man den Deckel von außen betrachtet.
- Lichtleiter: PETG transparent/natur, 100 % Infill, 0,1-0,15 mm Schicht, Wandlinien-Überlappung hoch, stehend; Stirnflächen ggf. mit Feinschleifpapier glätten. Länge 17,6 mm (LED-Oberkante + 0,3 mm bis Deckeloberseite), Ø3,0 (LD5: Ø2,4, 0,8 mm nach -X versetzt, da LD5 nur 1,2 mm neben dem ESP32-Modul sitzt).
- Maßtoleranz: Lochdurchmesser sind für 0,4-mm-Druck mit +0,1...0,2 mm Spiel gewählt; bei Schwergängigkeit `lip_clr` bzw. `led_hole_pipe` anpassen.

## Aufbau

1. Gewindeeinsätze mit 200-220 °C (PETG) bzw. 180-200 °C (PLA) von oben in die vier Posten eindrücken, bündig mit der Posten-Oberkante.
2. Platine auf die vier Posten legen (Schrauben-Löcher zentrieren); die Rippe in der Mitte (x = 0) liegt 0,3 mm unter der Platine, die Zungen greifen in die beiden Optokoppler-Schlitze.
3. P1-Gegenstecker mit Leitungen bestücken (Leitungen vorher durch den Schlitz in der linken Wand fädeln), auf P1 stecken.
4. Lichtleiter von oben in die Deckellöcher stecken (Flansch bündig), Taster-Stößel (optional) von unten durch die Hülsen einsetzen.
5. Deckel aufsetzen (umlaufender Falz in den Wänden links/oben/unten), mit 4 x M3 x 22 verschrauben; die Deckelhülsen klemmen die Platine (Luft 0,0 mm) und führen die Schrauben.
6. Gehäuse über die Laschen (oder Schlüssellöcher) an der Wand befestigen.

**Deckel: Schrauben statt Rastung** – die vier Schrauben sitzen in den Montagelöchern, keine zusätzlichen Eckschrauben, **keine Schraube am Antennenende** (die Posten bei x = +42,25 liegen 5 mm außerhalb der Antennensperrzone x >= 48).

## Öffnungen

| Ort | Öffnung |
|---|---|
| Linke Schmalwand (-X) | Leitungsschlitz 12 x 8 mm, Mitte z = 13,6 mm (5,5 mm über Platine), y = 0 (P1) |
| Deckel links | Fenster 22 x 14 mm (x = -64...-42, y = ±7) über dem Gegenstecker: Schraubzugang von oben, Stecker abziehbar |
| Lange Wand oben (+Y), x = 33 | USB-C-Ausschnitt **12 x 7 mm**, Mitte z = 9,73 mm (Buchse 1,63 mm über Platine); Wand 2,0 + 0,4 mm Luft = Steckermündung 2,4 mm hinter der Außenfläche, der Ausschnitt nimmt Stecker mit Knickschutz auf (Overmould 10-11 x 6 mm) |
| Deckel, über P2 (x 5,5...18,5, y -29...-24) | **Standard `p2_mode=knockout`**: Ausbruchfenster, von innen auf 0,6 mm Reststärke ausgespart, mit Messer/Zange herausbrechen; `open` = offen, `closed` = ganz geschlossen. P2 (1x4, stehend) ist nur von oben erreichbar, daher im Deckel. |
| Deckel über LD1..LD5 | Lichtleiter-Löcher Ø3,2 (Ø2,6 bei LD5) mit Hülsen bis knapp über die LED, Gravur: **EMS** (LD1), **RX** (LD3), **TX** (LD2), **3V3** (LD5), **STATUS** (LD4) |
| Deckel über SW1/SW2 | Loch Ø2,4 für Stift/Stößel mit Führungshülse, Gravur **RESET** (SW1 bei 33,5 | -23,5), **BOOT** (SW2 bei 34,0 | -14,8) |
| Lüftung | optional `vent=1`: 6 Schlitze 1,6 x 14 mm im Deckel über der EMS-Seite (Standard aus) |

## Galvanische Trennung

- Alles Kunststoff; keine Metallteile überbrücken x < 0 (EMS) und x > 0 (MCU): die Schrauben stecken in getrennten Posten (2 links, 2 rechts), der Deckel ist Kunststoff, Gewindeeinsätze sitzen einzeln in den Posten.
- Interne Trennrippe bei x = 0 im Unterteil (1,2 mm dick, von Wand zu Wand, 0,3 mm unter der Platine) mit Zungen durch die Optokoppler-Schlitze (OC1/OC2, Zungen enden 0,4 mm unter der Platinenoberseite, damit die Optokoppler-Gehäuse frei bleiben), plus Rippe im Deckel bei x = 0 (endet 5,5 mm über der Platinenoberseite, Optokoppler 4,0 mm hoch). Sie verlängern Kriechstrecke/Luftweg um die Platine herum, ersetzen aber nicht die Layout-Abstände.
- Antennenende: Wand 1,2 mm, Deckel 1,6 mm, Boden 1,2 mm, keine Rippen, keine Schrauben, keine Lüftung. Im Zusatzraum rechts bleiben nur 0,4 mm Luft zur Platinenkante.

## Wandmontage (`mount`)

- `ears` (Standard): 4 Laschen (Ø4,5-Loch) bodenbündig an den langen Seiten bei x = -40 und x = +20 (nicht am Antennenende).
- `keyholes`: 2 Schlüssellöcher im Boden bei (±25 | 0) (Kopf Ø7 passiert den Boden, Schlitz 3,8 mm, Schraubenkopf ragt max. 2,5 mm in den Innenraum, unter der Platine ist 4,5 mm Platz).
- `both` / `none` möglich.

## Prüfergebnisse (`data/fit_check.json`, Einbaulage, manifold3d-Boolean-Schnitt)

- Alle 4 STL: wasserdicht, Windungsrichtung konsistent (trimesh).
- Volumen-Überschneidung Unterteil / Deckel / Lichtleiter / Stößel / Schrauben mit Platinenmodell (Platine, alle Bauteile als Boxen, THT-Beinchen 2,5 mm unter der Platine, P1-Stecker): **0,0 mm³** überall.
- Mindestabstände: Unterteil (ohne Posten) zur Platine 0,3 mm (Rippe) / Wand 0,4 mm, Deckel zu Bauteilen >= 0,4 mm, Deckelunterseite zu C12/C14 (12,5 mm) 3,5 mm, zu P1 + Stecker (14,5 mm) 1,5 mm.

## Äquivalenzprüfung CadQuery gegen alte STL (`data/cq_check.json`)

| Teil | Volumen alt / CadQuery (mm³) | Differenz | Bounding Box max. Abw. | symmetrische Differenz |
|---|---|---|---|---|
| bottom | 31737 / 31741 | 0,012 % | 0,002 mm | 6 mm³ (0,02 %) |
| lid | 25046 / 25053 | 0,028 % | 0,000 mm | 23 mm³ (0,09 %) |
| light_pipes | 607 / 609 | 0,29 % | 0,001 mm | 1,5 mm³ |
| buttons | 164 / 165 | 0,29 % | 0,001 mm | 0,4 mm³ |

Die Restabweichung stammt vom 48-Eck der alten STL gegenüber echten Kreisen. Kollisions- und Abstandsprüfung mit den CadQuery-Teilen ergibt dasselbe Bild wie oben (0,0 mm³ Überschneidung, Abstände 0,3 / 0,4 / 0,0 mm). `buttons` liegt jetzt mit der Kappe auf z = 0 (vorher 1 mm darunter).

## Annahmen und offene Punkte

- **Bauteilhöhen** aus Datenblatt/Typwerten geschätzt (EasyEDA liefert keine 3D-Höhen): C12/C14 JVJ25V1000M10X12 = 12,5 mm; P1-Header 10 mm, Gegenstecker 14,5 mm; P2 11,5 mm; USB-C 3,3 mm; Optokoppler 4,0 mm; ESP32-Modul 3,3 mm; Taster 1,5 mm. Vor dem Druck P1-Stecker und P2-Gegenstecker real messen (`h_above`, `ext_left`, `p1_*`).
- Tatsächliche Gegenstecker-Länge/Leitungsaustritt von P1 offen: `ext_left` = 12 mm Reserve.
- Lichtleiter, Stößel und Heat-Set-Maße ungetestet (kein Probedruck); ein Teststück der Posten/Hülsen und eines Lichtleiters vorab drucken.
- Stößel (`buttons.stl`) sind optional; Standard ist das Loch Ø2,4 für einen Stift.
- Vorschaubilder sind einfache Software-Renderings; die Bauteile der Platine sind Quader-Platzhalter.
