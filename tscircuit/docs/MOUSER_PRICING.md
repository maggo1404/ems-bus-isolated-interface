# Mouser-Preisvergleich: Nicht-Basic-Teile fuer 5 Platinen (erstes Design, WROOM-Version)

Stand: 2026-11-28. Nur Recherche; keine Design- oder Fab-Datei wurde veraendert.

## 0. Wichtig: Was verifiziert ist und was nicht

* **Mouser ist von hier aus nicht direkt erreichbar.** `www.mouser.de` und `www.mouser.com` (Suche `/c/?q=`, `/ProductDetail/...`) liefern per curl
  "Access to this page has been denied" (Bot-Schutz), der WebFetch-Weg scheitert an DNS (`www.mouser.de` nicht in der erlaubten Netzliste),
  `api.mouser.com`, Octopart, Findchips, DigiKey sind gesperrt. Mouser-API braucht ausserdem einen Key.
* Einziger Weg: **Websuche-Snippets von Mouser-Seiten** (gecachte Momentaufnahmen, undatiert, teils Monate alt). Diese Werte sind unten
  mit **[V]** (aus Mouser-Snippet, exakte oder explizit genannte Alternative) markiert. Mouser-Bestellnummern habe ich nur genannt, wo sie im Snippet standen.
* Alle mit **[S]** markierten Preise sind **Schaetzungen** (typische Mouser-Staffelpreise fuer diese Teileklasse, nicht abgerufen). Gesamtsumme
  daher als Bereich/Richtwert verstehen (ca. +-20 %). Vor der Bestellung im Mouser-Warenkorb (BOM-Upload, "Kosten pruefen") gegenpruefen.
* Waehrung/MwSt: mouser.de zeigt Preise in EUR **netto (ohne MwSt)**; Privatkunden zahlen im Warenkorb 19 % MwSt dazu (aus dem Gedaechtnis, **nicht verifiziert**).
  Versand nach DE: kostenlos ab ca. 50 EUR Warenwert, darunter Pauschale (ca. 8-12 EUR; **nicht verifiziert**). Mindestbestellwert: keiner; Mindestmengen/Vielfache
  je Teil im Warenkorb (Gurt-/Reel-Teile haben eigene Vielfache, z. B. 3000, wir kaufen Cut-Tape ab 1 Stk).
* JLC-Preise: JLC-API `selectSmtComponentList` am 2026-11-28 live abgefragt (Stufe 1 = unterste Staffel). Reichelt: Einzelpreise aus `docs/BASIC_PARTS_RESEARCH.md` Abschnitt 6 (2026-11-26, brutto).

## 1. Teileliste und Mengen (5 Platinen)

Mengenregel: Menge je Platine x 5. Kleine Passivteile mit Zuschlag (+5 bzw. aufgerundet auf 10), weil Cut-Tape-Preis fast gleich und Verlieren/Fehler beim Handloeten.
Klasse: Ext = Extended (3 USD JLC-Gebuehr je Typ), Pref = Preferred-Extended (gebuehrenfrei bei JLC), U3 = nur Handloeten.

| Ref | Teil (JLC, LCSC) | Klasse | pro Platine | Bedarf x5 | Bestellmenge |
|---|---|---|---|---|---|
| U3 | ESP32-S3-WROOM-1-N16R8 (C2913202) | Ext, "Standard Only", Handloeten | 1 | 5 | 5 |
| C1 | 68 pF C0G 0805 CC0805JRNPO9BN680 (C107120) | Ext | 1 | 5 | 10 |
| C12, C14 | 1000 uF 25 V Elko SMD 10x12 JVJ25V1000M10X12 (C49256851) | Ext | 2 | 10 | 10 |
| F1, F2 | PTC 0805 0,5 A 24 V BSMD0805-050-24V (C910822) | Ext | 2 | 10 | 10 |
| F3 | PTC 1206 1,1 A 8 V SMD1206B110TFT (C269119) | Ext | 1 | 5 | 5 |
| J2 | USB-C 16P TYPE-C-31-M-12 (C165948) | Ext | 1 | 5 | 5 |
| L1, L2 | 4,7 uH 1210 LQH32PN4R7NN0L (C98021) | Ext | 2 | 10 | 10 |
| L3 | 4,7 uH 5x5x2 SWPA5020S4R7MT (C43183) | Ext | 1 | 5 | 5 |
| OC1 | 6N137S-TA1-L (C92651) | Ext | 1 | 5 | 5 |
| OC2 | 6N136S-TA1-L (C336082) | Ext | 1 | 5 | 5 |
| P1 | 2-pol 5,08 mm KF2EDGRC-5.08-2P (C441236) | Ext | 1 | 5 | 5 (+5 Gegenstecker, nicht in BOM) |
| P2 | 1x4 Stiftleiste 2,54 mm (C32713270) | Ext | 1 | 5 | 5 |
| R2-R4 | 68R 1 % 2010 CL2010FN68RB (C53284030) | Ext | 3 | 15 | 20 |
| R15 | 1k3 1 % 0805 (C17384) | Ext | 1 | 5 | 10 |
| U2 | JW5017S Buck SOT-23-6 (C371172) | Ext | 1 | 5 | 5 |
| U4 | USBLC6-2SC6 (C7519) | Ext | 1 | 5 | 5 |
| C4 | 1n5 X7R 0805 (C1717) | Pref | 1 | 5 | 10 |
| D1-D5 | BAT42W SOD-123 (C22466362) | Pref | 5 | 25 | 30 |
| Q1 | BC817-40 SOT-23 (C20069155) | Pref | 1 | 5 | 5 |

Ext-Typen (gebuehrenpflichtig bei JLC, ohne U3): **15** (C107120, C49256851, C910822, C269119, C165948, C98021, C43183, C92651, C336082, C441236, C32713270, C53284030, C17384, C371172, C7519).

## 2. Mouser-Tabelle (EUR netto, mouser.de, Stand der Snippets)

[V] = aus Mouser-Snippet, [S] = Schaetzung (Teil bei Mouser nicht verifiziert gefunden), "Alt" = nicht dieselbe MPN, Ersatz vorgeschlagen.

| Ref | Mouser-Teil / Mouser-Nr. | Status | Stueckpreis (Menge) | Summe | Lager / Hinweis |
|---|---|---|---|---|---|
| U3 | Espressif ESP32-S3-WROOM-1-N16R8 (selbe MPN) | [V] | 5,80 EUR bei 1 Stk; Staffel ab 5 nicht bekannt (US: 6,72 USD bei 1, bis 4,30 USD bei Top-Staffel) | 29,00 (Obergrenze) | DE-Lager ca. 61k, Lieferzeit Nachschub 18 Wochen |
| C1 | 68 pF C0G 0805 50 V (z. B. Yageo CC0805JRNPO9BN680 / KEMET C0805C680J5GACTU) | [S] | ca. 0,12 (10) | 1,20 | Standardteil, nicht abgerufen |
| C12, C14 | Alt: Panasonic EEV-FK1E102V (1000 uF 25 V, SMD 10x10,2 mm, Anti-Vibe) | [V] 2,24 USD bei 1 Stk, Lager ca. 2,7k (US) | ca. 2,05 (1) | 20,50 (Obergrenze) | JIERR JVJ25V1000M10X12 nicht bei Mouser gefunden. Panasonic EEE-FK1E102AQ (Standard-FK): ca. 1,62/1,13/0,84 USD gestaffelt, aber 0 Lager (neu erwartet 18.01.2027). Pads/Hoehe (L12 vs 10,2) gegen Footprint pruefen. Preis fuer 10 Stk vermutlich ca. 1,6-1,8 EUR -> ca. 17 EUR |
| F1, F2 | Alt: 24 V / 0,5 A PTC (BSMD0805-050-24V nicht bei Mouser; 0805 mit 24 V gibt es dort kaum, ggf. 1206 Littelfuse/Bourns -> Footprint-Wechsel) | [S] | ca. 0,40 (10) | 4,00 | nicht verifiziert |
| F3 | SMD1206B110TFT (Yageo SMD1206-Serie, Datenblatt auf Mouser, Einzelteilseite nicht gefunden); Alt: 1206L110THYR (Littelfuse) | [S] | ca. 0,35 (5) | 1,75 | Footprint gleich (1206) |
| J2 | Alt: GCT USB4105-GF-A (16 Kontakte, SMD+THT-Beine, USB 2.0), Mouser-Nr. 640-USB4105-GF-A | [V] | 0,80 USD (1) ca. 0,74 EUR | 3,70 | Lager ca. 381k. **TYPE-C-31-M-12 nicht bei Mouser gefunden; GCT-Teil hat anderen Footprint/Beinlage -> Footprint-Aenderung (`lib/usbc16.tsx`) noetig** |
| L1, L2 | Murata LQH32PN4R7NN0L (Mouser-Seite im Snippet nicht auffindbar) | [S] | ca. 0,45 (10) | 4,50 | Murata-Serie bei Mouser ueblich gelistet; nicht verifiziert |
| L3 | Alt: Pulse BWVS005050204R7M00 (4,7 uH, 5x5x2 mm, geschirmt, 2,2 A, 60 mOhm) | [V] Lager ca. 9,7k, Preis nicht im Snippet | ca. 1,00 (5) | 5,00 | SWPA5020S4R7MT nicht gefunden; Bourns SRN5020-4R7M (2 A, halbgeschirmt) ist EOL-markiert. Footprint: ohnehin laut FOOTPRINT_CHECK von der Lib abweichend, Pads pruefen |
| OC1 | Alt: Lite-On 6N137S-TA1 (Mouser-Nr. 859-6N137STA1), SMD-8, 10 MBd, 2,5 kVrms | [V] ca. 0,82 USD (1) ca. 0,75 EUR | 0,75 (5) | 3,75 | Der Zusatz "-L" (bleifrei) nicht bei Mouser gelistet; elektrisch/mechanisch gleich. Isolation 2,5 kV laut Snippet (JLC-Doc sagt 5 kV: Datenblatt pruefen) |
| OC2 | Lite-On 6N136S-TA1 (Mouser-Nr. 859-6N136STA1), SMD-8, 5 kVrms | [V] 0,85 USD (1) ca. 0,78 EUR | 0,78 (5) | 3,90 | Lager ca. 6k, Packungsgroesse 1000 (Cut-Tape ab 1) |
| P1 | KF2EDGRC-5.08-2P nicht bei Mouser; Alt: gleicher Raster 5,08 mm 2-pol Stiftleiste (Wuerth WR-TBL / Phoenix MSTBA 2,5/2-G-5,08 = urspruenglich gewuenschtes Teil) | [S] | ca. 1,00 (5) | 5,00 | plus Gegenstecker (Phoenix MSTB 2,5/2-STF-5,08 o. ae., ca. 1,2 EUR [S], nicht eingerechnet) |
| P2 | 1x4 Stiftleiste 2,54 mm gerade (z. B. Wuerth 61300411121 / Samtec TSW-104) | [S] | ca. 0,40 (5) | 2,00 | |
| R2-R4 | 68R 1 % 2010 (Vishay CRCW201068R0FKEF, 0,75 W; Familie im Snippet bestaetigt, Einzelteil nicht) | [S] | ca. 0,10 (20) | 2,00 | |
| R15 | 1k3 1 % 0805 (Yageo RC0805FR-071K3L) | [S] | ca. 0,10 (10) | 1,00 | |
| U2 | JW5017S **nicht bei Mouser**. Alt (kein Drop-in, nur Idee): TI TPS54202DDCR (SOT-23-6, 4,5-28 V, 2 A) | [S] ca. 1,30 | 1,30 (5) | 6,50 | Feedback-Teiler (R12/R15) muesste neu gerechnet werden (anderes Vref), Pinout vorher pruefen. Sinnvoller: JW5017S bei LCSC/JLC |
| U4 | STMicroelectronics USBLC6-2SC6 (selbe MPN) | [V] 0,48 EUR (1), DE-Lager ca. 108k | 0,48 (5), Staffel niedriger | 2,40 | Mouser-Link: mouser.de/en/ProductDetail/STMicroelectronics/USBLC6-2SC6 |
| C4 | 1n5 X7R 0805 50 V (z. B. Yageo CC0805KRX7R9BB152) | [S] | ca. 0,10 (10) | 1,00 | |
| D1-D5 | Diodes Inc. BAT42W-7-F, SOD-123 (Mouser-Nr. 621-BAT42W-F; **Original-Diodes-Teil statt hongjiacheng-BAT42W**) | [V] Cut-Tape 0,323 (1) / 0,223 (10) / 0,103 (100) / 0,079 (1000), Reel 0,067 (3000); Lager 24k | 0,223 (30) | 6,69 | Staffel 30 Stk. vermutlich bei 0,223 (Stufe 10), evtl. etwas guenstiger |
| Q1 | Nexperia BC817-40,215 (SOT-23) | [V] 0,14 USD (1) ca. 0,13 EUR | 0,13 (5) | 0,65 | Lager ca. 764k; Mindestmenge 1 |
| | **Summe Teile (netto)** | | | **ca. 104,5 EUR** | davon ESP32 29,00, Elkos 20,50 (Obergrenze) |
| | Summe ohne U3 | | | ca. 75,5 EUR | |

## 3. Gesamtkosten Mouser fuer 5 Platinen (Richtwert)

| Posten | EUR |
|---|---|
| Teile netto (19 Positionen inkl. ESP32) | ca. 104,5 (realistisch 95-105; Elkos/ESP32 mit Mengenrabatt eher niedriger) |
| Versand DE | 0 (Warenwert > ca. 50 EUR, Schwelle **nicht verifiziert**) |
| MwSt 19 % | ca. 19,9 |
| **Gesamt brutto** | **ca. 124,4 EUR** (ohne ESP32: ca. 75,5 netto / 89,9 brutto) |

Nicht eingerechnet: Gegenstecker zu P1, ggf. Kleinteile-Zuschlaege, ggf. Zoll/Gebuehren (EU, keine).

## 4. Vergleich

Wechselkurs 0,87 EUR/USD (Annahme aus BASIC_PARTS_RESEARCH.md). JLC-Preise live (API 2026-11-28, Stufe 1, 5 Platinen).

| Variante | Teile | Gebuehr / Versand | Summe |
|---|---|---|---|
| **(a) JLC bestueckt** die 18 Ext/Pref-Zeilen (ohne U3) | ca. 13,3 USD = 11,6 EUR | 15 Ext-Typen x 3 USD = 45 USD = 39,2 EUR | ca. 50,8 EUR (ohne Basic-Teile, Platine, Setup/Versand) |
| U3 beim LCSC/JLC bestellt und selbst geloetet | 5 x 5,31 USD = 26,5 USD = 23,1 EUR | Versand LCSC separat | ca. 23 EUR (Mouser: 29 EUR) |
| **(b) Mouser komplett** (alles hier handgeloetet) | 104,5 EUR netto | Versand 0 | **ca. 124 EUR brutto** |
| **(c) Reichelt** (nur Teile, die Reichelt hat: P1, P2, C12/C14 (2x820 uF), F1/F2 (1206!), F3, OC1, OC2, U4) | 17,8 EUR brutto (Einzelpreise, 8 Typen) | Versand Reichelt (nicht eingerechnet) | ca. 17,8 EUR + Versand; **ca. 8 von 15 Ext-Typen**, Rest (J2, L1-L3, R2-R4, U2, C1, R15) nicht bei Reichelt |

Fazit: Mouser ist als Komplettquelle **etwa 2,4x so teuer wie JLC-Bestueckung (ca. 51 EUR + ESP32)** und liefert nur dann etwas, wenn man JLC-Gebuehren/-Teile
umgehen will. Die Hauptkosten sind ESP32 (29 EUR) und die Elkos (bis 20 EUR). Ohne diese beiden ca. 55 EUR netto.
Risiken bei Mouser: J2 hat anderen Footprint, U2 (JW5017S) und P1 (KF2EDGRC) gibt es nicht, F1/F2 nur mit Footprintwechsel, L3 anderer Hersteller: **nicht alle Zeilen sind 1:1 kaufbar.**

## 5. Handloet-Schwierigkeit

| Teil | Bewertung |
|---|---|
| P1, P2 (THT) | trivial |
| C1, R15, C4, R2-R4 (0805/2010) | leicht (0805 mit Pinzette/Lot; 2010 grosse Pads, leicht) |
| Q1, U4 (SOT-23, SOT-23-6) | leicht bis mittel |
| U2 (SOT-23-6, sehr kleiner Buck) | mittel; Layout eng, Waermeabfuhr |
| OC1/OC2 (SO-8 Gull-Wing, 2,54 mm Raster) | leicht bis mittel (grosses Raster) |
| D1-D5 (SOD-123, 5 Stk.) | leicht, aber Polaritaet beachten |
| F1/F2, F3 (0805/1206 PTC) | leicht |
| L1/L2 (1210), L3 (5x5) | leicht bis mittel (Pads unter dem Gehaeuse bei L3) |
| C12/C14 (Elko SMD 10 mm) | mittel (grosse Waermesenke, 2 grosse Pads, Heissluft/Kolben mit Vorheizen) |
| J2 (USB-C 16P) | **schwer** (0,5 mm Raster, Schirmbeine/THT-Haken; besser JLC) |
| U3 (ESP32-Modul, EPAD) | mittel bis schwer (Pastenschablone fehlt laut Doku; Heissluftplatte oder Kolben mit Flux, GND ueber Via-/EPAD-Loecher) |

## 6. Empfehlung

1. **Nicht komplett bei Mouser bestellen.** Fuer 5 Platinen ist JLC-Bestueckung (ca. 51 EUR incl. Gebuehr) deutlich billiger, und Mouser liefert mehrere Teile
   nicht passend (J2, U2, P1, F1/F2, L3, C12/C14).
2. **Bei JLC lassen** (schwer/ohne Alternative): J2, U2, U4, L1-L3, R2-R4, C1, R15, OC1/OC2 (alternativ Reichelt, gleiche MPN-Klasse).
   Nur die Gebuehr-Typen, die durch Wertetausch entfallen koennen, ersetzen (siehe `docs/BASIC_PARTS_RESEARCH.md` Szenario A: C1, R12/R15, U4).
3. **Bei Reichelt kaufen und per Hand loeten** (billigster Weg, geringer Aufwand): P1 + Gegenstecker, P2, C12/C14 (2x820 uF), F3 (und F1/F2 nur mit 1206-Footprint): spart ca. 4 Ext-Typen = ca. 12 USD Gebuehr.
4. **ESP32 (U3):** bei Mouser (5,80 EUR netto/Stk, Lager DE ca. 61k) oder LCSC (5,31 USD): Preis aehnlich; Mouser ist schnell lieferbar in DE und hat Original-Espressif-Ware (Mouser-Link:
   mouser.de/en/ProductDetail/Espressif-Systems/ESP32-S3-WROOM-1-N16R8). Wenn ohnehin eine Mouser-Bestellung laeuft (Kleinteile), erreicht man damit die 50-EUR-Schwelle ohne Versandkosten.
5. Mouser nur sinnvoll fuer: U3 (+ Ersatzmodule), Q1/D1-D5 als Ersatz, falls JLC-Teile ausgehen. Vor jeder Mouser-Bestellung Warenkorb pruefen (Preise [S] sind Schaetzungen).

## 7. Nicht verifiziert

* Alle Live-Preise/-Lagerstaende von Mouser (Seiten gesperrt, nur undatierte Snippets); Mouser-Nr. nur 859-6N137STA1, 859-6N136STA1, 640-USB4105-GF-A, 621-BAT42W-F.
* Preise [S] (C1, F1/F2, F3, L1/L2, L3, P1, P2, R2-R4, R15, U2, C4) sind Schaetzungen; Teile TYPE-C-31-M-12, SWPA5020S4R7MT, JVJ25V1000M10X12, KF2EDGRC-5.08-2P, JW5017S, BSMD0805-050-24V, SMD1206B110TFT, LQH32PN4R7NN0L nicht bei Mouser belegt.
* Versandschwelle (ca. 50 EUR) und Pauschale, MwSt-Anzeige (netto auf mouser.de).
* Quellen: Mouser-Seiten via Websuche (mouser.de/.com/eu.mouser.com, 2026-11-28), JLC-API `selectSmtComponentList` (2026-11-28), `docs/BASIC_PARTS_RESEARCH.md`, `docs/JLCPCB_PARTS.md`, `docs/JLC_ECONOMIC.md`.

## Nachprüfung mit pcbparts.dev (Mouser-Daten, Cache vom 25.11.2026)

Abfrage über das MCP `pcbparts.dev` (`mouser_get_part`). Die Preise kommen aus dem Mouser-Katalog, teils in CAD (mouser.ca), teils in USD. Umrechnung grob: 1 USD ≈ 0,86 EUR, 1 CAD ≈ 0,62 EUR (Annahme, Kurs nicht geprüft). Netto, ohne MwSt.

| Ref | Mouser-Nr. / MPN | Lager | Staffelpreis für Bedarf (5 Platinen) | Summe ≈ EUR | Bemerkung |
|---|---|---|---|---|---|
| U3 | 356-ESP32S3WRM1N16R8 | 29.648 | 5 × 9,68 CAD | 30,0 | identische MPN |
| C1 | 603-CC805JRNPO9BN680 | 1.647 | 10 × 0,096 CAD | 0,6 | identische MPN |
| C12, C14 | 667-EEV-FK1E102V (Panasonic, 10 × 10,2 mm) | 6.376 | 10 × 1,80 USD | 15,5 | Ersatz; Footprint gegen unser 10×12-Land prüfen |
| F3 | 603-SMD1206B110TFT | 11.638 | 5 × 0,158 CAD | 0,5 | identische MPN |
| J2 | 640-USB4105-GF-A (GCT) | 370.736 | 5 × 0,80 USD | 3,4 | Ersatz, **anderer Footprint** |
| L1, L2 | 81-LQH32PN4R7NN0L | 18.432 | 10 × 0,219 USD | 1,9 | identische MPN |
| OC1 | 859-6N137STA1 | 47.088 | 5 × 0,88 USD | 3,8 | ohne „-L“, sonst gleich |
| OC2 | 859-6N136STA1 | 23.848 | 5 × 0,88 USD | 3,8 | ohne „-L“, sonst gleich |
| U4 | 511-USBLC6-2SC6 | 93.014 | 10 × 0,239 USD (10 billiger als 5) | 2,1 | identische MPN |
| D1–D5 | 621-BAT42W-F (BAT42W-7-F) | 2.115 | 25 × 0,191 USD | 4,1 | identische Funktion |
| Q1 | 771-BC817-40-T/R | 701.317 | 10 × 0,121 CAD | 0,8 | identische MPN |
| R15 | 603-RC0805FR-071K3L | 41.562 | 10 × 0,018 USD | 0,2 | identische MPN |
| P1 | 651-1757242 (Phoenix MSTBA 2,5/2-G-5,08) | 21.733 | 5 × 0,806 CAD | 2,5 | Ersatz; Gegenstecker nicht abgefragt |
| P2 | 710-61300411121 (Würth 1×4) | 113.438 | 5 × 0,274 CAD | 0,9 | Ersatz, gleicher Raster |
| R2–R4 | 71-CRCW201068R0FKEF | **0** | – | – | nicht lieferbar |
| C4 | 603-CC805KRX7R9BB152 | **0** | – | – | nicht lieferbar |
| J2 orig., U2 JW5017S, L3 SWPA5020S4R7MT, F1/F2 BSMD0805-050-24V | – | – | – | – | **bei Mouser nicht gefunden** |

Summe der lieferbaren Positionen: **ca. 70 EUR netto** (ca. 83 EUR brutto), davon ESP32 ca. 30 EUR; ohne ESP32 ca. 40 EUR netto. Fehlend: R2–R4, C4, U2, L3, F1/F2 (diese müssten weiter von JLC kommen). Versandkostenfrei-Grenze von Mouser DE nicht geprüft.
