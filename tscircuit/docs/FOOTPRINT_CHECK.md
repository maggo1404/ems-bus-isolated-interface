# Footprint check vs real EasyEDA / JLCPCB footprints (2026-11-26)

Source of reference data: JLCEDA / EasyEDA official library (https://easyeda.com , https://lceda.cn), fetched via
`https://easyeda.com/api/products/<LCSC>/components?version=6.4.19.5` (pad coordinates in 10 mil units, converted to mm
and to a Y-up frame, same as tscircuit `pcbX/pcbY`). Lib files were NOT edited; apply the corrections below in
`lib/usbc16.tsx`, `lib/esp32s3wroom1.tsx`, `lib/thtparts.tsx`, `lib/opto_so8_gw300.tsx` (applied in V1 of the layout; see the addendum at the end for the R4/R5 follow-up).
Priority: **1. tactile pad-to-net mapping (functional bug), 2. USB-C pad order vs mating direction (functional bug),
3. ESP32 EPAD + bottom row, 4. USB-C shell offsets, 5. opto/inductor/terminal geometry.**

---
## 1. Tactile switch `Tactile5x5` (TS-1187A-B-A-B, C318884) -- FUNCTIONAL BUG
Real footprint `SW-SMD_4P-L5.1-W5.1-P3.70-LS6.5` (centre origin, Y up):

| Pad | x | y | size (x * y) |
|---|---|---|---|
| 1 | -3.00 | +1.85 | 1.00 x 0.75 |
| 2 | +3.00 | +1.85 | 1.00 x 0.75 |
| 3 | -3.00 | -1.85 | 1.00 x 0.75 |
| 4 | +3.00 | -1.85 | 1.00 x 0.75 |

The EasyEDA symbol shows **1 and 2 permanently connected (top row, y=+1.85) and 3 and 4 permanently connected
(bottom row, y=-1.85)**; pressing the button connects the two rows (pitch 3.70 mm).
Current lib: port `pin1` = both LEFT pads (x=-3, y=+-1.85), `pin2` = both RIGHT pads (x=+3). With the real switch this
would short A to B permanently (top-left and top-right are the same terminal) -> EN / GPIO0 stuck low.
**Fix:** `pin1` pads at (-3.0,+1.85) and (+3.0,+1.85); `pin2` pads at (-3.0,-1.85) and (+3.0,-1.85); all pads
`width=1.0mm height=0.75mm` (lib has 1.4 x 1.0; positions are right). Body outline 5.1 x 5.1 as in lib.

---
## 2. USB-C `UsbC16Footprint` (HRO TYPE-C-31-M-12, C165948)
Real footprint `USB-C_SMD-TYPE-C-31-M-12_1`. EasyEDA frame converted so the signal-pad row is at y=0 and x as in
EasyEDA top view. In that frame the **mating face is toward -Y** (body spans y = -7.57 ... -0.23, i.e. the 12 SMD tails
stick out of the rear edge at y=0; body width 8.94 -> x = -4.47 ... +4.47):

| Pad | x | y | size | note |
|---|---|---|---|---|
| A1B12 (GND) | -3.20 | 0 | 0.6 x 1.3 | |
| A4B9 (VBUS) | -2.40 | 0 | 0.6 x 1.3 | |
| B8 (SBU2) | -1.75 | 0 | 0.3 x 1.3 | |
| A5 (CC1) | -1.25 | 0 | 0.3 x 1.3 | |
| B7 (DN) | -0.75 | 0 | 0.3 x 1.3 | |
| A6 (DP) | -0.25 | 0 | 0.3 x 1.3 | |
| A7 (DN) | +0.25 | 0 | 0.3 x 1.3 | |
| B6 (DP) | +0.75 | 0 | 0.3 x 1.3 | |
| A8 (SBU1) | +1.25 | 0 | 0.3 x 1.3 | |
| B5 (CC2) | +1.75 | 0 | 0.3 x 1.3 | |
| B4A9 (VBUS) | +2.40 | 0 | 0.6 x 1.3 | |
| B1A12 (GND) | +3.20 | 0 | 0.6 x 1.3 | |
| shell rear pair | +-4.325 | **-0.768** | PTH outer 1.2 x 2.0, slot 0.8 x 1.5 | EasyEDA pads 1,4 |
| shell front pair | +-4.325 | **-4.948** | PTH outer 1.2 x 1.8, slot 0.8 x 1.2 | EasyEDA pads 2,3 |
| NPTH peg holes | +-2.90 | -1.268 | drill 0.6 | missing in lib |

Findings vs `lib/usbc16.tsx`:
* Signal pad X positions and widths are correct; pad height should be **1.3 mm** (lib 1.15).
* **Mating-direction bug:** lib places the mating face at +Y but keeps the EasyEDA left-to-right pad order, which is only
  correct when the mating face is at -Y. With the face at +Y the connector is a 180-degree rotation, so the order must be
  mirrored in X or D+/D- (and CC1/CC2, SBU) land on the wrong pads (D+ pads at x=-0.25/+0.75 would physically be D-).
  **Option A (keep lib order, simplest):** mating face toward -Y: keep x as listed above, use the Y values in the table
  (shell rear -0.768, front -4.948, NPTH -1.268, silk body y = -7.57 ... -0.23) and place the part rotated accordingly.
  **Option B (mating face +Y as lib comment says):** negate both x and y of every entry: signal pads left to right
  GND(-3.2), VBUS(-2.4), CC2(-1.75), SBU1(-1.25), DP(-0.75), DN(-0.25), DP(+0.25), DN(+0.75), CC1(+1.25), SBU2(+1.75),
  VBUS(+2.4), GND(+3.2); shell rear pair y=+0.768, front pair y=+4.948, NPTH (+-2.9,+1.268), silk y=+0.23 ... +7.57.
* Shell legs: lib front pair y=4.5 (1.0 x 2.1, hole 0.6 x 1.7) and rear pair y=0 (1.0 x 1.6, hole 0.6 x 1.2) -> real are
  y=4.948 (1.2 x 1.8, slot 0.8 x 1.2) and y=0.768 (1.2 x 2.0, slot 0.8 x 1.5) in the Option-B frame; x=+-4.325 (lib 4.32 ok).
  Note the *longer* leg is the one closer to the SMD row, opposite to the lib.
* Silkscreen: lib y -1.0 ... 6.35 (7.35 deep, but offset); real body 7.34 deep from y=0.23 to 7.57 (Option B).

---
## 3. ESP32-S3-WROOM-1 `Esp32S3Footprint` (C2913202)
EasyEDA footprint `WIRELM-SMD_ESP32-S3-WROOM-1`; body 18.0 x 25.5, antenna end +Y. Converted to module-centre frame
(centre = body bbox centre; the EasyEDA origin is 3.6465 mm below it in Y, so y_lib = y_easyeda - 3.6465):
* Left pads 1..14: x=-8.75, y = 5.25 - (n-1)*1.27, 1.5 x 0.9. Lib 5.26: matches within 0.01 mm. OK.
* Right pads 27..40: x=+8.75, y = -11.26 + (n-27)*1.27 (lib -11.25): OK.
* Bottom pads 15..26: x = -6.985 + (n-15)*1.27 (matches), **y = -12.54** (pad 0.9 wide x 1.5 tall, so it overhangs the body
  edge y=-12.75 by 0.54 mm). **Lib uses y=-12.0: wrong by 0.54 mm** (pads would sit entirely under the body and the
  solder fillet area outside is missing). Fix: `pcbY={-12.54}`.
* **EPAD (pin 41) is not centred:** real = 3x3 array of 0.9 x 0.9 pads (all `pin41`), pitch 1.4, pad centres
  x in {-2.9, -1.5, -0.1}, y_lib in {-3.87, -2.47, -1.07}; overall **3.7 x 3.7 mm centred at (-1.5, -2.47)**.
  Lib has one 3.9 x 3.9 pad at (0, -3.0): **off by 1.5 mm in X and 0.53 mm in Y**. Cross-checked with a second EasyEDA
  entry (C2913197): same EPAD offset (-1.5 in X, 7.72 mm below the pin-1 pad). Use either the 9 small pads or one
  3.7 x 3.7 pad at (-1.5, -2.47).
* Pad numbering/positions otherwise identical to lib; pin 1 = top left (antenna side). Keepout (lib y=9.25, 7 mm high)
  is plausible: Espressif asks keep-out for the antenna area; the antenna-end of the body is y=+12.75.

---
## 4. 6N137 / 6N136 `OptoSo8Gw300Footprint` vs real parts (row pitch 9.38?)
EasyEDA footprints of the stocked SMD-8 gull-wing 2.54 mm parts (pitch along the row 2.54 mm in all cases; coordinates
here = distance between pad-row centres, pad size across-row x along-row):

| Part (LCSC) | package | row centre-to-centre | pad (across x along) |
|---|---|---|---|
| 6N137S-TA1-L Lite-On (C92651), 6N136S-TA1-L (C336082), Everlight 6N136S(TA) (C118756) | SOP-8 L9.8 W6.6 LS10.3 | **9.09** | 1.78 x 1.525 |
| Everlight 6N137S(TA)-V (C883170), onsemi 6N136SDM (C24402) | SMD-8 LS10.3 | 9.60 | 2.60 x 1.78 |
| onsemi 6N137SDM (C15825) | OPTO-SMD-8P LS10.0 | 10.05 | 2.45 x 1.42 |
| UMW 6N137S (C5123515) | SMT-8 | 9.90 | 2.00 x 1.80 |
| Broadcom 6N137-560E (C691908) | SMD-8 LS9.7 | 8.87 | 1.95 x 1.42 |

Lib / Eagle SO8-GW300: row 9.38, pad 1.0 x 1.27: all stocked parts have lead tip-to-tip (LS) 9.7-10.3 mm, so
tips reach out to +-4.85...5.15 from centre; lib pad spans x = 4.19 ... 5.19, i.e. covers the foot of all parts but is
small (1.0 mm across, 1.27 along; real 1.5-1.8 along). It will solder, but for reliability use
**pad 1.8 (across) x 1.4 (along), row centres +-4.75 (9.50)**: spans 3.85 ... 5.65, inner edge stays > 3.3 (body half
width) and covers all variants. Pin 1 location and pitch 2.54 (y = +-1.27, +-3.81!) -> **note lib uses +-3.937 for the outer
pads, real pitch is 2.54 so the outer pads are at +-3.81**. (3.937 is the Eagle value; the lbr pads are 0.127 mm further out.
Real parts: 3.81. With 1.4-long pads the difference is tolerable but fix to 3.81 if the footprint is rewritten.)
Creepage across the part body stays the package's (isolation over the 10.3 mm / 6.6 mm body fine; the board cutout slot
is below the body, as per DESIGN_SPEC).

---
## 5. Other footprints touched by the new part choices
* **L3** (`Inductor0520`, pads 2.0 x 2.5 at +-2.5): real SWPA5020S4R7MT (C43183) = pads 2.124 x 4.22 at x=+-2.0 (pads span x 0.94 ... 3.06, 4.22 tall); ZECD54-4R7M (C41408590) = pads 2.5 x 5.5 at +-2.0; SWPA4030S4R7MT (C57269)
  = pads 1.6 x 3.5 at +-1.6. The lib pads are too short (2.5) and too far out (centres 2.5); replace by
  `width=2.124mm height=4.22mm pcbX=+-2.0` for C43183.
* **L1/L2** (`Inductor3225`, 1.6 x 2.2 at +-1.4): fine for 3.2 x 2.5 inductors (LQH32PN4R7NN0L uses 1.52 x 3.1 at +-1.145;
  TDK L1210 uses 1.2 x 2.0 at +-1.6); lib pads cover the terminals, keep.
* **P1** (`Mstba2`): real KF2EDGRC-5.08-2P: pads at x=+-2.54, pad 2.5 mm, **drill 1.8 mm** (lib drill 1.4 -> too small for
  the pins; set `holeDiameter=1.8mm`, `outerDiameter=2.8mm` is fine). KF2EDGR-5.08-2P: drill 1.6, pad 2.5.
* **P2 header 1x4 2.54** (HX PZ2.54-1x4P ZZ C32713270): pads 1.7 round (pad 1 square), drill 1.1, x = -3.81, -1.27, +1.27, +3.81.
* **C12** (`CapE5_10p5`, +-2.54, drill 1.016, pad 2.54): real PA25V2200M10x17: pitch 5.0 (x=+-2.5), drill 1.0, pad 1.6; the
  0.08 mm offset per lead is irrelevant for a 0.6 mm lead; body 10 mm dia (silk circle r=5.25 is fine).

---
## Nachtrag nach Review R4/R5 (V2-Fixes)
* **U1 LM393 (C7955)**: eigener Footprint `lib/soic8_lm393.tsx` aus EasyEDA SOIC-8_L5.0-W4.0-P1.27-LS6.0-BL (Pads 0,568 x 1,95 mm, Reihenabstand 5,41 mm, Aussenmass 7,4 mm), Pin 1 = (-1,905 / -2,705) im EasyEDA-Rahmen, Platzierung pcbRotation 270. `cpl_check.py`: theta 0, Restfehler 0,000 mm (vorher generisches `soic8`: 0,555 mm).
* **L1/L2 (C98021)**: `Inductor3225` = EasyEDA IND-SMD_L3.2-W2.5 (Pads 1,52 x 3,1 mm bei x = +-1,145 mm), Restfehler 0,000 mm.
* **P2 (C32713270)**: `PinHeader1x4` (`lib/thtparts.tsx`) = Loch 1,1 mm, Pad 1,7 mm (Pin 1 quadratisch), Raster 2,54 mm.
* U3-, J2-, SW-, P1-Silkscreen so gezeichnet, dass keine Linie ueber einem Pad liegt (siehe FAB_CHECKLIST).
