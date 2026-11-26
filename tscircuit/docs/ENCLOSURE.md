# Gehäuse-Recherche EMS-Bus-Interface (ESP32-S3, galvanisch getrennt)

Stand: 2026-11-26. **Wichtige Einschränkung:** In der Recherche-Umgebung waren WebFetch-Zugriffe auf
hammfg.com, tme.eu und electrokit.com gesperrt (DNS nicht erreichbar); es standen nur WebSearch-Snippets
zur Verfügung. Alle Maße unten stammen aus Suchergebnis-Snippets oder sind als **[ungeprüft]** markiert.
Bohrungsabstände / Domkoordinaten konnten **nicht** aus Zeichnungen gelesen werden. Vor dem PCB-Layout-Freeze
MUSS die Herstellerzeichnung (PDF/STEP, Links unten) geprüft werden. Preise sind Größenordnungen aus dem
Gedächtnis [ungeprüft], keine abgefragten Shop-Preise.

## Anforderungen (Kurzfassung)
- PCB 110 x 60 mm (anpassbar), ESP32-S3-WROOM-1 mit PCB-Antenne an einer kurzen Kante -> Kunststoff, kein Metall dort.
- Höhe innen >= ca. 25 mm (Elkos 12 mm, Klemme ca. 15 mm inkl. Stecker, plus PCB 1,6 mm und Abstand) -> realistisch >= 28-30 mm.
- Wandmontage (Flansch/Laschen), USB-C seitlich/optional, 2-pol. 5,08-mm-Klemme + Kabeleinführung, 4-6 LEDs.
- IP-Schutz: Heizungskeller trocken -> **IP40 reicht**. IP54/65 ist nicht nötig, aber bei gedichteten Boxen
  (Gainta G3xx, Euromas) vorhanden; Dichtung stört nicht, verteuert aber ggf. die Kabeleinführung (M16/M20-Verschraubung).

## Kandidaten

| # | Gehäuse | Außen L x B x H | Innen (belegt?) | Flansch | Material / IP | Bemerkung |
|---|---------|-----------------|-----------------|---------|---------------|-----------|
| 1 | **Hammond 1591DSFLGY** (grau, Flansch) | 150 x 80 x 50 | ca. 143,6 x 73,6 x 46,1 (Hammond-Zeichnung 1591DSFL laut Snippet; Teilenummer-Zuordnung prüfen) | ja, integriert | ABS flammhemmend (UL94 V-0), IP54 | PCB 110x60 passt mit Luft; viel Höhe; Reichelt/Farnell/Mouser/RS/TME. STEP über hammfg.com / Farnell-CAD |
| 2 | **Gainta G308MF** (115x65x55, Flansch; vermutlich = V1-Box laut Foto mit Messing-Einsätzen) | 115 x 65 x 55 | [ungeprüft] ca. 105 x 55 (Wand ca. 3 mm abzüglich Eckdome) -> 110x60 passt NICHT | ja | ABS, IP65 (Dichtung) | günstig (ca. 4-6 EUR [ungeprüft]), TME/Reichelt. Dome in den Ecken für Deckelschrauben; Platinen-Bosse am Boden laut Händlerbeschreibung. PCB müsste auf ca. 95 x 50 schrumpfen |
| 3 | Hammond 1591BFLGY (112x62x31, Flansch) | 112 x 62 x 31 | [ungeprüft] ca. 106 x 56 x 27 | ja | ABS, IP54 | zu schmal für 60 mm Breite; Höhe knapp für Klemme+Elko. Nur mit PCB ca. 100 x 50 und liegenden Elkos |
| 4 | OKW Smart-Box C6011141 | 140 x 110 x 60 (Farnell; andere Quellen widersprüchlich) | [ungeprüft] | Wandlaschen-Variante vorhanden | ABS, IP66, Schraubdome für PCB | größer als nötig, teurer (ca. 12-20 EUR [ungeprüft]); Datenblatt enthält Tabelle "max. PCB size" |
| 5 | Bopla Euromas M/T-Serie (z. B. M/T 208: 98x64x36,4; größere 120x80x85) | siehe links | [ungeprüft] | Schraubkanäle im Boden / Wandwinkel | ABS, IP65 | M/T 208 zu klein; 122x120x55 (Flansch) deutlich zu groß; Bopla-STEP je Artikel verfügbar |
| 6 | RS PRO / Hammond DIN-Schienengehäuse ABS, z. B. 107 x 90 x 65 | 107 x 90 x 65,2 | [ungeprüft] | DIN-Schiene TS35 (3 Rasten) | ABS, flammhemmend | Alternative statt Wandmontage; Platine 110x60 passt hier nicht, Layout müsste auf Modulbreite angepasst werden. Phoenix ME-MAX/Italtronic nicht geprüft |

Transluzent: Bei Hammond gibt es 1591-Varianten mit transparentem/transluzentem Deckel (z. B. "...TBU" bei 1591S laut Datenblattlistung);
für 1591D/E-Größen **prüfen**. Sonst Lichtleiter (3 mm Rundstab, wie bei V1 im Deckel verklebt) oder Löcher im Deckel.

## Empfehlung
**Primär: Hammond 1591DSFLGY** (Flansch, ABS V-0, 46 mm Innenhöhe, ca. 143 x 73 mm Innenfläche).
Gründe: Platz für bestehende 110x60-Platine inkl. Antennenfreiraum (Antennenkante zeigt zu einem freien Ende,
Kunststoffwand, kein Metall), reichlich Höhe, Wandflansch, in DE breit verfügbar, STEP vorhanden.
Nachteil: Platine hat im Boden keine passenden Standard-Aufnahmen -> Befestigung über ein 3D-gedrucktes
Trägerblech/Standoffs oder selbstklebende/gesteckte M3-Abstandshalter; Deckelschrauben-Dome sitzen in den Ecken.

**Alternative: Gainta G308MF** (gleiches Prinzip wie V1, sehr günstig), aber nur wenn die Platine auf ca. 95 x 50 mm
verkleinert wird [ungeprüft, V1-Box nachmessen: Innenmaß + Abstand der Bodenbosse]. Praktischer Tipp: Das physische V1-Gehäuse
vorhanden -> Innenmaße und Bossen-Positionen direkt mit Messschieber ermitteln.

### Vorgeschlagener PCB-Umriss / Bohrungen (vorläufig, bis Zeichnung gelesen)
- Umriss: 110 x 60 mm beibehalten (passt in Innen 143,6 x 73,6 -> je Seite >= 3 mm Luft in Breite, 16 mm in Länge).
- Vier M3-Bohrungen (3,2 mm) bei 4,0 mm Randabstand: Raster **102 x 52 mm**, bei Gehäuse-Standoff-Träger (3D-Druck) 1:1 anlegbar.
- Platine in der Gehäuselängsachse mittig, ESP32-Antennenkante an die kurze Seite, >= 10 mm Abstand zur Wand/Metallteilen.
- USB-C: an die lange Seite nahe Ecke, Öffnung ca. 10 x 4 mm in der Gehäusewand fräsen/bohren (nur zum Flashen: Gummistopfen ok).
- Klemmleiste 5,08 mm: an die kurze Seite gegenüber der Antenne; Kabeleinführung per M16-Verschraubung oder Ausbruch.
- LEDs: auf der Platinen-Oberseite in einer Reihe, Lichtleiter/Löcher im Deckel; RESET/BOOT intern.
Diese Werte sind **Vorschlag**, nicht aus Hersteller-Datenblatt; sie sind gegen die Zeichnung zu validieren.

## 3D-Druck-Alternative
Eigenes Gehäuse (PETG oder ASA, Wandstärke 2 mm, Heizungskeller bis ca. 40-50 C: kein PLA) mit exakt
passenden PCB-Domen, USB-C-Ausschnitt, Klemmenöffnung, Lichtleiter-Schächten und Wandlaschen; Deckel verschraubt.
Vorteil: Maße exakt zur Platine, Antenne frei. Nachteil: Flammschutz (V-0) fehlt, was für ein
Netz-nahes/Heizungsprodukt zu bedenken ist; ASA/PC-FR bevorzugen.

## Offene Punkte (vor Bestellung klären)
1. Zeichnung 1591DSFL lesen: Innenmaße, Position/Durchmesser der Deckelschraubdome, Bodenrippen.
2. Prüfen, ob 1591D eine transluzente Deckelvariante hat.
3. Aktuelle Preise/Verfügbarkeit bei Reichelt, TME, Mouser, Farnell abfragen.
4. V1-Box (Gainta?) nachmessen.

## Quellen (Suchergebnisse; nicht alle per Fetch geprüft)
- Hammond 1591 Serie: https://www.hammfg.com/electronics/small-case/plastic/1591
- Hammond 1591 Datenblatt GS: https://www.hammfg.com/files/parts/pdf/1591GSGY.pdf
- Hammond 1591XXBFLGY: https://www.hammfg.com/files/parts/pdf/1591XXBFLGY.pdf
- Hammond 1591SFLGY: https://www.hammfg.com/part/1591SFLGY
- RS 1591 DSFL 150x80x50: https://nz.rs-online.com/web/p/general-purpose-enclosures/4935900
- Farnell Hammond CAD: https://www.farnell.com/cad/2237862.pdf
- Gainta G308MF (Electrokit): https://www.electrokit.com/en/enclosure-115x65x55mm-ip65-with-flange-grey-abs
- Gainta bei TME: https://www.tme.eu/html/EN/gainta-enclosures-with-fixation/ramka_15942_EN_pelny.html
- Jaycar G308MF: https://jaycar.co.nz/abs-seal-box-115x65x55-with-flange-g308mf/p/HB6138
- OKW Smart-Box (Farnell): https://uk.farnell.com/okw-enclosures/c6011141/enclosure-smart-box-ip66-140x110x60mm/dp/3378270
- OKW Smart-Box Datenblatt: https://www.farnell.com/datasheets/1675107.pdf
- Bopla Euromas: https://datasheet.sic-components.com/euromas-abs-pc-f05_en.pdf
- RS PRO DIN-Rail ABS 107x90x65: https://uk.rs-online.com/web/p/din-rail-enclosures/2069059
- Phoenix Contact DIN-Gehäuse: https://www.phoenixcontact.com/en-dk/products/electronics-housings/din-rail-housing
