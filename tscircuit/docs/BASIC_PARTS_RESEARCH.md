# Basic-/Preferred-Teile statt Extended: Recherche (Stand 2026-11-26)

Ziel: Extended-Teiletypen der JLCPCB-Economic-Bestueckung (je ca. 3 USD einmalige Gebuehr pro Typ) durch Basic- oder
Preferred-Extended-Teile ersetzen. Nur Recherche, kein Design- oder Fab-File wurde veraendert.
Vorgaenger-Entscheidungen: `docs/review/FIX_LIST_R2.md` (m10), `FIX_LIST_R3.md` (m6, m9), `docs/JLCPCB_PARTS.md`.

## 1. Methode und Quellen

* JLC-Teilebibliothek: `POST https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`
  mit `{"keyword":..,"currentPage":1,"pageSize":100,"componentLibraryType":"base"}` (nur Basic) bzw.
  `"preferredComponentFlag":true` (nur Preferred). Felder: `componentLibraryType` (base/expand), `preferredComponentFlag`, `stockCount`.
  Beide Filter funktionieren (geprueft: BAT42 + Pref-Filter liefert C22466360/C22466362).
* Per-Teil-Seite `https://jlcpcb.com/partdetail/<LCSC>`, Feld "PCBA Type" (Funktion `live()` aus `scripts/jlc_economic.py`).
  Alle vorgeschlagenen Ersatzteile unten wurden damit geprueft: "Economic and Standard" (Ausnahmen sind ausdruecklich genannt).
* `jlcsearch.tscircuit.com/components/list.json?search=Cxxxx` und `/capacitors/list.json?json=true&is_basic=true` (Kontrolle, Beschreibung, Strom/DCR von Ferriten).
* Reichelt: `https://www.reichelt.de/de/de/shop/suche/<Begriff>` (HTML geparst). Der in der Aufgabe genannte Weg `index.html?ACTION=446&SEARCH=` leitet auf
  `reichelt.com` um, das vom Proxy gesperrt ist; der Pfad `/de/de/shop/suche/` funktioniert. Preise = Einzelstueckpreis laut Suchergebnis
  (vermutlich brutto in EUR); Versand nicht beruecksichtigt (Nutzer bestellt ohnehin bei Reichelt).
* **Nicht verifizierbar:** Datenblatt-PDFs (Host `jlc-prod-smt.oss-eu-central-1.aliyuncs.com`) sind vom Proxy gesperrt. Alle Werte, die aus dem Gedaechtnis /
  Familiendatenblaettern stammen statt aus dem konkreten Datenblatt, sind unten mit "(pruefen)" markiert.
* Annahme Gebuehr: "Extended Components Fee" ca. 3 USD je Typ (docs/JLC_ECONOMIC.md); Basic und Preferred-Extended = keine Gebuehr.

## 2. Ist-Zustand (live neu geprueft)

15 Extended-Typen (ohne U3/ESP32, der ist DNP): C107120 (C1), C49256851 (C12/C14), C910822 (F1/F2), C269119 (F3), C165948 (J2), C98021 (L1/L2),
C43183 (L3), C92651 (OC1), C336082 (OC2), C441236 (P1), C32713270 (P2), C53284030 (R2-R4), C17384 (R15), C371172 (U2), C7519 (U4).
Bereits gebuehrenfrei (Preferred, live bestaetigt): **C22466362 BAT42W (D1-D5)**, **C20069155 BC817-40 (Q1; in `JLCPCB_PARTS.md` noch "check": ist Preferred)**,
C1717 (C4 1n5). Alle anderen Zeilen sind Basic (C7955 LM393, C6186 AMS1117, C16133 Tantal, C318884 Taster, LEDs, Dioden D6/D7, alle R/C ausser den genannten).

Fazit Vorab: Basic-Bibliothek enthaelt **keine** Aluminium-Elkos, keine PTC, keine USB-C-Buchse, keine Stiftleisten/Klemmen, keine Leistungsinduktivitaet 4,7 uH,
keine 2010-Widerstaende, keinen Hochgeschwindigkeits-Optokoppler (API: `Aluminum Electrolytic Capacitors`, `Resettable Fuses`, `USB Connectors`, `Pin Headers`,
`6N137`/`6N136` jeweils 0 Treffer mit Basic- und mit Preferred-Filter).

## 3. Tabelle je BOM-Zeile (nur Extended-Zeilen + Kandidaten)

Legende Empfehlung: **Tauschen** = geringes Risiko, Footprint gleich; **Optional** = elektrisch machbar, aber Layout-/Funktionsaenderung oder Messung noetig;
**Nicht tauschen** = kein sinnvoller Ersatz / Risiko zu hoch.

| Ref | aktuell (LCSC / Typ) | Vorschlag (LCSC / Typ) | Lager | Elektrische Auswirkung (Rechnung) | Footprint | Empfehlung |
|---|---|---|---|---|---|---|
| C1 68p C0G | C107120 Ext | **C1790** CL21C101JBANNNC 100 pF C0G 50 V 0805, **Basic** (alt.: C14857 47 pF Basic 177k) | 792k | C1 liegt differentiell ueber den Bruecken-Eingaengen (EMV/ESD, nicht Teil der Signalfunktion). 68 pF -> 100 pF: +32 pF. Zeitkonstante mit z. B. 1 kOhm Quellimpedanz = 0,1 us << 104 us Bitzeit. LC mit L1+L2 = 9,4 uH: f = 1/(2 pi sqrt(9,4 uH * 100 pF)) = 5,2 MHz (vorher 6,3 MHz), unkritisch. | gleich (0805) | **Tauschen** (-1 Ext) |
| R15 1k3 / R12 6k8 | R15 C17384 Ext | **R15 -> 5k1 C27834 (Basic, bereits in BOM als R23/R24), R12 -> 27k C17593 (Basic, 304k)** | 2,4M / 304k | JW5017S: Vout = 0,8 V * (1 + R12/R15) (V1: 0,8*(1+6,8/1,3) = 4,985 V). Neu: 0,8*(1+27/5,1) = **5,035 V (+1,0 %)**. Worst case 1 %-Widerstaende: alt 4,90..5,07 V, neu 4,95..5,12 V. Teiler-Strom 157 uA statt 615 uA, FB-Knoten 4,3 kOhm (unkritisch). Folgen: OC1-LED R10 470R: (5,035-1,5-0,15..0,4)/470 = 6,7..7,2 mA (vorher 6,4..7); 6N136 VCC 5,035 V < 5,5 V; LD1 (R17 1k2) 2,5 mA. Frueher untersuchte Paare (5k1/1k0 = 4,88 V, 6k2/1k2) waren die falschen; 27k/5k1 ist beides Basic und 1 % genau. (Vref 0,8 V aus V1-Werten abgeleitet, JW5017S-Datenblatt nicht abrufbar.) | gleich (0805) | **Tauschen** (-1 Ext; R12-Typ 6k8 C17772 entfaellt, Basic-Typenzahl unveraendert) |
| U4 USBLC6-2SC6 | C7519 Ext | **C7420376 SRV05-4 (hongjiacheng, SOT-23-6L), Preferred** (Economic ok) | 540k | Pinbelegung SRV05-4: 1/3/4/6 = I/O, 2 = GND, 5 = VP (EasyEDA-Symbol C7420376 bestaetigt 6 Pins, I/O 1,3,4,6; Funktionsnamen im Symbol nicht vorhanden -> Datenblatt pruefen). Auf der Platine sind U4.1+6 = USB_DP, 3+4 = USB_DN, 5 = VBUS bereits so verdrahtet -> pin-kompatibel, jede Leitung hat zwei parallele Kanaele. Cj je Kanal typ. 2-4 pF (pruefen) -> ca. 5-8 pF je Leitung, USB-FS (12 Mbit/s) erlaubt bis 75 pF. VRWM 5 V, VBUS max 5,25 V (pruefen Leckstrom). Peak 4 A (8/20 us) vs 5 A USBLC6. Preis 0,085 vs 0,15 USD. | gleich (SOT-23-6) | **Tauschen**, vorher Datenblatt (Pinout, Cj, VRWM) lesen (-1 Ext) |
| D1-D5 BAT42W | C22466362 **Pref** | keine Aenderung | 22k | Basic-Schottky gibt es nur als Leistungstypen: SS14/SS34/SS54/SS210 (SMA), B5819W SL C8598 (SOD-123), 1N5819WS (SOD-323) = ca. 100 pF, hoher Leckstrom. BAT54-Familie ist Ext/Pref (BAT54C C37704 Pref SOT-23 Dual, 421k). 1N4148W (C81598, Basic, ca. 4 pF) hat Vf ca. 0,8 V statt 0,4 V: Bruecke = 2 Dioden -> +0,8 V Verlust bei 10 mA, bei TX-Strom 73 mA ca. +0,9 V auf dem Bus-Low-Pegel. BAT42W ist schon Preferred = keine Gebuehr. | - | **Nicht tauschen** (kein Gewinn, B5819W/1N4148W verschlechtern Bus) |
| Q1 BC817-40 | C20069155 Pref | keine Aenderung | 132k | Preferred (live: `expand`+`preferredComponentFlag=true`). Alternative Basic MMBT3904 C20526 (hFE 100-300, 200 mA) waere nur Typenwechsel ohne Nutzen. | - | **Nicht tauschen** |
| L1,L2 4u7 1210 | C98021 Ext | **C1017** GZ2012D601TF Ferrit 600 Ohm@100 MHz, 500 mA, 300 mOhm, 0805, **Basic** (alt.: C1015 100 Ohm@100 MHz, 800 mA, 150 mOhm Basic) | 681k | Pref-Induktivitaeten 4,7 uH (C1034 0603, C1049 1206 "25 mA, 650 mOhm") sind viel zu schwach: Strom durch L1/L2 = TX-Last 73 mA + Versorgung. Ferrit-Perle ersetzt die 4,7 uH nur als HF-Filter (4,7 uH = 295 Ohm @10 MHz; 600-Ohm-Perle ca. 100-300 Ohm @10-30 MHz, bei 9600 Baud nur DCR 0,3 Ohm, Spannungsabfall bei 73 mA = 22 mV). Einschaltstrom in C12/C14 (R6 m7): DCR 0,3 statt 0,22 Ohm, praktisch gleich. Wirkung auf Burst/ESD-Festigkeit ohne Messung unklar. 500 mA Nennstrom < PTC-Trip 1 A (L1/L2 jetzt 1 A). | **0805 statt 1210** (neue Pads, Neuroute des Bus-Eingangs) | **Optional** (-1 Ext); empfohlen nur, wenn EMV-Dämpfung nicht kritisch ist |
| L3 4u7 5x5 | C43183 Ext (nur 1,9k Lager) | kein Basic/Pref | - | Keine Basic/Pref-Leistungsdrossel (Basic nur 10 uH 0603/0805-Multilayer C1035/C1046 mit mA-Strom). Lager-Risiko: 1,9k. Ausweg siehe Zeile U2 (78L05 ohne Spule). | - | **Nicht tauschen** (ausser U2-Umbau) |
| U2 JW5017S | C371172 Ext | **Variante A: 78L05G-AB3-R (UTC) C71136, SOT-89, 5 V 100 mA, Vin max 30 V, Basic** (statt Buck). **Variante B: XL1509-5.0E1 C61063 Basic SOIC-8** | 333k / 445k | Variante A ersetzt U2, L3, R12, R15, R16 (EN-Pullup) und C9 (Bootstrap) durch 1 Linearregler: **-3 Ext (U2, L3, R15)**. Last 5 V ca. 10-15 mA (LD1 2,5 + OC1-LED 7 + R9/R11 je 1 + U1 0,5 mA). Verlust bei 15 V Bus (nach D7 ca. 14,3 V): (14,3-5)*(15+5 mA Iq) = 0,19 W; bei 24 V: (23,3-5)*20 mA = 0,37 W, SOT-89 auf Pour ca. +40 K (unkritisch). Dropout ca. 2 V -> Bus >= 7,5 V noetig, Abfall bei Low-Bits traegt C12/C14 (15 mA / 2000 uF = 7,5 V/s). **Busstrom steigt** von ca. 5 mA (Buck, 5V*15mA/15V/0,85) auf ca. 20 mA; Strombudget des EMS-Master nicht bekannt, vorher pruefen. Ausgang 5 V +-4 % = 4,8..5,2 V (statt 4,98): OC1-LED 6,5..7,8 mA, 6N136 VCC ok. Stabilitaet: 78L05 bipolar, 22 uF Keramik am Ausgang normalerweise ok (pruefen, ggf. C11 verkleinern). Plus: kein 150-kHz-Schaltrauschen auf dem Bus. Variante B (XL1509): L3 bleibt Extended (68-100 uH noetig) -> nur -1/-2, mehr Aufwand (Freilaufdiode, Elko), nicht empfohlen. L78M05ABDT-TR C58069 (Basic, 500 mA, DPAK) als groesserer Ersatz. Pinout 78L05 SOT-89 (1=OUT, 2=GND, 3=IN ?) UTC-Datenblatt pruefen. | **neues Layout** (SOT-89 statt SOT-23-6 + 5x5-Spule; Buck-Bereich neu) | **Optional, groesster Hebel** (-3 Ext statt -1 beim reinen R15-Tausch, also +2 zusaetzlich) |
| OC1 6N137 | C92651 Ext | **C109227 LTV-817S-TA1-C (Lite-On, SMD-4P, 5 kV rms, CTR-Rang C 200-400 %), Basic** (alt.: C115450 LTV-217-B-G SOP-4 Basic, 3,75 kV) | 307k | Logik: LED an -> Kollektor low, gleich wie 6N137 (invertierend). Keine VCC/VE-Pins mehr (VE-Netz entfaellt). LED-Strom bleibt (R10 470R: 6,7..7,2 mA). Kollektorstrom-Reserve 200 % * 6,7 = 13 mA gegen Last 1 mA (R13) + LD3 <= 4,8 mA: saettigt, VCE(sat) ca. 0,15 V < VIL 0,82 V. **Geschwindigkeit ist der Haken:** 817-Familie tr/tf typ. 4/3 us, max 18 us bei RL = 100 Ohm; mit R13 3k3 steigt toff auf geschaetzt 40-60 us (Kurve "Ansprechzeit vs. RL", pruefen). Bitzeit 104 us -> Pulsweitenverzerrung bis 40 %: zu viel. Abhilfe: **R13 -> 1k (C17513 Basic)**: RL 1k -> toff ca. 15-30 us (PWD 15-30 %), Strom 3,3 mA + LD3 4,8 mA = 8,1 mA < 13 mA ok. 6N137 hatte 75 ns, Reserve war riesig, hier nicht. | **neuer Footprint SMD-4P** (Reihenabstand ca. 10 mm, Pins 2,54 mm Raster liegen in der Mitte der 8 Pads: 817-Pin1/2 auf SO8-Pad 2/3, Pin 4/3 auf Pad 7/6), Barriere-Slot bleibt; Verdrahtung VCC/VE/Pins 1,4 entfaellt | **Optional**, nur nach Bench-Test (-1 Ext) |
| OC2 6N136 | C336082 Ext | **C109227 LTV-817S-TA1-C Basic** (wie OC1, dann OC1/OC2 ein Typ) | 307k | Min-CTR 19 % (6N136) -> 200 % (817-C): Reserve steigt von 1,76x auf >= 19x. IF mit R14 150R: 8,7..13 mA bleibt zulaessig (IF max 50 mA), aber tiefe Saettigung verlaengert toff: **R14 -> 330R (C17630, Basic vorhanden)**: IF = (3,234-1,4-0,33)/330 = 4,6 mA worst, 6,2 mA typ -> IC >= 9 mA gegen 0,94 mA benoetigt (**9,8x**), GPIO17-Last sinkt von 12 auf ca. 6 mA. Ausgang: R11 4k7 gegen 5 V + C5 4,7 nF: steigende Flanke bis 0,65 V = 0,14 * 22 us = 3 us + toff (Speicherzeit) ca. 10-25 us: vergleichbar mit der bisherigen 6N136-Rechnung (R6 m4: 10..27 us). VCC-Pin (5 V) und VB entfallen. | wie OC1 | **Optional**, nur nach Bench-Test (zusammen mit OC1 -2 Ext) |
| F1,F2 PTC 0805 24 V | C910822 Ext | kein Basic/Pref (API: `PTC`, `Resettable Fuses`, `BSMD`, `SMD1206` Basic/Pref: nur Widerstaende/Kondensatoren; alle JDT/BHFUSE-PTC sind Ext) | - | Ersatz durch 0 Ohm (C17477) wuerde den Busschutz entfernen: nicht empfohlen. | - | **Nicht tauschen** |
| F3 PTC 1206 1,1 A | C269119 Ext | **C17888 0 Ohm 1206 Basic** (nur wenn Schutz entbehrlich) | 1,7M | USB-Host begrenzt selbst (500/900 mA); PTC-Abfall 0,04..0,21 Ohm entfaellt -> mehr LDO-Reserve (+0,07 V bei 0,35 A). Verlust: kein Schutz vor Platinenfehler / Netzteil mit mehreren A (R3-Entscheidung m2/m9 wollte genau diesen Schutz). ESP32-DevKits haben oft keine PTC. | Pads 1206 (Ptc1206Footprint 1,19x1,73 bei +-1,445) passen fuer 0-Ohm-1206 | **Optional / eher Nein** (Sicherheit) |
| J2 USB-C 16P | C165948 Ext | kein Basic/Pref (`USB Connectors`, `TYPE-C` Basic/Pref: 0 Treffer) | 405k | - | - | **Nicht tauschen** |
| P1 2-pol 5,08 | C441236 Ext | siehe Abschnitt 5 (SMD-Klemmen alle Ext) | 21k | - | - | **Nicht tauschen** (Fee nur per Hand-Loeten sparbar) |
| P2 1x4 2,54 | C32713270 Ext | kein Basic/Pref (`Pin Headers`: 0) | 107k | - | - | Hand-Loeten (Abschnitt 6) |
| R2-R4 68R 2010 | C53284030 Ext | kein Basic/Pref (Basic nur 0402/0603/0805/1206; Pref 68R nur 0603/0805: C27592/C17802, 100-125 mW) | - | Leistung: Q1 an = 15 V / 204 Ohm = 73 mA -> 15 V*73 mA = 1,1 W gesamt, je Widerstand 0,36 W (2010: 0,75 W). Reine Basic-Loesung: 10 x 20R 1206 (C17955, 250 mW) in Reihe = 200 Ohm, je 0,11 W (44 %): 10 Teile, ca. 80 mm2 statt 37 mm2, Neuroute; auf 4 x 51R/ 1206-Typen gibt es keine passenden Basic-Werte (nur 10/20/22/100/120/300 Ohm). | stark (10 Teile) | **Nicht tauschen** (Layout-Aufwand > 3 USD) |
| C12,C14 1000u 25 V SMD | C49256851 Ext | kein Basic/Pref (`Aluminum Electrolytic Capacitors` Basic/Pref: 0 Treffer; Basic nur Keramik/Tantal) | 39k | Keramik-Ersatz fuer 2000 uF bei 25 V ist nicht darstellbar. | - | **Nicht tauschen**; Hand-Loeten moeglich (Abschnitt 6) |
| U1 LM393DR2G, U5 AMS1117, C29, LEDs, SW, D6, D7, R/C | alle Basic | - | - | - | - | unveraendert |

### Basic-Typen zusammenlegen
In der Economic-Bestueckung haben Basic-Teile keine Typ-Gebuehr; weniger verschiedene Basic-Werte sparen nichts (nur Feeder-Aufwand bei JLC).
Keine Zusammenlegung empfohlen. Nach den Empfehlungen gilt: neu 100 pF (C1790), 27 kOhm (C17593); entfallen 68 pF (C107120, Ext), 6k8 (C17772), 1k3 (C17384, Ext).
Moegliche harmlose Zusammenlegungen, falls gewuenscht: R17 1k2 -> 1k (C17513, LD1 3,0 statt 2,5 mA); R5 390R/R10 470R besser nicht anfassen (Comparator-Referenz, OC1-Strom).

## 4. Summen

| Szenario | Ext-Typen (ohne U3) | Einsparung je Bestellung | Inhalt |
|---|---|---|---|
| Ist | 15 | - | |
| **A "sicher"** (nur Wertetausch / pin-kompatibel) | **12** | **ca. 9 USD** | C1 -> C1790; R12/R15 -> 27k/5k1; U4 -> SRV05-4 Pref (Datenblatt pruefen) |
| B (A + moderate Layoutaenderung) | 9 | ca. 18 USD | zusaetzlich L1/L2 -> Ferrit C1017 (-1), OC1/OC2 -> LTV-817S (-2) |
| C (B + Linearregler statt Buck) | 7 | ca. 24 USD | zusaetzlich U2 und L3 entfallen (+2; R15 steckt schon in A) |
| C + F3 -> 0 Ohm | 6 | ca. 27 USD | Rest: J2, P1, P2, C12/C14, F1/F2, R2-R4 |
| C + Hand-Loeten P1, P2, C12/C14 (Abschnitt 6) | 3 (J2, F1/F2, R2-R4) | ca. 36 USD | |

Dazu kommen geringere Stueckkosten (z. B. LTV-817S 0,075 USD statt 0,36 + 0,54 USD der beiden Optos).

### Risiken
1. **Optokoppler-Tausch (B):** Hoechstes Risiko. 817-Familie ist ein langsamer Phototransistor-Koppler (us statt ns); Bitzeit 104 us. Pulsweitenverzerrung ist nur abgeschaetzt (Datenblatt nicht abrufbar). Vorher Bench-Test der RX-/TX-Kette (Oszilloskop an MCU_RX, MCU_TX, N$15, Q1-Kollektor) mit bestueckten Mustern. Die V1-Wahl 6N137/6N136 war bewusst; der Tausch muss gemessen werden. Neuer Footprint und neues Routing an der Isolationsbarriere (Creepage >= 6 mm erneut mit `check_isolation.py` pruefen).
2. **Linearregler (C):** hoehere Busstromaufnahme (ca. +15 mA), 5 V +-4 %, Verlustleistung bis 0,37 W bei 24 V Bus, Dropout 2 V (Bus >= 7,5 V). Buck-Bereich komplett neu (Layout, Router). Strombudget des Heizungs-Masters pruefen, sonst Variante A (nur R15-Tausch) behalten.
3. **U4 SRV05-4:** Clone-Hersteller (R+O/hongjiacheng); Pinbelegung, Cj und Leckstrom bei 5,25 V im Datenblatt gegenpruefen; ESD-Wirkung (4 A) etwas geringer als USBLC6.
4. **L1/L2 Ferrit:** Filterwirkung ohne Messung nicht aequivalent; nur sinnvoll, wenn keine EMV-Pruefung geplant.
5. **F3 -> 0 Ohm:** Schutzfunktion entfaellt.
6. Alle Aussagen "Basic/Pref/Economic" gelten am 2026-11-26; Klassen aendern sich (siehe `JLCPCB_PARTS.md`). Vor der Bestellung `python3 scripts/jlc_economic.py --live` und API-Pruefung wiederholen.

## 5. P1 als SMD-Klemme (nur Empfehlung, keine Designaenderung)

Aktuell: C441236 KF2EDGRC-5.08-2P, steckbare THT-Leiste 5,08 mm (Wave Soldering, Economic ok, Ext). Suche (API, Filter Basic/Pref: **nichts**; alle SMD-2-Pol-Klemmen sind Extended, also **keine Gebuehrersparnis**):

| LCSC | Teil | Raster | Lager | Preis | PCBA Type (live) | Bemerkung |
|---|---|---|---|---|---|---|
| C2765058 | WAGO 2061-602/998-404 (Federklemme SMD, Drueckertaste) | 6,0 mm | 1636 | 1,25 USD | Economic and Standard | einzige robuste SMD-Variante, die Economic erlaubt; Leiterbereich/Spannung laut WAGO-Datenblatt pruefen (WAGO-Serie 206x typ. 250 V, **pruefen**) |
| C2765060 | WAGO 2059-302/998-403 | 3,0 mm | 7376 | 0,44 USD | Economic and Standard | fuer duenne Leiter (ca. 0,25-0,5 mm2, **pruefen**), fuer Heizungs-Buskabel eher zu klein |
| C19108923 | WECO 110-M-211-SMD/02-MAG (steckbar, Schraube) | 3,5 mm | 784 | 0,83 USD | Economic and Standard | niedriger Lagerbestand |
| C5149246 | Phoenix 1778764 | 2,5 mm | 372 | 1,49 USD | Economic and Standard | zu klein |
| C2765055 | WAGO 2060-452/998-404 | 4,0 mm | 3071 | 0,44 USD | **Standard Only** | blockiert Economic |
| C5118805 | JILN JL212R-SMT-50002BP1 (Feder) | 5,0 mm | 1776 | 0,51 USD | **Standard Only** | blockiert Economic |

Einschaetzung: SMD-Klemmen haben nur die Laschenhaftung auf dem Pad (Schraub-/Zugkraefte); der Schraubklemmen-Bus-Anschluss einer Heizung ist mechanisch beansprucht (Abziehen,
Kabelzug). Empfehlung: **bei THT bleiben** (Fee-Ersparnis gibt es ohnehin nicht). Falls doch: C2765058 (6 mm) mit Rasterwechsel 5,08 -> 6,0 mm, Klemme ragt je nach Typ weiter nach innen,
Gehaeuse-Oeffnung/Hoehe (ENCLOSURE.md: P1 am linken Rand, Austritt nach aussen) neu vermessen; Drahteinfuehrung parallel zur Platine (Drueckertaste oben, ca. 10 mm Bauhoehe, **STEP pruefen**).

## 6. Reichelt-Alternativen fuer Teile, die Extended bleiben (Hand-Loeten statt JLC)

Idee: Teil in JLC-BOM/CPL weglassen (DNP) und selbst loeten: spart ca. 3 USD (ca. 2,6 EUR, Kurs ~0,87 angenommen) je Typ und das Teil. Preise laut Reichelt-Suche, Einzelstueck.

| Ref | JLC (Ext) | Reichelt-Artikel (Art.-Nr. = Bezeichnung) | Preis | Hand-Loeten | Bewertung / Kostenvergleich |
|---|---|---|---|---|---|
| P2 1x4 | C32713270 (3 USD + 0,03) | **SL 1X36G 2,54** (36pol Stiftleiste RM2,54, abbrechbar) | 0,30 EUR | trivial (THT) | **sinnvoll**: spart ca. 2,6 EUR, Leiste reicht fuer ca. 9 Stueck |
| P1 2-pol 5,08 | C441236 (3 USD + 0,06) | **AKL 230-02** (Wannenstecker, 2-pol RM5,08, 0,37 EUR) + Gegenstueck **AKL 249-02** (Klemmensystem 2-pol RM5,08, 0,78 EUR) | 0,37 EUR | leicht (THT) | **sinnvoll**, aber Bohrung/Pad (1,8/2,5 mm Kefa-Teil) gegen AKL-230-Datenblatt vergleichen; Gegenstecker kaufst du ohnehin separat (Plug nicht in der BOM) |
| C12,C14 | C49256851 (3 USD fuer beide + 2x ca. 0,2) | **ECC ZR250821MJA** Elko SMD 820 uF/25 V Low ESR 10x10 mm | 0,50 EUR je | leicht (2 grosse Pads, Heissluft/Kolben) | **sinnvoll**: 2 x 820 = 1640 uF statt 2000 uF (-18 %); Footprint D10 passt (10x10, 10,2 mm hoch). Alternativ 560 uF/25 V (VF 560/25 P-G, 0,70 EUR). Kosten 1,00 EUR statt ca. 2,6+0,4 EUR |
| F3 | C269119 (3 USD + 0,1) | **SMD1206P110TFT** (PTC SMD 1206, 8 V, 1,1 A) | 0,14 EUR | leicht (1206) | **sinnvoll**: gleiche Serie/Daten wie C269119, gleicher Footprint; spart ca. 2,6 EUR |
| F1,F2 | C910822 (3 USD + 2 x 0,02) | **SMD1206P050TF24** (1206, 24 V, 0,5 A) | 0,14 EUR je | leicht | **bedingt**: Reichelt hat 24 V/0,5 A nur in 1206 (0805: nur 24 V/0,1 A oder 6 V/0,5 A) -> Footprint-Wechsel 0805 -> 1206 noetig (auf dem Bus-Eingang). |
| OC1 | C92651 (3 USD + 0,36) | **6N137S EVL** (HIGH SPEED 10 MBit/s, PDIP-8-SMD) 0,72 EUR; alt. **EL2601S(TA)** (5 kV, 10 MBd, SO-8) 0,99 EUR | 0,72 EUR | leicht-mittel (SOP-8, Raster 2,54 mm, Gull-Wing, 8 Pins) | **moeglich**: ca. 2,3 EUR gespart; Footprint (SO8-GW300) vor Kauf gegen Reichelt-Zeichnung pruefen |
| OC2 | C336082 (3 USD + 0,54) | **EL4502S(TA)-V** (5 kV, 1 MBd, SO-8, 6N136-kompatibel) | 0,91 EUR | leicht-mittel | **moeglich**: ca. 2,2 EUR gespart; Pinout 6N136 (2 A, 3 K, 5 GND, 6 Vo, 7 Vb, 8 Vcc) und Gehaeuse (Wide-Gull-Wing?) im Everlight-Datenblatt pruefen |
| U4 | C7519 (3 USD + 0,15) | **USBLC6-2SC6** (TVS-Array, SOT-23-6) | 0,14 EUR | leicht (SOT-23-6) | nicht noetig, wenn SRV05-4 (Pref) getauscht wird |
| J2 USB-C | C165948 | keine 16-polige SMD-USB-C-Buchse bei Reichelt gefunden (nur Keystone-Module, Adapter, Typ-B) | - | schwer (16 Kontakte 0,5 mm, Schirmbeine) | **JLC behalten** |
| L1,L2 | C98021 | kein 4,7-uH-Leistungs-/Bus-Induktor gefunden (Suche: "SMD-Induktivitaet 4,7", L-1206F 4,7u (Ferrit, 0,30 EUR, Strom unklar)) | - | - | JLC behalten oder Ferrit-Perle C1017 |
| L3 | C43183 | keine 4,7-uH-5x5-Leistungsdrossel (nur L-PISA2812 10 u 0,99 EUR) | - | - | JLC behalten oder Linearregler (Abschnitt 3) |
| U2 JW5017S | C371172 | kein JW5017/XL1509/TPS5430; als Linearregler **L78L05ABU STM** (SOT-89, 0,14 EUR) / TS 78L05 ACY (0,20 EUR) | 0,14 EUR | leicht | nur im Linearregler-Szenario, dort ist die Basic-Variante C71136 gebuehrenfrei |
| R2-R4 | C53284030 | keine 68R 2010 bei Reichelt (nur 2010 100 mOhm) | - | - | JLC behalten |

Kostenvergleich je Bestellung (nur Teile, die sinnvoll Hand-Loeten sind): P1 + P2 + C12/C14 + F3 = 4 Ext-Typen = ca. 12 USD Gebuehr + ca. 1,2 USD JLC-Teilepreis
gegen ca. 3,4 EUR Reichelt (0,37+0,78+0,30+1,00+0,14 plus Gegenstecker ohnehin) -> **ca. 9-10 EUR gespart**, Mehraufwand 9 Loetstellen-Gruppen. Mit OC1/OC2 (je 8 Pins) zusaetzlich ca. 4,5 EUR.
Schwierigkeit: SOT-23/SOIC einfach; QFN/Feinraster gibt es hier nicht ausser J2 (bleibt bei JLC). Hand-geloetete Teile gehoeren dann in `fab/EMSinterface_V2.0-HANDSOLDER.csv` und werden aus BOM/CPL genommen (so wie U3).

## 7. Empfehlung (Reihenfolge)

1. **Jetzt** (Szenario A, 15 -> 12 Ext, ca. 9 USD): C1 -> C1790 (100 pF C0G), R12 -> 27k C17593 / R15 -> 5k1 C27834, U4 -> SRV05-4 C7420376 (nach Datenblattpruefung). Alle drei mit gleichem Footprint; nur LCSC-Nummer/Wert in `src/*.tsx`, BOM, JLCPCB_PARTS.md anpassen; `scripts/jlc_economic.py` Tabelle ergaenzen (C1790, C17593, C7420376 sind "Economic and Standard").
2. Zusaetzlich per Hand-Loeten (kein Redesign): P2, P1, C12/C14 (820 uF), F3 -> -4 Ext.
3. Erst nach Bench-Test / Strombudget-Pruefung erwaegen: Optokoppler LTV-817S (-2), Linearregler 78L05 (+2 gegenueber Variante A), Ferrit-Perlen statt L1/L2 (-1).
4. Nicht anfassen: BAT42W (Pref), BC817-40 (Pref), J2, R2-R4, F1/F2 (bzw. nur mit 1206-Footprint von Reichelt), C4 1n5 (Pref).

Reproduktion der API-Abfragen: Muster `curl -s -X POST <API> -H 'Content-Type: application/json' -d '{"keyword":"78L05","currentPage":1,"pageSize":50,"componentLibraryType":"base"}'`.
