# R7 - Independent layout / manufacturing review (third round)

Scope: `fab/EMSinterface_V2.0-gerbers.zip` (unzipped to scratch, parsed with gerbonara + shapely, own scripts, project check scripts NOT used),
`fab/*BOM*.csv`, `fab/*CPL*.csv`, `dist/index/circuit.json` (consistent with the zip: build 10:40:48, zip 10:40:52, sources older).
Reference data: `scratch/easyeda/*.json` (EasyEDA footprints), `docs/ENCLOSURE.md`, `docs/DESIGN_SPEC.md`.

Result: **0 BLOCKER, 1 MAJOR, 9 MINOR, 4 INFO.** The board is electrically and mechanically consistent; the Gerbers can be uploaded.

## What was verified and passed (evidence)

| Item | Method | Result |
|---|---|---|
| Copper connectivity vs. netlist | Gerber copper (both layers, pours with LPC clears applied in file order) merged through all 120 vias + PTHs, pads of circuit.json mapped onto copper | 49 nets = 49 copper groups: **no short, no open, no floating copper island**; every pad lies in copper; every via/PTH has copper on both layers |
| Netlist vs. V1 | `docs/netlist_v1.json` pins mapped to V2 nets | identical except the intended MCUVCC -> V3V3 / P2_3V3 split at JP2 |
| Isolation (EMS <-> MCU) | min distance EMS-group copper to MCU-group copper per layer, incl. NC pads, pours, vias | **top 7.05 mm, bottom 7.40 mm** (>= 6 mm). No hole/via/NPTH on the wrong side. Slots 2 x 12 mm at x = +-1 (y 2..14, -2..-14), closed contours in Edge_Cuts, nearest copper 2.35 mm top / 2.7 mm bottom |
| Clearance | all different-net copper pairs per layer | min **0.200 mm** (J2 pads, pour-to-pad), nothing < 0.2 |
| Copper to edge / holes | outline polygon from Edge_Cuts, drills from .drl | edge >= 0.75 mm (top), 1.0 mm (bottom); NPTH 0.6 mm to copper 0.27 mm; 3.5 mm holes 2.23 mm to copper |
| Via / annular | Gerber apertures + drill | 120 vias 0.30/0.60 (ring 0.15); P1 1.8/2.5; P2 1.1/1.7; J2 slots 0.8 x 1.5 / 0.8 x 1.2 (= EasyEDA 1.5 / 1.2) |
| Trace width | circuit.json routes per net | power/bus 0.4-0.5 mm, signals 0.25 mm, VBUS 0.275 minimum |
| Outline | Edge_Cuts.gbr | closed 110 x 60 with 4 notches 5.5 x 8, R3.5 (6-segment polyline), matches ENCLOSURE.md; holes (+-42.25, +-19.75) = 12.75/97.25 x 10.25/49.75 on the Hammond grid |
| JP1/JP2 | paste + mask Gerbers | **no paste** on all four pads, pads 1.6 x 1.2, gap 0.4 mm, nets ESP_TX/MCU_TX and V3V3/P2_3V3 stay separate, not in BOM/CPL -> stay open |
| Paste | F_Paste vs pads | 100 % of pad on all SMD pads, none on PTH/slots, none on TP pads |
| Vias vs. pads/mask | positions | no via within 0.26 mm of an SMD pad, no via has a mask opening (all tented) |
| Antenna | copper in x >= 48, |y| <= 24 | none on either layer (top max x 47.6, bottom 47.2; only module pad GND1 touches x 48.26); keepouts present in circuit.json |
| BOM/CPL | CSV vs circuit.json | JLC headers correct (`Comment,Designator,Footprint,LCSC Part #` / `Designator,Mid X,Mid Y,Layer,Rotation`), 83 = 83 designators, LCSC numbers equal the design, JP1/JP2/TP1-3 correctly absent |
| CPL vs EasyEDA | own re-computation: EasyEDA pad (number) -> CPL mid + rotation (CCW) -> compared with our pad of the same number | worst residual 0.27 mm (U5), U3 40 pads 0.03 mm, OC1/OC2/Q1/F 0.2 mm; J2 matched geometrically by previous round |
| Polarity | EasyEDA symbol/footprint JSON | BAT42W pad 1 = anode, 1N4148W/B5819W pad 1 = cathode, LED C2297 pad 1 = anode (cathode left), C84256 pad 1 = cathode (left), tantalum pad 1 = +, electrolytic pad 1 = + (chamfer side): all consistent with `lib/diodes.tsx`, `lib/thtparts.tsx`, CPL |
| Zip set | `unzip -l` | F/B Cu, Mask, Paste, Silk, Edge_Cuts, PTH + NPTH drill; tscircuit bom/pick_and_place removed; X2 `TF.FileFunction` present in every file; units mm 4.6, drill METRIC decimal |
| Mechanics vs ENCLOSURE.md | coordinates compared | P1, U3, J2, SW1/SW2, LD1-LD5, slots, notches, holes all as documented; C12 (body x -37.5..-27.5) keeps 0.75 mm to the 8 mm screw-head keepout; C14 0.7 mm to edge; tall parts 12 mm << 36 mm |
| Placement | pads / key distances | buck: C10 1.4 mm / C30 2.6 mm from U2 VIN (pin 5), SW to L3 4.5 mm; AMS1117: C24/C25 3.5 mm, C29 3.2 mm from tab, 2 x ~145 mm^2 V3V3 copper + 8 thermal vias; opto bypass C7/C13 4-5 mm (< 1 cm datasheet limit); USB: J2 -> U4 -> ESP direct, 22.0 / 22.3 mm D+/D-, 2-4 vias each (FS only, fine) |

## Findings

### MAJOR

**M1 - Silkscreen text is below the JLC minimum height (and `check_fab.py` G5 is checking the wrong number).**
Evidence: all 37 texts use `fontSize = 1.0 mm`; measured glyph envelope in F_SilkScreen.gbr (incl. 0.15 stroke) is **0.62-0.64 mm high** ("PWR" 0.62, "TX EN" 0.62, "3V3 OUT" 0.64), i.e. cap height ~0.47 mm + stroke. JLC minimum is 1.0 mm height (0.153 mm width); stroke here is 0.15 mm (`postprocess_gerbers.py` uses 0.15, comment says 0.153). At this size counters of 8/B/R/3 are ~0.2 mm and fill in; JLC either blurs or silently deletes the text. Designator-type texts (D1..D7, F1-F3, U2, U4, U5, Q1, "+") are affected as well.
Fix: `fontSize >= 1.8mm` for every `silkscreentext`/`pcbStyle.silkscreenFontSize` (glyph = 0.47 x fontSize + 0.15 >= 1.0), set `MIN_STROKE = 0.16`; free space exists on both sides of the board; shorten "EMS-ESP Isolated Interface V2.0" or place it on the bottom side (bottom silk is empty). Make G5 measure the glyph envelope from the Gerber.

### MINOR

**m1 - Solder-mask opening = pad size (expansion 0) on all 273 openings.** JLC mask registration is +-0.05 mm; with 0 expansion the mask can overlap the pad edge, critical on J2 signal pads (0.3 mm), U3 (0.9 mm) and U2/U4 (0.6 mm). JLC CAM normally adds its own expansion, but do not rely on it. Fix: `solderMaskMargin="0.05mm"` on the board/pads. Mask dams then stay >= 0.1 mm (J2 pad gap 0.2). JP1/JP2 will keep one merged opening (intended).

**m2 - Copper slivers narrower than 0.127 mm in the GND_EMS pour.** 4 fingers of **0.06 mm** x 2.3 mm between the 2010 pads R2/R3/R4 (x = -26.53 and -23.18, y -0.3..2.0 and 4.2..6.4) and 5 fingers of **0.1 mm** x 1.8-2.5 mm between U1 pad rows (y = -8.58, -9.85, -11.12, x -18.8..-10.8). Cause: pour clearance 0.3 mm eats both sides of a 0.66 mm pad gap. They are same-net and harmless electrically but can peel and float (acid trap/short risk) and JLC DFM will flag or remove them. Also 2 on the MCU side (0.09-0.11 x 0.7 mm near x = 26-28, y = 15.3-16.0). Fix: `clearance="0.25mm"` on the pours (leaves 0.16 mm fingers) or increase R2-R4 pitch by 0.3 mm. A 0.075 mm same-net slit between C28.pin1 and the V3V3 pour (x 8.42-8.5, y 24.8-26.2) closes with the same change or by `V_X0 = 7`.

**m3 - Two same-net via pairs only 0.25 / 0.30 mm hole-edge apart** (-13.55/9.42 vs -14.10/9.40 on V5_EMS; 46.90/18.50 vs 46.90/19.10 on GND) and a third at 0.447 mm. JLC hole-to-hole minimum is 0.5 mm in general (0.254 mm same net only). Fix: move one via of each pair >= 0.5 mm away; `minViaHoleEdgeToViaHoleEdgeClearance` is set to 0.25 mm, raise to 0.5 mm.

**m4 - ESP32 100 nF is far from the 3V3 pin.** U3 3V3 pad (46.24, 8.75): C22 10 uF pad at 4.2 mm, C23 100 nF pad at 6.4 mm (feed is a 22 mm V3V3 trace from U5, not a pour). Fix: swap/move so the 100 nF sits <= 2 mm from pin 2 and the 10 uF next to it; there is room at x 40-45, y 10-13 beside R20/C20 (keep x < 47).

**m5 - Placement DRC was bypassed.** `export_fab.sh` builds with `--ignore-placement-drc`; courtyard overlaps exist (D5/D6 4.4 mm^2, C24/C25 1.6, C22/R20 1.1, C4/R15 0.8, F3/U5 0.5, C10/C30 0.3, U5/C27 0.06). Pad clearances are >= 0.2 mm and body gaps are >= 0.5 mm in the cases checked, so no assembly error is expected, but this hides future errors. Fix: shrink the courtyards of the 0805 parts or move the pairs 0.5 mm apart, then drop the flag.

**m6 - No pin-1 marks on U1 (LM393), U2, U4, U5, Q1 and no designators on R/C.** Only OC1/OC2 carry a "1". JLC assembles by CPL, so this only affects rework/debug. Fix: add a pin-1 dot/line to the five footprints (or a "1" text) once M1 sizes are fixed.

**m7 - Gerber file names (`F_Cu.gbr`, `drill-L1-L2.drl`, ...) are not the JLC/KiCad pattern (`<proj>-F_Cu.gbr`, `-PTH.drl`, `-NPTH.drl`).** All files carry correct X2 `TF.FileFunction`, so the JLC viewer should classify them, but this was not testable here. Check on upload that top/bottom, mask polarity (files are `Negative`, dark = opening, correct) and the two drill files (PTH incl. G85 slots, NPTH) are all recognised; the PTH file contains 4 oval slots as `G85` (valid, KiCad style).

**m8 - Antenna end is flush with the board edge (module x 29.5..55), no overhang.** The keepout (48..57 x +-24, both layers) is correct and verified empty, but LD4/R22 (x 47, y -12.5/-16.5) and C22/C23/R20 (x 44-47, y 11-17) are 1-3 mm outside the zone beside the antenna region and the GND pour reaches x = 47.1 under the antenna part of the module (Espressif wants the antenna area itself copper-free from the module's antenna edge, ~x >= 48.5 here - satisfied, no margin). Expect somewhat reduced range; acceptable for a hall/basement unit. Optional: pull the pour back to x = 45 and move LD4/R22 to x <= 44.

**m9 - F3 PTC 0.5 A hold (BSMD0805-050-24V) is tight for ESP32-S3 Wi-Fi bursts (peaks 350-500 mA) + LEDs on 5 V via AMS1117** and trips earlier when warm (80 % at 50 C), resetting the module. Fix: 1 A hold 0805/1206 PTC, or accept as documented in the spec; keep in mind that the USB host side limits 500 mA anyway.

### INFO

- i1 - JLC order options: P1 (KF2EDGRC), P2 (header) and the J2 shell legs are through-hole -> Standard PCBA with THT/hand soldering, not "Economic"; ESP32 module C2913202 and the 2010 resistors are Extended parts. Components within 3-5 mm of the long edges (J2, C28, R25, C14, P2) -> let JLC add process rails (or panelise) when ordering; no fiducials present (not required).
- i2 - The CPL convention (positive = counter-clockwise on the EasyEDA footprint) and the pad-grid origin of U3 (Mid X 38.608 instead of module centre 42.25) are consistent with my independent pad-by-pad comparison, but JLC's rotation sign cannot be proven offline. **Before paying, check in the JLC assembly preview**: U3 antenna toward +X (right edge), J2 mouth toward the top edge, OC1/OC2 pin 1 at the top-left, U4/U5/Q1/U2 pin 1, LED cathodes (left at rotation 0), C29/C12/C14 "+" marks.
- i3 - USB-C height in the 1591XXCFLBK box is still unverified (ENCLOSURE.md: post height unknown); the 12 x 7 mm cut-out is centred on an assumed height. Re-measure with the Hammond STEP before cutting; the connector mouth is 2.3 mm behind the outer wall surface, tight but covered by the 12 mm width.
- i4 - Silk lines run to 0.1 mm from the board edge (module outline at x = +-54.8, J2 outline y = 29.8) and 10 silk strokes touch via drills; silk over exposed pad copper totals 0.6 mm^2 (U2 label, C27/R25 area). JLC clips silk on pads automatically.

## Suggested actions before upload (in order)
1. M1: silk font size >= 1.8 mm, stroke 0.16 mm, regenerate Gerbers.
2. m2 + m3 + m1: pour clearance 0.25 mm, move the three via pairs, mask margin 0.05 mm; rerun the same scripts and re-run isolation (will stay > 7 mm).
3. m4: move C23 next to the ESP32 3V3 pin.
4. Upload, then confirm the JLC layer assignment and the CPL orientation preview (i2).
