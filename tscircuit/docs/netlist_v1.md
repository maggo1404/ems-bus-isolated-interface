# EMS bus isolated interface V1.0 - netlist

Generated from `hardware/EMSinterface_V1.0.sch` (Eagle 7.7). Gate/pin names mapped to pad numbers via the library `<connects>`. The `.brd` `<signals>` / `<contactref>` lists were cross-checked: all 33 nets and every pad connection agree exactly (no differences, no brd-only signals). Machine-readable version: `netlist_v1.json`.

Conventions: `Ref.pad`. Diode / LED pads are `A`/`C`; C12 pads are `+`/`-`. Auto-named nets (`N$n`) keep their exact Eagle names. Supply symbols `P+1..P+3` (+5V) and `GND1..GND3` (GND) are symbols only, not parts.

## Nets

| Net | Side | Pins | Role |
|---|---|---|---|
| `+5V` | EMS | C6.2, C8.1, C11.1, C13.2, L3.1, OC2.8, R9.2, R10.2, R11.2, R12.2, R17.2, U1.8 | EMS-side 5V rail from JW5017S buck (U2) via L3 |
| `GND` | EMS | C4.1, C5.1, C6.1, C8.2, C10.1, C11.2, C12.-, C13.1, D2.A, D4.A, D5.A, D6.C, LD1.C, OC2.5, Q1.2, R8.1, R15.1, U1.4, U2.2 | EMS bus-side ground (EMS GND) |
| `N$1` | EMS | F2.2, L2.1 |  |
| `N$10` | EMS | C3.2, R7.2, R8.2, U1.2 |  |
| `N$11` | EMS | R3.2, R4.1 |  |
| `N$12` | EMS | R2.2, R3.1 |  |
| `N$13` | EMS | C4.2, Q1.3, R4.2 |  |
| `N$14` | EMS | Q1.1, R9.1, U1.7 |  |
| `N$15` | EMS | C5.2, OC2.6, R11.1, U1.6 |  |
| `N$16` | EMS | OC1.2, R10.1 |  |
| `N$17` | EMS | F1.1, P1.1 | P1.1 after fuse side (bus terminal 1) |
| `N$18` | EMS | OC1.3, U1.1 |  |
| `N$2` | EMS | F1.2, L1.1 |  |
| `N$23` | EMS | R12.1, R15.2, U2.3 |  |
| `N$25` | EMS | C9.1, U2.1 |  |
| `N$26` | EMS | C9.2, L3.2, U2.6 |  |
| `N$27` | EMS | LD1.A, R17.1 |  |
| `N$29` | EMS | R16.2, U2.4 |  |
| `N$3` | EMS | C1.1, D1.A, D2.C, L2.2 |  |
| `N$4` | EMS | C1.2, D3.A, D4.C, L1.2 |  |
| `N$5` | EMS | F2.1, P1.2 | P1.2 (bus terminal 2) |
| `N$6` | EMS | D1.C, D3.C, D5.C, D7.A, R1.1, R2.1 | Rectified bus rail (D1/D3/D5 cathodes, D7 anode, R1, R2) |
| `N$7` | EMS | D6.A, R5.1, R6.1, R7.1, U1.5 |  |
| `N$8` | EMS | C2.1, C3.1, R1.2, R5.2 |  |
| `N$9` | EMS | C2.2, R6.2, U1.3 |  |
| `VIN` | EMS | C10.2, C12.+, D7.C, R16.1, U2.5 | Rectified bus after D7 (buck input, C12/C10 bulk) |
| `MCUGND` | MCU | C7.1, OC1.5, P2.4 | MCU-side isolated ground (P2.4) |
| `MCURX` | MCU | LD3.C, OC1.6, P2.3, R13.1 | MCU Rx output to P2.3 (OC1 VO, R13 pull-up, LD3 cathode) |
| `MCUTX` | MCU | LD2.C, OC2.3, P2.2 | MCU Tx input from P2.2 (OC2 LED cathode, LD2 cathode) |
| `MCUVCC` | MCU | C7.2, OC1.7, OC1.8, P2.1, R13.2, R14.1, R18.2, R19.1 | MCU-side 3.3V from P2.1 |
| `N$19` | MCU | OC2.2, R14.2 |  |
| `N$20` | MCU | LD2.A, R19.2 |  |
| `N$24` | MCU | LD3.A, R18.1 |  |

### Pad maps worth knowing
- P2 (CON-LSTB_04): pad1 = `MCUVCC` (3.3V), pad2 = `MCUTX`, pad3 = `MCURX`, pad4 = `MCUGND`. Schematic image labels it "MCU (ESP32)".
- P1 (MSTBA2): pad1 -> `N$17` -> F1 -> L1; pad2 -> `N$5` -> F2 -> L2 (EMS bus, polarity-free: D1-D4 bridge).
- OC1 6N137: 2 = LED A (`N$16`, via R10 470R to +5V), 3 = LED C (`N$18` = U1.1 comparator A output), 5 = GND (`MCUGND`), 6 = VO (`MCURX`), 7 = VE (`MCUVCC`, enabled), 8 = VCC (`MCUVCC`). Pads 1, 4 NC.
- OC2 6N136: 2 = LED A (`N$19`, via R14 270R to `MCUVCC`), 3 = LED C (`MCUTX`), 5 = GND (`GND`), 6 = VO (`N$15`), 7 = VB (unconnected), 8 = VCC (`+5V`).
- U1 (value LMV393IDR in schematic, BOM says LM393): comparator A = pads 1 OUT / 2 IN- (`N$10`) / 3 IN+ (`N$9`) = RX; comparator B = pads 7 OUT (`N$14`) / 6 IN- (`N$15`) / 5 IN+ (`N$7`) = TX; 8 = `+5V`, 4 = `GND`.
- Q1 BC847B: 1 = B (`N$14`), 2 = E (`GND`), 3 = C (`N$13`).
- U2 JW5017S: 1 BST (`N$25`, C9 to SW), 2 GND, 3 FB (`N$23`), 4 EN (`N$29`, R16 100k to VIN), 5 VIN (`VIN`), 6 SW (`N$26`).

## Functional description

**Power path (EMS side).** Bus P1 -> fuses F1/F2 -> L1/L2 (4R7) -> Schottky bridge D1-D4 (BAT42; C1 68p across the two bridge inputs; D5 BAT42 clamp rail `N$6` to GND) -> rectified rail `N$6` -> D7 (PMEG3020EGW) -> `VIN` (C12 2200u/25V, C10 10u) -> U2 JW5017S buck (SW `N$26`, L3 4R7 to `+5V`, C9 100n bootstrap, FB divider R12 6k8 / R15 1k3, EN pulled to VIN by R16 100k) -> `+5V` (C11 22u, C8 100n, C6 100n, C13 100n). LD1 red + R17 1k2 = 5V power LED. The 3.3V `MCUVCC` is supplied from the MCU via P2.1 and only powers the LED side of OC2 and the output side of OC1; there is no on-board 3.3V regulator.

**RX path (bus -> MCU).** Rail `N$6` -> R1 10k -> `N$8` (C2 10u to U1.3 side, C3 1n to U1.2 side) with R5 390R into `N$7` (D6 1N4148 to GND = ~0.6V reference). U1 comparator A: IN+ (`N$9`, from `N$8` via C2, R6 47k to `N$7`), IN- (`N$10`, C3, R7 10k to `N$7`, R8 100k to GND). OUT A (`N$18`, open collector) sinks the OC1 LED cathode; the LED anode is fed from +5V through R10 470R (`N$16`). OC1 (6N137) VO = `MCURX` with R13 4k7 pull-up to `MCUVCC`; MCU sees inverted/re-squared bus signal on P2.3 (idle high). LD3 (+R18 1k2 to `MCUVCC`) lights when MCURX is low.

**TX path (MCU -> bus).** P2.2 `MCUTX` is the OC2 LED cathode (anode via R14 270R to `MCUVCC`): Tx low = LED on. OC2 (6N136) phototransistor collector VO = `N$15`, pulled up by R11 4k7 to +5V, filtered by C5 10n to GND, feeds U1.6 (IN- of comparator B). IN+ (U1.5, `N$7`) is the ~0.6V reference. OUT B (`N$14`, open collector) with R9 4k7 pull-up to +5V drives Q1 base. Q1 collector `N$13` pulls the rectified bus `N$6` down through R4+R3+R2 (3 x 68R) and C4 1n5 to GND: Tx low -> LED on -> VO low (<0.6V) -> comparator B released -> R9 turns Q1 on -> bus loaded (active/low). Tx high/idle -> LED off -> VO high (5V) -> OUT B low -> Q1 off -> bus idle. LD2 (+R19 1k2) in parallel with the OC2 LED lights when Tx is low. The RX path also sees the node `N$6`, so MCU receives its own transmission (echo).

## Answers to the review questions

**a) P2 pinout.** P2.1 = `MCUVCC` (3.3V, MCU supplies it), P2.2 = `MCUTX` (MCU Tx -> board; feeds OC2 LED cathode, LD2 cathode), P2.3 = `MCURX` (board -> MCU Rx; OC1 pin 6 output, R13 pull-up, LD3 cathode), P2.4 = `MCUGND`.

**b) Floating Tx.** OC2 LED: anode `N$19` = R14 -> `MCUVCC`; cathode = `MCUTX` (P2.2). LD2: anode via R19 to `MCUVCC`, cathode `MCUTX`. Both LEDs are forward-biased from the 3.3V side; the only current path to ground is through the MCU Tx driver pulling low. With Tx floating/high-Z there is no sink path, so no LED current flows and the cathode node sits at about `MCUVCC` (the LEDs themselves hold it high). So OC2 is off, VO (`N$15`) is pulled to +5V by R11, U1.6 (5V) > U1.5 (~0.6V), comparator B output stays low, Q1 off: the bus sees IDLE (no transmission). An open solder jumper in the Tx line is therefore safe by design, as long as `MCUVCC` is powered or off (0V: also off). A pull-up on the interface side is NOT needed to guarantee idle; it would be only a belt-and-braces option against EMI pickup on a long open wire (e.g. 47k-100k from `MCUTX` to `MCUVCC`; harmless: ~35-70uA extra only when Tx low). Do not add a pull-DOWN or tie Tx to GND: that would continuously transmit. Caveat: Tx must also be high at ESP32 boot, but a floating pin is equivalent.

**c) MCU-side helpers.** LD2 (green) + R19 1k2: Tx activity LED, shares `MCUTX` with the OC2 cathode, lit when Tx low (~1 mA extra sink current; OC2 LED about (3.3-1.4)/270 ~ 7 mA). LD3 (green) + R18 1k2: Rx activity LED, from `MCUVCC` to `MCURX`, lit when MCURX low. LD1 (red) + R17 1k2 is on the EMS side (+5V power-on LED), not an MCU-side part. R13 4k7: pull-up for the open-collector 6N137 output on `MCURX`. C7 100n: decoupling of OC1 VCC (`MCUVCC` to `MCUGND`). R14 270R: OC2 LED current limit.

**d) Isolation check.** Only OC1 and OC2 have pins on both an EMS net and an MCU net (checked per part from netlist). No shared nets: `GND` and `MCUGND` are not connected anywhere; `+5V`/`MCUVCC` are distinct. No exceptions (no Y-capacitor, no resistor across the barrier). Note: OC1.7 (VE) is on `MCUVCC` (MCU side) as intended, OC2.7 (VB) is left open.

## Layout V1

Source: `hardware/EMSinterface_V1.0.brd`, Dimension layer 20. All coordinates mm, origin = board lower-left corner, parts on top side unless stated.

- Board outline: rectangle 68.885 x 33.645 mm (0,0)-(68.885,33.645). Four 3.0 mm mounting holes at (4.445,4.445), (4.445,29.21), (64.77,29.21), (64.77,4.445).
- Copper pours (top and bottom, 0.254 mm): GND x 0.635..48.514, MCUGND x 53.6575..68.2625 (y 0.635..33.02). Isolation gap between the two pours: 5.14 mm (x 48.514 -> 53.6575). Smallest computed gap between any EMS-net copper and MCU-net copper (pads/traces/vias, excluding pours): 6.74 mm (GND/LD1.C to MCUTX/LD2.C area, y~31.25). The optocouplers sit in the gap at x = 52.07; their pads are at x = 52.07 +/- 4.69 (pad-to-pad spacing across the package 8.38 mm, centre to centre 9.38 mm).
- EMS side occupies x < ~49 mm, MCU side x > ~53.6 mm; P1 on the left edge, P2 on the right edge.

| Ref | Value | Package | x | y | rot |
|---|---|---|---|---|---|
| L1 | 4R7 | L3225M | 10.79 | 20.00 | R270 |
| L2 | 4R7 | L3225M | 10.79 | 12.38 | R270 |
| C1 | 68p | C0805K | 14.76 | 9.54 | R90 |
| D1 | BAT42 | SOD123 | 16.51 | 5.71 | R180 |
| D2 | BAT42 | SOD123 | 16.51 | 1.91 | R0 |
| D3 | BAT42 | SOD123 | 16.51 | 13.34 | R180 |
| D4 | BAT42 | SOD123 | 16.51 | 17.14 | R0 |
| D5 | BAT42 | SOD123 | 21.59 | 3.81 | R270 |
| R1 | 10k | R0805 | 22.54 | 13.34 | R0 |
| R2 | 68R | R2010 | 21.59 | 19.05 | R90 |
| R3 | 68R | R2010 | 25.40 | 19.05 | R270 |
| R4 | 68R | R2010 | 29.21 | 19.05 | R270 |
| C2 | 10u | C0805K | 28.57 | 8.26 | R0 |
| C3 | 1n | C0805K | 28.57 | 11.43 | R0 |
| R5 | 390R | R0805 | 24.77 | 10.48 | R90 |
| U1 | LMV393IDR | LM393 | 36.83 | 9.53 | R270 |
| D6 | 1N4148 | SOD123 | 24.77 | 3.81 | R90 |
| R6 | 47k | R0805 | 28.57 | 5.71 | R0 |
| R7 | 10k | R0805 | 28.57 | 1.91 | R0 |
| R8 | 100k | R0805 | 28.57 | 13.97 | R0 |
| R9 | 4k7 | R0805 | 43.81 | 12.70 | R270 |
| Q1 | BC847B | SOT23 | 42.70 | 16.85 | R90 |
| C4 | 1n5 | C0805K | 42.60 | 20.32 | R180 |
| C5 | 10n | C0805K | 43.81 | 4.39 | R90 |
| C6 | 100n | C0805K | 35.81 | 5.71 | R0 |
| R10 | 470R | R0805 | 42.23 | 24.13 | R180 |
| OC1 | 6N137 | SO8-GW300 | 52.07 | 22.86 | R0 |
| OC2 | 6N136 | SO8-GW300 | 52.07 | 10.16 | R180 |
| R11 | 4k7 | R0805 | 43.81 | 8.26 | R90 |
| C7 | 100n | C0805K | 59.37 | 19.21 | R90 |
| R13 | 4k7 | R0805 | 62.87 | 23.50 | R180 |
| P2 | CON-LSTB_0408 | CON-LSTB_04 | 66.04 | 16.83 | R90 |
| R14 | 270R | R0805 | 62.23 | 9.68 | R180 |
| P1 | MSTBA2 | MSTBA2 | 1.40 | 16.84 | R270 |
| D7 | PMEG3020EGW | SOD123 | 16.51 | 20.32 | R0 |
| U2 | JW5017S | SOT23-6 | 34.92 | 24.77 | R90 |
| R12 | 6k8 | R0805 | 37.47 | 24.45 | R90 |
| R15 | 1k3 | R0805 | 37.47 | 20.95 | R90 |
| C9 | 100n | C0805K | 32.07 | 24.45 | R90 |
| R16 | 100k | R0805 | 35.24 | 28.89 | R0 |
| C10 | 10u | C0805K | 32.07 | 28.57 | R270 |
| C11 | 22u | C1206 | 21.91 | 31.43 | R180 |
| F1 | FUSE0805R0805 | R0805 | 7.62 | 19.37 | R90 |
| F2 | FUSE0805R0805 | R0805 | 7.62 | 14.29 | R270 |
| R17 | 1k2 | R0805 | 42.23 | 28.89 | R180 |
| L3 | 4R7 | INDUCTOR_0520 | 26.99 | 27.62 | R270 |
| U$6 |  | 3,0 | 4.45 | 4.45 | R0 |
| U$7 |  | 3,0 | 4.45 | 29.21 | R0 |
| U$8 |  | 3,0 | 64.77 | 29.21 | R0 |
| U$9 |  | 3,0 | 64.77 | 4.45 | R0 |
| LD1 | RED | CHIP-LED0805 | 46.67 | 30.80 | R0 |
| LD3 | GREEN | CHIP-LED0805 | 60.01 | 30.80 | R0 |
| R18 | 1k2 | R0805 | 59.85 | 26.35 | R270 |
| C12 | 2200u/25V | E5-10,5 | 14.61 | 27.62 | R90 |
| C8 | 100n | C0805K | 42.23 | 26.35 | R0 |
| C13 | 100n | C0805K | 47.62 | 3.17 | R90 |
| LD2 | GREEN | CHIP-LED0805 | 54.61 | 30.80 | R0 |
| R19 | 1k2 | R0805 | 56.52 | 29.53 | R90 |


## V2 deviations from the V1 circuit (tscircuit board, fixes of review R4/R5)
Pin-for-pin the 33 V1 nets are unchanged (`scripts/check_netlist.py`); the following parts/values differ or were added:

| Item | V1 | V2 | Reason |
|---|---|---|---|
| C30 (new) | - | 100 nF 50 V X7R (C49678) parallel to C10 (EMS_VIN / GND_EMS) | buck input HF decoupling directly at U2 VIN (R5 M2) |
| F3 (new, MCU side) | - | PTC 0805 BSMD0805-050-24V (C910822, 500 mA hold, same part as F1/F2) between J2/U4 `VBUS` and `VBUS_F` (U5.VIN, C24, C25) | USB host protection, a fault on the 3V3 rail cannot load the host above the PTC trip (R4 m5) |
| R14 | 270R | **150R** (C17471, Basic) | OC2 CTR margin, calculation below (R4 m3) |
| R18, R19 (LD3, LD2) | 1k2 | **220R** (C17557, Basic) | green LEDs about 2 mA from 3.3 V (R4 m6) |
| R22, R26 (LD4 GPIO2, LD5 3V3) | 1k (V2 draft) | **220R** (C17557) | same, R4 m6 |
| U1 / L1, L2 / P2 | generic soic8, V1 L3225M, `<pinheader>` | footprints copied from EasyEDA C7955 / C98021 / C32713270 | R4 M1, m2, m8 |

### OC2 (6N136S-TA1-L) LED current, R14 = 150 R
Path: 3V3 -> R14 -> OC2 LED (A->K) -> `MCU_TX` -> ESP32 GPIO17 (open sink through JP1, low = transmit).  Parallel branch 3V3 -> R19 -> LD2 -> `MCU_TX` (about 2 mA).
Requirement: with TX low the phototransistor must pull `VO` below the comparator reference of about 0.6 V (D6, `N$7`): IC >= (V5 - 0.6 V) / R11 = (4.81 .. 5.0 V - 0.6 V) / 4k7 = 0.9 .. 0.94 mA (V5 = 4.98 V +- 3 %).
CTR: JLC/datasheet minimum of the 6N136 class is 19 % (at IF = 16 mA); assumed flat at lower IF (conservative: CTR at 5..10 mA is not lower for this device class), temperature/ageing not included.

| Case | V3V3 | Vf (OC2) | GPIO VOL | IF with 270 R (V1) | IF with 150 R (V2) | IC min (19 %) | margin to 0.94 mA |
|---|---|---|---|---|---|---|---|
| worst (V3V3 -2 %, Vf 1.6 V, VOL 0.33 V) | 3.234 V | 1.6 V | 0.33 V | 4.8 mA -> 0.92 mA | 8.7 mA | 1.65 mA | **1.76 x** (270 R: 0.98 x) |
| typical | 3.30 V | 1.4 V | 0.10 V | 6.7 mA -> 1.27 mA | 12.0 mA | 2.28 mA | **2.4 x** (270 R: 1.35 x) |
| best (V3V3 +2 %, Vf 1.3 V, VOL 0.1 V) | 3.366 V | 1.3 V | 0.1 V | | 13.1 mA | | |

Limits: GPIO17 sink = IF(OC2) + IF(LD2) = 12 + 2.3 mA typical, 16 mA worst-high (ESP32-S3 default drive strength 20 mA, IOL abs max 28 mA); OC2 LED (6N136 absolute max 25 mA): <= 13.1 mA; R14 dissipation 25 mW.
220 R (C17557, Basic) would give only 1.2 x in the worst case, 100/120 R would raise the GPIO load without need: 150 R (C17471, Basic) is the choice.
V1 never ran from a 3.3 V LDO rail; with 270 R the worst-case margin is below 1 (marginal switching with an aged LED or a hot, low-CTR part), so this is a real improvement, not cosmetics.

### Green LEDs (LD2..LD5) at about 2 mA
KT-0805G (C2297): Vf 2.6 .. 3.1 V at 20 mA, 2.8 V typical at 2 mA.  With 220 R from 3.3 V: IF = (3.3 - 2.8 V) / 220 = 2.3 mA typical (0.9 mA at Vf 3.1 V, 3.2 mA at 2.6 V).
LD2/LD3 are active-low (`MCU_TX`/`MCU_RX` low: GPIO VOL 0.1 V gives 2.3 mA); LD3 adds that current to the OC1 output sink (6N137 IOL max 13 mA, here 0.7 mA R13 + 2.3 mA).
