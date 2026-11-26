# R3 – MCU side review: ESP32-S3 / USB-C / power / EMS-ESP32 / JP1

Reviewer: independent (R3). Date: 2026-11-26. Design state: git `e454bb9`, `dist/index/circuit.json` built 07:43:15
(newer than all sources), `fab/EMSinterface_V2.0-gerbers.zip` (07:43:33). Design files were not modified.

Primary sources used:
* EasyEDA / JLCEDA official library (https://easyeda.com, https://lceda.cn), footprint + symbol data fetched through the
  EasyEDA product API for C2913202 (ESP32-S3-WROOM-1-N16R8), C165948 (TYPE-C-31-M-12), C7519 (USBLC6-2SC6),
  C6186 (AMS1117-3.3) and C318884 (TS-1187A-B-A-B). Source: JLCEDA/EasyEDA official library.
* AMS1117 datasheet (Advanced Monolithic Systems), LCSC copy `datasheet.lcsc.com/.../e6935943fc6b1bbf350a1a0f3e90dc4a.pdf`.
* jlcsearch.tscircuit.com for part values (C27834 5.1 k, C17414 10 k, C28323 1 µF X7R, C149504 100 k, C12891 22 µF X5R 1206,
  C15850 10 µF X5R 0805, C1744 4.7 nF, C17514 1 M).
* EMS-ESP32 `main` (raw.githubusercontent.com): `src/core/system.cpp`, `src/web/WebSettingsService.cpp`,
  `src/uart/emsuart_esp32.cpp/.h`, `src/core/led.h`, `src/core/default_settings.h`, `platformio.ini`, `boards/s3_16M_P.json`.
* Analysis scripts (scratchpad, not part of the design): pad/net dump of circuit.json, geometric copper connectivity
  (traces + vias + pours), Gerber region/flash parser; a fresh `tsci export -f gerbers` into the scratchpad to cross-check.

## Summary

| # | Severity | Finding |
|---|---|---|
| 1 | **BLOCKER** | USB-C: the second D+ pad (A6) and the second D- pad (B7) of J2 have no connection. Only B6 (D+) and A7 (D-) are routed, so USB data cannot work with the plug either way round. |
| 2 | **BLOCKER** (found while checking JP1 in the Gerbers; this is a fab-output problem, not only R3) | The Gerbers in `fab/` (and a fresh `tsci export -f gerbers`) have **no traces at all**. There are zero draws outside regions on F_Cu or B_Cu. The MCU GND pour runs as solid copper through the routed paths, so the board would be shorted and unconnected. |
| 3 | **MAJOR** | P2 pin 1 (V3V3) connects directly to the AMS1117 output and the ESP32 3V3 rail. An external MCU on P2 back-feeds the LDO, through its internal OUT→IN diode, onto USB VBUS, powers the on-board ESP32 and can fight the LDO. There is no diode and no jumper. |
| 4 | MINOR | AMS1117 (C6186) uses ceramic capacitors only. The datasheet gives 22 µF solid tantalum as the stability condition and specifies no ESR window for MLCC. |
| 5 | MINOR | AMS1117 dropout margin at low VBUS (1.3 V max at 0.8 A). At 4.4–4.75 V in, VOUT can sag to about 3.1–3.3 V. This is still above the 3.0 V ESP32 minimum. |
| 6 | MINOR | JP1 is two 1.5×1.5 mm pads with a 1.04 mm gap, which is hard to bridge with solder by hand. The "TX EN" silkscreen label is about 11 mm away from JP1. |
| 7 | MINOR | J2 second VBUS pad (B4/A9) not connected (A4/B9 pad carries VBUS in both orientations; OK for 500 mA but should be connected). |
| 8 | MINOR | Antenna: there are parts within about 3–5 mm of the antenna sides (C22/C23 at y=12.8, SW1, LD5/R26, C26–C28, LD4/R22). The board edge and keepout are correct. |
| 9 | MINOR (doc) | `docs/ESP32_EMSESP.md` says S32S3 must be chosen manually on a DIY board. In fact the firmware auto-selects `S32S3` on every ESP32-S3 when the profile is "default". |
| – | OK | ESP32-S3-WROOM-1 footprint, pin map, EPAD, keepout; EN RC; BOOT; strapping pins; USB polarity ESP↔ESD↔J2; USBLC6 pinout incl. VBUS; CC 5.1 k ×2; shell RC; tactile switch pairing; EMS-ESP profile and TX/RX polarity; JP1 open; bus idle with JP1 open. |

---

## 1. BLOCKER – USB-C D+/D- duplicate pads not connected

`lib/usbc16.tsx` gives the two D+ pads the same port hint (`pin5`), and does the same for the two D- pads (`pin6`) and
the two VBUS pads (`pin2`). tscircuit turns each duplicate pad into its own port (`pin5_internal_1`, `pin6_internal_1`,
`pin2_internal_1`) and marks the pair as a `source_component_internal_connection`. That means "connected inside the
part", so the autorouter **does not route between them**. Inside the HRO TYPE-C-31-M-12 these contacts are *not* joined:
the EasyEDA symbol lists DP1 (A6), DP2 (B6), DN1 (A7) and DN2 (B7) as separate pins.

What the build contains (board coordinates, J2 at (24, 22.4), signal-row y = 22.4):

| x (mm) | contact (EasyEDA, after the 180° rotation in lib) | port | copper connection |
|---|---|---|---|
| 23.25 | B6 D+ | `DP` | trace → U4.1/6 → U3.IO20 ✔ |
| 23.75 | A7 D- | `DN` | trace → U4.3/4 → U3.IO19 ✔ |
| 24.25 | **A6 D+** | `pin5_internal_1` | **none** |
| 24.75 | **B7 D-** | `pin6_internal_1` | **none** |
| 26.40 | B4/A9 VBUS | `pin2_internal_1` | none (see #7) |
| 27.20 | B1/A12 GND | `pin1_internal_1` | GND pour ✔ |

Checked three ways: (a) the geometric connectivity script (traces, vias and pours) finds these pads isolated;
(b) no `pcb_trace` route point lies on them; (c) the trace list around J2 has only the DP, DN and CC1 routes.
A USB 2.0 plug carries D+/D- only on its A6/A7 contacts. Plugged one way it meets receptacle A6 (open) and A7 (connected).
Plugged the other way it meets B6 (connected) and B7 (open). **Either way one data line is open, so the device never
enumerates.** VBUS and CC still work, so the board powers up and looks fine, but you cannot flash or log over USB. The
only fallback is the UART0 test pads TP1/TP2 with an external USB-UART adapter and BOOT held.

Fix: give the pads distinct ports in `lib/usbc16.tsx` (for example `DP1`/`DP2`, `DN1`/`DN2`, `VBUS1`/`VBUS2`) and add
explicit traces `DP1–DP2` and `DN1–DN2` (short stubs or a via crossover right at the connector). Then connect both to
`net.USB_DP`/`net.USB_DN`, and both VBUS pads to `net.VBUS`. The same tscircuit behaviour should be checked on every
other library part with repeated port hints. Here the ESP32 EPAD (relies on the GND pour; OK) and the SW1/SW2 tactile
pads (internally connected in the switch; OK per EasyEDA) are fine.

Pin mapping itself is correct (verified against EasyEDA C165948). Raw EasyEDA order of the signal row, with the
mating face toward EasyEDA +y (down): GND, VBUS, B8, A5 CC1, B7 D-, A6 D+, A7 D-, B6 D+, A8, B5 CC2, VBUS, GND, at
x = ±3.2/±2.4/±1.75/±1.25/±0.75/±0.25 mm. Pads are 0.3×1.3 and 0.6×1.3 mm. The shell slots are 0.8×1.5 mm on
1.2×2.0 mm pads (rear, y 0.77) and 0.8×1.2 mm on 1.2×1.8 mm pads (front, y 4.95). The pegs are Ø0.6 mm at ±2.9 / 1.27.
The lib is a 180° rotation of this (mating face to +Y). That keeps the chirality, and the lib's pad table matches
exactly: CC1 at +1.25, CC2 at -1.75, DP at -0.75/+0.25, DN at -0.25/+0.75.

## 2. BLOCKER – Gerbers contain no traces

Found while checking JP1 copper and paste in the Gerbers. In `fab/EMSinterface_V2.0-gerbers.zip` and in a fresh
`npx tsci export index.circuit.tsx -f gerbers` into the scratchpad:
* F_Cu: 1256 `D01` all inside `G36/G37` regions, **0 linear draws**; aperture `D76 C0.150` (track width) defined but never selected. B_Cu: 616 / 0, same.
* A point on the routed USB_DN bottom-layer segment (23.6, 18.0) lies inside the solid MCU GND pour region of B_Cu
  with no clearance cut-out there. The pour was computed without the traces, so it would short the vias and
  connections that are missing.
* Pad flashes and pad clearances are present, which is why JP1 (below) looks correct in the Gerbers.

The traces do exist in `dist/index/circuit.json` (160 `pcb_trace`, 104 vias). The export path used for `fab/` loses
the autorouted traces. Regenerate the Gerbers from the routed circuit.json, for example with circuit-json-to-gerber
on `dist/index/circuit.json`, or with an export option that keeps the build's routing. Then open the result in a
Gerber viewer before ordering. Owner: fab/integration reviewer, flagged here because ordering as-is gives a dead board.

## 3. MAJOR – P2.1 V3V3 is tied to the LDO output with no back-feed protection

`P2.pin1 = net.V3V3` is the same net as `U5.VOUT/TAB`, `U3.3V3`, OC1 VCC, and so on. V1 used P2.1 as the 3V3
*input* from an external MCU. V2 now also has its own regulator and its own ESP32 on that rail. Risks when an
external MCU is attached to P2 as the spec intends:
* **External 3V3 without USB attached.** The AMS1117 datasheet ("Protection Diodes") says *"…the internal diode
  between the input and output pins of the device…"*, so VOUT > VIN conducts into VIN. VBUS (C24/C25, U4 VBUS, the
  USB-C VBUS pins) is back-fed to about 2.6–2.8 V. The external MCU's regulator then also powers the on-board
  ESP32-S3: Wi-Fi bursts of about 355 mA (JLC C2913202 data) on top of its own load, and a typical devkit AMS1117
  is shared with its own ESP32.
* **External 3V3 and USB both present.** Two regulators are paralleled. AMS1117 cannot sink current, so whichever
  rail is higher supplies everything. That is not destructive, but the rail and the load sharing are undefined.
* **USB attached with an external board that has no supply on its 3V3 pin.** This board's LDO powers the external
  MCU (up to 1 A current limit), which may not be wanted.

Recommendation: put a solder jumper (open by default, labelled "3V3 EXT") in series with P2.1, or a Schottky
diode if P2.1 is only ever an input, or at least a silkscreen and README warning "P2.1 is 3V3 OUT – do not feed".
With the jumper open, an external MCU supplies only GND, TX and RX. That works because the opto MCU side (OC1 VCC,
R13, R14/OC2 LED) is powered from this board's V3V3.

## 4. MINOR – AMS1117 stability with MLCC only

The datasheet ("Stability") says *"requires the use of an output capacitor as part of the device frequency
compensation. The addition of 22 µF solid tantalum on the output will ensure stability for all operating
conditions."* It gives no ESR range for ceramics. This design has only MLCC on the output: C26 22 µF X5R 25 V 1206
(about 15–18 µF effective at 3.3 V), C27 10 µF, C28 100 nF, plus C22 10 µF and C23 100 nF at the module, about
40 µF in total with ESR in the mΩ range. Many ESP32 boards run AMS1117 like this, but it is outside the documented
condition. Recommendation: make C26 a 22 µF tantalum (A/B case; check the JLC basic/extended range), or keep the MLCC
and bench-test the load step (0→400 mA Wi-Fi TX) on the prototype. Minimum load of 10 mA is met: the ESP32 plus the
LEDs draw more than 10 mA at all times except deep sleep.

## 5. MINOR – Dropout and 3V3 budget

* Dropout: 1.1 V typ / **1.3 V max at 0.8 A** (datasheet table; Note 4). Required VIN is 3.3 + 1.3 = 4.6 V worst case
  at 0.8 A, roughly 4.4–4.5 V at the 0.4–0.5 A peak. VBUS is 4.75 V min at a host port, minus about 0.1–0.2 V of
  cable and connector drop at 0.4 A. That gives about 0.0–0.2 V of margin at worst-case peaks. With a weak hub
  (4.4 V) VOUT drops to about 3.1 V during TX bursts. That is above the ESP32-S3 minimum of 3.0 V, so not a
  blocker. Better LDOs are AP2112K-3.3 (0.6 A, 250 mV) or an LDO specified for MLCC, but the 1 A budget is not needed.
* Load on 3V3 (peak / typical):

| item | estimate |
|---|---|
| ESP32-S3-WROOM-1 | 355 mA peak TX, about 80–100 mA average Wi-Fi |
| OC1 6N137 (ICC) | 10–15 mA |
| OC2 LED via R14 270 Ω (during TX low) | about 6.7 mA |
| R13 4.7 k RX pull-up (bus low) | 0.7 mA |
| LD2, LD3 (1.2 k), LD4, LD5 (1 k) green | about 1.1–1.3 mA each, about 5 mA |
| **total** | **about 385 mA peak, about 110–130 mA average** |

* Thermal: (5 − 3.3) V × 0.13 A ≈ 0.22 W average, 0.65 W peak. Fine on SOT-223 with the tab on the V3V3 copper.
* VBUS input: C24 10 µF + C25 100 nF, which is ≤ 10 µF as USB inrush rules require. OK. There is no fuse or
  reverse-current protection on VBUS, which is acceptable for a USB device.

## 6. JP1 (ESP_TX ↔ MCU_TX) – OK, with MINOR usability notes

* circuit.json: `JP1.pin1` at (36.1, 15.0) is on net ESP_TX, with copper only to `U3.IO17` (pad 10 at (36.08, 8.75)).
  `JP1.pin2` at (36.1, 17.54) is on net MCU_TX, with copper to `R27.pin1`, `P2.2`, `OC2.3` (LED cathode) and
  `LD2.K`. The geometric connectivity check puts them in **separate groups, so JP1 is OPEN**. The solderjumper has no
  `bridged`/`bridgedPins`, and no trace or route point lies in the gap.
* Gerbers: F_Cu shows two separate 1.5×1.5 flashes, each with its own pour-clearance cut-out, and no copper between
  them. F_Paste has two 1.05×1.05 apertures with about 1.49 mm between deposits, so no paste bridge is possible. F_Mask
  has two separate openings. JP1 is not in the BOM or CPL, so nothing is placed.
* R27 100 k is from MCU_TX (interface side) to V3V3. ✔
* Bus idle with JP1 open: the OC2 LED path is V3V3 → R14 270 Ω → LED → MCU_TX. With MCU_TX held at V3V3 by R27,
  the LED has 0 V across it and is off, so the EMS TX transistor stays idle. ✔ With JP1 closed, R27 also keeps the
  line high while GPIO17 is high-Z during reset or boot.
* MINOR: the pad gap is 1.04 mm. Typical solder jumpers use 0.2–0.5 mm gaps or a split-pad shape, so a 1 mm gap
  needs a wire or a big blob. Consider a custom split pad (two 1.0×1.5 mm pads with a 0.3–0.4 mm gap, no paste) or
  an 0805 0 Ω DNP footprint.
* MINOR: the silkscreen "TX EN - open = RX only" sits at (47.5, 14.6), about 11 mm right of JP1, over the R20, C22
  and C23 area. Only the refdes "JP1" (0.6 mm) is next to the pads. Move the label next to JP1.

## 7. MINOR – J2 second VBUS pad unconnected

Pad `pin2_internal_1` (B4/A9, x = 26.4) has no copper. The A4/B9 pad still gets two VBUS plug contacts in either
orientation, so 500 mA is fine, but connect it (same fix as #1). GND pad B1/A12 connects through the pour. ✔

## 8. ESP32-S3-WROOM-1-N16R8 footprint – OK

Compared with EasyEDA C2913202 (WIRELM-SMD_ESP32-S3-WROOM-1, 10 mil units converted, origin = module outline centre;
the outline in layer 99 is 70.866 × 100.39 units = **18.00 × 25.50 mm**):

| item | EasyEDA | lib/esp32s3wroom1.tsx |
|---|---|---|
| side pads x | ±34.449 u = ±8.75 mm | ±8.75 ✔ |
| pin 1 y (from centre, toward antenna) | +20.65 u = +5.25 mm | +5.26 ✔ |
| pitch | 5 u = 1.27 mm | 1.27 ✔ |
| pin 14 / pin 27 y | −11.25 mm | −11.25 / −11.26 ✔ |
| bottom row y, x | −12.54 mm, −6.985…+6.985 | −12.54, same ✔ |
| pad size | 1.50 × 0.90 mm | 1.5 × 0.9 ✔ |
| EPAD | 3×3 of 0.9 × 0.9 mm, pitch 1.40, centre (−1.50, −2.47) | same ✔ |
| antenna boundary (silk line) | y = +6.71 mm (to +12.75) | keepout y 5.75…12.75, both layers ✔ |

Pin functions (EasyEDA symbol = lib `ESP32S3_PINLABELS`, all 41): 1 GND, 2 3V3, 3 EN, 4 IO4, 5 IO5, 6 IO6, 7 IO7,
8 IO15, 9 IO16, 10 IO17, 11 IO18, 12 IO8, 13 IO19, 14 IO20, 15 IO3, 16 IO46, 17–22 IO9–IO14, 23 IO21, 24 IO47,
25 IO48, 26 IO45, 27 IO0, 28–35 IO35–IO42, 36 RXD0, 37 TXD0, 38 IO2, 39 IO1, 40 GND, 41 GND (EPAD). ✔
Pin 1 is top-left with the antenna up in both, so there is no mirror. Placement uses rotation −90° (clockwise) with
the antenna end at x = 55 = board edge. The keepout (pcb_keepout x 48…55, |y| ≤ 9.3) and the pour notch
(x ≥ 47.95, |y| ≤ 9.5, both layers) are free of traces and vias (checked). MINOR #8: several parts sit 3–5 mm beside
the antenna end. Espressif recommends keeping metal well clear (around 15 mm) on the antenna sides as well. This
costs some range, not function.

## 9. Schematic vs Espressif guidelines – OK

* EN: R20 10 k to 3V3 and C20 1 µF X7R (C28323) to GND, SW1 EN→GND. ✔ (Espressif S3 guideline: RC 10 k / 1 µF.)
* BOOT: GPIO0 (pad 27) with R21 10 k pull-up and SW2 to GND. ✔
* Strapping: GPIO45 (pad 26), GPIO46 (pad 16) and GPIO3 (pad 15) are not connected, and no copper touches them.
  GPIO45 floats on its internal weak pull-down, so VDD_SPI = 3.3 V. That is correct for N16R8, where flash and octal
  PSRAM are 3.3 V parts; pulling GPIO45 high would select 1.8 V. ✔ GPIO46 also has a weak pull-down, which is
  required low for download mode. ✔ GPIO3 is only relevant with the JTAG-select eFuse set. ✔
* Octal PSRAM pins IO35–IO37 (pads 28–30) are unused. ✔ USB GPIO19/20 are used only for USB. ✔
* Decoupling: C22 10 µF + C23 100 nF about 4 mm from pad 2, plus C26 22 µF, C27 10 µF and C28 100 nF at the LDO. ✔
* UART0 (TXD0/RXD0) goes to TP1/TP2 with TP3 GND. ✔ Useful as the recovery path.
* USB polarity: U3.IO20 (pad 14) → USB_DP → U4 pins 1+6 → J2 DP. U3.IO19 (pad 13) → USB_DN → U4 pins 3+4 → J2 DN.
  Not swapped. ✔ (Apart from the open duplicate pads, #1.)
* USBLC6-2SC6 (EasyEDA C7519): pins 1/6 = I/O1, 2 = GND, 3/4 = I/O2, 5 = VBUS. The footprint numbering (1–3 left
  column top→bottom, 4–6 right column bottom→top) matches EasyEDA. VBUS pin 5 is on net VBUS. ✔
* CC1 → R23 5.1 k → GND and CC2 → R24 5.1 k → GND, each with its own resistor (C27834 is 5.1 kΩ). ✔ Shell: four
  THT legs. One leg is routed to R25 1 M ∥ C21 4.7 nF to GND. The other three are joined by the metal shell. ✔
* SW1/SW2 TS-1187A-B-A-B: the EasyEDA symbol joins pins 1+2 (one row) and 3+4. The lib uses row A = pins 1+2 and
  row B = pins 3+4, so the switch is not permanently shorted. ✔
* GPIO2 LED: R22 1 k → LD4 anode, cathode to GND, active high. ✔

## 10. EMS-ESP32 compatibility – OK

* Build: `platformio.ini` `[env:s3_16M_P]` ("16MB ESP32-S3 - with PSRAM - like a BBQKees S3"). `boards/s3_16M_P.json`
  has `memory_type qio_opi`, `BOARD_HAS_PSRAM`, 16 MB QIO flash, `ARDUINO_USB_MODE=1` and
  `ARDUINO_USB_CDC_ON_BOOT=1`, which matches N16R8 with native USB CDC. ✔
* Profile: `system.cpp` defines `S32S3`: `data = {2, 18, 5, 17, 0, PHY_NONE, 0,0,0,0}`, meaning LED 2, Dallas 18,
  **Rx 5, Tx 17**, button 0, led_type 0 (plain GPIO). That matches the board: IO5 = MCU_RX, IO17 = ESP_TX, IO2 = LED,
  IO0 = BOOT. ✔ `WebSettingsService.cpp set_board_profile()` sets `board_profile = "S32S3"` under
  `#elif CONFIG_IDF_TARGET_ESP32S3` when the profile is "default", so a fresh board works without configuration.
  (#9: correct `docs/ESP32_EMSESP.md`.)
* LED polarity: `led.h` has `LED_ON = HIGH`, and `led.cpp` does `digitalWrite(led_gpio_, color==OFF ? !LED_ON : LED_ON)`.
  That is active high and matches LD4 to GND. ✔
* UART: `emsuart_esp32.cpp` uses UART1, 9600 8N1, `uart_set_line_inverse(inverse_mask)`, with inversion only when
  `EMSUART_TX_INVERT`/`EMSUART_RX_INVERT` is defined. Neither is set in `platformio.ini`, so TX idles HIGH. A break is
  made by temporarily inverting TXD (`uart_gen_break`), which drives TX LOW for 10–11 bit times. Default `tx_mode` is
  5 (auto: EMS / EMS+ / HT3 timing in software). Mode 4 "HW" uses `uart_write_bytes_with_break`. None of these needs
  special hardware. The hardware logic (TX low → OC2 LED on → bus pulled; idle high → LED off) is the V1 polarity
  that worked with an S3 devkit on GPIO5/17 (README table). ✔ The RX pin gets `gpio_pullup_en(rx_gpio)` in parallel
  with R13 4.7 k, which is harmless. ✔
* GPIO validity on S3 with PSRAM: valid = 0–48 minus {3, 45–46, 26–37, 19–20, 22–25}, which includes 0, 2, 5, 17, 18. ✔
