# R5 - Isolation / layout / fab review (independent)

Scope: `fab/EMSinterface_V2.0-gerbers.zip`, `fab/*_BOM_JLCPCB.csv`, `fab/*_CPL_JLCPCB.csv`, `dist/index/circuit.json`.
Method: own parser (Python, shapely) for the RS-274X/Excellon files (pours, clear polarity, regions, flashes, draws, G85 slots),
copper rebuilt per layer, connected components + via/PTH links, each component compared with the source netlist from circuit.json.
EasyEDA footprints fetched from easyeda.com/api/products/<LCSC>/components and fitted to the placed pads (own code, not `cpl_check.py`).
Hammond drawing 1591XXCFL (hammfg.com PDF) read for the mechanical data. No design file was modified.

Result: **0 BLOCKER, 3 MAJOR, 9 MINOR.** Isolation, connectivity, drills, edge clearance, jumper paste, mask, CPL geometry all verified OK.

## Verified OK (evidence)

| Item | Result |
|---|---|
| Isolation EMS<->MCU copper, top | min 7.085 mm (EMS GND_EMS pour island edge (-3.385,-10.31) to MCU pad at x=+3.7). |
| Isolation, bottom | min 7.40 mm (pours end at x=-3.7 / +3.7). Vias/PTH/pads/pours all included, NC pads of OC1/OC2 included (x<0 -> EMS side: 7.7 mm to MCU pads). |
| Mounting holes | 4 x NPTH 3.5, no copper in them; they sit one per side, no metal path across the barrier. |
| Slots | Edge_Cuts contains two closed 2 x 12 mm loops at x=-1..1, y=2..14 and y=-14..-2 (matches 2 x 12 mm, y=+-2..14). Copper to slot >= 2.385 mm (top) / 2.70 mm (bottom). OC bodies (9.8 mm long along y, y=3.1..12.9) are fully inside the slot span. Board stays one piece. |
| Opto pad creepage | Pad rows at x=+-4.75, pad inner edges at +-3.85 -> 7.70 mm pad-to-pad across the body (>= 6). Path around the slot end is longer. Package-internal creepage (6N137S/6N136S datasheet) not verifiable offline. |
| Connectivity vs source | 0 shorts, 0 opens: every one of 48 copper nets maps to exactly one connected copper island (top+bottom+vias+PTH). No orphan copper. 35 NC pads (U3 unused IOs, OC NC pins, SBU1/2) are isolated as intended. |
| Drills | PTH: 126 via 0.3 (pad 0.6, ring 0.15), P1 1.8/2.5 (ring 0.35), P2 1.0/1.5, J2 shell slots 0.8 wide (G85). NPTH 0.6 x2 (J2), 3.5 x4. |
| Copper to edge | min 0.75 mm top, 1.00 mm bottom (>= 0.3). No copper outside the outline. |
| Trace widths (circuit.json + Gerber apertures) | Power nets VIN/V3V3/V5_EMS 0.5; bus nets EMS_N1..6/11/12/13/17/26 0.4; signals 0.25; min 0.25 everywhere (JLC min 0.127). |
| JP1 / JP2 paste | Pads (21,-10.3/-8.7) and (26,-21.8/-20.2): no aperture in F_Paste/B_Paste (checked by point containment), mask opening present, gap 0.4 mm. |
| Vias | all tented (no mask apertures at vias). |
| BOM vs CPL | 81 designators in both, identical sets. |
| CPL vs EasyEDA footprints (own fit, CCW, y-up) | Rotation and origin of all 36 parts with a number-matched footprint reproduce the CPL file exactly (C1, C2.., C12, C14, C29, D1-D7, F1/F2, L1-L3, LD1-5, OC1/OC2, P1, P2, Q1, SW1/2, U1, U2, U4, U5). U3 (270, origin 38.608) and J2 (180, origin 33.0/24.904) fitted geometrically/by pin function: correct. |
| Polarity (EDA symbol pin names vs our nets) | BAT42W pad1=A/pad2=K: D1-D5 orientations match V1 netlist (D5 A=GND K=N6; D1/D3 A=bridge node K=N6; D2/D4 A=GND). 1N4148W pad1=K: D6 K=GND, A=N7 OK. B5819W pad1=K: D7 K=VIN, A=N6 OK. LED C2297 pad1=A: LD2-5 anode on resistor side OK; LED C84256 pad1='-': LD1 K=GND_EMS OK. Tantalum C29 and electrolytics C12/C14: footprint '+' marking at pad1, pad1 = V3V3 / EMS_VIN OK. U1 LM393, U2 JW5017S (BST/GND/FB/EN/VIN/SW), U4 USBLC6, U5 AMS1117, Q1 (B/E/C), OC1 6N137 (pin7 VE high, pin8 VCC), OC2 6N136 pin map OK. U3 ESP32 pin functions (GND1, 3V3, EN, IO5, IO17, IO19/20, IO0, RXD0/TXD0, IO2, GND2, EPAD x9) OK. |
| J2 pad names | EDA names A1B12/B1A12 GND, A4B9/B4A9 VBUS, A5 CC1, B5 CC2, A6/B6 DP, A7/B7 DN, A8/B8 SBU, 1-4 shell: all map to the expected nets after rot 180. |
| Mechanical (Hammond 1591XXCFL drawing) | Inner 115.15 x 60.65 x 36. Max PCB 114.5 x 60.5, straight length between notches 99.0, width 44.5, R3.5. Board 110 x 60, notch 5.5 x 8 (straight length 99.0 / 44.0), PCB posts 84.5 x 39.5 -> holes (+-42.25, +-19.75) OK. Screw-dome centre (+-53.5,+-26.25) is 4.0 mm from the nearest outline (needs ~3.5). U3 antenna ends flush at x=+55; no copper at x>=47.96 (keepout x>=48, |y|<=24 respected, both layers). P1 body flush at x=-55. J2 mouth at y=30.0 (= board edge), width centred at x=33. LEDs match ENCLOSURE.md table, pitch >= 5 mm. 12 mm caps (C12 at (-32.5,22.5), C14 at (-13.5,-24.3)) lie inside the outline, 4.6 mm / > 4 mm from screw-head keepout; height fits 36 mm inner height easily. |

## Findings

### MAJOR

**M1 - Solder paste apertures are 70 % x 70 % of the pad (49 % area) on every SMD pad.**
Evidence: all 248 rectangular top pads: paste/pad = 0.70/0.70 (e.g. 0805 pad 1.4 x 1.025 -> 0.98 x 0.7175, TSSOP/SOP/USB-C pads likewise); mask opening = pad exactly (0.000 expansion).
Risk: if JLC uses the paste file as delivered, solder volume is about half of normal -> opens/weak joints on 0805/1206/SOT/ESP32 pads. JLC may re-derive stencils itself, but that is not guaranteed.
Fix: re-export (or post-process) F_Paste with 90-100 % scaling (or `solderPasteMargin`/negative margin of <=0.05 mm) for all pads except JP1, JP2, TP pads you do not want; keep JP1/JP2 free of paste. Verify in JLC's PCBA preview.

**M2 - Buck input capacitor C10 is not at the JW5017S VIN pin.**
Evidence: U2.VIN (-15.18,10.72); C10 (10 uF, -13.4,13.29/15.11). The EMS_VIN copper between C10.pin2 and U2.VIN is a 9.7 mm 0.5 mm trace that changes layer twice (top->bottom->top at (-11.5,12.5) and (-12.1,10.6)); the only other VIN branch (C10 -> R16, 4.4 mm) does not reach the pin. SW node EMS_N26 (U2.SW -> L3.B) is 9.2 mm at 0.4 mm plus the C9 branch.
Risk: large high-di/dt loop (C10 - VIN - GND pin on the opposite side of the package), ringing at SW/VIN, EMI and possible instability/overshoot with a 24 V-class bus.
Fix: place C10 (and a 100 nF) directly beside U2 pins 5/2 with a short top-layer path (<= 2 mm, no vias), GND return through the pour at the C10 pad; keep SW copper short and with L3 close to pin 6.

**M3 - Four via pairs closer than JLC's hole spacing.**
Evidence (all same net, drills 0.3, annular rings overlap): V3V3 (8.00,9.90)/(8.42,9.96) c-c 0.421 (hole edge gap 0.121 mm); V3V3 (12.05,10.18)/(12.37,10.50) 0.458 (0.158); VBUS (30.83,24.30)/(30.90,23.90) 0.405 (0.105); VBUS (33.53,24.69)/(33.93,24.48) 0.454 (0.154).
Risk: below the JLC minimum hole-to-hole distance (check DFM; typical >= 0.2 mm edge-to-edge for same-net vias, 0.5 mm otherwise); drill breakage/hole merging, DFM hold.
Fix: tell the autorouter a via-to-via clearance (minViaToViaClearance >= 0.5 c-c extra) or merge the pairs into one via / move one via >= 0.8 mm c-c (rest of the board already has >= 0.8).

### MINOR

**m1 - Silkscreen is below JLC limits.** Gerber silk stroke widths are 0.036 / 0.045 / 0.072 mm (JLC min 0.153 mm line, ~1.0 mm character height); refdes use 0.4-0.5 mm text, labels PWR/RX/TX/3V3, "TX EN", "3V3 OUT" 0.8 mm. They will print as unreadable or drop out. Fix: font size >= 1.0 mm with the thicker stroke (or use `strokeWidth`/`pcbStrokeWidth` >= 0.15 mm) at least for the jumper and LED labels.

**m2 - Silk over exposed pads:** 5.6 mm^2 total (U3 3.70, J2 1.28, SW1 0.30, SW2 0.30). JLC clips silk on pads automatically; adjust outlines if you want control. Silk also sits on the board outline (bounds +-55.05 / 30.05) and text "ISOLATION BARRIER" crosses the barrier between the slots (harmless).

**m3 - JP1/JP2 mask:** two separate mask openings (web 0.4 mm). A hand solder bridge works but is easier with one common opening over both pads and the gap.

**m4 - Mask expansion 0 on every pad.** JLC normally compensates but a 0.05 mm expansion in the file is safer, especially at the 0.5 mm-pitch USB-C pads (web would still be 0.1 mm, minimum for JLC; use 0.025-0.05).

**m5 - Copper clearance 0.196-0.215 mm in many places** (USB-C fanout, ESP32 area, pour-to-pad), intended 0.25 / spec 0.2. Above JLC 0.127 mm, so fabricable; USB_DP/USB_DN/GND around J2/U4 have exactly 0.20 mm. Only informational.

**m6 - GND / GND_EMS routed with 0.25 mm stitching traces** (352 mm GND, 167 mm GND_EMS) while the spec says power >= 0.5. Pours on both layers carry the current and all GND pads are in one island, so fine; VBUS narrows to 0.375-0.475 mm in short segments at J2 (ok for < 0.9 A).

**m7 - USB pair:** D+ 33.4 mm / D- 22.2 mm total (including J2 A/B branches and the U4 stubs), 6 resp. 2 vias, 0.2 mm spacing. Full-speed only (ESP32-S3 USB serial/JTAG), so tolerated; for cleanliness pair-route with equal length and fewer vias.

**m8 - Thermal:** AMS1117 (U5) tab pad is in a V3V3 pour of 143 mm^2 (top) + 146 mm^2 (bottom), stitched by 8 vias. At 5 V in, 3.3 V out and 150-350 mA, 0.25-0.6 W -> about +12...+30 K. Acceptable; a few more vias under the tab would help. USB-C opening: receptacle mouth flush with the PCB edge, wall 2 mm + 0.325 mm gap -> recess 2.3 mm; the planned 10 x 4 mm cut-out only passes slim plugs. Make it ~13 x 7 mm for overmoulded cables. LED light pipes must span roughly 25 mm (board on box posts), plan them in the lid.

**m9 - Process residuals (cannot be verified offline):** (a) JLC's internal rotation offset for 90/270 and polarised parts is the one thing the EasyEDA fit cannot prove; confirm in the JLC PCBA preview especially D1-D7, LD1-LD5, C12/C14/C29, U1, U2, U4, U5, Q1, OC1/OC2, J2, U3, P1. (b) The gerber zip also contains tscircuit's `bom.csv` and `pick_and_place.csv` (untransformed rotations, centre points); do not upload those to the PCBA step and remove them from the Gerber zip. (c) P1, P2 (THT) and J2 shell legs need JLC through-hole/manual soldering service. (d) PCB post centring (84.5 x 39.5 grid centred in the box) assumed from the drawing; confirm against the STEP file. (e) USB-C positioning NPTH 0.6 mm: copper only 0.225 / 0.29 mm from the hole edge (from the vendor footprint; JLC accepts).

## Notes on what was checked and not
- Buck, USB pair and thermal were assessed from circuit.json routes and copper geometry (no field simulation).
- `tsci check shorts` was not needed: independent copper connectivity (Gerber-level) gave 0 shorts / 0 opens.
- Antenna: no copper and no parts at x>=48 (both layers); C22/C23/R22/LD4 and the right-hand screws sit just outside the keepout (x=46.9..47) beside the antenna end; acceptable per the documented rule but Espressif recommends a clean flank, so keep these as they are or move them left.
