# JLCPCB / LCSC parts plan

**Verification status: NOT verified online.** The sandbox proxy blocks jlcpcb.com / lcsc.com / jlcsearch
(403), so Basic/Extended status and part numbers below are from memory. Confidence: H = sure, M = fairly sure,
L = guess / must look up. Before ordering, run (with network) `npx tsci import --jlcpcb "<Cnumber>"` or check
jlcpcb.com/parts. Basic-vs-extended can change; "Pref." = preferred extended (no fee at JLC "economic" tier
doesn't apply; fee waived only for Basic).

In tscircuit set the number on the component: `supplierPartNumbers={{ jlcpcb: ["C17414"] }}` (verified prop
name/keys; build accepts it, offline it only warns "may not have availability").

| Ref (Eagle) | Value / function | Package | Suggested part | LCSC | Class | Conf. | Notes |
|---|---|---|---|---|---|---|---|
| U-ESP | ESP32-S3-WROOM-1-N16R8 | module | Espressif ESP32-S3-WROOM-1-N16R8 | C2913202 | Ext | H(PN from user) | footprint `lib/esp32s3wroom1.tsx` |
| J-USB | USB-C 16P USB2.0 | SMD+THT | HRO TYPE-C-31-M-12 | C165948 | Ext | H(PN from user) | `lib/usbc16.tsx`, Y offsets approx |
| U-LDO | 3.3V LDO | SOT-223 | AMS1117-3.3 | C6186 | **Basic** | H | recommended, see below |
| (alt) | 3.3V 600mA LDO | SOT-23-5 | AP2112K-3.3TRG1 | C51118 | Ext | H | fallback if noise/dropout matters |
| (alt) | 3.3V 1A LDO | SOT-23-5 | TLV75733PDBVR | look up | Ext | L | best performance, costlier |
| U-ESD | USB ESD | SOT-23-6 | USBLC6-2SC6 | C7519 | Ext | M | also look for 'SRV05-4'/'USBLC6' clones if basic needed |
| SW-BOOT/RST | tactile 5.1x5.1 | SMD | TS-1187A-B-A-B | C318884 | Ext | M | `Tactile5x5` in lib/thtparts.tsx |
| OC1 | 6N137 | SMD-8 gull-wing 300mil | 6N137S(TA)-V / LTV-6N137-TA type | look up | Ext | L | search "6N137 SMD"; pads from Eagle lbr (9.38 mm row, 2.54 pitch) |
| OC2 | 6N136 | SMD-8 gull-wing 300mil | 6N136S(TA) type | look up | Ext | L | |
| U1 | LM393 | SOIC-8 | LM393DR (TI) | C7955 | Ext | L-M | if LM393 not basic: LM358DR C7950 is basic but NOT a comparator |
| U2 | JW5017S buck | SOT-23-6 | JW5017S | look up | Ext | L | Joulwatt; ensure stocked |
| P1 | MSTBA2 5.08 2-pin THT | THT | Phoenix MSTBA2,5/2-G-5,08 (or KF2EDGR-5.08-2P clone) | look up | Ext | L | hand-solder fine |
| P2 | CON-LSTB 1x4 | 2.54 header | 1x4 pin header 2.54 | look up | - | L | or hand-solder |
| Q1 | NPN SOT-23 (BC847B) | SOT-23 | MMBT3904 (CJ/LRC) | C20526 | **Basic** | M | pinout 1=B 2=E 3=C same as BC847 |
| D1-D5 | BAT42 Schottky | SOD-123 | B5819W (1A 40V) | C8598 | **Basic** | M | alt SS14 (SMA, C2480 Basic, bigger footprint) |
| D7 | PMEG3020EGW | SOD-123 | B5819W (or SS14) | C8598 | Basic | M | |
| D6 | 1N4148 | SOD-123 | 1N4148W | C81598 | **Basic** | M | |
| F1,F2 | fuse 0805 | 0805 | PTC 0805 resettable or 0805 fuse | look up | - | L | |
| LD1 | LED red | 0805 | 0805 red LED | C84256 | **Basic** | M | |
| LD2,LD3 | LED green | 0805 | 0805 green LED | look up | Basic | L | JLC basic 0805 green exists (~C19171 is 0603?) check |
| L1,L2 | 4.7uH | 3225 (3.2x2.5) | e.g. FHP/Sunlord 4.7uH 3225 shielded | look up | Ext | L | check current >= 1A |
| L3 | 4.7uH | 0520 (5x2?) | 4.7uH power inductor | look up | Ext | L | footprint `Inductor0520` pads 2.0x2.5 @+-2.5 |
| R2,R3,R4 | 68R | 2010 | 2010 68R 1% (UNI-ROYAL 2010W…) | look up | Ext? | L | footprint `Res2010Footprint`; fallback 2x 1206 130R parallel |
| R1,R7 | 10k | 0805 | 0805W8F1002T5E | C17414 | Basic | H | |
| R8,R16 | 100k | 0805 | 0805W8F1003T5E | C149504 | Basic | M | |
| R9,R11,R13 | 4k7 | 0805 | 4.7k 0805 | C17673 | Basic | M | |
| R6 | 47k | 0805 | 47k 0805 | C17713 | Basic | M | |
| R10 | 470R | 0805 | 470R 0805 | C17710 | Basic | M | |
| R5 | 390R | 0805 | 390R 0805 | C17655 | Basic | L-M | |
| R14 | 270R | 0805 | 270R 0805 | C17697 | Basic | L-M | |
| R17-19 | 1k2 | 0805 | 1.2k 0805 | C17379 | Basic | L-M | |
| R15 | 1k3 | 0805 | 1.3k 0805 | look up | Basic? | L | else use 1k2/1k5 (check circuit) |
| R12 | 6k8 | 0805 | 6.8k 0805 | C17772 | Basic | L-M | |
| C5,C6-C9,C13 | 100n / 10n | 0805 | CL21B104KBCNNNC (100n), CL21B103KBANNNC (10n) | C49678 / C1710 | Basic | M | |
| C3,C4,C1 | 1n, 1n5, 68p | 0805 | 1n C46653, 68p C1799?, 1n5 look up | | Basic? | L | NP0/C0G for 68p |
| C2,C10 | 10u | 0805 | CL21A106KAYNNNE | C15850 | Basic | H | |
| C11 | 22u | 1206 | CL31A226KAHNNNE | C12891 | Basic | M | LDO output cap |
| C12 | 2200u/25V | E5-10.5 THT | Lelon/Aishi 2200uF 25V radial D10 | look up | Ext | L | hand-solder or drop to 1000uF/16-25V; footprint `CapE5_10p5` |

## LDO recommendation (5 V USB -> 3.3 V for ESP32-S3 WiFi)
* ESP32-S3 WiFi TX bursts reach ~350-500 mA; Espressif asks for >= 500 mA supply.
* **Recommended: AMS1117-3.3 (C6186, Basic).** 1 A, dropout 1.1 V (4.7 V USB min minus connector/ESD drop still leaves
  > 1 V headroom), in SOT-223, no extra JLC fee. Needs output cap with some ESR: the existing 22uF 1206 ceramic (C11)
  usually works; add 10uF + 100n at the module. Dissipation (5-3.3)*0.25 A avg ~0.4 W, peaks ~0.8 W: give the tab copper.
  Weakness: ~5-10 mA quiescent and noisier.
* Alternative: **AP2112K-3.3 (C51118, Ext)** 600 mA, 250 mV dropout, ceramic stable, 55 uA Iq. Borderline on
  peak current but used in many ESP32 boards. Choose it if the extended fee and 600 mA limit are acceptable.
* TLV75733P (1 A, SOT-23-5): best, but extended and pricier.

## Other JLC notes
* Hand-solder (not assembled) candidates: MSTBA2, 2200uF cap, 1x4 header, tactile switches if not JLC stocked.
* 2010/3225/0520 parts are mostly Extended; each distinct extended part adds a one-time fee.
* Design in 0805 (current) is fine; 0603 resistors/caps have equal basic coverage and could shrink the board.
