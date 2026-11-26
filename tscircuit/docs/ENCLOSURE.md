# Gehäuse-Recherche EMS-Bus-Interface (ESP32-S3, galvanisch getrennt)

Stand: 2026-11-26. Quellen: Hammond-Zeichnungen (PDF, hammfg.com, gelesen und als Bild geprüft) und
Reichelt-Produktseiten (reichelt.de, Preis/Lager am Abrufdatum). Reichelt-Datenblatt-CDN (cdn-reichelt.de),
tme.eu, Gainta, OKW-/Bopla-Zeichnungen waren nicht lesbar bzw. nicht in Reichelts Sortiment -> dort "ungeprüft".

> **Wichtig (Stand Platine 110 x 70 mm):** Die Platine ist jetzt ein einfaches Rechteck **110 x 70 mm** (x -55..55, y -40..30, scharfe 90-Grad-Ecken, keine Eckausschnitte, kein Panel; siehe docs/FAB_CHECKLIST.md). Das **Hammond 1591XXCFLBK passt damit NICHT mehr**: Innenraum 115,15 x 60,65 mm, die Platine ist 70 mm breit, und die Eckausschnitte fuer die Deckelschraub-Domes, mit denen die Platine ueberhaupt in das Gehaeuse kam, gibt es nicht mehr. Alle Hammond-Angaben unten sind **historisch** (Stand 110 x 60) und nur zur Dokumentation stehen geblieben. Gehaeuse jetzt: das 3D-gedruckte Gehaeuse in `enclosure/` (Aussenmass 126,0 x 74,8 x 26,9 mm, Innenraum 122,8 x 70,8 mm). Ein Reichelt-Standardgehaeuse mit Innenmass >= ca. 112 x 72 mm: einzig die Hammond-1591XXD-Reihe aus der Tabelle unten (XXDFLBK, Innen 145,40 x 75,40 x 46,5 laut Hammond-Zeichnung) ist dimensionsmaessig gross genug; Lage/Raster der Platinenposten und Eignung fuer die 84,5 x 39,5-Bohrungen sind dort **nicht geprueft** (nur 145 x 75 Innenmass bekannt), deshalb keine Empfehlung. Empfehlung: gedrucktes Gehaeuse.

## Anforderungen
PCB 110 x 70 mm (Rechteck; frueher 110 x 60 mm), ESP32-S3-WROOM-1 mit PCB-Antenne an kurzer Kante (Kunststoff, kein Metall),
Innenhöhe >= ca. 25-30 mm (Elko 12 mm, Klemme ca. 15 mm), Wandmontage, USB-C seitlich, Klemme 5,08 mm + Kabeleinführung,
4-6 LEDs, RESET/BOOT intern. Heizungskeller trocken -> **IP40 genügt** (IP54 der Hammond-Boxen ist ausreichend).

## Verifiziert: Hammond 1591 bei Reichelt (Reichelt führt keine Gainta/Bopla/Fibox; Strapubox, OKW, Hammond ja)

| Reichelt Art.-Nr. | Gehäuse | Innen L x B x H (Hammond-Zeichnung) | Flansch | Preis (brutto) | Bemerkung |
|---|---|---|---|---|---|
| **1591XXCFLBK** (reichelt-ID 221253) | 1591XXC, 121 x 66 x 40, schwarz, FR-ABS UL94 V-0, IP54 | **115,15 x 60,65 x 36,0** | ja (Laschen mit Langloch) | 6,99 EUR, ab Lager 1-2 Werktage | **Primär.** Messingeinsätze für 4 Deckelschrauben M3x10, PCB-Posten in Box UND Deckel |
| 1591XXCGY (221272) | wie oben, grau, ohne Flansch | 115,15 x 60,65 x 36,0 (gleiche Serie) | nein | 7,10 EUR | falls Wandmontage anders (Klebe-/Schraubpads) |
| 1591CFLBK (121042) | 1591C alt, 120 x 65 x 40, schwarz, Flansch | 113,53 x 58,53 x 35,9; Kartenführung 1,6 mm Schlitz | ja | 6,25 EUR | PCB 110x60 passt NICHT (58,53 breit); max. ca. 110 x 56 |
| 1591CTCL (221271) | 1591C, **kristallklar (Polycarbonat)** | 113,53 x 58,53 x 35,9 | nein | 8,20 EUR | transluzent -> LEDs sichtbar ohne Lichtleiter; PCB max. ca. 110 x 56 |
| 1591BFLBK (121041) / XXBFLBK (221252) | 112 x 62 x 31 | XXB: 108,15 x 57,65 x 27,0 | ja | 4,90 EUR | zu klein/flach, PCB max. ca. 100 x 52 |
| 1591DFLBK (221256) / XXDFLBK (221258) | 150 x 80 x 50 | XXD: 145,40 x 75,40 x 46,5 | ja | 7,90 / 7,99 EUR | Reserve, wenn mehr Platz nötig |

Nicht Hammond bei Reichelt: Strapubox 115x65x27 (Art. SP, 6,10 EUR; mit Batteriefach, Innenhöhe zu gering, Maße ungeprüft),
OKW SMART-CASE 140x62,7x30,5 (Art. OKW, 22,95 EUR, ABS UL94HB, Befestigungsdome; Zeichnung ungeprüft) -> beide nicht empfohlen.
Hammond 1591-Zeichnungen: https://www.hammfg.com/files/parts/pdf/1591XXCFLGY.pdf (identische Geometrie wie CFLBK),
https://www.hammfg.com/files/parts/pdf/1591CTCL.pdf. STEP/IGES lt. Zeichnung bei Hammond verfügbar (Download-Link nicht verifiziert).

## Empfehlung
**Primär: Reichelt 1591XXCFLBK** (6,99 EUR): Innenmaß 115,15 x 60,65 x 36, Flansch zur Wandmontage, FR-ABS, definierte
PCB-Posten. **Alternative (transluzent): 1591CTCL** (8,20 EUR, klares PC, ohne Flansch; Platine auf ca. 110 x 56 verkleinern,
Wandmontage dann über Klebe-/Montagelaschen oder Variante CFL mit 3D-gedruckten Winkeln).
Hinweis: Eine transluzente XX-C-Variante gibt es lt. Zeichnung nicht (nur BK/GY); TBU existiert bei XXA/XXB/XXE.
Hinweis Antenne: Kunststoff-Wand, Antennenkante zu einer kurzen Gehäusewand legen; Wand ist 2,0 mm ABS (unkritisch).

### PCB-Umriss und Bohrungen für 1591XXCFL (aus Hammond-Zeichnung "MAX SIZE PCB", Maße in mm)
Hammond-Maximalplatine: 114,5 x 60,5, Eckausschnitte um die Deckelschraub-Dome (gerade Länge zwischen Ausschnitten 99,0,
gerade Breite 44,5; Ausschnitt-Radius R3,5). PCB-Posten: Raster **84,5 x 39,5** (Ø3,5 Bohrung, #4 x 1/4" Blechschraube).
Vorschlag (Ursprung unten links, Platine mittig im Gehäuse):
- Außenmaß **110,0 x 60,0**, 4 Eckausschnitte je **5,5 (X) x 8,0 (Y)** mit R3,5 an den Innenecken. (Ableitung: (114,5-110)/2 = 2,25 weniger Länge: 7,75 - 2,25 = 5,5; Breitenausschnitt 8,0 unverändert.)
- 4 Bohrungen Ø3,5 bei **(12,75 | 10,25), (97,25 | 10,25), (12,75 | 49,75), (97,25 | 49,75)** (Raster 84,5 x 39,5, zentriert).
- Hinweis: Schrauben sind #4 x 1/4" selbstschneidend (Hammond 1593ATS50) oder M3-Blechschrauben; M3-Gewinde in den Posten nicht vorgesehen. Pilotloch-Durchmesser der Posten nicht in der Zeichnung -> ungeprüft.
- Bauteilhöhen: Innenhöhe gesamt 36 mm (Box + Deckel); Pfostenhöhe nicht bemaßt (ungeprüft), Elko 12 mm + Klemme 15 mm passen mit großem Spiel.

### Öffnungen (Vorschlag)
- Klemmleiste 5,08 mm: an einer kurzen Wand, Antenne an gegenüberliegender kurzer Seite; Kabelloch Ø6-7 mm oder M12/M16-Verschraubung; 2 mm Wand lässt sich bohren/fräsen (Hammond bietet auch Bearbeitung/Bedruckung an).
- USB-C: lange Wand nahe Ecke, Ausschnitt **12 x 7 mm** (Mitte x = 33 / Wand bei y = +30; siehe "USB-C-Ausschnitt" unten; nur zum Flashen; Gummistopfen/Aufkleber).
- LEDs: Löcher Ø3 oder Ø5 im Deckel (Lichtleiter wie V1), Taster intern.

## 3D-Druck-Alternative
ASA/PETG (kein PLA), 2 mm Wand, exakt zur Platine mit Domen, USB-C-Ausschnitt, Lichtleiterschächten, Wandlaschen. Nachteil: kein UL94-V0.

## Ungeprüft / offen
- STEP-Download-Link, Posten-Höhe und Pilotloch-Ø; Reichelt-eigene Datenblatt-PDFs (cdn-reichelt.de gesperrt).
- Gainta G308MF (Innenmaß), OKW Smart-Box, Bopla: nicht im Reichelt-Sortiment, nicht geprüft. V1-Box nachmessen, falls Gainta-Option gewünscht.
- Preise/Lager: Stand Abrufdatum, Reichelt-Preise brutto inkl. 19 % MwSt.

## Quellen
- https://www.reichelt.de/de/de/shop/produkt/x-221253 (1591XXCFLBK), -221272, -221271, -121042, -221256
- https://www.hammfg.com/files/parts/pdf/1591XXCFLGY.pdf, https://www.hammfg.com/files/parts/pdf/1591CFLBK.pdf, https://www.hammfg.com/files/parts/pdf/1591CTCL.pdf, https://www.hammfg.com/files/parts/pdf/1591XXBFLGY.pdf, https://www.hammfg.com/files/parts/pdf/1591XXDFLGY.pdf

## Platinenlayout V2.0 (Koordinaten gelten unveraendert fuer 110 x 70; Titel historisch: Hammond 1591XXCFLBK, Stand Layout AP7b)
Koordinaten: tscircuit-Koordinatenursprung (0|0) = Mitte der frueheren 110 x 60-Platine, jetzt 5 mm ueber der Platinenmitte (die Platine reicht y -40..30), X nach rechts, Y nach oben (Maße in mm). Für "unten links = Ursprung" (Hammond-Zeichnung): X + 55, Y + 30.

| Objekt | Lage (Mitte) | Lage ab unten links | Bemerkung |
|---|---|---|---|
| Umriss | **110,0 x 70,0 Rechteck, scharfe Ecken** (x -55..55, y -40..30; 10 mm nur nach unten verlaengert; frueher 110 x 60 mit Eckausschnitten) | | `index.circuit.tsx` (`board outline`) |
| Montagebohrungen MH1..MH4 | (-42,25 / +19,75), (-42,25 / -19,75), (+42,25 / +19,75), (+42,25 / -19,75) | (12,75 / 49,75), (12,75 / 10,25), (97,25 / 49,75), (97,25 / 10,25) | Ø3,5 NPTH; Kupfer-/Bauteil-Sperrzone Ø8 (Schraubenkopf) um jede Bohrung, Pour-Abstand >= 2,25 mm zum Loch |
| P1 Klemme (KF2EDGRC-5.08-2P, rechtwinklig) | Stiftachse x = -44,1, Pins bei y = +-2,54, Steckseite bündig an der linken Kante (x = -55) | Kabelloch Ø6..7 bei (0 / 30) in der linken kurzen Wand | Gegenstecker (nicht in der BOM, separat kaufen): 2-poliger 5,08-mm-Schraubsteckverbinder KF2EDGK-5.08-2P / Phoenix MSTB 2,5/2-STF-5,08-Klasse, Leitungsaustritt parallel zur Platine; Steckerrichtung nach außen (EasyEDA-Körper -10,9 .. +1,3 mm um die Pinachse, Drehung 270); Körper 11,8 x 12,2 mm überdeckt nur den freien Streifen x -55 .. -42,8 |
| ESP32-S3-WROOM-1 (U3) | Mitte (42,25 / 0), Antenne zeigt nach +X, endet bündig an x = +55 | | Antennenzone x >= 48, \|y\| <= 24 (= 9 mm halbe Modulbreite + 15 mm): auf beiden Lagen weder Kupfer noch Bauteile (Keepout, geprüft von `check_fab.py`) |
| USB-C J2 | Mitte Steckeröffnung (33,0 / +30,0), Öffnung bündig an der oberen langen Kante, Breite 9 mm | (88,0 / 60,0) | Gehäuseausschnitt **12 x 7 mm** (B x H) in der langen Wand, Mitte 22 mm von der rechten Wand (x = 33); Steckermündung 2,3 mm hinter der Außenfläche, siehe "USB-C-Ausschnitt"; nur zum Flashen |
| Tasten SW1 (RESET) / SW2 (BOOT) | (33,5 / -23,5) / (34,0 / -14,8) | | intern, durch Deckel nicht bedienbar (Büroklammer/Stift durch ein Ø2-Loch falls gewünscht: Loch im Boden der Box unter SW1/SW2 oder Deckel bei (88,5 / 6,5) / (89,0 / 15,2)) |
| Isolationsschlitze | 2 x 12 mm, x = 0 (Breite 2 mm), y = +2 .. +14 und -2 .. -14 | | nur unter den Optokopplern, enden nicht an der Platinenkante |

### Leuchtdioden für Lichtleiter im Deckel (Bohrungen Ø3 oder Lichtleiter-Ø3..5)
Alle LEDs 0805 (Seite oben), Lichtleiter-Abstand >= 5 mm. Koordinaten = LED-Mitte; Deckelbohrung bei gleichen X/Y (Deckel mit gleicher Außenmaß-Orientierung auflegen, X/Y wie Platine).

| LED | Funktion | Mitte (Platinenmitte = 0|0) | ab unten links | Farbe |
|---|---|---|---|---|
| LD1 | EMS-Seite Betriebsspannung (5 V Buck) | (-8,0 / +24,0) | (47,0 / 54,0) | rot |
| LD3 | RX (EMS-Bus -> ESP) | (+16,0 / +13,6) | (71,0 / 43,6) | gelb (R3: KT-0805Y statt grün, Position unverändert) |
| LD2 | TX (ESP -> EMS-Bus) | (+12,5 / -13,8) | (67,5 / 16,2) | gelb (R3: KT-0805Y statt grün, Position unverändert) |
| LD5 | 3,3 V Betriebsspannung MCU-Seite | (+28,0 / +8,5) | (83,0 / 38,5) | gelb (R3: KT-0805Y statt grün, Position unverändert) |
| LD4 | Status GPIO2 | (+47,0 / -16,5) | (102,0 / 13,5) | gelb (R3: KT-0805Y statt grün, Position unverändert) |

Hinweis LD4: liegt 5 mm neben der Antennenzone (x < 48) und 0,3 mm neben der Sperrzone des Schraubenkopfes (Hole 42,25 / -19,75); Lichtleiter dort bitte nicht aus Metall.
Silkscreen auf der Platine: "PWR" (LD1), "RX" (LD3), "TX" (LD2), "3V3" (LD5; Beschriftung unter der LED bei (26,0 / 5,9)); Text jetzt 1,85 mm Schrift (Glyphe 1,04 mm hoch, R3); neu: "RESET" (SW1), "BOOT" (SW2). LED-/Steckerpositionen haben sich in R3 NICHT geändert (nur die LED-Farbe grün -> gelb).

### USB-C-Ausschnitt (R5 m8)
Die Buchse J2 steht bündig mit der Platinenkante (Mündung bei y = +30,0). Die Gehäusewand ist 2,0 mm dick, zwischen Platinenkante und Wand bleiben rund 0,3 mm Spiel (Hammond: Innenmaß 60,65 gegen Platine 60,0): die Steckermündung liegt damit **2,3 mm hinter der Außenfläche**.
Ein Standard-USB-C-Stecker (Metallhülse 8,4 x 2,6 mm, Kabel-Knickschutz meist größer) greift nur mit ca. 2 mm Hülse bis in die Buchse, wenn der Ausschnitt den Stecker-Overmould aufnimmt. Empfehlung: **Ausschnitt 12 x 7 mm (Breite x Höhe), Mitte bei x = 33,0 und in der Höhe auf die Buchse zentriert** (Buchse 9,0 x 3,2 mm, Mitte der Buchse ca. 1,6 mm über der Platinenoberseite + Platinendicke 1,6 mm + Postenhöhe), Ecken R1 bei gefrästem/gebohrtem Ausschnitt. Das passt auch für Stecker mit Overmould (typisch 10-11 x 6 mm) und lässt 0,5 mm Toleranz. Ein 10 x 4 mm Ausschnitt lässt nur schlanke Stecker (Hülse ohne Overmould) durch, die 2,3 mm tiefer in der Wand stecken.
Die Höhenlage hängt vom Pfosten (Pfostenhöhe ist in der Hammond-Zeichnung nicht bemaßt, ungeprüft: mit dem STEP der 1591XXC nachmessen).

### Lichtleiter (R5 m8)
Die Platine liegt auf den Gehäuseposten, die LEDs (0805, Höhe ca. 0,8 mm) sitzen auf der Oberseite; der Abstand LED-Oberfläche zur Innenseite des Deckels beträgt ungefähr Innenhöhe 36 mm (Box + Deckel) - Pfostenhöhe - Platinendicke 1,6 mm - Deckeldicke. Mit den üblichen Postenhöhen ergibt das **ca. 25 mm Lichtleiterlänge** (Ø3 mm Acryl-/PC-Stab oder gedruckter Lichtleiter, Planungswert; nach STEP-Messung der Pfostenhöhe korrigieren). Lichtleiter-Abstand >= 5 mm, Lichtleiterenden auf der LED zentrieren (Toleranz Platine/Posten +-0,3 mm), LD4 (GPIO2) liegt 5 mm neben der Antennenzone: kein Metall.

Hinweis (Silk): Das Black-Swan-Logo (10 x 10 mm, Mitte 20,5 / 0,0) und das 2D-Barcode-Feld (8 x 8 mm, Mitte -50,0 / 11,5) liegen auf der Platinen-Oberseite unter dem Deckel; reine Silkscreen-Flaechen ohne Bauhoehe, der Deckel braucht dort keine Aussparung.
