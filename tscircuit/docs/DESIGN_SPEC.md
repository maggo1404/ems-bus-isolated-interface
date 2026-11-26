# EMS-Bus Isolated Interface V2.0 – Design Spec (tscircuit)

Binding spec for all work packages. Source of truth for the V1 circuit: `docs/netlist_v1.json` / `netlist_v1.md`.
Toolchain/API: `docs/TOOLCHAIN.md`, `docs/TSCIRCUIT_API.md`. Parts: `docs/JLCPCB_PARTS.md`. GPIOs: `docs/ESP32_EMSESP.md`.

## Goals
1. Re-implement the complete V1 circuit (all 54 parts, all 33 nets) 1:1 in tscircuit.
2. Add an on-board **ESP32-S3-WROOM-1-N16R8** (native USB, no USB-UART IC) supported by EMS-ESP32 (env `s3_16M_P`, board profile `S32S3`).
3. Add a **USB-C** receptacle (USB 2.0, device) for power + programming/serial via native USB (GPIO19 D-, GPIO20 D+).
4. **Galvanic isolation must be kept**: EMS side and MCU/USB side share NO copper; only OC1/OC2 bridge the barrier.
5. **Open solder jumpers**: JP1 between ESP32 TX (GPIO17) and the interface TX net → ex works the board cannot transmit on the EMS bus; JP2 between V3V3 and P2 pin 1 (net `P2_3V3`) so the header does not back-feed 3V3 (both jumpers: custom footprint `lib/jumper.tsx`, 0.4 mm gap, no paste).
6. Manufacturing at **JLCPCB (PCBA)**: prefer JLC **Basic** parts; every component gets `supplierPartNumbers={{ jlcpcb: ["Cxxxx"] }}` where known.

## Net naming (shared contract between files)
| Net | Side | Meaning | V1 name |
|---|---|---|---|
| `GND_EMS` | EMS | bus-side ground | GND |
| `V5_EMS` | EMS | +5 V from JW5017S buck | +5V |
| other V1 EMS nets | EMS | keep V1 names where sensible, prefix `EMS_` for N$xx | N$… |
| `GND` | MCU | MCU/USB ground (V1 MCUGND) | MCUGND |
| `V3V3` | MCU | 3.3 V from LDO (V1 MCUVCC) | MCUVCC |
| `MCU_RX` | MCU | OC1 output → ESP32 GPIO5 (V1 MCURX) | MCURX |
| `MCU_TX` | MCU | OC2 LED cathode / LD2 cathode, interface side of JP1 (V1 MCUTX) | MCUTX |
| `ESP_TX` | MCU | ESP32 GPIO17, ESP side of JP1 | – |
| `VBUS` | MCU | USB 5 V at J2 / U4 (connector side of the PTC F3) | – |
| `VBUS_F` | MCU | 5 V behind PTC F3 (SMD1206B110TFT C269119, 1.1 A hold, <= 0.21 ohm; R3 R6 m2/R7 m9): U5.VIN, C24, C25 | – |
| `USB_DP`/`USB_DN` | MCU | USB data (both A/B contacts of J2 tied to the same net) | – |
| `P2_3V3` | MCU | P2 pin 1, connected to `V3V3` only through the open jumper JP2 | – |
| `SHELL` | MCU | USB shield (4 legs), 1 MΩ ∥ 4.7 nF to GND | – |

## Part decisions
- EMS side: keep V1 values. Substitutions for JLC Basic:
  - Q1 BC847B → **BC817-40 (C20069155)**, user decision. EasyEDA SOT-23-3 pads verified: pad 1 = B, 2 = E, 3 = C (modelled as `<chip>` pins B/E/C, not `<transistor>`). R9 stays 4k7.
  - D6 1N4148 → 1N4148W SOD-123 (C81598).
  - U1 LMV393IDR → LM393DR (SOIC-8) acceptable (reviewers will check common-mode/supply current); keep LMV393 noted as fallback.
  - **D1–D5 BAT42: keep BAT42-class small-signal Schottky (low capacitance, bus signal path!)**, do NOT swap to B5819W. Footprint SOD-123. Mark LCSC "look up".
  - D7 PMEG3020EGW (power path) → B5819W SOD-123 (C8598, Basic) allowed.
  - R2–R4 68R: keep 2010.
  - C12 + C14: 2 × 1000 µF/25 V SMD electrolytic (JVJ25V1000M10X12, C49256851) in parallel, replacing the V1 2200 µF THT.
- MCU side additions:
  - U5 AMS1117-3.3 (C6186 Basic, SOT-223), input VBUS_F (behind the PTC F3): 10 µF + 100 nF; output: 22 µF + 10 µF + 100 nF near module + **C29 tantalum 100 µF/6.3 V TAJB107K006RNJ (C16133, Basic, case B; pad 1 = +)** next to U5 for LDO stability (the U3 in older text is the ESP32).
  - J2 USB-C HRO TYPE-C-31-M-12 (C165948): **every physical contact is its own port** (VBUS_L/R, GND_L/R, DP_L/R, DN_L/R, CC1, CC2, SBU1, SBU2 (NC), SH1..SH4) and the A/B pairs are tied together at netlist level (both plug orientations work); CC1, CC2 each 5.1 kΩ to GND; VBUS + D+/D- via U4 USBLC6-2SC6 ESD; shell → GND via 1 MΩ ∥ 4.7 nF (all on MCU side, isolation unaffected). Optional 22–33 Ω series not needed for S3.
  - ESP32: EN with 10 kΩ pull-up + 1 µF to GND, RESET button (EN→GND), BOOT button (GPIO0→GND, 10 k pull-up), 10 µF+100 nF at 3V3 pins. EPAD = 9 separate pads (ports GND_EP1..9), each tied to GND explicitly. Tactile switches: pads 1/2 (A) and 3/4 (B) are joined inside the switch but each pad is a separate port tied to its net, so every pad gets copper.
  - GPIO5 = MCU_RX (EMS RX), GPIO17 = ESP_TX → JP1 → MCU_TX. GPIO2 = status LED (0805 LED + 1 kΩ to GND, active high, check S32S3 LED polarity in ESP32_EMSESP.md). GPIO43/44 (UART0) → test pads.
  - JP1: `<solderjumper pinCount={2} footprint={<SolderJumper2Footprint />}>` (lib/jumper.tsx: pads 1.2 × 1.6 mm, gap 0.4 mm, `noSolderPaste`) **NOT bridged**. Silkscreen label "TX EN". JP2 identical, V3V3 ↔ P2.1 (`P2_3V3`), label "3V3 OUT". Add **R_PU 100 kΩ MCU_TX → V3V3** (interface side) for defined idle (analysis in netlist_v1.md 4b: TX low = transmit, open = idle).
  - P2 4-pin header kept (user request): 1=3V3 (via JP2, default open), 2=MCU_TX, 3=MCU_RX, 4=GND (same as V1) so an external MCU can still be used; close JP2 only to supply an external device from the on-board 3V3 (never feed 3V3 in while USB is connected).
- Antenna: module antenna at a board edge, keepout (no copper, no parts, both layers) per Espressif (≥ 15 mm × module width beyond antenna region, or antenna overhanging the edge).

## Isolation rules
- EMS components x < barrier, MCU components x > barrier; OC1/OC2 straddle the barrier.
- Creepage/clearance ≥ 6 mm between any EMS and MCU copper (pads, traces, pours, vias, both layers) – V1 had ~5.1 mm pour gap / 6.7 mm copper.
- Milled slot (`<cutout>`) ≥ 1 mm wide under each optocoupler body between the pad rows, and along the barrier where possible.
- No copper pour, trace, via, mounting-hole copper, silkscreen-only is ok, crossing the barrier. Mounting holes non-plated or per-side.
- USB shield/GND, ESP32, LDO are all MCU side.

## Board
Size free (suggestion ~100 × 50 mm), 2 layers, 1.6 mm, JLC capabilities (≥0.15 mm track/space, 0.3 mm drill). EMS terminal P1 at one edge, USB-C at an edge on MCU side, ESP32 antenna at another edge on MCU side. 4 × M3 mounting holes.

## Fab rules (checked by scripts/check_fab.py)
Via 0.3 mm drill / 0.6 mm pad, annular ring ≥ 0.13 mm; trace width ≥ 0.4 mm on power/bus nets (VBUS, V3V3, GND, GND_EMS, V5_EMS, EMS_VIN, buck SW, bus path), ≥ 0.2 mm elsewhere; copper clearance between nets ≥ 0.2 mm; barrier creepage ≥ 6 mm (check_isolation.py). tscircuit settings: see docs/TSCIRCUIT_API.md "Fab settings".

## Files
- `src/ems-side.tsx` – export `EmsSide` (all V1 parts incl. OC1/OC2 and MCU-side opto helpers R13,R14,R18,R19,LD2,LD3,C7).
- `src/mcu-side.tsx` – export `McuSide` (ESP32, USB-C, LDO + C29 tantalum, ESD, buttons, LED, JP1, JP2, R_PU, P2, test pads).
- `lib/` – custom footprints (opto SO8-GW300, USB-C, ESP32, THT parts, diodes, `jumper.tsx`).
- `index.circuit.tsx` – `<board>` with both, outline, cutouts, pours, mounting holes.
- Connection between files only through the shared nets above (`net.V3V3`, `net.GND`, `net.MCU_RX`, `net.MCU_TX`).

## V2 review fixes (R4/R5), see docs/review/FIX_LIST_R2.md
Buck input: C10 10 µF + C30 100 nF directly at U2 VIN (pin 5), L3 moved towards the SW pin; U1 / L1, L2 / P2 footprints from EasyEDA; paste apertures 100 % of the pad;
hole-to-hole spacing checked (check_fab G4), silkscreen glyph ≥ 1.0 mm / stroke ≥ 0.16 mm measured in the Gerber, off pads, pin-1 marks (G5), pour slivers (G8), paste/mask parsed from the Gerbers (G6/G7); R14 150R, LD2..LD5 yellow KT-0805Y C2296 with 330R (R3, docs/netlist_v1.md "V2 deviations"), R13 3k3, C5 4.7 nF, F3 1.1 A PTC (docs/review/FIX_LIST_R3.md); VBUS fuse F3 (net VBUS_F behind it).
