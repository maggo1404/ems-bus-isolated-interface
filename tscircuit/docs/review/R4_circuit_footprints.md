# R4 - Circuit correctness and footprints (independent hardware review)

Scope: netlist vs Eagle V1, MCU-side additions, footprints vs LCSC/EasyEDA data, built copper, JLC parts.
No design file was modified. Review done only from primary data (Eagle `hardware/EMSinterface_V1.0.sch/.brd`, `src/*.tsx`, `lib/*.tsx`,
`dist/index/circuit.json`, `fab/*`, EasyEDA `api/products/<LCSC>/components`, JLCPCB parts API, EMS-ESP32 `dev` source on GitHub).
Scratch scripts were kept outside the repo.

## Verdict

BLOCKER 0, MAJOR 1, MINOR 11 (plus INFO notes). The circuit is electrically correct and matches V1; the MCU side is wired correctly for
EMS-ESP32; copper matches the intended netlist. The one real defect is the U1 SOIC-8 land pattern.

## What was verified (and how)

| Check | Method | Result |
|---|---|---|
| V1 netlist == Eagle | Parsed `.sch` myself (pinref -> pad via lib `<connects>`), compared to `docs/netlist_v1.json` and to `.brd` `<signal>/<contactref>` | 33/33 nets identical (only supply symbols P+/GND differ, not parts). sch == brd. |
| V1 nets in tscircuit | `scripts/check_netlist.py` (run by me) | ALL OK (33 V1 nets, 21 new MCU nets, EMS/MCU separation) |
| Copper == intent | Own script: rebuilt connectivity from `pcb_trace` + `pcb_via` + `pcb_copper_pour` + pads by geometry (shapely, per layer) and compared with `source_trace` groups | 0 shorts (no copper cluster with 2 source nets), 0 opens (every net is one copper cluster), 0 unnetted pad touching a net. Pours checked too. |
| EMS<->MCU copper distance | same geometry | 7.08 mm top / 7.40 mm bottom (>= 6 mm); OC pads on the correct side (OC1.1-4 EMS, 5-8 MCU; OC2 mirrored, 180 deg) |
| Antenna keepout | same geometry | no copper on either layer in the keepout |
| Pin names of U3 | compared `ESP32S3_PINLABELS` with EasyEDA C2913202 symbol, all 41 pins | identical |
| Pad numbering/geometry vs EasyEDA | compared every BOM part's pads by number after best rigid transform (no mirror) | see findings; all pin numbers consistent, no mirrored footprint |
| CPL vs EasyEDA frame | for every part: EDA origin rotated by CPL angle + CPL Mid == our pad positions | within 0.0-0.2 mm for all except U1 (0.56, see M1); J2 and U3 OK after pad-name mapping |
| EMS-ESP32 GPIOs | `src/core/system.cpp` `load_board_profile()` "S32S3" = `{led 2, dallas 18, rx 5, tx 17, pbutton 0, ...}`; `WebSettingsService.cpp` maps data[0..4] = led, dallas, rx, tx, pbutton | GPIO5 Rx, GPIO17 Tx, GPIO2 LED, GPIO0 button: confirmed |
| JLC parts | JLCPCB `selectSmtComponentList` API + EasyEDA | all 46 LCSC numbers exist, values/packages match the BOM comments, all in stock (lowest: L3 C43183 1885, U2 C371172 17827, L1/L2 C98021 5897, OC2 C336082 8645, BAT42W 22090) |

## Verified-correct items (no action)

- Strapping: GPIO0 = 10k pull-up + BOOT button; EN = 10k + 1 uF + RESET button; GPIO3/45/46 left floating (internal defaults: JTAG-pad, VDD_SPI 3.3 V, ROM print) - fine for N16R8 (3.3 V octal PSRAM). GPIO35/36/37 (octal PSRAM) unused.
- Native USB: pin13 IO19 = D- (USB_DN), pin14 IO20 = D+ (USB_DP); both A/B pad pairs of J2 tied; U4 USBLC6-2SC6 pinout (1/6 I/O1, 3/4 I/O2, 2 GND, 5 VBUS) correct; CC1/CC2 each 5.1k to GND (J2 pad mapping checked against EasyEDA A5/B5 under the 180 deg frame); SBU NC; SHELL = 1M || 4.7 nF to GND.
- J2 footprint (lib/usbc16.tsx) equals EasyEDA C165948 (12 row pads, 2x 1.2x2.0 / 2x 1.2x1.8 plated slots 0.8x1.5 / 0.8x1.2, 2 pegs 0.6, offsets 0.768/4.948) rotated 180 deg; pin order of all 12 signal pads verified one by one.
- AMS1117-3.3 pinout (1 GND, 2 VOUT, 3 VIN, 4 tab = VOUT) = EasyEDA; C29 tantalum pad 1 = + (EasyEDA symbol "+" at pin 1, bar region at pad 1), pad geometry identical to C16133 footprint; C12/C14 electrolytic pad 1 = + (EasyEDA chamfer/"+" at pad 1), geometry identical.
- Diode polarity vs EasyEDA: C81598 pad1 = K, C8598 pad1 = K, C22466362 (BAT42W) pad1 = A (handled by PAD_SWAP, checked in copper), LD1 C84256 pad1 = K, green C2297 pad1 = A; netlist after the swap equals V1 (A/C).
- Q1 BC817-40 C20069155: EasyEDA pad 1 B / 2 E / 3 C, same as V1 BC847B; footprint non-mirrored.
- OC1/OC2 pin functions (6N137: 1 NC 2 A 3 K 5 GND 6 VO 7 VE 8 VCC; 6N136: 7 = VB left NC) and counter-clockwise numbering match EasyEDA; 6N137S-TA1-L supply 2.7-5.5 V (3.3 V OK), 6N136S-TA1-L 4.5-15 V (5 V OK).
- JW5017S pinout (1 BST 2 GND 3 FB 4 EN 5 VIN 6 SW) = EasyEDA; divider R12 6k8 / R15 1k3 gives 0.8 V x (1+6.8/1.3) = 4.98 V (as V1).
- TS-1187A-B-A-B (C318884): EasyEDA symbol shows pins 1-2 shorted (top row) and 3-4 shorted (bottom row), footprint identical; our SW1/SW2 wiring (1,2 -> EN/BOOT; 3,4 -> GND) is right.
- JP1 OPEN: `ESP_TX` (GPIO17) and `MCU_TX` are separate nets, `MCU_TX` has R27 100k to V3V3, OC2 anode via R14 from V3V3, so with JP1 open no LED current flows and the bus stays idle (also with USB unplugged). JP2 open: `P2_3V3` only reaches V3V3 through JP2. JP pads have no paste (checked in circuit.json: JP1/JP2 pads have no `pcb_solder_paste`), gap 0.4 mm.
- BOM == design: every placed part with LCSC number is in the BOM with the identical LCSC (cross-checked designator by designator); JP1/JP2/TP1-3 correctly absent.
- Gerber vs circuit.json: 126 vias in both; `check_fab.py` and `check_isolation.py` pass when I ran them.

## Findings

### M1 - MAJOR - U1 (LM393, C7955) uses the generic tscircuit `soic8` land pattern, ~0.55 mm off the real one
- Evidence: `src/ems-side.tsx:170` `footprint="soic8"`. In `dist/index/circuit.json` the pads are 1.0 x 0.6 mm with row centre-to-centre 4.3 mm (outer 5.3 mm). EasyEDA C7955 (SOIC-8_L5.0-W4.0-P1.27-LS6.0) has pads 1.95 x 0.57 mm, row centre-to-centre 5.41 mm (outer 7.4 mm). tscircuit itself warns: `supplier_footprint_mismatch_warning ... "soic8" does not match jlcpcb:C7955 (copper IoU 0.7163)`. SOIC-8 lead foot spans about +-2.17..3.0 mm from centre; our pad covers only 1.65..2.65 mm, i.e. the toe (0.35 mm) is not on copper and the pad intrudes 0.3 mm under the body (inner edge 1.65 vs body half-width 1.95). CPL position check gives the worst pad error of the whole BOM (0.56 mm).
- Risk: weak or tombstoned solder joints on the only comparator of the RX/TX path (reflow still usually works, so not a blocker, but it is the one footprint that is clearly sub-standard).
- Fix: replace by a custom footprint copied from EasyEDA (pads at x = +-2.705 mm, y = +-1.905/+-0.635 mm, 1.95 (along x) x 0.57 mm, pad1 top-left, pins 1-4 left side down, 5-8 right side up), as already done for the optocouplers; or use the footprinter with explicit pad length/width and an outer width of 7.4 mm. Keep CPL rotation (270) - it stays valid because the EasyEDA frame is used. Re-run routing (the EMS side around U1 is dense).

### m1 - MINOR - BAT42W (D1-D5) library part has pad 1 = anode, opposite to the usual SOD-123 convention
- Evidence: EasyEDA C22466362 symbol pin 1 = A, pin 2 = K, silkscreen triangle/bar drawn with the bar at pad 2; `lib/diodes.tsx:3,15` and `PAD_SWAP` in `src/ems-side.tsx:118,126` compensate correctly (checked in the routed copper: D2.2 and D4.2 on GND_EMS are the anode pads). C81598 and C8598 use pad 1 = K.
- Risk: if JLC's pick-and-place orientation DB for this user-contributed (R+O, "BAT42W_C22466362") footprint were wrong, the bridge D1-D4 and clamp D5 would be reversed. The data is internally consistent, so this is a verification item, not a defect.
- Fix: in the JLC order preview (PCBA "Component placement" 3D view) check cathode band orientation of D1-D5 against the board silkscreen before paying; keep a photo of the result.

### m2 - MINOR - L1/L2 (LQH32PN4R7NN0L, C98021) footprint is the V1 `L3225M`, not the LCSC footprint
- Evidence: `lib/thtparts.tsx:47-56` pads 1.6 x 2.2 at +-1.4 mm (c-c 2.8, outer 4.4). EasyEDA IND-SMD_L3.2-W2.5: pads 1.52 x 3.1 at c-c 2.29 (outer 3.81). tscircuit warning IoU 0.6394.
- Impact: inner pad edge (0.8 mm) coincides with the terminal inner edge of the 3.2 mm body, outer edge extends 0.6 mm beyond the terminal: solderable, lower mechanical strength than the vendor land pattern; also keep-in is larger than the part.
- Fix: use pads 1.52 x 3.1 mm at x = +-1.145 mm (vendor/EasyEDA); re-run routing.

### m3 - MINOR - Opto LED current of OC2 is thin for the 6N136 CTR floor
- Evidence: JLC lists C336082 CTR = 19 % (min at IF = 16 mA, 6N136 class). With R14 = 270 R (`src/ems-side.tsx:228`), V3V3 = 3.3 V, Vf = 1.4 V, GPIO low 0.1 V: IF = 6.7 mA, IC(min) is about 1.3 mA, while R11 4k7 / 5 V needs 0.94 mA to bring VO below the 0.6 V comparator reference (margin 1.35x; with Vf = 1.7 V 1.13x, before LED ageing and temperature). Same values as V1, so not a regression, but V1 never had to meet a 3.3 V rail from an LDO.
- Fix (optional, cheap): R14 = 220 R (C17557, Basic) -> IF about 8.2 mA, GPIO sink still well inside limits; or keep 270 R and accept as V1.

### m4 - MINOR - LM393DR2G is a 0..70 deg C part
- Evidence: JLC attributes of C7955 "Operating Temperature 0C~+70C"; V1 schematic value is LMV393 (-40..125 C). Also VOL of LM393 (up to ~0.4 V at 4 mA) slightly reduces OC1 IF (5 V - 1.38 V - VOL)/470 = 6.4-7 mA vs the 5 mA threshold of 6N137: still OK.
- Fix: acceptable for indoor heating-room use; for an industrial range use LM2903 (-40..105 C, check JLC stock) with the same pinout. DESIGN_SPEC already accepts LM393.

### m5 - MINOR - USB VBUS has no fuse/series protection
- Evidence: `src/mcu-side.tsx:348,377`: J2 VBUS goes straight to U4/C24/C25/U5.VIN; no PTC/ideal diode. A fault on the AMS1117 or C29 loads the host directly (hosts limit current, but cheap boards usually add a 500 mA PTC).
- Fix: optional 0805 PTC (e.g. the already used F1/F2 part C910822) between J2.VBUS and the VBUS net; drop-in, one more extended-part line is not needed (same LCSC).

### m6 - MINOR - Green status LEDs are driven at under 1 mA from 3.3 V
- Evidence: C2297 Vf = 2.6-3.1 V (JLC attribute); LD2/LD3 via 1.2k (`src/ems-side.tsx:229-230`, V1 values), LD4 via R22 1k, LD5 via R26 1k (`src/mcu-side.tsx:331,392`) give roughly 0.3-0.8 mA: visible but dim, TX/RX activity flashes may hardly be visible.
- Fix: R22/R26 -> 470 R (C17710, already in BOM, Basic); R18/R19 -> 470 R (V1 deviation, optional).

### m7 - MINOR - JP1/JP2 solder-mask opening
- Evidence: `lib/jumper.tsx`: two separate rect pads with a 0.4 mm gap; tscircuit gives each pad its own mask opening, so a 0.4 mm mask web may remain between the pads. Soldering a blob across a mask web works, but a single opening is the common practice (KiCad `SolderJumper-2_P1.3mm_Open`).
- Fix: check Gerber `F_Mask.gbr` at JP1/JP2; if a web exists, enlarge the mask opening of both pads (mask margin) so the two openings merge into one. Not functional for the default (open) state.

### m8 - MINOR - P2 header pad/drill smaller than the vendor footprint
- Evidence: `<pinheader>` in `src/mcu-side.tsx:406` gives pads 1.5 mm / hole 1.0 mm; EasyEDA C32713270 (HX PZ2.54-1x4P): pad 1.7 mm / hole 1.1 mm. 0.64 mm square pin diagonal 0.9 mm in a 1.0 mm hole is tight for hand/wave soldering and pin tolerance.
- Fix: custom footprint with holeDiameter 1.1 mm, outerDiameter 1.7 mm (square pad 1.7 for pin 1), pitch 2.54.

### m9 - MINOR - C29 and the output capacitors are 10-16 mm from the AMS1117 VOUT pin
- Evidence: from pad coordinates: C29 10.1 mm, C27 9.2 mm, C26 14.4 mm, C28 16.4 mm from U5.2; C22/C23 4.2/6.4 mm from U3.2 (fine); C24/C25 4.4/5.2 mm from U5 VIN. DESIGN_SPEC says C29 "next to U5". The V3V3 pour (x 8..24.5, y 19..29.5) keeps inductance low and the LDO output cap needs ESR, not proximity, so this is a layout nicety only.
- Fix: move C29 (and C27) to within about 6 mm of U5 pin 2 if board space allows; no netlist change.

### m10 - MINOR - JLC cost: R15 (1.3k, C17384) is an Extended part; many other Extended parts
- Evidence: Extended (fee) parts in the BOM: C107120, C49256851, C910822, C165948, C98021, C43183, C92651, C336082, C441236, C32713270, C53284030, C17384, C371172, C2913202, C7519 (15, all in stock). "Preferred extended" (no fee): C1717, C22466362, C20069155, C17590. Only R15 has a trivial Basic alternative: R12 = 5.1k (C27834) / R15 = 1k (C17513) -> 0.8 V x (1 + 5.1) = 4.88 V rail (-2 %), all other consumers (6N137 VCC, LM393) unaffected. The LCSC numbers were verified for correct value/package; no part is out of stock.
- Fix: optional; saves one extended-part fee. Decide, then update BOM/CPL.

### m11 - MINOR - KF2EDGRC-5.08-2P (P1) is the board-side header only
- Evidence: C441236 is the right-angle pluggable-terminal header (EasyEDA CONN-TH_P5.08_KF2EDGRC-5.08-2P: pads 2.5 mm, drill 1.8 mm, pitch 5.08 mm - our footprint is identical). The mating plug (KF2EDGK-5.08-2P class) is not in the BOM, so the user must supply it.
- Fix: add a note in README/BOM comment (or an additional line, "not assembled").

## INFO (no action, for the record)
- `fab/*` (09:40) are slightly older than `dist/index/circuit.json` (09:41); via counts and `check_fab.py` agree, but re-export (`scripts/export_fab.sh`) after the final fix of M1 anyway.
- Other tscircuit mismatch warnings (SOD-123 D1-D7, IoU 0.74-0.78) are only pad-size differences (ours 1.2 x 0.9 at c-c 3.3, EasyEDA 1.2 x 1.4 at c-c 3.4); pad numbers are consistent, accepted. SOT-23/-6 (Q1, U2, U4), SOT-223 (U5), 0805/1206 pads differ by 0.05-0.4 mm from EasyEDA but are standard land patterns.
- OC1/OC2 pads are 9.5 mm c-c (EasyEDA 9.09 mm); the lead foot (tip at +-5.15 mm) is fully covered by 3.85..5.65 mm, fine; keeps the V1 creepage.
- THT parts: P1, P2, J2 shell legs need JLC through-hole/manual assembly; confirm quote.
- EMS-ESP32: choose board profile `S32S3` (or set GPIOs LED 2, Rx 5, Tx 17, button 0 manually); there is no Dallas (GPIO18) header on the board - not needed.
- No tscircuit errors in `circuit.json` (no `pcb_*_error`); only refdes-convention, availability, and pin-spec warnings.
