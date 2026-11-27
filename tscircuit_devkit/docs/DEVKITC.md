# DevKitC variant: ESP32-S3-DevKitC-1 (N16R8) plugged into the EMS-bus interface

This folder (`tscircuit_devkit/`) is a copy of `../tscircuit/` where the on-board ESP32-S3-WROOM-1 module, USB-C, LDO and
all their support parts are replaced by two 1x22 female sockets (J1, J3) for a hand-plugged **ESP32-S3-DevKitC-1-N16R8**.
`../tscircuit/` is untouched. Build/check: `cd tscircuit_devkit && bash scripts/export_fab.sh`; outputs `fab/EMSinterface_V2.0_DevKitC-*`.

## Sources (fetched 2026-11-27)
* User guide v1.1: https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html
  (components, header tables J1/J3, ordering table: `-N16R8` = ESP32-S3-WROOM-1-N16R8, 16 MB flash, 8 MB octal PSRAM, PCB antenna)
* Dimension drawing (PDF + DXF): https://dl.espressif.com/dl/schematics/esp_idf/DXF_ESP32-S3-DevKitC-1_V1.1_20220429.pdf / `.dxf`
  (parsed with ezdxf: BOARD_OUTLINE, header hole tool marks, antenna keepout rectangle)
* Schematic / PCB: https://dl.espressif.com/dl/schematics/SCH_ESP32-S3-DevKitC-1_V1.1_20221130.pdf, `PCB_ESP32-S3-DevKitC-1_V1.1_20220429.pdf`
* Photo (isometric, headers: black plastic body on the BOTTOM side, pins pointing down): `.../_images/esp32-s3-devkitc-1-v1.1-isometric.png`

## Mechanical facts (DXF, drawing frame: x right, y up, antenna up, origin = lower-left PCB corner = USB end)
| Item | Value |
|---|---|
| PCB outline | **25.40 x 62.86 mm** (DXF; the drawing label says 62.74), corner chamfer 0.5 mm |
| PCB antenna of the module | extends **6.3 mm beyond the PCB top edge** (x 3.75..21.75), total length **69.15 mm** |
| Headers | J1 at x = 1.27 (left), J3 at x = 24.13 (right): **row spacing 22.86 mm (0.9 in)**, rows 1.27 mm inside the long edges |
| Pin pitch / count | 2.54 mm, 22 pins per row, pin 1 (3V3 / G) at y = 61.30 (1.56 mm below the antenna end of the PCB), pin 22 at y = 7.96 |
| USB | two **Micro-USB** receptacles at the lower end: left "UART" (x about 2.1..9.9 -> centre 6.0), right "USB" (ESP32-S3 native USB, centre about 19.4), front shell flush with the end of the PCB |
| Height (not in the drawing, typical values, verify with the real board) | PCB 1.6 mm; module 3.2 mm (WROOM-1 datasheet) on top; micro-USB about 2.8 mm; male header plastic body 2.5 mm below the PCB, pins about 6 mm below that |

## Pin assignment (user guide "Header Block"; J1 / J3 pin number -> name / function)
J1: 1 3V3, 2 3V3, 3 RST(EN), 4 GPIO4, **5 GPIO5**, 6 GPIO6, 7 GPIO7, 8 GPIO15, 9 GPIO16, **10 GPIO17**, 11 GPIO18, 12 GPIO8, 13 GPIO3, 14 GPIO46, 15 GPIO9, 16 GPIO10, 17 GPIO11, 18 GPIO12, 19 GPIO13, 20 GPIO14, 21 5V, 22 G.
J3: 1 G, 2 TX (GPIO43/U0TXD), 3 RX (GPIO44/U0RXD), 4 GPIO1, **5 GPIO2**, 6 GPIO42, 7 GPIO41, 8 GPIO40, 9 GPIO39, 10 GPIO38 (RGB LED, v1.1), 11 GPIO37, 12 GPIO36, 13 GPIO35, 14 GPIO0 (BOOT), 15 GPIO45, 16 GPIO48, 17 GPIO47, 18 GPIO21, 19 GPIO20 (USB D+), 20 GPIO19 (USB D-), 21 G, 22 G.
(N16R8 has octal PSRAM: GPIO35/36/37 are not usable. The initial v1.0 board has the RGB LED on GPIO48, v1.1 on GPIO38; no LED on GPIO2 or any pin used here.)

## Placement on the 110 x 60 mm board (board centre = origin, barrier x = 0, MCU side x > 0)
The DevKitC is **not rotated in the drawing frame** (its long side already runs along Y = parallel to the barrier), J1 (the row with 3V3, GPIO5, GPIO17) faces the barrier, the antenna points to +Y.
* PCB lower-left corner at **(11.00, -32.90)**, upper right (36.40, 29.96): x 11.00 .. 36.40, y -32.90 .. +29.96.
* J1 pin 1 at **(12.27, 28.40)**, J3 pin 1 at **(35.13, 28.40)**, pin n at y = 28.40 - 2.54 (n - 1); pin 22 at y = -24.94.
* **USB end overhangs the bottom board edge (y = -30) by 2.90 mm**: both micro-USB ports (centres x about 17.0 and 30.4) are outside the board and reachable.
  The top PCB edge ends 0.04 mm inside y = +30; the **antenna (6.3 mm) overhangs by 6.26 mm** (tip at y = +36.26); nothing is below it (outside the board).
  Keepout on the carrier: x 14.0 .. 33.4, y 26 .. 30, both layers (no copper, no parts, also the GND pour has a notch), checked by `check_fab.py`.
* Why this position: pin 1 of the socket must keep >= 1 mm of copper to the board edge (pin 1 at y = 28.4, body 29.67); x: the plate has to stay clear of the 4 screw-head keepouts (r 4 at +-42.25/+-19.75: plate edge 36.4 leaves 1.85 mm) and the left row at x = 12.27 leaves a 5 mm corridor (x 6..11) for the optocoupler helpers, JP1, JP2, P2.
* **Isolation**: the DevKitC plate (incl. the module above) is 14.05 mm from the nearest EMS copper (>= 8 target, >= 6 rule); it does not come closer than x = 11.0 to the barrier (limit 3.7).
* Mounting-hole keepouts free (smallest distance plate - keepout circle 1.85 mm).
* The female sockets are THT (LCSC **C20071202**, F185-1122A0ASUC2, 1x22, 2.54 mm, 8.5 mm body, "Wave Soldering", PCBA type **Economic and Standard**, extended part; only ~89 pcs in stock when checked: for 5 boards order extras or hand-solder; alternatives are 2x 1x20+1x2 strips). Footprint: hole 1.0 mm / pad 1.6 mm, origin = pin 1. No EasyEDA footprint could be fetched (host blocked), so the 1.0 mm hole and the CPL origin (assumed pin 1) must be checked in the JLC DFM / CPL preview.

## Circuit (MCU side)
| DevKitC pin | net | notes |
|---|---|---|
| J1.1, J1.2 (3V3) | `V3V3` | 3V3 produced by the DevKitC LDO (output!). Feeds OC1 VCC, pull-ups, LEDs, JP2 only |
| J1.22, J3.1, J3.21, J3.22 (G) | `GND` | MCU-side pour |
| J1.5 (GPIO5) | `MCU_RX` | OC1 output (+ R13 3k3 pull-up, LD3), P2.3 |
| J1.10 (GPIO17) | `ESP_TX` -> **JP1 (open)** -> `MCU_TX` | MCU_TX = OC2 LED cathode, R27 100k pull-up to V3V3, LD2, P2.2 |
| J3.5 (GPIO2) | R22 330R -> LD4 (yellow) -> GND | status LED beside the DevKitC (x 38.4), visible |
| all other pins incl. J1.21 (5V), J1.3 (RST), J3.14 (GPIO0) | not connected | 5V pin is never connected (it is an output while USB powers the DevKitC) |

Removed (the DevKitC provides them): U3 WROOM module, J2 USB-C, R23/R24 CC, R25/C21 shield, U4 ESD, F3 PTC, U5 AMS1117, C22-C29 (incl. tantalum C29),
R20/C20 EN, SW1/SW2 (+R21), TP1-TP3, R26/LD5 (the DevKitC has its own 3.3 V power LED). Kept: OC1/OC2 helpers (R13, R14, R18, R19, LD2, LD3, C7), JP1, JP2 + P2, R27, R22 + LD4.
Programming / firmware flashing / logs: the DevKitC's own USB ports ("UART" CP2102-type bridge = GPIO43/44, or "USB" = native USB, GPIO19/20), BOOT/RESET buttons on the DevKitC.

**Power rule**: power the DevKitC either from its own USB or via P2 + external 3V3 - never both. P2 pin 1 (3V3) is disconnected from V3V3 by the open jumper JP2; close JP2 only to power an external device from the DevKitC 3V3. Do not feed 3V3 into P2.1 while USB is connected (it would be connected to the DevKitC 3V3 net only through JP2 if closed).

## EMS-ESP32 firmware (verified 2026-11-27, raw.githubusercontent.com/emsesp/EMS-ESP32/main/src/core/system.cpp, `System::load_board_profile`)
`board_profile == "S32S3"` -> `data = {2, 18, 5, 17, 0, PHY_TYPE_NONE, ...}` = **LED GPIO2, Dallas GPIO18, Rx GPIO5, Tx GPIO17, button GPIO0**, `valid_system_gpios_ = {0, 2, 5, 17, 18}`.
This matches the DevKitC directly: Rx = J1.5 (GPIO5), Tx = J1.10 (GPIO17), LED = J3.5 (GPIO2, LD4, active high), button = GPIO0 (BOOT button on the DevKitC). Use the `s3_16M_P` firmware (16 MB flash + PSRAM, see `ESP32_EMSESP.md`). Dallas GPIO18 = J1.11, free (not connected).

## Overall envelope (for the enclosure variant, enclosure/ not touched)
* PCB 110 x 60 mm (Hammond corner notches as before, mounting holes unchanged).
* DevKitC overhang: **Y from -32.90 (USB end) to +36.26 (antenna tip) = 69.16 mm**, i.e. 2.9 mm beyond the bottom board edge (both micro-USB plugs and cables leave in -Y) and 6.26 mm beyond the top edge. X unchanged (the DevKitC lies at x 11 .. 36.4). The Hammond 1591XXCFLBK interior is 60.65 mm wide, so the box does not fit the overhang: the enclosure variant needs pockets/extensions in both long walls (top: antenna 18 mm wide at x 14.75..32.75, plastic wall, no metal; bottom: two micro-USB openings at x about 17.0 and 30.4, each about 8 x 4 mm plus plug body).
* Stack height above the carrier PCB top (typical values, to be verified): female socket 8.5 + male header plastic 2.5 + DevKitC PCB 1.6 + module 3.2 = **15.8 mm** (micro-USB tops at about 11 + 1.6 + 2.8 = 15.4 mm); plus carrier 1.6 mm: **about 17.4 mm** from the underside of the carrier. Other parts: C12/C14 electrolytics 12 mm, P1 15 mm, P2 header about 11.5 mm (stands beside the plate at x 8.6 and is plugged from above).
