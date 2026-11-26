# CPL-Pruefung (JLCPCB Pick&Place) - FIX_LIST #7

Datei: `fab/EMSinterface_V2.0-CPL_JLCPCB.csv`, erzeugt von `scripts/jlc_bom_cpl.py` aus `dist/index/circuit.json`
mit `scripts/cpl_check.py`.  Die CPL-Daten sind NICHT mehr die tscircuit-Mittelpunkte/-Drehungen (`pick_and_place.csv` der Gerber-ZIP).

## Methode
JLCPCB bestueckt mit Ursprung und Drehung der **EasyEDA-Bibliotheks-Footprints**. Fuer jedes Bauteil mit LCSC-Nummer wird der
EasyEDA-Footprint (`scratch/easyeda/<LCSC>.json`, Einheit 10 mil, y gespiegelt auf y-aufwaerts) mit unserem tscircuit-Footprint
ueber die Pad-Nummern verglichen: `p_eda = R(theta) * p_ts + t`.  Ein Teil mit Ursprung `O` und Platzierungsdrehung `phi` hat dann
`CPL-Drehung = phi - theta`, `CPL-Position = O - R(phi - theta) * t`.  Fuer J2 (USB-C) unterscheiden sich die Pad-Nummern der beiden
Bibliotheken; dort wird die Pad-Punktmenge geometrisch zugeordnet (Restfehler 0,000 mm).  Teile ohne gecachte EasyEDA-Daten
(0805-R/C, die Standard-Footprints von tscircuit) sind symmetrisch und werden als gleich angenommen (theta = 0).
Annahme: positive CPL-Drehung = gegen den Uhrzeigersinn (wie KiCad/tscircuit).  **In der JLC-Vorschau nach dem Upload pruefen**
(besonders die Teile mit CPL-Drehung 90/270: U1, U4, U5, OC1, OC2, Q1, P1).

## Ergebnis je Teil (`python3 scripts/cpl_check.py`)
Spalten: Mid X/Y = Ursprung des EasyEDA-Footprints auf der Platine, rot = CPL-Drehung, phi = tscircuit-Drehung,
theta = Drehung EasyEDA <-> tscircuit, t = Versatz EasyEDA-Ursprung gegenueber unserem Footprint-Ursprung.
```
ref   lcsc      CPL mid x/y        rot  phi   theta  t(eda-ts)      note
C1    C107120    -28.000  -10.500  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C2    C15850     -22.060  -11.570  0    0     0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C3    C46653     -22.060   -7.290  0    0     0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C4    C1717       -9.720    4.710  0    0     0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C5    C1710       -8.650  -16.790  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C6    C49678     -15.690  -15.010  0    0     0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C7    C49678       8.500    8.000  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C8    C49678      -8.370   12.850  0    0     0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C9    C49678     -20.630   10.290  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C10   C15850     -12.900   11.100  180  180   0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C11   C12891     -25.000   19.000  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C12   C49256851  -32.500   22.500  90   90    0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.000 mm
C13   C49678      -7.000   -8.300  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C14   C49256851  -13.500  -24.300  0    0     0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.000 mm
C20   C28323      38.600   12.800  180  180   0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C21   C1744       26.600   23.000  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C22   C15850      46.900   12.000  270  270   0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C23   C49678      46.900   16.000  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C24   C15850      22.500   11.600  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C25   C49678      20.000   11.600  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C26   C12891       6.500   20.000  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C27   C15850      14.800   22.600  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C28   C49678       7.000   25.500  180  180   0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
C29   C16133      14.600   18.300  270  270   0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.000 mm
C30   C49678     -12.900   12.900  180  180   0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
D1    C22466362  -32.680  -15.010  180  180   0      (-0.00, 0.00)  EasyEDA match on 2 pads, residual 0.050 mm
D2    C22466362  -32.680  -20.140  0    0     0      (-0.00, 0.00)  EasyEDA match on 2 pads, residual 0.050 mm
D3    C22466362  -32.680   -4.710  180  180   0      (-0.00, 0.00)  EasyEDA match on 2 pads, residual 0.050 mm
D4    C22466362  -32.680    0.420  0    0     0      (-0.00, 0.00)  EasyEDA match on 2 pads, residual 0.050 mm
D5    C22466362  -28.210  -17.580  90   90    0      (-0.00,-0.00)  EasyEDA match on 2 pads, residual 0.050 mm
D6    C81598     -25.410  -17.580  90   90    0      (-0.00,-0.00)  EasyEDA match on 2 pads, residual 0.085 mm
D7    C8598      -32.680    4.710  0    0     0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.050 mm
F1    C910822    -40.500    3.430  90   90    0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.187 mm
F2    C910822    -40.500   -3.430  270  270   0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.187 mm
F3    C910822     26.200   15.000  180  180   0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.187 mm
J2    C165948     33.000   24.904  180  0     180    (-0.00, 2.47)  EasyEDA match on 16 pads, residual 0.000 mm (geometric pad-set match)
L1    C98021     -37.710    4.280  270  270   0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.000 mm
L2    C98021     -37.710   -6.010  270  270   0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.000 mm
L3    C43183     -20.600   14.570  180  0     180    ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.000 mm
LD1   C84256      -8.000   24.000  0    0     0      (-0.00, 0.00)  EasyEDA match on 2 pads, residual 0.050 mm
LD2   C2297       12.500  -13.800  90   90    0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.000 mm
LD3   C2297       16.000   13.600  90   90    0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.000 mm
LD4   C2297       47.000  -16.500  90   90    0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.000 mm
LD5   C2297       28.000    8.500  90   90    0      (-0.00,-0.00)  EasyEDA match on 2 pads, residual 0.000 mm
OC1   C92651       0.000    8.000  270  0     90     ( 0.00, 0.00)  EasyEDA match on 8 pads, residual 0.205 mm
OC2   C336082      0.000   -8.000  90   180   90     ( 0.00, 0.00)  EasyEDA match on 8 pads, residual 0.205 mm
P1    C441236    -44.100    0.000  270  270   0      ( 0.00, 0.00)  EasyEDA match on 2 pads, residual 0.000 mm
P2    C32713270   12.000  -26.500  0    0     0      ( 0.00, 0.00)  EasyEDA match on 4 pads, residual 0.000 mm
Q1    C20069155   -9.630   -0.019  270  90    180    (-0.05,-0.00)  EasyEDA match on 3 pads, residual 0.196 mm
R1    C17414     -27.370   -4.710  0    0     0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R2    C53284030  -28.210    3.000  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R3    C53284030  -24.850    3.000  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R4    C53284030  -21.500    3.000  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R5    C17655     -25.410   -8.570  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R6    C17713     -22.060  -15.010  0    0     0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R7    C17414     -22.060  -20.140  0    0     0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R8    C149504    -22.060   -3.860  0    0     0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R9    C17673      -8.650   -5.580  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R10   C17710      -8.370    9.860  0    0     0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R11   C17673      -9.000  -11.570  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R12   C17772     -12.360    8.600  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R13   C17673      12.500    8.200  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R14   C17471       9.000   -9.500  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R15   C17384     -12.360    3.870  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R16   C149504    -14.600   16.300  0    0     0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R17   C17379     -14.000   24.000  0    0     0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R18   C17557      16.000    8.200  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R19   C17557      12.500   -9.500  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R20   C17414      44.400   11.400  270  270   0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R21   C17414      28.000  -12.500  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R22   C17557      47.000  -12.500  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R23   C27834      28.600   19.200  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R24   C27834      37.000   20.300  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R25   C17514      26.600   26.500  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R26   C17557      24.000    8.500  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
R27   C149504     16.500   -9.500  90   90    0      ( 0.00, 0.00)  assumed equal to EasyEDA footprint (no cached EasyEDA data)
SW1   C318884     33.500  -23.500  0    0     0      ( 0.00, 0.00)  EasyEDA match on 4 pads, residual 0.000 mm
SW2   C318884     34.000  -14.800  0    0     0      ( 0.00, 0.00)  EasyEDA match on 4 pads, residual 0.000 mm
U1    C7955      -14.800   -9.850  270  270   0      (-0.00, 0.00)  EasyEDA match on 8 pads, residual 0.000 mm
U2    C371172    -16.480   10.720  180  0     180    ( 0.00, 0.00)  EasyEDA match on 6 pads, residual 0.050 mm
U3    C2913202    38.608   -0.000  270  270   0      (-0.00, 3.64)  EasyEDA match on 40 pads, residual 0.033 mm
U4    C7519       32.300   17.400  270  0     90     ( 0.00, 0.00)  EasyEDA match on 6 pads, residual 0.151 mm
U5    C6186       20.500   18.110  270  90    180    (-0.09, 0.00)  EasyEDA match on 4 pads, residual 0.270 mm
```

## Teile mit Korrektur (theta != 0 oder t != 0)
| Teil | Befund | Korrektur |
|---|---|---|
| J2 USB-C C165948 | EasyEDA-Footprint 0 deg hat die Steckseite bei -Y, unserer bei +Y (theta 180), Ursprung 2,47 mm versetzt (Pad-Reihe vs. Gehaeusemitte) | Rotation 180, Mid Y = 22,43 + 2,47 = 24,904 (alt: 0 / 24,999) |
| U3 ESP32-S3 C2913202 | Drehung stimmt (270); EasyEDA-Ursprung = Mitte des Pad-Rasters, nicht Modulmitte (t_y = 3,64) | Mid X = 38,608 statt 42,25 / 41,98 |
| U1 LM393 C7955 | V2: eigener Footprint `lib/soic8_lm393.tsx` im EasyEDA-Rahmen (theta = 0, Restfehler 0,000 mm; vorher generisches `soic8`: theta 90, Restfehler 0,555 mm); Platzierung mit pcbRotation 270 (Pin 1 oben links) | Rotation 270 |
| U2 JW5017S C371172 | EasyEDA 180 deg gegenueber unserem sot23_6 | Rotation 180 |
| U4 USBLC6 C7519, Q1 BC817-40 C20069155, U5 AMS1117 C6186 | theta 90 / 180 / 180 | Rotation 270 / 270 / 270 (phi 0 / 90 / 90) |
| OC1 6N137 C92651, OC2 6N136 C336082 | Footprint (Reihen bei +-4,75, Pin 1..4 links, 5..8 aufwaerts) gegen EasyEDA-Footprint um 90 deg | OC1 Rotation 270, OC2 Rotation 90 |
| L3 SWPA5020 C43183 | Pad 1/2 vertauscht (symmetrisches Bauteil, Polung egal) | Rotation 180 |
| P1 KF2EDGRC-5.08-2P C441236 | Rechtwinkliger Klemmenkoerper -10,9 .. +1,3 mm um die Pinachse, Steckseite bei -Y des EasyEDA-Footprints | Platzierung 270 deg bei x = -44,1: Steckseite zeigt nach -X (Platinenkante), Koerper endet bei x = -55,0; CPL 270 (THT-Teil, wird von JLC von Hand/Welle bestueckt) |
| L1/L2 C98021, P2 C32713270 | V2: Footprints nach EasyEDA (Pads 1,52 x 3,1 bei +-1,145 bzw. Loch 1,1 / Pad 1,7), Restfehler 0,000 mm, theta = 0 | L1/L2 Rotation 270 (phi), P2 0 |
| D1..D7, LD1..LD5, C12/C14/C29, SW1/SW2 | theta = 0, Pad-Nummern wie JLC (siehe `lib/diodes.tsx`, `lib/thtparts.tsx`) | keine; Dioden/LEDs: Kathode links bei phi = 0 wie im JLC-Footprint |
| R2..R4 (2010, C53284030) | kein EasyEDA-Datensatz abrufbar (API liefert `success: false`); 2010-Widerstand ist symmetrisch | keine Korrektur noetig |

Alle uebrigen 0805-/1206-Teile: theta = 0, t = 0 (symmetrisch).  Mid X/Y = Footprint-Mitte = Pad-Mitte.
Nicht bestueckt (kein LCSC): TP1..TP3, JP1, JP2, Montagebohrungen.
