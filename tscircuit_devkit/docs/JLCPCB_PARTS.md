# JLCPCB / LCSC parts plan

**Verified online on 2026-11-26.** Every LCSC number below was looked up in the JLCPCB parts library
(`jlcpcb.com/api/.../selectSmtComponentList`: library type base/expand, preferred flag, stock) and cross-checked with
`jlcsearch.tscircuit.com` (value/package/mfr). Stock = JLC stock count on that day. Footprints were compared with the
EasyEDA library (see `docs/FOOTPRINT_CHECK.md`).

Class: **Basic** = no extra fee. **Pref** = "Preferred Extended" (no extra feeder fee, treated like Basic for cost).
**Ext** = Extended (one-time loading fee per distinct part number, ~3 USD each). Basic/Extended status can change; re-check
at order time (`npx tsci import --jlcpcb "<Cnumber>"` or jlcpcb.com/parts).

In tscircuit set the number on the component: `supplierPartNumbers={{ jlcpcb: ["C17414"] }}`.

## Corrections versus the previous (unverified) revision
| Item | Was | Now | Why |
|---|---|---|---|
| R14 270R | C17697 (Basic) | **C17590** (Pref) | C17697 is 44.2 kOhm! 270R is not Basic, only Preferred |
| C1 68p | C1799 (Basic?) | **C107120** (Ext) | C1799 is 200 pF; no 68 pF is Basic (47 pF C14857 is, see notes) |
| R15 1k3 | "Basic?" | **C17384** (Ext) | 1.3k is not Basic |
| C3/C4 1n5 | "look up" | **C1717** (Pref) | |
| LM393 | C7955 "Ext" | C7955 is **Basic** | = LM393DR2G (onsemi, 0..70 C); TI LM393DR is C67470 (Ext) |
| SW tactile | C318884 "Ext" | C318884 is **Basic** | stock 651k |
| 100n | C49678 / C1710 | 100n **C49678**, 10n **C1710** (both Basic); note C1711 (CL21B104KBCNNNC) is Ext, do not use | |
| LD2/LD3 green | "look up" | **C2296** yellow KT-0805Y (Basic) (R3: C2297 green KT-0805G has Vf 2.6-3.1 V, unusable on 3.3 V) | |
| 1n | C46653 | ok (Basic) | |

## Verified table
| Ref (Eagle) | Value / function | Package | Part (mfr) | LCSC | Class | Stock | Notes |
|---|---|---|---|---|---|---|---|
| U3 (ESP) | ESP32-S3-WROOM-1-N16R8 | module 25.5x18 | Espressif ESP32-S3-WROOM-1-N16R8 | C2913202 | Ext | 35.7k | **DNP / hand-solder (Economic PCBA: JLC part page says "PCBA Type: Standard Only", true for all ESP32-S3 modules, docs/JLC_ECONOMIC.md)**; `doNotPlace` in `src/mcu-side.tsx`, not in BOM/CPL. `lib/esp32s3wroom1.tsx`: EPAD = 9 ports pin41..49 (all GND) |
| J2 | USB-C 16P USB2.0 | SMD+THT | HRO TYPE-C-31-M-12 | C165948 | Ext | 425k | `lib/usbc16.tsx`: 16 distinct ports (12 pads + 4 shell legs), pairs tied by nets |
| U5 (LDO) | 3.3V 1A LDO | SOT-223 | AMS1117-3.3 (AMS) | C6186 | **Basic** | 1.2M | OK |
| (alt) | 3.3V 600mA LDO | SOT-23-5 | AP2112K-3.3TRG1 (Diodes) | C51118 | Ext | 9.7k | fallback |
| (alt) | 3.3V 1A LDO | SOT-23-5 | TLV75733PDBVR (TI) | C485517 | Ext | 36k | best performance |
| U4 (ESD) | USB ESD | SOT-23-6 | USBLC6-2SC6 (ST) | C7519 | Ext | 35k | 3.5 pF; no Basic equivalent |
| SW1/SW2 | tactile 5.1x5.1 | SMD-4P | TS-1187A-B-A-B (XKB) | C318884 | **Basic** | 652k | pads 1/2 (top row) = A, 3/4 (bottom) = B; each pad own port |
| OC1 | 6N137 | SOP-8 2.54 gull-wing | **6N137S-TA1-L (Lite-On)** | **C92651** | Ext | 60k | 2.7-5.5 V, 15 Mbit/s, 5 kV; alts C883170 Everlight 6N137S(TA)-V (16.7k), C15825 onsemi 6N137SDM (64k) |
| OC2 | 6N136 | SOP-8 2.54 gull-wing | **6N136S-TA1-L (Lite-On)** | **C336082** | Ext | 8.6k | same footprint as C92651; alts C118756 Everlight 6N136S(TA) (7.8k), C3015393 Everlight 6N136S1(TA) (11.7k) |
| U1 | LM393 | SOIC-8 (V2 footprint = EasyEDA C7955: pads 0.568 x 1.95, rows 5.41 mm apart, `lib/soic8_lm393.tsx`) | LM393DR2G (onsemi) | C7955 | **Basic** | 272k | use this (0..70 C; -40 C option LM2903DR C7549 / LM2903DR2G C57474, same pinout, but all LM2903 are Extended = +1 fee, so not used: R4 m4); alt TI LM393DR C67470 (Ext, 191k). Fallback LMV393IDR C7984 (Ext, 11k, 2.7-5.5 V only!) |
| U2 | JW5017S buck | SOT-23-6 | JW5017SSOTB#TRPBF (JoulWatt) | C371172 | Ext | 17.8k | 4.5-26 V, 1.2 A; allowed alt RY8310 C370876 (Ext, 13k, 4.5-30 V, 1 A) |
| P1 | 2-pin 5.08 pluggable header, THT | THT | KF2EDGRC-5.08-2P (Cixi Kefa) | C441236 | Ext | 21k | MSTBA2,5/2-G-5,08 itself is not stocked (only 3-pin C5183941). Hole 1.8 mm, pad 2.5 mm (lib uses 1.4/2.8). alt KF2EDGR-5.08-2P C441204 (37k, hole 1.6). Screw type: KF128-5.08-2P-AA C474952 |
| P2 | 1x4 2.54 header, THT | THT | HX PZ2.54-1x4P ZZ (male, hanxia) | C32713270 | Ext | 107k | female socket: C2718488 (144k). Pad 1.7, hole 1.1 |
| Q1 | NPN SOT-23 (bus load transistor) | SOT-23 | **BC817-40** | **C20069155** | check | check | user decision; EasyEDA pads: 1 = B, 2 = E, 3 = C. (old: MMBT3904 C20526 Basic) |
| C29 | 100 uF 6.3 V tantalum, LDO output stability | case B 3528 | TAJB107K006RNJ (Kyocera AVX) | C16133 | **Basic** | see JLC | EasyEDA CASE-B_3528: pad 1 = + (left, polarity bar), pad 2 = - ; pads 1.5 x 2.4 at +-1.861 mm |
| JP1, JP2 | solder jumpers (open) | custom `lib/jumper.tsx` | - | - | - | - | not in BOM (no LCSC number); 0.4 mm gap, no paste |
| D1-D5 | BAT42-class low-cap Schottky | SOD-123 | **BAT42W (hongjiacheng)** | **C22466362** | **Pref** | 22k | 30 V, 200 mA, Cj ~7-10 pF @1 V (BAT42 class; vs B5819W ~100 pF). Genuine alt: BAT42W-7-F Diodes Inc C134396 (Ext, 10.7k). Higher-voltage alt: BAT46W (100 V) C7420332 (Pref, 643k) |
| D7 | PMEG3020EGW (power path) | SOD-123 | B5819W SL (Changjing) | C8598 | **Basic** | 886k | 1 A 40 V |
| D6 | 1N4148 | SOD-123 | 1N4148W | C81598 | **Basic** | 4.2M | |
| F1,F2 | resettable fuse 0805 (EMS bus) | 0805 | BSMD0805-050-24V (BHFUSE) | C910822 | Ext | 137k | 0.5 A hold / 1 A trip, 24 V (bus ~15 V). Cheaper 15 V: C883109 (46k); 100 mA types too low |
| F3 | PTC in the USB VBUS path (R3: was the 0.5 A 0805 part) | 1206 | SMD1206B110TFT | **C269119** | Ext | 99k | 1.1 A hold / 2.2 A trip, 8 V, R 0.04..0.21 ohm; EasyEDA pads 1.19 x 1.73 at +-1.445 mm (`Ptc1206Footprint`). AMS1117 headroom 0.2..0.28 V at 4.75 V host (docs/review/FIX_LIST_R3.md). Alternatives: C126818 1206L110THYR (13k), C70163 SL1206110 (100 mohm, 1.3k) |
| LD1 | LED red | 0805 | NCD0805R1 (NationStar) | C84256 | **Basic** | 3.2M | |
| LD2..LD5 | LED yellow (R3; was green KT-0805G C2297) | 0805 | KT-0805Y (Kento) | **C2296** | **Basic** | 429k | Vf 1.8..2.4 V @ 20 mA, 175 mcd; same EasyEDA footprint/polarity as C2297 (pad 1 = anode) |
| L1,L2 | 4.7uH series (V2 footprint = EasyEDA C98021: pads 1.52 x 3.1 at +-1.145) | 1210 (3225) | LQH32PN4R7NN0L (Murata) | C98021 | Ext | 5.9k | 1 A, 216 mOhm. Lower-stock/ lower-R: C90319 CBC3225T4R7MR 1.01 A (0.9k); pricey 1.9 A: C5331021. TDK NLV32T-4R7J-PF C76842 only 220 mA: too small if buck input flows through it |
| L3 | 4.7uH buck | 5x5x2 shielded | SWPA5020S4R7MT (Sunlord) | C43183 | Ext | 1.9k | 2.2 A Isat 2.7 A, 74 mOhm; footprint differs from lib `Inductor0520` (see FOOTPRINT_CHECK). alt CD54-style ZECD54-4R7M C41408590 (11.9k, 2.8 A, unshielded, 5.8x5.2); smaller 4x4: SWPA4030S4R7MT C57269 (45k, 2 A) |
| R2,R3,R4 | 68R 1% | 2010 | CL2010FN68RB (Changlong) | C53284030 | Ext | 23k | alts: FRC2010F68R0TS C3000767 (12k), RTT2068R0FTE C159225 (3.4k). No Basic/Pref 2010 68R |
| R1,R7 | 10k | 0805 | 0805W8F1002T5E | C17414 | Basic | 43.8M | also EN/BOOT pull-ups |
| R8,R16,R_PU | 100k | 0805 | 0805W8F1003T5E | C149504 | Basic | 2.7M | |
| R9,R11 | 4k7 | 0805 | 0805W8F4701T5E | C17673 | Basic | 5.1M | |
| R13 | **3k3** (R3; V1 4k7, 6N137 RL 330R..4k) | 0805 | 0805W8F3301T5E | **C26010** | Basic | 1.4M | OC1 output pull-up at 3.3 V |
| R6 | 47k | 0805 | 0805W8F4702T5E | C17713 | Basic | 1.2M | |
| R10 | 470R | 0805 | 0805W8F4700T5E | C17710 | Basic | 1.5M | |
| R5 | 390R | 0805 | 0805W8F3900T5E | C17655 | Basic | 1.1M | |
| R14 | **150R** (V2; V1: 270R) | 0805 | 0805W8F1500T5E | **C17471** | **Basic** | 538k | OC2 LED current limit, CTR margin >= 1.5 (calculation: docs/netlist_v1.md "V2 deviations"); old 270R C17590 (Pref) no longer used |
| R18, R19, R22, R26 | **330R** (R3; V2 220R C17557 for green LEDs) | 0805 | 0805W8F3300T5E | **C17630** | **Basic** | 1.1M | yellow LD2..LD5: 2.0..4.8 mA from 3.3 V (Vf 1.7..2.2 V), docs/netlist_v1.md |
| R17 | 1k2 | 0805 | 0805W8F1201T5E | C17379 | Basic | 1.3M | red power LED on 5 V (V1 value) |
| R15 | 1k3 | 0805 | 0805W8F1301T5E | **C17384** | **Ext** | 116k | 6k8/1k3 sets 5.0 V; 1k5 C4310 is Basic (-> 4.4 V, not suitable), 1k2 -> 5.3 V |
| R12 | 6k8 | 0805 | 0805W8F6801T5E | C17772 | Basic | 395k | |
| R(CC1,CC2) | 5.1k | 0805 | 0805W8F5101T5E | C27834 | Basic | 2.4M | |
| R(shield) | 1M | 0805 | 0805W8F1004T5E | C17514 | Basic | 1.66M | |
| C5,C6,C8,C9,C13,C7,C30,100n | 100n 50V X7R | 0805 | CC0805KRX7R9BB104 (Yageo) | C49678 | Basic | 20M | |
| C5 | **4.7n** (R3; V1 10n C1710, TX falling delay) | 0805 | 0805B472K500NT (FH) | C1744 | Basic | 200k | same part as the shield cap |
| C3 | 1n 50V X7R | 0805 | CL21B102KBCNNNC | C46653 | Basic | 1.08M | |
| C4 | 1n5 50V X7R | 0805 | 0805B152K500NT (FH) | C1717 | **Pref** | 89k | |
| C1 | 68p 50V C0G/NP0 | 0805 | CC0805JRNPO9BN680 (Yageo) | C107120 | Ext | 68k | alt FH C1834 (28k). Basic-only option: 47p C0G C14857 (178k) if circuit tolerates |
| C(shield) | 4.7n 50V X7R | 0805 | 0805B472K500NT (FH) | C1744 | Basic | 200k | |
| C(EN) | 1u 50V X7R | 0805 | CL21B105KBFNNNE | C28323 | Basic | 3.6M | |
| C2,C10 (+LDO 10u) | 10u 25V X5R | 0805 | CL21A106KAYNNNE | C15850 | Basic | 9.3M | |
| C11 (+LDO 22u) | 22u 25V X5R | 1206 | CL31A226KAHNNNE | C12891 | Basic | 2.5M | |
| C12, C14 | 2 x 1000u/25V SMD electrolytic (parallel = 2000 uF; replaces the single 2200 uF THT of V1) | SMD D10 x L12 (BD10.0-L10.3-W10.3) | JVJ25V1000M10X12 (JIERR) | C49256851 | Ext | see JLC | pads 4.5 x 1.65 at +-4.5 mm, pad 1 = +, chamfered corner = + side (EasyEDA). Replaces PA25V2200M10x17 C46550439 (THT, hand-soldered). Both on EMS_VIN / GND_EMS near D7/U2 |

## Economic PCBA (checked 2026-11-26, docs/JLC_ECONOMIC.md)
JLC part page field "PCBA Type" per BOM part (table in `scripts/jlc_economic.py`): all 45 assembled LCSC numbers are "Economic and Standard" (P1 C441236 / P2 C32713270 are "Wave Soldering", J2 C165948 "SMT Assembly").
Only U3 C2913202 is "Standard Only" -> DNP, hand-solder, listed in `fab/EMSinterface_V2.0-HANDSOLDER.csv`. The fee count below therefore drops by one for JLC-assembled Extended parts (ESP32 not assembled).

## Extended-part count (extra fees)
Q1 BC817-40 (C20069155) and C29 (C16133) need an availability/class check at order time. Distinct **Ext** (fee) part numbers: C2913202 (ESP32), C165948 (USB-C), C7519 (USBLC6), C92651 (6N137), C336082 (6N136),
C371172 (JW5017S), C98021 (L1/L2), C43183 (L3), C53284030 (68R 2010), C17384 (1k3), C107120 (68p), C441236 (P1),
C32713270 (P2), C49256851 (C12/C14, one fee for both), C910822 (F1/F2), C269119 (F3, R3) = **16**; 14 if P1 and P2 are hand-soldered (THT, not assembled). C12/C14 are now SMD and assembled by JLC.
Preferred-extended (no fee): C22466362 (BAT42W), C1717 (1n5). V2 changes (R4/R5 fixes): C30 (C49678), R14 150R C17471 are Basic. R3 (FIX_LIST_R3.md): LD2..LD5 C2296 / R18,R19,R22,R26 C17630 / R13 C26010 / C5 C1744 are Basic, F3 C269119 is Extended (+1 fee, 1.1 A hold for the Wi-Fi peaks).
R15 (C17384, Ext) is kept on purpose: R12 5k1 / R15 1k gives 4.88 V (R4 m10) and R12 6k2 (C17767) is Extended itself (R6 m9, FIX_LIST_R3.md); C4 1n5 C1717 is Preferred-extended (no fee).
P1 mating plug (NOT in the BOM, bought separately): 2-pole 5.08 mm pluggable screw-terminal plug of the KF2EDGK-5.08-2P / Phoenix MSTB 2,5/2-STF-5,08 class (wire entry parallel to the board, 90 deg); article number to be chosen at the distributor (not verified here).
Possible fee savings: C1 68p -> 47p Basic C14857 (-1); LM393 already Basic; no Basic alternative for 2010 68R
(two 1206/0805 in parallel would need a footprint change); fuses could be Pref if a Pref 0805 PTC is chosen.

## Availability problems / warnings
* No real availability problem: all chosen parts have stock >= 1.9k (lowest: L3 SWPA5020 1.9k, L1/L2 alt C90319 0.9k).
* MSTBA2,5/2-G-5,08 (Phoenix) not available in 2-pin; use KF2EDGRC-5.08-2P (compatible 5.08 mm pitch, but check mating plug/flange).
* LM393DR2G (C7955) is rated 0..70 C only (TI LM393DR C67470 likewise); the -40..125 C LMV393IDR (C7984, Ext) is a
  2.7-5.5 V part: usable on the 5 V rail (max 5.5 V) but with little margin, so LM393 stays the default.
* 6N137S-TA1-L has 2.7-5.5 V supply (OC1 runs from the 3.3 V MCUVCC: fine). 6N136 needs 4.5 V min on VCC: OC2's output side is on +5V: fine.

## LDO recommendation (5 V USB -> 3.3 V for ESP32-S3 WiFi)
* ESP32-S3 WiFi TX bursts reach ~350-500 mA; Espressif asks for >= 500 mA supply.
* **Recommended: AMS1117-3.3 (C6186, Basic).** 1 A, dropout 1.1 V, SOT-223, no extra JLC fee. Needs output cap with some ESR:
  the 22 uF 1206 ceramic usually works; add 10 uF + 100 n at the module. Dissipation (5-3.3)*0.25 A avg ~0.4 W, peaks ~0.8 W:
  give the tab copper. Weakness: ~5-10 mA quiescent and noisier.
* Alternative: **AP2112K-3.3 (C51118, Ext)** 600 mA, 250 mV dropout, ceramic stable, 55 uA Iq.
* TLV75733P (C485517, 1 A, SOT-23-5): best, extended.

## Other JLC notes
* Hand-solder (not assembled) candidates: P1, P2 (THT). C12/C14 are SMD (C49256851). Tactile switches are Basic and SMD: assemble.
* 2010/3225/5x5 parts are Extended; each distinct extended part adds a one-time fee.
* Design in 0805 is fine; 0603 resistors/caps have equal basic coverage and could shrink the board.
