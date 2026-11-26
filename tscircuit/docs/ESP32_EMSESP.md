# EMS-ESP32 firmware requirements and GPIO plan for ESP32-S3-WROOM-1-N16R8

Source: EMS-ESP32 `main` branch fetched via raw.githubusercontent.com on 2026-11-26
(`src/core/system.cpp` `System::load_board_profile()` / `set_valid_system_gpios()`, `platformio.ini`,
`boards/s3_16M_P.json`). ESP32-S3 pin facts from my knowledge of the Espressif datasheet (not re-fetched).

## Board profiles in firmware (order of data: led, dallas, rx, tx, button, phy, eth_power, eth_addr, eth_clk, led_type)
| profile | LED | Dallas | Rx | Tx | Button | note |
|---|---|---|---|---|---|---|
| S32 | 2 | 18 | 23 | 5 | 0 | BBQKees S32 (ESP32) |
| E32 / E32V2 / E32V2_2 | 2/2/32 | 4/14/14 | 5/4/4 | 17/5/5 | 33/34/34 | ethernet boards |
| MH-ET, NODEMCU, LOLIN | 2 | 18 | 23 / 23 / 17 | 5 / 5 / 16 | 0 | generic ESP32 |
| OLIMEX, OLIMEXPOE(W) | 0 | 0 | 36 | 4 | 34 | |
| C3MINI | 7 | 1 | 4 | 5 | 9 | Lolin C3 mini (led_type 1 = RGB) |
| S2MINI | 15 | 7 | 11 | 12 | 0 | Lolin S2 mini |
| S3MINI | 17 | 18 | 8 | 5 | 0 | LilyGO T7-S3 |
| **S32S3** | **2** | **18** | **5** | **17** | **0** | **BBQKees Gateway S3 (ESP32-S3, 16MB, PSRAM)** |

The BBQKees S3 gateway (`S32S3`) is the reference hardware for an S3 + EMS bus interface: Rx=GPIO5, Tx=GPIO17,
LED=GPIO2, Dallas=GPIO18, button=GPIO0. Its `valid_system_gpios_ = {0,2,5,17,18}`.

## ESP32-S3 16MB flash / 8MB PSRAM support: YES
* `platformio.ini` env `s3_16M_P`: "16MB ESP32-S3 - with PSRAM - like a BBQKees S3".
  `boards/s3_16M_P.json`: `memory_type qio_opi`, `-DBOARD_HAS_PSRAM`, `flash_size 16MB`, 80 MHz QIO flash,
  USB CDC on boot -> this IS the N16R8 configuration (quad flash, OCTAL PSRAM). Use the `s3_16M_P` binary.
  (`s3_32M_P` exists for 32 MB.)
* Flash requirement: 4MB builds exist (`s_4M`, english only, no SSL) but 16MB builds use partitions
  `esp32_partition_16M.csv` (OTA + recovery factory partition, 4608KB code/OTA, 2MB FS). 16MB is fine, no minimum
  beyond that. PSRAM is optional but used when present (`ENABLE_PSRAM`).
* Because PSRAM is detected, firmware additionally excludes GPIO33-37 from user GPIOs (octal).
  Generic S3 rule in firmware: valid = 0-48 minus {3, 45, 46, 26-32, 33-37 (if PSRAM), 19-20, 22-25}.
* Default build is USB-CDC on boot (`ARDUINO_USB_CDC_ON_BOOT=1`): GPIO19/20 = USB D-/D+ -> first flash via USB-C
  works with BOOT (GPIO0) + EN reset; no UART bridge needed. Keep GPIO43/44 (UART0) free/test pads for recovery.

## N16R8 pin constraints (module pins that are NOT usable)
* GPIO26-32: flash/PSRAM internal, not on module pads. GPIO33-37 (module IO35/36/37 pads 28-30): octal PSRAM, unusable on R8.
* Strapping: GPIO0 (boot, pull-up; BOOT button), GPIO3, GPIO45 (VDD_SPI, keep low/NC), GPIO46 (keep NC/low).
* USB: GPIO19 (D-), GPIO20 (D+). UART0: GPIO43 (TXD0), GPIO44 (RXD0). JTAG default pads: GPIO39-42 (MTCK/MTDO/MTDI/MTMS).

## Recommended assignment (matches BBQKees S3 profile so default `S32S3` profile or custom values work)
| function | GPIO | module pad | reason |
|---|---|---|---|
| EMS Rx (from RX optocoupler output) | **GPIO5** | pin 5 | profile S32S3 Rx; no boot function; plain GPIO |
| EMS Tx (to TX optocoupler/driver) | **GPIO17** | pin 10 | profile S32S3 Tx; no boot function |
| Status LED | **GPIO2** | pin 38 | profile S32S3 LED (LED via resistor, active high; here yellow LD4) |
| BOOT / user button | **GPIO0** | pin 27 | strapping + firmware button (profile: button=0); tactile to GND, 10k pull-up already internal |
| EN / RESET | EN | pin 3 | tactile to GND + 10k pull-up + 1uF-100nF to GND |
| optional Dallas 1-wire | GPIO18 | pin 11 | profile S32S3 Dallas, spare |
| spare 2nd LED / status | GPIO4 / GPIO6 / GPIO7 | | plain GPIOs |
| USB D-/D+ | GPIO19 / GPIO20 | pins 13 / 14 | native USB, via USBLC6-2SC6 and 0R/22R optional |
| UART0 test pads | GPIO43/44 | pins 37 / 36 | recovery / log, route to pads |

Tx note: the EMS-ESP firmware idles Tx so the bus is not driven; the opto/transistor stage polarity is from the
existing Eagle schematic. Avoid GPIO45/46/3/0 for Tx so boot-time levels cannot key the bus.
Rx/Tx use a UART with GPIO matrix, any valid GPIO works (UART1/2 chosen by firmware; GPIO5/17 are conventional).

## Settings to enter in web UI (if profile not auto-selected)
Board profile `S32S3` (BBQKees Gateway S3), or "Custom" with Rx=5, Tx=17, LED=2, Button=0, Dallas=18, led type normal.
The `S32S3` profile is auto-selected by the firmware on ESP32-S3 builds (R3 review); if it is not, choose it manually in the web UI.

## This board (V2.0 as built in tscircuit)
* GPIO5 = `MCU_RX` (OC1 output, direct), GPIO17 = `ESP_TX` -> **JP1 (default OPEN: RX-only)** -> `MCU_TX` (OC2 LED / R27 100 k pull-up to 3V3). Close JP1 to allow transmitting on the EMS bus.
* GPIO2 = status LED (R22 330 R + yellow LD4 KT-0805Y, 2.7..4.8 mA, active high), GPIO0 = BOOT button, EN = RESET button, GPIO19/20 = USB D-/D+ (USBLC6-2SC6 + USB-C), GPIO43/44 test pads TP1 (TXD0, pin 37) / TP2 (RXD0, pin 36) (+ TP3 GND) at x = 41.3 / 43.2 / 45.1, y = -13 (below the module, left to right; no silk labels since R3: the legible 1.85 mm text does not fit between the vias).
* P2 (1=3V3 via JP2 default OPEN, 2=MCU_TX, 3=MCU_RX, 4=GND) is kept for an external MCU; close JP2 only to power it from the on-board 3V3.
* 3V3 from AMS1117-3.3 (USB VBUS) with 22 uF + 10 uF + 100 nF + 100 uF tantalum (C29).
