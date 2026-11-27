# 3D-gedrucktes Gehäuse für das EMS-Bus-Interface, DevKitC-Variante (ESP32-S3-DevKitC-1 mit 2 x USB-C, galvanisch getrennt)

Zweiteiliges Gehäuse für die Platine aus `tscircuit_devkit/` (110 x 60 x 1,6 mm, 4 Eckausschnitte, 4 x Ø3,5 Montagebohrungen bei (±42,25 | ±19,75)) **mit aufgestecktem ESP32-S3-DevKitC-1** (25,4 x 62,86 mm + 6,3 mm PCB-Antenne, zwei 1x22-Buchsenleisten J1/J3).
FDM, PETG oder PLA, 0,4-mm-Düse, **ohne Stützstrukturen** druckbar. Das Gehäuse für die WROOM-Variante in `../enclosure/` bleibt unverändert; dies ist eine Kopie, angepasst an das DevKitC (`../tscircuit_devkit/docs/DEVKITC.md`).

**Ausgelegt für:** ESP32-S3-DevKitC-1 **N16R8-Klon mit zwei USB-C-Buchsen** am -Y-Ende (nicht das Micro-USB-Original v1.1), Buchsenmitten laut Zeichnung bei x ≈ 17,0 und 30,4 (Platinenkoordinaten, Platinenmitte = 0|0). Klone weichen um ±1..2 mm ab: Standard ist deshalb **ein gemeinsamer USB-Schlitz** 28,4 x 8 mm.

## Koordinaten und Lage

Wie in `tscircuit_devkit/`: Platinenmitte = (0|0), X nach rechts (EMS-Klemme P1 links, MCU-Seite rechts), Y nach oben. Das DevKitC liegt unverdreht bei x 11,0..36,4, y -32,9..+29,96, die Antennenspitze bei y = +36,26. Das USB-Ende ragt 2,9 mm über die untere Platinenkante (y = -30) hinaus, die Antenne 6,26 mm über die obere. Deshalb:

- **-Y-Wand** sitzt direkt hinter dem DevKitC-Ende (y = -33,4 innen, 0,5 mm Luft), die USB-C-Stecker stecken durch die Wand.
- **+Y: Antennentasche** (x 9,75..37,75, bis y = +41,26): Wand, Boden und Deckel nur **1,2 mm**, **5,0 mm Luft** um die Antenne (Seiten und Ende; Boden 19,5 mm, Deckel 7,2 mm), kein Metall, keine Schraube, keine Rippe, keine Lüftung.

## Dateien

| Datei | Inhalt |
|---|---|
| `enclosure.py` | parametrische Quelle (Python + manifold3d + trimesh). Alle Maße in `PARAMS` am Dateianfang. Schreibt STL (Netz-Variante), Prüfungen, Bilder |
| `enclosure_cq.py` | gleiche Geometrie mit CadQuery (echtes B-Rep): erzeugt **STEP, 3MF und die endgültigen STL**; importiert `PARAMS` aus `enclosure.py` und prüft Äquivalenz und Passung |
| `render.py` | Vorschaubilder |
| `extract_pcb_parts.py` | erzeugt `data/pcb_parts.json` aus `../tscircuit_devkit/dist/index/circuit.json` (nur lesen; Design unverändert) |
| `data/pcb_parts.json` | Bauteilpositionen, Umriss, THT-Löcher, Schlitze der Trägerplatine |
| `data/fit_check.json`, `data/cq_check.json` | Prüfergebnisse (Netz-Variante bzw. B-Rep-Variante inkl. 3MF-Reload) |
| `step/bottom.step`, `lid.step`, `light_pipes.step` | Einzelteile als B-Rep, Lage wie die STL (Deckel mit Außenseite unten) |
| `step/assembly.step` | Baugruppe in Einbaulage mit Namen/Farben: Unterteil, Deckel, 4 Lichtleiter, Platine, Bauteile als Quader, THT-Beinchen, **DevKitC** (Platine, 2 Stiftleisten, Modul, Antennenüberstand, 2 USB-C-Buchsen), P1-Gegenstecker-Platzhalter, 4 Schrauben |
| `3mf/bottom.3mf`, `lid.3mf`, `light_pipes.3mf` | je ein Druckteil, mm, Druckausrichtung |
| `3mf/plate.3mf` | Druckplatte: Unterteil, Deckel (Außenseite unten) übereinander, Lichtleiter daneben; Belegung ca. 161 x 170 mm, passt auf 180 x 180 mm und größer |
| `stl/bottom.stl`, `stl/lid.stl`, `stl/light_pipes.stl` | Druckausrichtung: Unterteil offene Seite oben; Deckel Oberseite auf dem Bett (Pfosten nach oben); Lichtleiter stehend, Flansch unten |
| `img/` | `assembly_exploded.png`, `assembly_fit.png`, `assembly_cutaway.png`, `sections.png` (Schnitte y = 0 und x = 23,7), `plan_lid.png`, `plan_bottom.png` |

**Format:** STEP zum Weiterkonstruieren (Fusion, FreeCAD), 3MF zum Slicen (PrusaSlicer, Bambu Studio, Cura; `plate.3mf` fertig belegt), STL als Dreiecksnetz aus derselben CadQuery-Geometrie.

## Neu erzeugen

`pip install cadquery manifold3d trimesh numpy matplotlib scipy networkx shapely lxml`, dann **in dieser Reihenfolge**:

1. (nur falls `circuit.json` sich geändert hat) `python3 extract_pcb_parts.py`
2. `python3 enclosure.py` (STL-Referenz, Fit-Check, Bilder; nur Prüfung: `--check`)
3. `python3 enclosure_cq.py` (STEP, 3MF, endgültige STL, Äquivalenz- und Fit-Check; ca. 20 s)

Parameter per Umgebungsvariable (nur skalare), z. B. `P_USB_MODE=separate P_INSERT=0 python3 enclosure.py && P_USB_MODE=separate P_INSERT=0 python3 enclosure_cq.py`.

## USB-Positionen anpassen (`PARAMS` in `enclosure.py`)

| Parameter | Standard | Bedeutung |
|---|---|---|
| `usb_x` | `(17.0, 30.4)` | Mitten der beiden USB-C-Buchsen (x, Platinenkoordinaten) |
| `usb_mode` | `'combined'` | `'combined'` = ein Schlitz von `min(usb_x) - usb_pad` bis `max(usb_x) + usb_pad`; `'separate'` = zwei Schlitze mit je `usb_w` Breite |
| `usb_pad` | 7,5 | Überstand des gemeinsamen Schlitzes (Standard: x 9,5..37,9 = 28,4 mm breit) |
| `usb_w` | 12,0 | Breite je Schlitz bei `separate` (Stecker-Overmould typisch 10-11 mm) |
| `usb_h` | 8,0 | Schlitzhöhe (Stecker-Overmould typisch 6 mm); Mitte z = 22,33 mm = 14,2 mm über der Platinenoberseite |
| `usb_z_mid_above_dk` | 1,63 | Höhe der Buchsenmitte über der DevKitC-Oberseite (Buchse 3,26 hoch, Oberseite-Montage angenommen) |
| `usb_rc_w/d/h` | 8,94 / 7,35 / 3,26 | Buchsenkörper (Pass-Körper im Fit-Check) |
| `usb_clr_y` | 0,5 | Luft zwischen DevKitC-Ende und Innenseite der -Y-Wand (verschiebt die Wand) |

Nach Änderung beide Skripte neu laufen lassen; der Fit-Check prüft Stecker-Overmould (11 x 6,4 mm) auch bei ±1,5 mm seitlichem und ±0,7 mm Höhenversatz. Der Schlitz muss unter dem Falz (z = 27,1 mm) enden: bei größerem `usb_h` auch `h_above` erhöhen.

## Maße (Standardparameter)

- **Außen 126,8 x 77,9 x 31,9 mm** (Hauptkasten 126,8 x 67,8, plus Antennentasche +Y bis y = +42,46; x -69,4..+57,4, y -35,4..+42,46); mit Wandlaschen 85,9 mm tief.
- Druckteile: Unterteil 126,8 x 85,9 x 29,1 mm, Deckel 126,8 x 77,9 x 23,8 mm (2,8 Platte + 21 mm Hülsen).
- Innenraum 122,8 x 63,8 mm (+ Tasche); die Platine liegt 12 mm vom linken Innenrand entfernt (P1-Gegenstecker), 0,4 mm Luft zu rechter und oberer Wand.
- Wand 2,0 mm, Antennentasche 1,2 mm (Wand, Boden, Deckel), Boden 2,0 mm, Deckel 2,8 mm.
- Z-Lagen: Platinenunterseite 6,5, Platinenoberseite 8,1, DevKitC-Unterseite 19,1, DevKitC-Oberseite 20,7, Modul-Oberkante 23,9, Deckelunterseite 29,1, Deckeloberseite 31,9 mm. Stapel auf der Platine 15,8 mm (Buchse 8,5 + Stiftleistenkörper 2,5 + DevKitC-PCB 1,6 + Modul 3,2), **5,2 mm Luft über dem Modul**.

## Teileliste

| Menge | Teil | Hinweis |
|---|---|---|
| 1 | `bottom.stl` | |
| 1 | `lid.stl` | |
| 4 | Lichtleiter aus `light_pipes.stl` | klares PETG; oder `led_mode=hole` (nur Löcher) |
| 4 | **M3 x 28** Linsenkopfschraube (ISO 7380, Kopf Ø5,7) | **länger als beim WROOM-Gehäuse (22 mm)**, da der Kasten höher ist (`screw_len`); Schrauben liegen in den Montagelöchern, berühren nur Kunststoff |
| 4 | **M3-Gewindeeinsatz (Heat-Set) M3 x 4, Außen ca. Ø4,6**, Bohrung Ø4,2 x 5 | Standard (`insert=1`); alternativ selbstschneidend in Kernloch Ø2,6 (`P_INSERT=0`) |
| 2-4 | Schrauben für die Wandlaschen (Ø4,5-Loch, Kopf bis Ø8) | nach Wand/Dübel |
| 1 | P1-Gegenstecker 2-polig, 5,08 mm, Leitungsaustritt parallel zur Platine | nicht in der BOM |
| 1 | P2-Gegenstecker 1x4 (Dupont) | von oben durch das Ausbruchfenster |
| 1 | ESP32-S3-DevKitC-1 (USB-C-Klon) | in J1/J3 gesteckt |
| optional | 0,5-1 mm selbstklebendes Moosgummi/Silikon auf den Niederhalter-Rippen | gibt Anpressdruck, siehe unten |

## Druckeinstellungen

- Material: PETG (oder PLA; Heizungskeller < 50 °C: PETG/ASA bevorzugt). Düse 0,4, Schichthöhe 0,2 mm, 3 Wandlinien (1,2 mm Antennenwand = 3 Linien), Boden/Deckel 4-5 Schichten, Infill 20 %.
- **Keine Stützen.** Überbrückungen im Unterteil: **gemeinsamer USB-Schlitz 28,4 mm** (Oberkante, abgerundete Ecken; Brücke mit Lüfter 100 %, 30-40 mm/s; bei schlechter Brücke `usb_mode=separate`, dann 12 mm Spannweite) und P1-Leitungsschlitz 12 mm. Im Deckel (Außenseite unten gedruckt) nur kurze Brücken (Senkungen, Gravur, Flanschsitze <= 6,4 mm).
- Deckel liegt bereits mit der Außenseite unten, Hülsen/Niederhalter zeigen nach oben (bis 21 mm hohe Hülsen, 7 mm Ø: langsam drucken, ggf. Brim).
- Lichtleiter: transparentes PETG, 100 % Infill, 0,1-0,15 mm Schicht, stehend; Länge 22,6 mm. **LD2/LD3: Ø1,8 mm**, 0,7 mm nach -X versetzt (siehe offene Punkte); LD1/LD4: Ø3,0 (LD4 1,0 mm nach +X versetzt).

## Aufbau

1. Gewindeeinsätze von oben in die vier Posten eindrücken (200-220 °C PETG), bündig.
2. Platine auf die vier Posten legen; Rippe x = 0 (0,3 mm unter der Platine) und Zungen in den Optokoppler-Schlitzen. **Zwei Auflagerippen** unter den Buchsenleisten (x 17,5..29,5, 0,25 mm Luft) stützen die Platine beim Aufstecken des DevKitC.
3. P1-Gegenstecker mit Leitungen durch den Schlitz in der linken Wand führen und aufstecken.
4. **DevKitC in J1/J3 stecken** (J1 mit 3V3/GPIO5/GPIO17 zur Platinenmitte, Antenne nach +Y, USB-C-Enden nach -Y). Die Antenne ragt in die Tasche.
5. Lichtleiter von oben in den Deckel stecken (Flansch bündig).
6. Deckel aufsetzen (umlaufender Falz um den Hauptraum), mit 4 x M3 x 28 verschrauben. Die Deckelhülsen klemmen die Platine, die **Niederhalter-Rippen** (x 17..30,5, y 13,5..16,5 und 21,5..24,5) liegen auf dem Modul-Schirmblech (nicht auf der Antenne) und halten das DevKitC in den Buchsen.
7. USB-C-Kabel durch den Schlitz stecken; Gehäuse über die Laschen (oder Schlüssellöcher) an der Wand befestigen.

## Öffnungen

| Ort | Öffnung |
|---|---|
| -Y-Wand (unten), x 9,5..37,9 | **gemeinsamer USB-C-Schlitz 28,4 x 8 mm**, z 18,33..26,33 (Mitte 22,33), Ecken R1; pro Buchse > 12 x 7 mm Platz, Toleranz ±1,5 mm seitlich |
| Linke Schmalwand (-X) | Leitungsschlitz 12 x 8 mm, Mitte z = 13,6 mm (P1) |
| Deckel links | Fenster 22 x 14 mm über dem P1-Gegenstecker (Schraubzugang) |
| Deckel über P2 (x 6,4..10,8, y -30,2..-18) | P2 ist jetzt **senkrecht bei x = 8,6**; Standard `p2_mode=knockout` (Ausbruchfenster, Reststärke 0,6 mm), `open`/`closed` möglich; Gravur **P2** |
| Deckel über LD1..LD4 | Lichtleiterlöcher mit Hülsen, Gravur **EMS** (LD1 bei -8|24), **RX** (LD3 bei 9,6|15,5), **TX** (LD2 bei 9,9|-13,5), **STATUS** (LD4 bei 38,4|7,4); LD5 entfällt |
| Antennentasche | geschlossen, Deckel 1,2 mm |

## DevKitC-Taster (BOOT/RST), RGB-LED

**Nicht vorgesehen (Standard `btn_mode='none'`):** Die Lage der Taster und der RGB-/Power-LED auf dem DevKitC steht weder in `DEVKITC.md` noch in der Maßzeichnung (nur Header, Antennen-Keepout, USB-Enden), und die Taster liegen beim Klon zwischen/neben den USB-C-Buchsen am Ende, wo gesteckte Stecker den Zugang versperren. Im Betrieb nicht nötig: Flashen per USB (Auto-Download/Reset über DTR/RTS bzw. native USB), Reset durch Spannung trennen. Zum Flashen im Download-Modus Deckel abschrauben (4 Schrauben) und BOOT/RST von Hand drücken.
Falls gewünscht: Positionen am echten Board messen, in `dk_btn` eintragen (`(Name, x, y)`), `btn_mode='plunger'` setzen, `btn_top_above_dk` (Tasterhöhe über DevKitC-Platine, 2,0 geschätzt) prüfen; es entstehen Stößel (`buttons.stl`) und Deckelhülsen mit Gravur. Die Standardpositionen in `dk_btn` sind nur Platzhalter (kollisionsfrei, nicht gemessen). Die RGB-LED des DevKitC ist im Deckel nicht sichtbar; falls gewünscht Fenster/Lichtleiter nach Messung ergänzen.

## Galvanische Trennung

- Alles Kunststoff; die Schrauben stecken in getrennten Posten (2 links, 2 rechts).
- Rippe bei x = 0 im Unterteil (1,2 mm, 0,3 mm unter der Platine, Zungen durch die Optokoppler-Schlitze, Zungen enden 0,4 mm unter der Platinenoberseite) und im Deckel (endet 5,5 mm über der Platinenoberseite, bis 15,5 mm lang). Das DevKitC liegt ab x = 11,0 (nächstes Metall: 11 mm von der Rippe); Rippen berühren es nicht (0 mm³). Die Rippen ersetzen nicht die Layout-Abstände (Isolation: `tscircuit_devkit/docs/DEVKITC.md`).

## Wandmontage (`mount`)

- `ears` (Standard): 4 Laschen (Ø4,5-Loch) bodenbündig an den langen Seiten bei x = -40 und x = **+46** (rechts außerhalb der Antennentasche).
- `keyholes`: 2 Schlüssellöcher im Boden bei (-25 | 0) und (45 | 0); `both` / `none` möglich.

## Prüfergebnisse (Einbaulage; `data/fit_check.json` Netz, `data/cq_check.json` B-Rep)

Prüfkörper: Trägerplatine mit allen Bauteilen als Quader und THT-Beinchen, **DevKitC** (PCB 25,4 x 62,86 x 1,6, zwei Stiftleistenkörper, Buchsenleisten J1/J3 8,5 mm, Modul 18 x 19,2 x 3,2, Antennenüberstand 18 x 6,3, zwei USB-C-Buchsen 8,94 x 7,35 x 3,26), USB-Stecker-Overmould 11 x 6,4 mm, P1-Stecker, 4 Schrauben M3 x 28.

- Alle STL: wasserdicht, Windung konsistent, `is_volume` (trimesh); 3MF-Reload wasserdicht.
- Boolesche Überschneidungen Unterteil / Deckel / Lichtleiter / Schrauben / Stecker gegen Platine und DevKitC: **0,0 mm³ überall** (Unterteil x DevKitC, Deckel x DevKitC inkl. Niederhalter, Unterteil x Deckel, Stecker bei ±1,5 mm / ±0,7 mm Versatz, Lichtleiter, Schrauben).
- Abstände: Unterteil zur Platine 0,25 mm (Auflagerippen) / 0,3 mm (Rippe), Unterteil zum DevKitC 0,9 mm (USB-Schlitz-Rand; Wand 0,5 mm), Deckel zum Modul 5,2 mm, Niederhalter 0,0 mm (Kontakt), **Antenne zu Taschenwand/Boden/Deckel >= 5,0 mm**, Deckel zu C12/C14 8,5 mm, zu P1 + Stecker 6,5 mm.
- CadQuery gegen Netz-STL: Volumen 0,01-0,29 %, Bounding Box <= 0,002 mm.

## Annahmen und offene Punkte

- **USB-C-Lage:** Mitten (17,0 / 30,4) stammen aus der Zeichnung des Original-Micro-USB-Boards; der Klon wurde nicht vermessen. Vor dem Druck Buchsenmitten, Buchsenhöhe (Oberseitenmontage, Mitte 1,63 mm über der PCB) und Stecker-Overmould prüfen; `usb_x`, `usb_pad`, `usb_h`, `usb_z_mid_above_dk` anpassen.
- **Höhen des DevKitC** sind Typwerte (Buchse 8,5, Stiftleiste 2,5, Modul 3,2); beim Klon ggf. abweichend. 5,2 mm Luft über dem Modul fangen ±1 mm auf. Modul-Lage (y ab 10,76) und Schirmblech unter den Niederhalter-Rippen ungeprüft (Rippen y 13,5..24,5 liegen sicher im Blech).
- **Niederhalter:** starre Rippen mit `hold_gap=0,0` berühren das Modul nur; Anpressdruck erst mit 0,5-1 mm Moosgummi/Silikon (dann `hold_gap` = Padstärke minus gewünschte Vorspannung setzen, z. B. 0,8 mm Pad und 0,3 mm Vorspannung ergibt `hold_gap` 0,5). Ohne Pad dient das Gehäuse nur als Sicherung gegen Herausrutschen.
- **LD2/LD3 (x ≈ 9,7)** liegen nur 1,1..1,4 mm neben dem DevKitC-Rand (x 11,0): Lichtleiter dünner (Ø1,8) und versetzt, Hülsenwand 0,6 mm, **nur 0,2 mm (LD2) bzw. 0,5 mm (LD3) Luft zum DevKitC**; Lichtausbeute etwas geringer. Bei Schwergängigkeit LED-Optionen `LED_OPT` anpassen.
- **Taster/RGB-LED** des DevKitC: siehe oben (nicht vorgesehen, Lage unbekannt).
- **Platine wird beim Aufstecken belastet:** Auflagerippen (0,25 mm Luft) fangen die Durchbiegung ab; Aufstecken am besten bei eingelegter Platine vor dem Verschrauben.
- Bauteilhöhen der Trägerplatine aus Typwerten geschätzt (C12/C14 12,5, P1 10 + Stecker 14,5, P2 11,5); P1-/P2-Gegenstecker real messen. Lichtleiter, Heat-Set-Maße und Passungen ungetestet (kein Probedruck): Teststück Posten/Hülse und Lichtleiter vorab drucken.
- Vorschaubilder sind einfache Software-Renderings; Bauteile sind Quader-Platzhalter, das DevKitC ohne Eckfasen.
