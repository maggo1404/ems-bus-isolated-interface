# FIX_LIST_R2 - fixes for review R4 (circuit / footprints) and R5 (isolation / layout / fab)

Status after `scripts/export_fab.sh 120s`: `check_netlist.py` ALL OK, `check_isolation.py` 7.047 mm top / 7.400 mm bottom (>= 6.0), `check_fab.py` 0 FAIL / 0 WARN,
`tsci build` autorouting errors: none (no `errors.json`), `tsci check shorts`: no shorts. JP1/JP2 open (no paste, one merged mask opening), every part keeps its LCSC number.
Status values: DONE = changed and checked, DOC = documented decision / manual step, NOT CHANGED = reason given.

## R5 (isolation / layout / fab)
| Finding | Action | Status |
|---|---|---|
| M1 paste apertures 70 % x 70 % | Source: tscircuit core (`getSolderPasteSize` = pad x 0.7 when no margin is set), not the Gerber exporter. `<board defaultSolderPasteMargin="0mm">` -> 100 % of the pad on all SMD pads; JP1/JP2 and TP1..3 `noSolderPaste`; paste on the J2 shell slots removed by `scripts/postprocess_gerbers.py`. `check_fab.py` G6 parses F_Paste/B_Paste: 252 pads, aperture/pad area 100..100 %, JP1/JP2 without paste. Mask expansion stays 0 (JLC adds its own compensation, see m4) | DONE |
| M2 C10 not at U2 VIN | C10 (10 uF) and new C30 (100 nF) placed at U2 pin 5 (pad edge to pad edge 0.36 mm, hand-routed 0.5 mm VIN trace < 2 mm, no vias), GND through the pour/via; L3 moved 2.85 mm towards U2 (SW trace 3.3 mm instead of 5.3 mm); R12/R15/R16/R10/C8/R11 nudged for the router (see TSCIRCUIT_API.md) | DONE |
| M3 via pairs < 0.8 mm | Board `minViaHoleEdgeToViaHoleEdgeClearance="0.25mm"` (router honours it); new check `check_fab.py` G4: hole edge to hole edge >= 0.25 mm same net, >= 0.5 mm different nets, vias + round PTH. Result: all 126 holes pass, smallest gap 0.250 mm (the four R5 pairs are gone; the only pair left after the re-route, V5_EMS at (-13.5/9.4), was removed by the router setting) | DONE |
| m1 silkscreen stroke / text | Text >= 1.0 mm (labels TX EN, 3V3 OUT, PWR, RX, TX, 3V3, TP labels, ICs); stroke >= 0.15 mm in the Gerber (`postprocess_gerbers.py`, tscircuit writes 0.09 x font size); refdes of the 0805/1206 R and C hidden (1.0 mm does not fit between the pads, assembly drawing docs/img/assembly.png has them). G5 checks text height + Gerber stroke width | DONE |
| m2 silk over exposed pads | G5 check added (per item <= 0.30 mm2). U3, J2, SW1/SW2, P1 outlines redrawn off the pads and off the board edge, "3V3" label moved from U3.14 to (26.0 / 5.9). Remaining: 0.62 mm2 total (C10/C30/C27/C29/C24 0805 outlines touching a neighbour pad; JLC clips silk on pads). "ISOLATION BARRIER" text across the barrier unchanged (harmless) | DONE (remaining overlaps accepted) |
| m3 JP1/JP2 two mask openings | `solderMaskMargin="0.22mm"` on the jumper pads -> one common opening 2.04 x 3.24 mm, verified in F_Mask (`check_fab.py` G7) | DONE |
| m4 mask expansion 0 | Not changed: JLC adds its own mask expansion (about 0.05 mm) in CAM; a file expansion would eat the 0.2 mm web at the 0.5 mm-pitch USB-C pads. Documented in FAB_CHECKLIST | DOC |
| m5 clearance 0.196..0.215 | `CLEAR_TOL` tightened 0.002 -> 0.0005 mm: all different-net copper >= 0.2 mm except 4 fine-pitch pairs at U4 (VBUS vs USB_DP/DN 0.152..0.192 mm, JLC minimum 0.1). Raising the router clearance props to 0.22/0.25 mm broke the routing (dozens of errors), so the props stay 0.2 mm | DONE / limit documented |
| m6 GND stitching 0.25 mm, VBUS narrowing | Not changed: solid pours on both layers carry GND; VBUS narrowing (>= 0.31 mm, only near fine-pitch pads) is now behind the 500 mA PTC F3 on the board side and below 0.9 A | NOT CHANGED |
| m7 USB pair length / vias | Not changed: full-speed only (USB serial/JTAG), tolerated per R5; re-routing the pair is not possible without destabilising the autorouter | NOT CHANGED |
| m8 thermal U5, USB-C opening, light pipes | U5: not changed (143 + 146 mm2 pour + 8 vias, +12..30 K acceptable, R5). ENCLOSURE.md: USB-C opening 12 x 7 mm for the 2.3 mm recess (overmoulded plugs), light pipes about 25 mm (planning value, check post height in the Hammond STEP) | DONE (U5 NOT CHANGED) |
| m9 process residuals | (a) JLC preview rotation check of all 90/270/polarised parts, (b) tscircuit `bom.csv`/`pick_and_place.csv` now removed from the Gerber zip by `postprocess_gerbers.py`, (c) THT P1/P2/J2 legs need JLC THT service, (d) post grid vs STEP, (e) NPTH pegs: (a), (c), (d) listed in FAB_CHECKLIST "Manuelle Pruefung", (e) accepted | DONE (b) / DOC |
| Antenna note (INFO) | C22/C23/R22/LD4 stay beside the keepout as before | NOT CHANGED |

## R4 (circuit / footprints)
| Finding | Action | Status |
|---|---|---|
| M1 U1 LM393 generic soic8 | Custom footprint `lib/soic8_lm393.tsx` copied from EasyEDA C7955 (pads 0.568 x 1.95, rows 5.41 mm apart, outer 7.4 mm), placed with pcbRotation 270; re-routed; `cpl_check.py`: theta 0, residual 0.000 mm (was 0.555 mm), CPL rotation 270 | DONE |
| m1 BAT42W orientation | Footprint/PAD_SWAP verified in copper by R4; manual check of the cathode bands in the JLC preview added to FAB_CHECKLIST ("Manuelle Pruefung") | DOC |
| m2 L1/L2 land pattern | `Inductor3225` = EasyEDA C98021: pads 1.52 x 3.1 at +-1.145 mm; re-routed; CPL residual 0.000 mm | DONE |
| m3 OC2 LED current | R14 270R -> **150R (C17471, Basic)**: worst case IF 8.7 mA, IC(min 19 % CTR) 1.65 mA = 1.76 x the 0.94 mA needed (270R: 0.98 x); GPIO17 sink 12 + 2.3 mA typical (16 mA worst), OC2 LED <= 13.1 mA. Calculation in docs/netlist_v1.md "V2 deviations" | DONE |
| m4 LM393 0..70 C | Kept: LM393DR2G C7955 is Basic; the -40..125 C LM2903DR (C7549) / LM2903DR2G (C57474) are all Extended (+1 fee, 15 -> 16 Ext lines) so there is no Basic/Preferred -40 C part. Option documented in JLCPCB_PARTS.md (same SOIC-8 pinout: swap LCSC number only) | DOC |
| m5 VBUS fuse | F3 = BSMD0805-050-24V (C910822, 500 mA hold, same part as F1/F2, no extra Extended fee) between J2/U4 `VBUS` and new net `VBUS_F` (U5.VIN, C24, C25); check_netlist / netclass / check_fab updated | DONE |
| m6 green LEDs < 1 mA | R18, R19, R22, R26 -> 220R (C17557, Basic): about 2.3 mA typ. (0.9..3.2 mA over Vf 3.1..2.6 V) | DONE |
| m7 JP1/JP2 mask | see R5 m3 (merged opening) | DONE |
| m8 P2 hole / pad | `PinHeader1x4` footprint: hole 1.1 mm, pad 1.7 mm, pin 1 square (EasyEDA C32713270), CPL residual 0.000 mm | DONE |
| m9 C29 / C27 distance to U5 | C29 -> (14.6 / 18.3) rot 270: pad 2.8 mm from the AMS1117 VOUT tab pad (was 8.8 mm to pin 2); C27 -> (14.8 / 22.6): 3.1 mm from the tab pad. C26/C28 unchanged (bulk/HF at the module side, R4: layout nicety) | DONE |
| m10 R15 Extended part | Not changed. R12 5k1 / R15 1k would put the buck output at 4.88 V (-2 %; JW5017S FB 0.8 V reference, V1 design 4.98 V). V5_EMS feeds 6N136 VCC (min 4.5 V), 6N137 LED current via R10 (needs 5 mA, 6.4..7 mA today), the comparator U1 and the 5 V bias of R9/R11: the V1 values were tuned for 5.0 V, so the saving (one Extended fee, about 3 USD per order) does not justify a different rail. Decision documented in JLCPCB_PARTS.md | NOT CHANGED |
| m11 P1 mating plug | Not in the BOM; listed in JLCPCB_PARTS.md and ENCLOSURE.md (2-pole 5.08 mm pluggable screw plug, KF2EDGK-5.08-2P / Phoenix MSTB 2,5/2-STF-5,08 class, distributor article number not verified) | DOC |
| INFO re-export after M1 | `scripts/export_fab.sh` run after the last change; fab/ files, docs/img PNGs and docs/CPL_CHECK.md regenerated | DONE |

## New / changed tooling
* `scripts/postprocess_gerbers.py` (silk stroke, bom/pnp removal, paste on plated slots), called by `scripts/export_fab.sh` step 3b.
* `scripts/check_fab.py`: G4 hole-to-hole, G5 silkscreen (height, stroke, off pads), G6 paste vs pads, G7 JP mask merge, `CLEAR_TOL` 0.0005, narrow-segment coordinates printed.
* `scripts/check_netlist.py`: VBUS / VBUS_F, C30 mirrors C10.
